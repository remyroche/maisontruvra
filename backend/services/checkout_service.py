"""
Service layer for handling the checkout process.
This includes order creation, payment processing, and orchestrating post-order tasks.
"""

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from backend.extensions import db
from backend.models import (
    Cart,
    CartItem,
    DiscountType,
    Order,
    OrderItem,
    Product,
    db,
)
from backend.models.cart_models import Cart, CartItem
from backend.models.delivery_models import DeliveryOption
from backend.models.order_models import Order, OrderItem
from backend.models.product_models import Product
from backend.models.user_models import UserType
from backend.services.address_service import AddressService
from backend.services.background_task_service import BackgroundTaskService
from backend.services.discount_service import DiscountService
from backend.services.email_service import EmailService
from backend.services.inventory_service import InventoryService
from backend.services.loyalty_service import (
    LoyaltyService,
)

# from backend.services.payment_service import PaymentService
from backend.services.pdf_service import PDFService
from backend.services.referral_service import ReferralService
from backend.services.user_service import UserService

from .exceptions import (
    CartEmptyError,
    CheckoutError,
    InsufficientStockError,
    LoyaltyError,
    PaymentError,
    ProductNotFoundError,
)


class CheckoutService:
    def __init__(self, logger):
        self.logger = logger
        self.email_service = EmailService(logger)
        self.inventory_service = InventoryService(logger)
        self.loyalty_service = LoyaltyService(logger)
        self.discount_service = DiscountService(logger)
        #        self.payment_service = PaymentService(logger)
        self.pdf_service = PDFService(logger)
        self.background_task_service = BackgroundTaskService(logger)
        self.user_service = UserService(logger)
        self.address_service = AddressService(logger)
        self.referral_service = ReferralService(logger)
        self.referral_service = ReferralService(logger)

    def process_checkout(self, validated_data, current_user=None):
        """
        Processes a checkout request for any user type (guest, B2C, B2B).
        """
        cart_id = validated_data["cart_id"]
        cart = (
            db.session.query(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.product))
            .get(cart_id)
        )
        if not cart or not cart.items:
            raise CartEmptyError("Your cart is empty or could not be found.")

        user = current_user
        shipping_address_id = validated_data.get("shipping_address_id")
        billing_address_id = validated_data.get("billing_address_id")

        # Handle Guest Checkout
        if not user:
            guest_data = validated_data["guest_info"]
            user = self.user_service.get_or_create_guest_user(
                email=guest_data["email"],
                first_name=guest_data["shipping_address"]["first_name"],
                last_name=guest_data["shipping_address"]["last_name"],
            )

            shipping_address_data = guest_data["shipping_address"]
            shipping_address_data["user_id"] = user.id
            shipping_address = self.address_service.create_address(
                shipping_address_data
            )
            shipping_address_id = shipping_address.id

            billing_address = shipping_address
            if "billing_address" in guest_data:
                billing_address_data = guest_data["billing_address"]
                billing_address_data["user_id"] = user.id
                billing_address = self.address_service.create_address(
                    billing_address_data
                )
            billing_address_id = billing_address.id

        # Core order creation logic
        try:
            # Stock Validation
            for item in cart.items:
                if not self.inventory_service.check_stock(
                    item.product_id, item.quantity
                ):
                    raise InsufficientStockError(
                        f"Insufficient stock for product: {item.product.name}"
                    )

            # Payment Processing
            total_price = self.loyalty_service.calculate_total(cart)
            payment_successful, payment_intent_id = (
                self.payment_service.process_payment(
                    total_price, validated_data["payment_token"]
                )
            )
            if not payment_successful:
                raise PaymentError("Payment processing failed.")

            is_first_order = (
                not db.session.query(Order).filter_by(user_id=user.id).first()
            )

            # Create the Order
            order = Order(
                user_id=user.id,
                total_price=total_price,
                status="paid",
                shipping_address_id=shipping_address_id,
                billing_address_id=billing_address_id or shipping_address_id,
                payment_intent_id=payment_intent_id,
                discount_id=cart.discount_id,
            )
            db.session.add(order)
            db.session.flush()

            for item in cart.items:
                price = item.price if item.price is not None else item.product.price
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=price,
                )
                db.session.add(order_item)
                self.inventory_service.decrease_stock(item.product_id, item.quantity)

            if cart.discount_id:
                self.discount_service.record_discount_usage(cart.discount_id)

            if not user.is_guest:
                self.loyalty_service.add_points(user.id, total_price)
                if is_first_order:
                    self.background_task_service.submit_task(
                        self.referral_service.complete_referral_after_first_order,
                        user.id,
                    )

            # Clear the cart
            db.session.delete(cart)
            db.session.commit()

            self.background_task_service.submit_task(
                self.send_order_confirmation, order.id
            )
            self.logger.info(
                f"Order {order.id} created successfully for user {user.id}."
            )
            return order

        except (
            SQLAlchemyError,
            CartEmptyError,
            InsufficientStockError,
            PaymentError,
        ) as e:
            db.session.rollback()
            self.logger.error(f"Checkout failed for user {user.id}: {e}")
            raise CheckoutError(f"Checkout failed: {e}") from e

    def send_order_confirmation(self, order_id):
        # This method remains largely the same, but now correctly handles all user types
        try:
            order = (
                db.session.query(Order)
                .options(
                    joinedload(Order.user),
                    joinedload(Order.items).joinedload(OrderItem.product),
                    joinedload(Order.shipping_address),
                    joinedload(Order.billing_address),
                )
                .get(order_id)
            )

            if not order:
                self.logger.error(
                    f"Order with id {order_id} not found for sending confirmation."
                )
                return

            user = order.user
            invoice_pdf_path = self.pdf_service.generate_invoice(order)
            subject = "Your Maison Truvra Order Confirmation"
            template = (
                "b2b_order_confirmation"
                if user.user_type == UserType.B2B
                else "b2c_order_confirmation"
            )
            context = {"order": order, "user": user}
            attachments = [invoice_pdf_path] if invoice_pdf_path else []

            self.email_service.send_email(
                user.email, subject, template, context, attachments
            )
        except Exception as e:
            self.logger.error(
                f"Failed to send order confirmation for order {order_id}: {e}"
            )

    def create_guest_order(self, cart_id, guest_data, payment_details):
        """
        Creates an order for a guest user.
        """
        try:
            # Get or create a guest user account
            guest_user = self.user_service.get_or_create_guest_user(
                email=guest_data["email"],
                first_name=guest_data["shipping_address"]["first_name"],
                last_name=guest_data["shipping_address"]["last_name"],
            )

            # Create shipping address for the guest
            shipping_address_data = guest_data["shipping_address"]
            shipping_address_data["user_id"] = guest_user.id
            shipping_address = self.address_service.create_address(
                shipping_address_data
            )

            # Use shipping address for billing if not provided
            billing_address_data = (
                guest_data.get("billing_address") or shipping_address_data
            )
            if "user_id" not in billing_address_data:
                billing_address_data["user_id"] = guest_user.id
            billing_address = (
                self.address_service.create_address(billing_address_data)
                if billing_address_data != shipping_address_data
                else shipping_address
            )

            # Now, call the main order creation logic with the new guest user's ID
            return self.create_order_from_cart(
                user_id=guest_user.id,
                cart_id=cart_id,
                payment_details=payment_details,
                shipping_address_id=shipping_address.id,
                billing_address_id=billing_address.id,
            )
        except Exception as e:
            self.logger.error(f"Guest checkout process failed: {e}")
            raise CheckoutError(f"Guest checkout failed: {e}") from e

    def create_order_from_cart(
        self,
        user_id,
        cart_id,
        payment_details,
        shipping_address_id,
        billing_address_id=None,
    ):
        """
        Creates an order from a cart for a given user (registered or guest).
        """
        try:
            # A guest cart won't have a user_id, so we filter by cart_id only
            cart = db.session.query(Cart).filter_by(id=cart_id).first()
            if not cart or not cart.items:
                raise CartEmptyError("Cannot create an order from an empty cart.")

            # Validate stock before creating the order
            for item in cart.items:
                if not self.inventory_service.check_stock(
                    item.product_id, item.quantity
                ):
                    product = db.session.query(Product).get(item.product_id)
                    raise InsufficientStockError(
                        f"Insufficient stock for product: {product.name}"
                    )

            # Process payment
            total_price = self.calculate_total(cart)
            payment_successful, payment_intent_id = (
                self.payment_service.process_payment(total_price, payment_details)
            )

            if not payment_successful:
                raise PaymentError("Payment failed.")

            # Create the order
            order = Order(
                user_id=user_id,
                total_price=total_price,
                status="paid",
                shipping_address_id=shipping_address_id,
                billing_address_id=billing_address_id or shipping_address_id,
                payment_intent_id=payment_intent_id,
                discount_id=cart.discount_id,
            )
            db.session.add(order)
            db.session.flush()

            # Create order items and update inventory
            for item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                db.session.add(order_item)
                self.inventory_service.decrease_stock(item.product_id, item.quantity)

            if cart.discount_id:
                self.discount_service.record_discount_usage(cart.discount_id)

            # Only add loyalty points for non-guest users
            user = self.user_service.get_user_by_id(user_id)
            if not user.is_guest:
                self.loyalty_service.add_points(user_id, total_price)

            # Clear the cart
            for item in cart.items:
                db.session.delete(item)
            db.session.delete(cart)

            db.session.commit()

            self.background_task_service.submit_task(
                self.send_order_confirmation, order.id
            )

            self.logger.info(
                f"Order {order.id} created successfully for user {user_id}."
            )
            return order

        except (
            SQLAlchemyError,
            CartEmptyError,
            InsufficientStockError,
            PaymentError,
            LoyaltyError,
        ) as e:
            db.session.rollback()
            self.logger.error(f"Error during checkout for user {user_id}: {e}")
            raise CheckoutError(f"Checkout failed: {e}") from e

    def calculate_total(self, cart):
        """
        Calculates the total price of the cart, including discounts.
        """
        subtotal = sum(item.product.price * item.quantity for item in cart.items)
        if cart.discount and self.discount_service.is_discount_valid(cart.discount):
            if cart.discount.discount_type == DiscountType.PERCENTAGE:
                discount_amount = (subtotal * cart.discount.value) / 100
                return max(0, subtotal - discount_amount)
            elif cart.discount.discount_type == DiscountType.FIXED_AMOUNT:
                return max(0, subtotal - cart.discount.value)
        return subtotal

    @staticmethod
    def create_order_from_cart(
        self,
        user_id,
        cart_id,
        payment_details,
        shipping_address_id,
        billing_address_id=None,
    ):
        """
        Creates an order from the user's cart.
        """
        try:
            cart = db.session.query(Cart).filter_by(id=cart_id, user_id=user_id).first()
            if not cart or not cart.items:
                raise CartEmptyError("Cannot create an order from an empty cart.")

            # Validate stock before creating the order
            for item in cart.items:
                if not self.inventory_service.check_stock(
                    item.product_id, item.quantity
                ):
                    product = db.session.query(Product).get(item.product_id)
                    raise InsufficientStockError(
                        f"Insufficient stock for product: {product.name}"
                    )

            # Process payment
            total_price = self.calculate_total(cart)
            payment_successful, payment_intent_id = (
                self.payment_service.process_payment(total_price, payment_details)
            )

            if not payment_successful:
                raise PaymentError("Payment failed.")

            # Create the order
            order = Order(
                user_id=user_id,
                total_price=total_price,
                status="paid",
                shipping_address_id=shipping_address_id,
                billing_address_id=billing_address_id or shipping_address_id,
                payment_intent_id=payment_intent_id,
                discount_id=cart.discount_id,
            )
            db.session.add(order)
            db.session.flush()  # Flush to get the order ID

            # Create order items and update inventory
            for item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                db.session.add(order_item)
                self.inventory_service.decrease_stock(item.product_id, item.quantity)

            # Record discount usage and add loyalty points
            if cart.discount_id:
                self.discount_service.record_discount_usage(cart.discount_id)

            self.loyalty_service.add_points(user_id, total_price)

            # Clear the cart
            db.session.delete(cart)
            db.session.commit()

            # Send order confirmation email
            self.background_task_service.submit_task(
                self.send_order_confirmation, order.id
            )

            self.logger.info(
                f"Order {order.id} created successfully for user {user_id}."
            )
            return order

        except (
            SQLAlchemyError,
            CartEmptyError,
            InsufficientStockError,
            PaymentError,
            LoyaltyError,
        ) as e:
            db.session.rollback()
            self.logger.error(f"Error during checkout for user {user_id}: {e}")
            raise CheckoutError(f"Checkout failed: {e}") from e

    def get_order_details(self, order_id):
        """
        Retrieves the details of a specific order.
        """
        try:
            order = (
                db.session.query(Order)
                .options(
                    db.joinedload(Order.user),
                    db.joinedload(Order.items).joinedload(OrderItem.product),
                    db.joinedload(Order.shipping_address),
                    db.joinedload(Order.billing_address),
                )
                .filter_by(id=order_id)
                .first()
            )

            if not order:
                raise ProductNotFoundError(f"Order with id {order_id} not found.")

            return order
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while retrieving order {order_id}: {e}")
            raise

    def get_user_orders(self, user_id):
        """
        Retrieves all orders for a specific user.
        """
        try:
            orders = (
                db.session.query(Order)
                .filter_by(user_id=user_id)
                .order_by(Order.created_at.desc())
                .all()
            )
            return orders
        except SQLAlchemyError as e:
            self.logger.error(
                f"Database error while retrieving orders for user {user_id}: {e}"
            )
            raise

    def apply_discount_code(self, cart_id, discount_code):
        """
        Applies a discount code to the cart.
        """
        try:
            cart = db.session.query(Cart).filter_by(id=cart_id).first()
            if not cart:
                raise CartEmptyError("Cart not found.")

            discount = self.discount_service.get_discount_by_code(discount_code)
            if not discount or not self.discount_service.is_discount_valid(discount):
                raise ValueError("Invalid or expired discount code.")

            cart.discount_id = discount.id
            db.session.commit()
            self.logger.info(f"Discount '{discount_code}' applied to cart {cart_id}.")
            return cart
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error applying discount to cart {cart_id}: {e}")
            raise

    def calculate_total(self, cart):
        """
        Calculates the total price of the cart, including discounts.
        """
        subtotal = sum(item.product.price * item.quantity for item in cart.items)
        if cart.discount and self.discount_service.is_discount_valid(cart.discount):
            if cart.discount.discount_type == DiscountType.PERCENTAGE:
                discount_amount = (subtotal * cart.discount.value) / 100
                return max(0, subtotal - discount_amount)
            elif cart.discount.discount_type == DiscountType.FIXED_AMOUNT:
                return max(0, subtotal - cart.discount.value)
        return subtotal

    @staticmethod
    def get_available_delivery_methods(address: dict = None, cart_total: float = 0.0):
        """
        Fetches available delivery methods.
        Can be extended with logic based on address, weight, or cart value.
        """
        current_app.logger.info("Fetching available delivery methods.")
        return (
            DeliveryOption.query.filter_by(is_active=True)
            .order_by(DeliveryOption.price)
            .all()
        )
