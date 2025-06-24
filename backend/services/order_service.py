from backend.models.order_models import Order
from backend.database import db
from sqlalchemy import desc
from backend.services.loyalty_service import LoyaltyService
from backend.models.order_models import Order
from backend.models.cart_models import Cart # Assuming Cart model exists
from backend.services.invoice_service import B2BInvoiceService
from sqlalchemy.orm import joinedload, subqueryload
import uuid
from utils.sanitization import sanitize_input


class OrderService:
    @staticmethod
    def get_orders_by_user(self, user_id, limit=None):
        """
        Gets a paginated list of orders for a user, eagerly loading items and addresses.
        """
        return Order.query.filter_by(user_id=user_id).options(
            subqueryload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.shipping_address)
        ).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    
    @staticmethod
    def get_order_by_id(self, order_id, user_id=None):
        """
        Gets a single order for a user, eagerly loading its details.
        """
        return Order.query.filter_by(id=order_id, user_id=user_id).options(
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
            raise ValueError("Le panier est vide.")

        # --- This should be a single database transaction ---
        try:
            # 1. Create the order and order items from the cart
            # (Detailed implementation for creating order and order_items would be here)
            new_order = Order(
                user_id=user_id,
                total=cart.calculate_total(), # Assumes cart has a total calculation method
                shipping_address=checkout_data['shipping_address'],
                # ... other order details
            )
            db.session.add(new_order)
            
            # (Loop through cart.items to create OrderItem records...)
            
            # 2. Process payment via a payment gateway
            # payment_successful = PaymentGateway.charge(checkout_data['payment_token'], new_order.total)
            # if not payment_successful:
            #     raise ValueError("Le paiement a échoué.")

            # Flush to get the new_order.id before committing
            db.session.flush()

            # --- 3. AWARD LOYALTY POINTS (NEWLY ADDED HOOK) ---
            # If payment is successful, call the LoyaltyService to award points.
            LoyaltyService.add_points_for_purchase(
                user_id=user_id,
                order_total=new_order.total,
                order_id=new_order.id
            )

            # Send invoice & email based on user type (managed later)
            InvoiceService.create_invoice_for_order(new_order)

            # 4. Clear the user's cart
            # CartService.clear_cart(user_id=user_id)

            # 5. Commit the entire transaction
            db.session.commit()
            
            return new_order

    @staticmethod
    def get_all_orders_paginated(self, page, per_page, status=None, sort_by='created_at', sort_direction='desc'):
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
        # Basic validation
        if not all(k in data for k in ['guest_details', 'shipping_address', 'cart_items', 'payment_token']):
            raise ServiceError("Missing required data for guest order.", 400)

        session = db.session()
        try:
            # 1. Create a non-persistent address for the guest
            address_data = data['shipping_address']
            # AddressService would need a method to create an address without a user_id
            # or we create it here directly.
            guest_address = Address(
                street=address_data['street'],
                city=address_data['city'],
                postal_code=address_data['postal_code'],
                country=address_data['country'],
                # user_id is null for guest addresses
            )
            session.add(guest_address)
            
            # 2. Create the Order object
            new_order = Order(
                guest_email=data['guest_details']['email'],
                guest_phone=data['guest_details'].get('phone'),
                shipping_address=guest_address,
                status='PENDING', # Or a similar initial status
                # Price calculation logic would go here
                total_price=OrderService._calculate_total(data['cart_items']) 
            )
            session.add(new_order)
            
            # 3. Create OrderItems from cart_items
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
                session.add(order_item)

            # 4. Process Payment (pseudo-code)
            # payment_success = PaymentGateway.charge(data['payment_token'], new_order.total_price)
            # if not payment_success:
            #    raise ServiceError("Payment failed.", 402)
            
            new_order.status = 'PROCESSING'
            
            session.commit()
            return new_order
        except Exception as e:
            session.rollback()
            # In a real app, log the exception e
            raise ServiceError("Could not process the guest order.")

    @staticmethod
    def _calculate_total(cart_items):
        # Implement price calculation based on products in DB
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
