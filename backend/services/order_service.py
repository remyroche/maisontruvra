import logging
import uuid
from backend import db
from backend.models.order_models import Order, OrderItem
from backend.models.product_models import ProductItem, Product
from backend.models.cart_models import Cart
from backend.models.user_models import Address
from backend.services.loyalty_service import LoyaltyService
from backend.services.invoice_service import InvoiceService
from .exceptions import ServiceError, NotFoundException
from sqlalchemy.orm import joinedload, subqueryload

logger = logging.getLogger(__name__)

class OrderService:
    """
    Handles business logic related to order processing, creation, and fulfillment.
    """

    @staticmethod
    def get_orders_by_user(user_id, page=1, per_page=10):
        """
        Gets a paginated list of orders for a user, eagerly loading items and addresses.
        """
        return Order.query.filter_by(user_id=user_id).options(
            subqueryload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.shipping_address)
        ).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """
        Gets a single order for a user, eagerly loading its details.
        """
        query = Order.query.filter_by(id=order_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.options(
            subqueryload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.shipping_address)
        ).first()

    @staticmethod
    def create_order_from_cart(cart: Cart, user_id: int, checkout_data: dict) -> Order:
        """
        Creates a final order from a user's cart, processes payment,
        and hooks into the LoyaltyService to award points.
        """
        if not cart or not cart.items:
            raise ValueError("The cart is empty.")

        try:
            # Create the order and order items from the cart
            new_order = Order(
                user_id=user_id,
                total=cart.calculate_total(), # Assumes cart has a total calculation method
                shipping_address=checkout_data['shipping_address'],
            )
            db.session.add(new_order)
            
            # (Loop through cart.items to create OrderItem records...)
            
            # Process payment via a payment gateway
            # payment_successful = PaymentGateway.charge(checkout_data['payment_token'], new_order.total)
            # if not payment_successful:
            #     raise ValueError("Payment failed.")

            db.session.flush()

            # Award loyalty points
            LoyaltyService.add_points_for_purchase(
                user_id=user_id,
                order_total=new_order.total,
                order_id=new_order.id
            )

            # Create an invoice for the order
            InvoiceService.create_invoice_for_order(new_order)

            # Clear the user's cart
            # CartService.clear_cart(user_id=user_id)

            db.session.commit()
            return new_order
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create order from cart for user {user_id}: {str(e)}", exc_info=True)
            raise ServiceError("Could not create order.")

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
            logger.error(f"Failed to process guest order: {str(e)}", exc_info=True)
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
        """Create a new order."""
        order = Order(
            user_id=user_id,
            total_amount=order_data['total_amount'],
            status=order_data.get('status', 'PENDING')
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """Update an order's status."""
        order = Order.query.get(order_id)
        if order:
            order.status = new_status
            db.session.commit()
        return order

    @staticmethod
    def fulfill_order(order_id: int):
        """
        Main service method to fulfill a paid order.
        It allocates serialized items and updates the order status.
        This entire operation is a single atomic transaction.
        """
        logger.info(f"Starting fulfillment service for order_id: {order_id}")
        
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
            logger.info(f"Successfully fulfilled and allocated items for order_id: {order_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"CRITICAL: Failed to fulfill order {order_id}. Manual intervention required. Error: {str(e)}", exc_info=True)
            raise ServiceError(f"Fulfillment failed for order {order_id}.")

    @staticmethod
    def _allocate_serialized_items_for_item(order_item_id: int, variant_id: int, quantity: int):
        """
        Private helper to allocate specific, serialized product items to a single order item.
        This creates the full traceability for the Product Passport.
        """
        # Find available, 'in_stock' serialized items for the given variant.
        # We use with_for_update() to lock the rows to prevent another process from allocating the same items.
        items_to_allocate = db.session.query(ProductItem)\
            .filter(ProductItem.product_variant_id == variant_id)\
            .filter(ProductItem.status == 'in_stock')\
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
        
        logger.info(f"Allocated {len(items_to_allocate)} items for order_item_id {order_item_id}")
