from backend.database import db
from backend.models.b2b_models import B2BUser, B2BAccount, B2BInvoice, B2BOrder, B2BCart, B2BCartItem, B2BOrderItem, B2BTier
from backend.models.product_models import Product
from backend.services.exceptions import NotFoundException, ServiceError
from backend.extensions import redis_client # Assuming redis_client is initialized in extensions.py
from .monitoring_service import MonitoringService
import json

CACHE_TTL_SECONDS = 600 # Cache for 10 minutes

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
    def get_b2b_price(user, product):
        """
        Calculates the B2B price for a product based on the user's tier.
        This function now uses Redis to cache the results.
        """
        # The user object is assumed to be the main User model, with a `b2b_profile` relationship.
        if not user or not getattr(user, 'is_b2b', False) or not getattr(user, 'b2b_profile', None) or not user.b2b_profile.tier_id:
            return product.price

        tier_id = user.b2b_profile.tier_id
        
        cache_key = f"b2b_price:tier_{tier_id}:product_{product.id}"
        
        try:
            cached_price = redis_client.get(cache_key)
            if cached_price:
                return float(json.loads(cached_price))
        except Exception as e:
            MonitoringService.log_error(
                f"Redis GET error for key {cache_key}: {e}",
                "B2BService",
                level='WARNING'
            )
            # Proceed with calculation if cache is unavailable

        # If not in cache, calculate it
        # (Assuming B2BTier model has a `discount_percentage` field)
        tier = db.session.get(B2BTier, tier_id)
        if not tier or not tier.discount_percentage:
            calculated_price = float(product.price)
        else:
            discount = float(product.price) * (tier.discount_percentage / 100)
            calculated_price = round(float(product.price) - discount, 2)
        
        # Store the result in cache
        try:
            redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(calculated_price))
        except Exception as e:
            MonitoringService.log_error(
                f"Redis SETEX error for key {cache_key}: {e}",
                "B2BService",
                level='WARNING'
            )
            
        return calculated_price

    @staticmethod
    def invalidate_b2b_product_price_cache(product_id=None, tier_id=None):
        """
        Invalidates B2B price caches.
        - If only product_id is provided, invalidates for that product across all tiers.
        - If only tier_id is provided, invalidates for that tier across all products.
        WARNING: Using KEYS in production Redis is not recommended for large datasets.
        For larger scale, consider using Redis sets to track keys.
        """
        try:
            if product_id:
                keys_to_delete = redis_client.keys(f"b2b_price:tier_*:product_{product_id}")
                if keys_to_delete:
                    redis_client.delete(*keys_to_delete)
                    
            if tier_id:
                keys_to_delete = redis_client.keys(f"b2b_price:tier_{tier_id}:product_*")
                if keys_to_delete:
                    redis_client.delete(*keys_to_delete)
        except Exception as e:
            MonitoringService.log_error(
                f"Failed to invalidate B2B price cache (product: {product_id}, tier: {tier_id}): {e}",
                "B2BService",
                level='ERROR'
            )


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