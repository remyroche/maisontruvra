"""
Service layer for handling the checkout process.
This includes order creation, payment processing, and orchestrating post-order tasks.
"""
from flask import current_app
from sqlalchemy.orm import joinedload

from backend.extensions import db
from backend.models.order_models import Order, OrderItem, PaymentStatus, OrderStatus
from backend.models.product_models import Product
from backend.models.user_models import User, UserType
from backend.models.address_models import Address
from backend.models.delivery_models import DeliveryMethod
from backend.models.notification_models import NotificationType
from backend.models.cart_models import Cart, CartItem

from backend.services.product_service import ProductService
from backend.services.inventory_service import InventoryService
from backend.services.b2b_service import B2BService
from backend.services.cart_service import CartService
from backend.services.loyalty_service import add_loyalty_points_for_purchase
from backend.services.notification_service import NotificationService
from backend.services.exceptions import ServiceException, CheckoutValidationError, ResourceNotFound
from backend.services.payment_service import PaymentService # Assuming this service exists


from backend.tasks import (
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
                raise CheckoutValidationError(f"A product in your cart (ID: {item_data['product'].id}) is no longer available.")
            
            # Check for price changes
            if product.price != item_data['product'].price:
                raise CheckoutValidationError(f"The price of '{product.name}' has changed. Please review your cart.")
            
            # Check for stock changes
            if product.stock < item_data['quantity']:
                if product.stock == 0:
                        raise CheckoutValidationError(f"'{product.name}' is no longer in stock.")
                raise CheckoutValidationError(f"Insufficient stock for '{product.name}'. Only {product.stock} unit(s) left.")
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
    def create_order_from_cart(self, user_id, cart_id, payment_details, shipping_address_id, billing_address_id=None):
        """
        Creates an order from the user's cart.
        """
        try:
            cart = session.query(Cart).filter_by(id=cart_id, user_id=user_id).first()
            if not cart or not cart.items:
                raise CartEmptyError("Cannot create an order from an empty cart.")

            # Validate stock before creating the order
            for item in cart.items:
                if not self.inventory_service.check_stock(item.product_id, item.quantity):
                    product = session.query(Product).get(item.product_id)
                    raise InsufficientStockError(f"Insufficient stock for product: {product.name}")

            # Process payment
            total_price = self.calculate_total(cart)
            payment_successful, payment_intent_id = self.payment_service.process_payment(total_price, payment_details)

            if not payment_successful:
                raise PaymentError("Payment failed.")

            # Create the order
            order = Order(
                user_id=user_id,
                total_price=total_price,
                status='paid',
                shipping_address_id=shipping_address_id,
                billing_address_id=billing_address_id or shipping_address_id,
                payment_intent_id=payment_intent_id
            )
            session.add(order)
            session.flush()  # Flush to get the order ID

            # Create order items and update inventory
            for item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                session.add(order_item)
                self.inventory_service.decrease_stock(item.product_id, item.quantity)

            # Apply discounts and loyalty points
            if cart.discount_id:
                self.discount_service.apply_discount_to_order(order.id, cart.discount_id)
            
            self.loyalty_service.add_points(user_id, total_price)

            # Clear the cart
            session.delete(cart)
            session.commit()

            # Send order confirmation email
            self.background_task_service.submit_task(self.send_order_confirmation, order.id)

            self.logger.info(f"Order {order.id} created successfully for user {user_id}.")
            return order

        except (SQLAlchemyError, CartEmptyError, InsufficientStockError, PaymentError, LoyaltyError) as e:
            session.rollback()
            self.logger.error(f"Error during checkout for user {user_id}: {e}")
            raise CheckoutError(f"Checkout failed: {e}") from e

    @staticmethod
    def process_user_checkout(user_id: int, checkout_data: dict):
        """
        Processes checkout for a given user, routing to B2C or B2B flow based on user type.

        :param user_id: The ID of the user checking out.
        :param checkout_data: A dictionary containing all necessary data for the checkout.
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
