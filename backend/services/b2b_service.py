from backend.database import db
from backend.models.b2b_models import B2BUser, B2BAccount, B2BInvoice, B2BOrder, B2BCart, B2BCartItem, B2BOrderItem
from backend.models.product_models import Product
from backend.services.exceptions import NotFoundException, ServiceError

class B2BService:
    """
    Handles business logic related to B2B accounts, carts, and orders.
    """

    @staticmethod
    def get_company_profile_by_user(user_id: int):
        user = db.session.get(B2BUser, user_id)
        if not user or not user.account:
            raise NotFoundException("B2B profile not found for this user.")
        return user.account

    @staticmethod
    def update_company_profile_by_user(user_id: int, data: dict):
        profile = B2BService.get_company_profile_by_user(user_id)
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        db.session.commit()
        return profile

    @staticmethod
    def get_b2b_invoices_paginated(user_id: int, page: int, per_page: int):
        """Fetches paginated invoices for the user's company account."""
        user = db.session.get(B2BUser, user_id)
        if not user:
            raise NotFoundException("B2B user not found")
        
        invoices_pagination = B2BInvoice.query.filter_by(account_id=user.account_id)\
            .order_by(B2BInvoice.issue_date.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        return invoices_pagination

    @staticmethod
    def get_b2b_cart(user_id: int):
        """Fetches or creates a cart for the user's company account."""
        user = db.session.get(B2BUser, user_id)
        if not user:
            raise NotFoundException("B2B user not found")
        
        cart = B2BCart.query.filter_by(account_id=user.account_id).first()
        
        if not cart:
            cart = B2BCart(account_id=user.account_id)
            db.session.add(cart)
            db.session.commit()
            
        return cart

    @staticmethod
    def create_b2b_order(user_id: int, data: dict):
        """Creates a B2B order from the company's cart."""
        user = db.session.get(B2BUser, user_id)
        if not user:
            raise NotFoundException("B2B user not found")
            
        cart = B2BService.get_b2b_cart(user_id)
        if not cart.items:
            raise ServiceError("Cannot create an order from an empty cart.", 400)
            
        new_order = B2BOrder(
            account_id=user.account_id,
            created_by_user_id=user_id,
            shipping_address=data.get('shipping_address'),
            status='pending_review'
        )
        
        # This is a simplified version. A real implementation would move items,
        # calculate totals, and clear the cart within a transaction.
        db.session.add(new_order)
        db.session.commit()
        
        return new_order