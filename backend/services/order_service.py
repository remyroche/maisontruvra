import uuid
import logging
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..extensions import socketio
from ..models import (
    Order,
    OrderItem,
    Product,
    Cart,
    OrderStatusEnum,
    CartItem,  # Added CartItem to the import list
)
from .exceptions import (
    ServiceException,
    NotFoundException,
    ValidationException,
    BusinessRuleException,
)
from .inventory_service import InventoryService
from .loyalty_service import LoyaltyService

# Note: NotificationService is no longer imported here to prevent circular dependency
from .monitoring_service import MonitoringService
from .invoice_service import InvoiceService
from .email_service import EmailService

# Configure a logger for this service
logger = logging.getLogger(__name__)


class OrderService:
    """
    Handles all business logic related to order processing, creation, and fulfillment.
    """

    def __init__(self, session=None):
        """
        Initializes the OrderService with necessary dependent services.
        A session can be passed for specific transactional contexts, otherwise uses the global db.session.
        """
        self.session = session or db.session
        self.inventory_service = InventoryService(self.session)
        self.loyalty_service = LoyaltyService()
        self.email_service = EmailService()
        self.invoice_service = InvoiceService()
        self.monitoring_service = MonitoringService()
        self.logger = logger
        # self.notification_service is removed from __init__

    # --- Core Order Creation ---

    def create_order_from_cart(self, user_id: uuid.UUID, checkout_data: dict):
        """
        Creates a final order from a user's cart, processes payment, updates inventory,
        and hooks into loyalty/referral services. This is a single, atomic transaction.
        """
        cart = self.session.query(Cart).filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            raise ValidationException("Cannot create an order from an empty cart.")

        # Extract data from the checkout payload
        shipping_address_id = checkout_data.get("shipping_address_id")
        checkout_data.get("payment_token")  # Placeholder for payment gateway token
        creator_ip = checkout_data.get("creator_ip_address")

        if not shipping_address_id:
            raise ValidationException(
                "Shipping address is required to create an order."
            )

        try:
            # --- Transaction Start ---

            # 1. Lock inventory rows for products in the cart to prevent race conditions
            product_ids = [item.product_id for item in cart.items]
            products = (
                self.session.query(Product)
                .filter(Product.id.in_(product_ids))
                .with_for_update()
                .all()
            )
            product_map = {p.id: p for p in products}

            # 2. Pre-check stock availability
            for item in cart.items:
                product = product_map.get(item.product_id)
                if not product or not self.inventory_service.is_stock_sufficient(
                    product.id, item.quantity
                ):
                    raise ValidationException(
                        f"Not enough stock for {getattr(product, 'name', 'Unknown Product')}."
                    )

            # 3. Create the initial Order record
            new_order = Order(
                user_id=user_id,
                shipping_address_id=shipping_address_id,
                billing_address_id=checkout_data.get(
                    "billing_address_id", shipping_address_id
                ),  # Default to shipping
                creator_ip_address=creator_ip,
                order_status=OrderStatusEnum.PENDING,
                total_amount=0,  # Will be calculated next
            )
            self.session.add(new_order)

            # 4. Create OrderItems, calculate total, and decrease stock
            total_amount = 0
            for item in cart.items:
                product = product_map[item.product_id]
                order_item = OrderItem(
                    order=new_order,
                    product_id=product.id,
                    quantity=item.quantity,
                    price_at_purchase=product.price,
                )
                self.inventory_service.decrease_stock(product.id, item.quantity)
                total_amount += order_item.price_at_purchase * order_item.quantity
                self.session.add(order_item)

            new_order.total_amount = total_amount

            # 5. Process Payment (Placeholder for real payment gateway logic)
            # payment_successful = PaymentGateway.charge(payment_token, new_order.total_amount)
            # if not payment_successful:
            #     raise BusinessRuleException("Payment processing failed.")
            new_order.order_status = (
                OrderStatusEnum.PROCESSING
            )  # Assume payment is successful

            # 6. Clear the user's cart
            self.session.query(CartItem).filter_by(cart_id=cart.id).delete()
            self.session.delete(cart)

            self.session.commit()
            # --- Transaction End ---

            # 7. --- Post-Transaction Asynchronous Tasks ---
            self._execute_post_order_tasks(new_order)

            return new_order

        except (ValidationException, NotFoundException) as e:
            self.session.rollback()
            self.monitoring_service.log_warning(
                f"Order creation failed for user {user_id}: {str(e)}", "OrderService"
            )
            raise e
        except Exception as e:
            self.session.rollback()
            self.monitoring_service.log_error(
                f"Critical error creating order for user {user_id}: {str(e)}",
                "OrderService",
                exc_info=True,
            )
            raise ServiceException(
                "Could not create order due to an unexpected server error."
            )

    # --- Order Retrieval ---

    def get_order_by_id(self, order_id: uuid.UUID, user_id: uuid.UUID = None):
        """
        Retrieves a single order by its ID, ensuring it belongs to the user if user_id is provided.
        """
        query = self.session.query(Order).options(
            subqueryload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.shipping_address),
        )
        if user_id:
            query = query.filter_by(id=order_id, user_id=user_id)
        else:
            query = query.filter_by(id=order_id)

        order = query.first()
        if not order:
            raise NotFoundException(resource_name="Order", resource_id=order_id)
        return order

    def get_user_orders_paginated(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 10
    ):
        """
        Gets a paginated list of orders for a specific user.
        """
        query = (
            self.session.query(Order)
            .filter_by(user_id=user_id)
            .order_by(Order.created_at.desc())
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_all_orders_paginated(
        self,
        page: int,
        per_page: int,
        status: str = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ):
        """
        Gets all orders for an admin view, with optional filtering and sorting.
        """
        query = self.session.query(Order).options(joinedload(Order.user))

        if status:
            try:
                status_enum = OrderStatusEnum(status)
                query = query.filter(Order.order_status == status_enum)
            except ValueError:
                self.logger.warning(f"Invalid status filter '{status}' provided.")

        order_by_attr = getattr(Order, sort_by, Order.created_at)
        if sort_direction == "desc":
            query = query.order_by(db.desc(order_by_attr))
        else:
            query = query.order_by(db.asc(order_by_attr))

        return query.paginate(page=page, per_page=per_page, error_out=False)

    # --- Order Management ---

    def update_order_status(
        self, order_id: uuid.UUID, new_status_str: str, tracking_number: str = None
    ):
        """
        Updates the status of an order and triggers relevant notifications.
        """
        try:
            order = self.get_order_by_id(order_id)
            original_status = order.order_status.value

            try:
                new_status_enum = OrderStatusEnum(new_status_str)
            except ValueError:
                raise ValidationException(
                    f"'{new_status_str}' is not a valid order status."
                )

            order.order_status = new_status_enum
            if tracking_number:
                order.tracking_number = tracking_number

            self.session.commit()
            self.logger.info(
                f"Order {order_id} status updated from '{original_status}' to '{new_status_str}'."
            )

            # ** FIX: Import NotificationService here **
            from .notification_service import NotificationService

            notification_service = NotificationService()

            # Trigger notification task
            notification_service.send_order_status_update.delay(
                order_id=order.id, new_status=new_status_str
            )

            return order
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(
                f"Database error updating order status for order {order_id}: {e}",
                exc_info=True,
            )
            raise ServiceException(
                "Failed to update order status due to a database error."
            )

    def cancel_order(self, order_id: uuid.UUID, user_id: uuid.UUID = None):
        """
        Cancels an order, restocks the items, and notifies the customer.
        """
        order = self.get_order_by_id(
            order_id, user_id
        )  # Ensures user can only cancel their own order

        if not order.is_cancellable():
            raise BusinessRuleException(
                f"Order in status '{order.order_status.value}' cannot be cancelled."
            )

        try:
            # Restock items by increasing inventory
            for item in order.items:
                # Assuming increase_stock handles serialized items correctly if applicable
                self.inventory_service.increase_stock(item.product_id, item.quantity)

            # Update status via the standardized method
            return self.update_order_status(order_id, "CANCELLED")

        except (SQLAlchemyError, BusinessRuleException) as e:
            self.session.rollback()
            self.logger.error(f"Error cancelling order {order_id}: {e}", exc_info=True)
            raise ServiceException("Failed to cancel the order.")

    # --- Private Helper Methods ---

    def _execute_post_order_tasks(self, order: Order):
        """
        Offloads non-critical, post-transaction tasks to background workers (Celery).
        This ensures the user gets a fast response and failures here don't block the order.
        """
        try:
            # ** FIX: Import NotificationService here **
            from .notification_service import NotificationService

            notification_service = NotificationService()

            # Notify admin dashboard of the new order via WebSockets
            socketio.emit(
                "new_order",
                {"order_id": str(order.id), "total": str(order.total_amount)},
                namespace="/admin",
            )

            # Queue tasks for Celery
            self.loyalty_service.add_points_for_purchase.delay(
                user_id=order.user_id, order_id=order.id
            )
            notification_service.send_order_confirmation.delay(order_id=order.id)
            self.invoice_service.generate_invoice_pdf.delay(order_id=order.id)

            self.monitoring_service.log_info(
                f"Successfully queued post-order tasks for order {order.id}",
                "OrderService",
            )
        except Exception as e:
            # Log failure to queue, but don't fail the entire request
            self.monitoring_service.log_error(
                f"Failed to queue post-order tasks for order {order.id}: {e}",
                "OrderService",
                exc_info=True,
            )
