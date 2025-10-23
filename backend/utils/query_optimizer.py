"""
Database Query Optimization Utilities

This module provides utilities for optimizing database queries by implementing
eager loading strategies and query optimization patterns.
"""

from sqlalchemy.orm import joinedload, selectinload, subqueryload
from sqlalchemy import func, and_, or_
from ..extensions import db


class QueryOptimizer:
    """Utility class for optimizing database queries."""
    
    @staticmethod
    def get_optimized_product_query():
        """
        Get an optimized product query with eager loading for related entities.
        
        Returns:
            Query: Optimized query with eager loading
        """
        from ..models.product import Product
        from ..models.category import Category
        from ..models.product_variant import ProductVariant
        from ..models.loyalty_tier import LoyaltyTier
        
        return Product.query.options(
            joinedload(Product.category),
            joinedload(Product.variants),
            joinedload(Product.restricted_to_tiers),
            joinedload(Product.images),
            joinedload(Product.reviews)
        )
    
    @staticmethod
    def get_optimized_order_query():
        """
        Get an optimized order query with eager loading for related entities.
        
        Returns:
            Query: Optimized query with eager loading
        """
        from ..models.order import Order
        from ..models.order_item import OrderItem
        from ..models.user import User
        from ..models.address import Address
        
        return Order.query.options(
            joinedload(Order.user),
            joinedload(Order.shipping_address),
            joinedload(Order.billing_address),
            selectinload(Order.items).joinedload(OrderItem.product),
            selectinload(Order.items).joinedload(OrderItem.variant)
        )
    
    @staticmethod
    def get_optimized_user_query():
        """
        Get an optimized user query with eager loading for related entities.
        
        Returns:
            Query: Optimized query with eager loading
        """
        from ..models.user import User
        from ..models.loyalty import Loyalty
        from ..models.address import Address
        
        return User.query.options(
            joinedload(User.loyalty),
            selectinload(User.addresses),
            selectinload(User.orders),
            selectinload(User.wishlist_items)
        )
    
    @staticmethod
    def optimize_product_recommendations_query(product_id):
        """
        Optimize the product recommendations query to avoid N+1 problems.
        
        Args:
            product_id (int): The product ID to find recommendations for
            
        Returns:
            Query: Optimized recommendations query
        """
        from ..models.order_item import OrderItem
        from ..models.product import Product
        from ..models.category import Category
        
        # Find orders that contain the target product
        subquery = (
            db.session.query(OrderItem.order_id)
            .filter(OrderItem.product_id == product_id)
            .subquery()
        )
        
        # Find all other products purchased in those same orders
        # with eager loading to avoid N+1 queries
        recommendations = (
            db.session.query(
                OrderItem.product_id,
                func.count(OrderItem.product_id).label("purchase_count"),
            )
            .join(Product, OrderItem.product_id == Product.id)
            .options(
                joinedload(OrderItem.product).joinedload(Product.category)
            )
            .filter(
                and_(
                    OrderItem.order_id.in_(subquery),
                    OrderItem.product_id != product_id,
                )
            )
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.product_id).desc())
            .limit(10)
        )
        
        return recommendations
    
    @staticmethod
    def get_products_with_variants_and_stock():
        """
        Get products with their variants and stock information in a single query.
        
        Returns:
            Query: Optimized query for products with variants and stock
        """
        from ..models.product import Product
        from ..models.product_variant import ProductVariant
        from ..models.inventory import InventoryItem
        
        return (
            db.session.query(Product)
            .join(ProductVariant, Product.id == ProductVariant.product_id)
            .outerjoin(InventoryItem, ProductVariant.id == InventoryItem.variant_id)
            .options(
                joinedload(Product.variants).joinedload(ProductVariant.inventory_items),
                joinedload(Product.category)
            )
        )
    
    @staticmethod
    def get_user_orders_with_items(user_id):
        """
        Get user orders with all related items in a single optimized query.
        
        Args:
            user_id (int): The user ID
            
        Returns:
            Query: Optimized query for user orders
        """
        from ..models.order import Order
        from ..models.order_item import OrderItem
        from ..models.product import Product
        from ..models.product_variant import ProductVariant
        
        return (
            db.session.query(Order)
            .filter(Order.user_id == user_id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.product),
                selectinload(Order.items).joinedload(OrderItem.variant),
                joinedload(Order.shipping_address),
                joinedload(Order.billing_address)
            )
            .order_by(Order.created_at.desc())
        )


def optimize_query_performance(query, use_cache=True, cache_timeout=3600):
    """
    Decorator to add caching to query methods for better performance.
    
    Args:
        query: The query to optimize
        use_cache (bool): Whether to use caching
        cache_timeout (int): Cache timeout in seconds
        
    Returns:
        Query result with optional caching
    """
    if not use_cache:
        return query
    
    from ..extensions import cache
    from ..utils.cache_helpers import get_query_cache_key
    
    # Generate cache key based on query
    cache_key = get_query_cache_key(str(query))
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    # Execute query and cache result
    result = query.all()
    cache.set(cache_key, result, timeout=cache_timeout)
    
    return result