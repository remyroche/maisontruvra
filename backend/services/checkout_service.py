from backend.database import db
from backend.models.user_models import User, Address
from backend.models.order_models import DeliveryMethod
from backend.services.exceptions import NotFoundException, ValidationException

# backend/services/checkout_service.py
from flask import current_app
from backend.services.cart_service import get_cart_by_id, clear_cart
from backend.services.order_service import create_order, create_b2b_order, get_order_by_id
from backend.services.inventory_service import update_stock_from_order
from backend.services.loyalty_service import add_loyalty_points_for_purchase
# Assuming a payment service exists
# from backend.services.payment.stripe_service import create_stripe_checkout_session 
from backend.models.order_models import OrderStatus
from backend.tasks import (
    generate_invoice_for_order_task, 
    generate_invoice_for_b2b_order_task,
    send_order_confirmation_email_task,
    send_b2b_order_confirmation_email_task,
    notify_user_of_loyalty_points_task
)

class CheckoutService:
    @staticmethod
    def create_order_from_cart(user_id: int, shipping_address_id: int, billing_address_id: int, payment_method: str, payment_token: str) -> Order:
        """
        Creates an order from the user's cart. Handles both B2B and B2C users.
        """
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found.")

        if user.user_type == UserType.B2B:
            # Use the dedicated B2B order creation which applies tier pricing
            return B2BService.create_b2b_order(user_id, shipping_address_id, billing_address_id)

        # B2C order creation logic
        cart_data = CartService.get_cart(user_id)
        if not cart_data or not cart_data['items_details']:
            raise ServiceError("Cannot create an order from an empty cart.")
        
        cart = cart_data['cart']
        
        # Here you would typically process payment with the payment_token
        # For now, we'll assume payment is successful
        
        new_order = Order(
            user_id=user_id,
            total_cost=cart_data['total'],
            status=OrderStatus.PENDING,
            shipping_address_id=shipping_address_id,
            billing_address_id=billing_address_id,
            payment_method=payment_method,
            user_type=UserType.B2C
        )
        
        for item_detail in cart_data['items_details']:
            item = item_detail['item']
            order_item = OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item_detail['discounted_price']
            )
            new_order.items.append(order_item)
            
        db.session.add(new_order)

        # Empty the cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        # Post-order actions
        EmailService.send_order_confirmation_email(user.email, order_id=new_order.id)
        NotificationService.create_notification(
            user_id, 
            f"Your order #{new_order.id} has been placed successfully.",
            NotificationType.ORDER_CONFIRMATION
        )

        return new_order


    @staticmethod
    def get_user_addresses(user_id: int):
        """Fetches all addresses for a given user."""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user.addresses

    @staticmethod
    def add_user_address(user_id: int, data: dict):
        """Adds a new address for a user and handles the 'is_default' flag."""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found")

        if data.get('is_default'):
            # If this new address is set as default, unset any other default addresses.
            Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

        new_address = Address(user_id=user_id, **data)
        db.session.add(new_address)
        db.session.commit()
        return new_address

    @staticmethod
    def update_user_address(user_id: int, address_id: int, data: dict):
        """Updates an existing address for a user."""
        address = db.session.get(Address, address_id)
        if not address or address.user_id != user_id:
            raise NotFoundException("Address not found or permission denied")

        if data.get('is_default'):
            # Unset other default addresses if this one is being set as default.
            Address.query.filter(Address.id != address_id, Address.user_id == user_id, Address.is_default == True).update({"is_default": False})

        for key, value in data.items():
            setattr(address, key, value)
        
        db.session.commit()
        return address

    @staticmethod
    def get_available_delivery_methods(address: dict, cart_total: float):
        """
        Fetches available delivery methods.
        This is a placeholder for more complex logic that might depend on address, weight, or cart value.
        """
        # For now, return all active delivery methods.
        return DeliveryMethod.query.filter_by(is_active=True).order_by(DeliveryMethod.price).all()

    @staticmethod
    def process_user_checkout(user, cart, payment_token):
        """Processes checkout for a logged-in user."""
        # This function would likely handle payment processing first
        # For this example, we assume payment is successful and an order is created.
        order = create_order(user.id, cart, "stripe_payment_intent_id") # Example
        
        if order:
            db.session.commit()
            update_stock_from_order(order.id, is_b2b=False)
            clear_cart(cart.id)
            
            # Schedule background tasks
            send_order_confirmation_email_task.delay(order.id)
            generate_invoice_for_order_task.delay(order.id)
            
            points_earned = add_loyalty_points_for_purchase(user.id, order.total)
            if points_earned > 0:
                notify_user_of_loyalty_points_task.delay(user.id, points_earned)
                
            return order
        return None
    
    @staticmethod
    def process_guest_checkout(guest_data, cart, payment_token):
        """Processes checkout for a guest user."""
        # Logic to create a temporary user or handle guest orders
        order = create_order(None, cart, "stripe_payment_intent_id", guest_data=guest_data)
    
        if order:
            db.session.commit()
            update_stock_from_order(order.id, is_b2b=False)
            clear_cart(cart.id)
    
            # Schedule background tasks
            send_order_confirmation_email_task.delay(order.id)
            generate_invoice_for_order_task.delay(order.id)
            
            return order
        return None
    
    @staticmethod
    def process_b2b_checkout(user, cart, payment_details):
        """Processes checkout for a B2B user."""
        b2b_order = create_b2b_order(user.id, cart, payment_details)
    
        if b2b_order:
            db.session.commit()
            update_stock_from_order(b2b_order.id, is_b2b=True)
            clear_cart(cart.id)
            
            # Schedule background tasks for B2B
            send_b2b_order_confirmation_email_task.delay(b2b_order.id)
            generate_invoice_for_b2b_order_task.delay(b2b_order.id)
    
            return b2b_order
        return None
