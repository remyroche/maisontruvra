"""
Service layer for handling the checkout process.
This includes order creation, payment processing, and orchestrating post-order tasks.
"""
from flask import current_app
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import (Order, OrderItem, Product, Cart, User, Address, 
                    DeliveryMethod, PaymentStatus, UserType, OrderStatus, 
                    NotificationType, CartItem)
from .cart_service import CartService
from .product_service import ProductService
from .inventory_service import InventoryService
from .b2b_service import B2BService
from .loyalty_service import add_loyalty_points_for_purchase
from .notification_service import NotificationService
from .exceptions import ServiceException, CheckoutValidationError, ResourceNotFound

from ..tasks import (
    generate_invoice_for_order_task, 
    generate_invoice_for_b2b_order_task,
    send_order_confirmation_email_task,
    send_b2b_order_confirmation_email_task,
    notify_user_of_loyalty_points_task
)

class CheckoutService:
    """
    Provides methods for processing user checkouts.
    """

    @staticmethod
    def _validate_cart_for_checkout(cart_items):
        """
        Re-validates cart items against the database to ensure stock and prices are current.
        Raises CheckoutValidationError if any discrepancy is found.
        """
        current_app.logger.info("Validating cart for checkout.")
        for item_data in cart_items:
            product = ProductService.get_product_by_id(item_data['product'].id)
            if not product:
                raise CheckoutValidationError(f"Un produit de votre panier (ID: {item_data['product'].id}) n'est plus disponible.")
            
            # Check for price changes
            if product.price != item_data['product'].price:
                raise CheckoutValidationError(f"Le prix de '{product.name}' a changé. Veuillez revoir votre panier.")
            
            # Check for stock changes
            if product.stock < item_data['quantity']:
                if product.stock == 0:
                     raise CheckoutValidationError(f"'{product.name}' n'est plus en stock.")
                raise CheckoutValidationError(f"Stock insuffisant pour '{product.name}'. Il ne reste que {product.stock} unité(s).")
        current_app.logger.info("Cart validation successful.")

    @staticmethod
    def _dispatch_post_order_tasks(order: Order):
        """
        Dispatches background tasks based on the order type (B2C or B2B).
        This centralizes post-order logic to avoid redundancy.
        """
        try:
            current_app.logger.info(f"Dispatching post-order tasks for order {order.id} (type: {order.user_type}).")
            if order.user_type == UserType.B2C:
                # --- B2C Post-Order Tasks ---
                send_order_confirmation_email_task.delay(order.id)
                generate_invoice_for_order_task.delay(order.id)
                
                points_earned = add_loyalty_points_for_purchase(order.user_id, order.total_price)
                if points_earned > 0:
                    notify_user_of_loyalty_points_task.delay(order.user_id, points_earned)

                NotificationService.create_notification(
                    order.user_id, 
                    f"Your order #{order.id} has been placed successfully.",
                    NotificationType.ORDER_CONFIRMATION
                )
            
            elif order.user_type == UserType.B2B:
                # --- B2B Post-Order Tasks ---
                send_b2b_order_confirmation_email_task.delay(order.id)
                generate_invoice_for_b2b_order_task.delay(order.id)

        except Exception as e:
            current_app.logger.error(f"Failed to dispatch one or more post-order tasks for order {order.id}: {e}")

    @staticmethod
    def create_order_from_cart(user_id: int, shipping_address_id: int, billing_address_id: int, delivery_method_id: int, payment_method: str, payment_transaction_id: str = None):
        """
        Creates a B2C order from the user's cart after validation.
        This is a core function that handles the transaction and database changes.
        """
        current_app.logger.info(f"Attempting to create B2C order for user {user_id}.")
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFound("User", user_id)

        if user.user_type == UserType.B2B:
            raise ServiceException("B2B users should use the professional checkout flow.")

        cart_contents = CartService.get_cart_contents(user_id)
        if not cart_contents or not cart_contents['items']:
            raise ServiceException("Cannot create an order from an empty cart.")
        
        CheckoutService._validate_cart_for_checkout(cart_contents['items'])

        shipping_address = Address.query.get(shipping_address_id)
        billing_address = Address.query.get(billing_address_id)
        delivery_method = DeliveryMethod.query.get(delivery_method_id)

        if not all([shipping_address, billing_address, delivery_method]) or shipping_address.user_id != user_id or billing_address.user_id != user_id:
            raise ServiceException("Invalid address or delivery method.")

        total_price = cart_contents['total'] + delivery_method.price
        payment_successful = True 
        if not payment_successful:
            raise ServiceException("Payment failed.")

        new_order = Order(
            user_id=user_id, total_price=total_price, status=OrderStatus.PENDING,
            shipping_address_id=shipping_address_id, billing_address_id=billing_address_id,
            delivery_method_id=delivery_method_id, payment_method=payment_method,
            payment_status=PaymentStatus.PAID, transaction_id=payment_transaction_id,
            user_type=UserType.B2C
        )
        db.session.add(new_order)
        db.session.flush()

        for item_data in cart_contents['items']:
            product = item_data['product']
            quantity = item_data['quantity']
            order_item = OrderItem(
                order_id=new_order.id, product_id=product.id,
                quantity=quantity, price=product.price
            )
            db.session.add(order_item)
            InventoryService.decrease_stock(product.id, quantity)

        CartService.clear_cart(cart_contents['cart'].id)
        db.session.commit()
        
        current_app.logger.info(f"Successfully created order {new_order.id} for user {user_id}.")

        # --- Trigger post-order background tasks using the centralized helper ---
        CheckoutService._dispatch_post_order_tasks(new_order)

        return new_order

    @staticmethod
    def process_user_checkout(user_id: int, checkout_data: dict):
        """
        Processes checkout for a given user, routing to B2C or B2B flow based on user type.

        :param user_id: The ID of the user checking out.
        :param checkout_data: A dictionary containing all necessary data for the checkout.
            For B2C, expects: {
                "shipping_address_id": int, "billing_address_id": int,
                "delivery_method_id": int, "payment_method": str,
                "payment_transaction_id": str | None
            }
            For B2B, expects: {
                "shipping_address_id": int, "billing_address_id": int,
                "payment_details": dict
            }
        :return: The created Order object.
        """
        current_app.logger.info(f"Processing checkout for user {user_id}")
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFound("User", user_id)

        if user.user_type == UserType.B2C:
            current_app.logger.info(f"Routing user {user_id} to B2C checkout flow.")
            try:
                order = CheckoutService.create_order_from_cart(
                    user_id=user_id,
                    shipping_address_id=checkout_data['shipping_address_id'],
                    billing_address_id=checkout_data['billing_address_id'],
                    delivery_method_id=checkout_data['delivery_method_id'],
                    payment_method=checkout_data['payment_method'],
                    payment_transaction_id=checkout_data.get('payment_transaction_id')
                )
                return order
            except KeyError as e:
                raise ServiceException(f"Missing required checkout data for B2C user: {e}")

        elif user.user_type == UserType.B2B:
            current_app.logger.info(f"Routing user {user_id} to B2B checkout flow.")
            try:
                b2b_order = B2BService.create_b2b_order(
                    user_id=user_id,
                    shipping_address_id=checkout_data['shipping_address_id'],
                    billing_address_id=checkout_data['billing_address_id'],
                    payment_details=checkout_data['payment_details']
                )

                if b2b_order:
                    CheckoutService._dispatch_post_order_tasks(b2b_order)
                    return b2b_order
                return None
            except KeyError as e:
                raise ServiceException(f"Missing required checkout data for B2B user: {e}")

        else:
            raise ServiceException(f"Unknown user type '{user.user_type}' for user {user_id}.")


    @staticmethod
    def get_available_delivery_methods(address: dict = None, cart_total: float = 0.0):
        """
        Fetches available delivery methods.
        Can be extended with logic based on address, weight, or cart value.
        """
        current_app.logger.info("Fetching available delivery methods.")
        return DeliveryMethod.query.filter_by(is_active=True).order_by(DeliveryMethod.price).all()
