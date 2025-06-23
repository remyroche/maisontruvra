from backend.models.order_models import Order
from backend.database import db
from sqlalchemy import desc
from backend.services.loyalty_service import LoyaltyService
from backend.models.order_models import Order
from backend.models.cart_models import Cart # Assuming Cart model exists
from backend.services.invoice_service import B2BInvoiceService


class OrderService:
    @staticmethod
    def get_orders_by_user(user_id, limit=None):
        """Get orders for a specific user, optionally limited."""
        query = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at))
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """Get a specific order, optionally filtered by user."""
        query = Order.query.filter_by(id=order_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()


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

            # Send invoice & email based on user type
            if order.user and order.user.user_type == 'B2B':
                B2BInvoiceService.create_and_send_b2b_invoice(order)
            if order.user and order.user.user_type == 'B2C':
                B2CInvoiceService.create_and_send_b2c_invoice(order)

            # 4. Clear the user's cart
            # CartService.clear_cart(user_id=user_id)

            # 5. Commit the entire transaction
            db.session.commit()
            
            return new_order

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
