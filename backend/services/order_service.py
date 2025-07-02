import uuid
from backend import db
from backend.models.order_models import db, Order, OrderItem
from backend.models.product_models import Product
from backend.models.cart_models import Cart
from backend.models.address_models import Address
from backend.services.loyalty_service import LoyaltyService
from .exceptions import ServiceError, NotFoundException, ValidationException, ServiceException
from sqlalchemy.orm import joinedload, subqueryload
from backend.models.user_models import User
from backend.models.b2b_models import B2BUser
from backend.services.inventory_service import InventoryService
from backend.services.referral_service import ReferralService
from backend.services.pdf_service import PDFService
from flask import current_app
from .notification_service import NotificationService
from .monitoring_service import MonitoringService
from ..extensions import socketio
from backend.services.invoice_service import InvoiceService

from backend.services.email_service import EmailService
from sqlalchemy.exc import SQLAlchemyError
from backend.extensions import db
from ..models import Order, OrderItem, Product, db
from ..models.order_models import OrderStatusEnum




class OrderService:
    """
    Handles business logic related to order processing, creation, and fulfillment.
    """
    def __init__(self, session):
        self.session = session
        self.inventory_service = InventoryService(session)
        self.referral_service = ReferralService(session) # Instantiate ReferralService
        self.email_service = EmailService()
        self.pdf_service = PDFService()
        self.logger = logger

    @staticmethod
    def get_orders_by_user(user_id, page=1, per_page=10):
        """
        Gets a paginated list of orders for a user, eagerly loading items and addresses.
        """
        return Order.query.filter_by(user_id=user_id).options(
            subqueryload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.shipping_address)
        ).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
    def get_order_by_id(self, order_id):
        """Retrieves a single order by its ID."""
        return db.session.query(Order).get(order_id)


    def get_all_orders(self, page=1, per_page=20):
        """Retrieves all orders with pagination."""
        return db.session.query(Order).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_user_orders(self, user_id):
        """Retrieves all orders for a specific user."""
        return db.session.query(Order).filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    def update_order_status(self, order_id, new_status, notify_customer=True):
        """
        Updates the status of an order and optionally notifies the customer.
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order with id {order_id} not found.")

            original_status = order.status
            order.status = new_status
            db.session.commit()
            self.logger.info(f"Order {order_id} status updated from '{original_status}' to '{new_status}'.")
    
            # Validate the status against the enum
            try:
                status_enum = OrderStatusEnum(status)
            except ValueError:
                raise ValueError(f"'{status}' is not a valid order status.")
    
            order.order_status = status_enum
            
            # Only add tracking info if provided.
            if tracking_number:
                order.tracking_number = tracking_number
            if tracking_url:
                order.tracking_url = tracking_url

            if notify_customer:
                user = order.user
                subject = f"Your Order #{order.id} Status Update"
                template = None

                if new_status == 'shipped':
                    template = "order_shipped"
                elif new_status == 'cancelled':
                    template = "order_cancelled"
                # Add more conditions for other statuses like 'delivered', 'processing', etc.

                if template and user:
                    context = {"order": order, "user": user}
                    self.email_service.send_email(user.email, subject, template, context)
                    self.logger.info(f"Sent order status update email to {user.email} for order {order_id}.")

            return order
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error updating order status for order {order_id}: {e}")
            raise

    def cancel_order(self, order_id):
        """
        Cancels an order and restocks the items.
        """
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order with id {order_id} not found.")

            if order.status in ['shipped', 'delivered', 'cancelled']:
                raise ValueError(f"Cannot cancel order with status '{order.status}'.")

            # Restock items
            for item in order.items:
                self.inventory_service.increase_stock(item.product_id, item.quantity)
            
            # Update status
            return self.update_order_status(order_id, 'cancelled', notify_customer=True)

        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            raise
            
    @staticmethod
    def create_order_from_cart(user_id, user_type, checkout_data):
        """
        Creates a final order from a user's cart, processes payment, updates inventory,
        and hooks into loyalty/referral services.
        Handles both B2C and B2B users.
        """
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            raise ValidationException("Cannot create an order from an empty cart.")

        # --- Data from checkout form ---
        shipping_address_id = checkout_data.get('shipping_address_id')
        billing_address_id = checkout_data.get('billing_address_id')
        payment_token = checkout_data.get('payment_token') # From payment gateway (e.g., Stripe)
        creator_ip = checkout_data.get('creator_ip_address')

        try:
            # The entire process is wrapped in a transaction
            with db.session.begin_nested():
                # 1. Lock inventory rows for products in the cart to prevent race conditions
                product_ids = [item.product_id for item in cart.items]
                products = Product.query.filter(Product.id.in_(product_ids)).with_for_update().all()
                product_map = {p.id: p for p in products}

                # 2. Check stock availability
                for item in cart.items:
                    product = product_map.get(item.product_id)
                    if not product or product.stock < item.quantity:
                        raise ValidationException(f"Not enough stock for {product.name}.")

                # 3. Create the Order record, handling B2C vs B2B
                new_order_data = {
                    "user_type": user_type,
                    "shipping_address_id": shipping_address_id,
                    "billing_address_id": billing_address_id,
                    "creator_ip_address": creator_ip,
                    "status": "pending_payment" 
                }
                if user_type == 'b2b':
                    b2b_user = B2BUser.query.get(user_id)
                    if not b2b_user:
                        raise NotFoundException("B2B user not found.")
                    new_order_data['b2b_account_id'] = b2b_user.account_id
                    new_order_data['created_by_user_id'] = b2b_user.id
                else: # b2c
                    new_order_data['user_id'] = user_id
                
                new_order = Order(**new_order_data)
                db.session.add(new_order)
                
                # 4. Create OrderItems, calculate total, and decrease stock
                total_amount = 0
                for item in cart.items:
                    product = product_map[item.product_id]
                    order_item = OrderItem(
                        order=new_order,
                        product_id=product.id,
                        quantity=item.quantity,
                        price_at_purchase=product.price
                    )
                    InventoryService.decrease_stock(product.id, item.quantity)
                    total_amount += order_item.price_at_purchase * order_item.quantity
                    db.session.add(order_item)

                new_order.total_amount = total_amount
                
                # 5. Process Payment (placeholder for payment gateway integration)
                # payment_successful = PaymentGateway.charge(payment_token, new_order.total_amount)
                # if not payment_successful:
                #     raise ServiceError("Payment processing failed.")
                new_order.status = "processing" # Assume payment is successful for now

                # 6. Clear the user's cart
                for item in cart.items:
                    db.session.delete(item)
                db.session.delete(cart)

            # 7. Commit the transaction
            db.session.commit()
            
            # --- Post-Transaction Tasks (safe to run after commit) ---
            socketio.emit('new_order', new_order.to_dict(), namespace='/admin')
            
            # 8. Award loyalty points for the purchase
            try:
                LoyaltyService.add_points_for_purchase(
                    user_id=user_id,
                    order_total=new_order.total_amount,
                    order_id=new_order.id
                )
            except Exception as e:
                MonitoringService.log_error(
                    f"Failed to award loyalty points for order {new_order.id}: {e}",
                    "OrderService"
                )

            # 9. Handle referral logic for the new user's first order
            try:
                LoyaltyService.reward_referrer_for_order(
                    referee_id=user_id,
                    order_total_euros=new_order.total_amount
                )
            except Exception as e:
                MonitoringService.log_error(
                    f"Failed to process referral for order {new_order.id}: {e}",
                    "OrderService"
                )

            # 10. Offload PDF and Email generation to Celery
            try:
                InvoiceService.create_invoice_for_order.delay(new_order.id)
                NotificationService.send_order_confirmation_email.delay(new_order.id)
                MonitoringService.log_info(
                    f"Successfully queued post-order tasks for order {new_order.id}",
                    "OrderService"
                )
            except Exception as e:
                MonitoringService.log_error(
                    f"Failed to queue post-order tasks for order {new_order.id}: {e}",
                    "OrderService"
                )

            return new_order

        except (ValidationException, NotFoundException) as e:
            db.session.rollback()
            MonitoringService.log_warning(
                f"Order creation failed for user {user_id}: {str(e)}",
                "OrderService"
            )
            raise e
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to create order from cart for user {user_id}: {str(e)}",
                "OrderService",
                exc_info=True
            )
            raise ServiceError("Could not create order due to an unexpected error.")


    @staticmethod
    def get_all_orders_paginated(page, per_page, status=None, sort_by='created_at', sort_direction='desc'):
        """
        Gets all orders for an admin, eagerly loading user and items.
        """
        query = Order.query.options(
            joinedload(Order.user),
            subqueryload(Order.items).joinedload(OrderItem.product)
        )
        if status:
            query = query.filter(Order.status == status)

        order_by_attr = getattr(Order, sort_by, Order.created_at)
        if sort_direction == 'desc':
            query = query.order_by(db.desc(order_by_attr))
        else:
            query = query.order_by(db.asc(order_by_attr))
        page=page
        per_page=per_page
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def create_guest_order(data):
        """
        Handles the logic for creating an order from a guest.
        """
        if not all(k in data for k in ['guest_details', 'shipping_address', 'cart_items', 'payment_token']):
            raise ServiceError("Missing required data for guest order.", 400)

        try:
            address_data = data['shipping_address']
            guest_address = Address(
                street=address_data['street'],
                city=address_data['city'],
                postal_code=address_data['postal_code'],
                country=address_data['country'],
            )
            db.session.add(guest_address)
            
            new_order = Order(
                guest_email=data['guest_details']['email'],
                guest_phone=data['guest_details'].get('phone'),
                shipping_address=guest_address,
                status='PENDING',
                total=OrderService._calculate_total(data['cart_items']) 
            )
            db.session.add(new_order)
            
            for item_data in data['cart_items']:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    raise ServiceError(f"Product with ID {item_data['product_id']} not found.", 404)
                
                order_item = OrderItem(
                    order=new_order,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    price_at_purchase=product.price
                )
                db.session.add(order_item)

            new_order.status = 'PROCESSING'
            db.session.commit()
            return new_order
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to process guest order: {str(e)}",
                "OrderService",
                exc_info=True
            )
            raise ServiceError("Could not process the guest order.")

    @staticmethod
    def _calculate_total(cart_items):
        total = 0
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product:
                total += product.price * item['quantity']
        return total
        
    @staticmethod
    def create_order(user_id, order_data):
        try:
            order_total = 0
            order_items = []

            for item_data in order_data:
                product = Product.query.filter_by(id=item_data['product_id']).with_for_update().first()

                if not product or product.stock_quantity < item_data['quantity']:
                    raise ServiceException(f"Product {product.name if product else item_data['product_id']} is out of stock or does not exist.")
                
                # Decrease stock
                product.stock_quantity -= item_data['quantity']
                
                order_item = OrderItem(
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    price=product.price
                )
                order_items.append(order_item)
                order_total += order_item.price * order_item.quantity

            new_order = Order(
                user_id=user_id,
                total_amount=order_total,
                items=order_items
            )

            db.session.add(new_order)
            db.session.commit()
            return new_order
            
        except Exception as e:
            db.session.rollback()
            # Log the exception e
            raise ServiceException("Failed to create order.") from e    

    

    @staticmethod
    def fulfill_order(order_id: int):
        """
        Main service method to fulfill a paid order.
        It allocates serialized items and updates the order status.
        This entire operation is a single atomic transaction.
        """
        MonitoringService.log_info(
            f"Starting fulfillment service for order_id: {order_id}",
            "OrderService"
        )
        
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundException(f"Order {order_id} not found for fulfillment.")
        
        try:
            for item in order.items:
                OrderService._allocate_serialized_items_for_item(
                    order_item_id=item.id,
                    variant_id=item.product_variant_id,
                    quantity=item.quantity
                )

            # Once all items are allocated, the order can be moved to 'Awaiting Shipment'.
            order.status = 'awaiting_shipment'
            db.session.commit()
            MonitoringService.log_info(
                f"Successfully fulfilled and allocated items for order_id: {order_id}",
                "OrderService"
            )

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_critical(
                f"CRITICAL: Failed to fulfill order {order_id}. Manual intervention required. Error: {str(e)}",
                "OrderService",
                exc_info=True
            )
            raise ServiceError(f"Fulfillment failed for order {order_id}.")

    @staticmethod
    def _allocate_serialized_items_for_item(order_item_id: int, variant_id: int, quantity: int):
        """
        Private helper to allocate specific, serialized product items to a single order item.
        This creates the full traceability for the Product Passport.
        """
        # Find available, 'in_stock' serialized items for the given variant.
        # We use with_for_update() to lock the rows to prevent another process from allocating the same items.
        items_to_allocate = db.session.query(OrderItem)\
            .filter(OrderItem.product_variant_id == variant_id)\
            .filter(OrderItem.status == 'in_stock')\
            .limit(quantity)\
            .with_for_update()\
            .all()

        # Critical check: Ensure the number of physical items matches the quantity ordered.
        if len(items_to_allocate) < quantity:
            # This signifies that inventory_count was out of sync with the actual items.
            # This is a major issue that needs immediate attention.
            raise ServiceError(f"Inventory mismatch for variant {variant_id}: Wanted {quantity}, found {len(items_to_allocate)}")

        # Update the status of the specific items to 'sold' and link them to the order item.
        for item in items_to_allocate:
            item.status = 'sold'
            item.order_item_id = order_item_id
        
        MonitoringService.log_info(
            f"Allocated {len(items_to_allocate)} items for order_item_id {order_item_id}",
            "OrderService"
        )
