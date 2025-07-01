"""
Centralized Caching Utility

This module provides functions for generating cache keys and clearing caches for different parts of the application. This helps to keep caching logic consistent and avoids scattering cache management code across services and routes.
"""
from ..extensions import cache

# --- Key Generation Functions ---

def get_product_list_key():
    """Cache key for the list of all products."""
    return "product_list"

def get_product_by_slug_key(slug):
    """Cache key for a single product fetched by its slug."""
    return f"product:slug:{slug}"

def get_product_by_id_key(product_id):
    """Cache key for a single product fetched by its ID."""
    return f"product:id:{product_id}"

def get_blog_post_list_key():
    """Cache key for the list of all blog posts."""
    return "blog_post_list"

def get_blog_post_by_slug_key(slug):
    """Cache key for a single blog post fetched by its slug."""
    return f"blog:slug:{slug}"

def get_site_settings_key():
    """Cache key for all site settings."""
    return "site_settings"

def get_delivery_methods_key():
    """Cache key for all active delivery methods."""
    return "delivery_methods"


# --- Cache Invalidation Functions ---

def clear_product_cache(product_id=None, slug=None):
    """
    Clears product-related caches.

    - Deletes the cache for the full product list.
    - If product_id is provided, deletes the cache for that specific product ID.
    - If slug is provided, deletes the cache for that specific product slug.
    """
    # Invalidate the main product list
    cache.delete(get_product_list_key())
    
    # Invalidate specific product entries
    if product_id:
        cache.delete(get_product_by_id_key(product_id))
    if slug:
        cache.delete(get_product_by_slug_key(slug))

def clear_blog_cache(slug=None):
    """
    Clears blog-related caches.

    - Deletes the cache for the full blog post list.
    - If slug is provided, deletes the cache for that specific blog post slug.
    """
    cache.delete(get_blog_post_list_key())
    if slug:
        cache.delete(get_blog_post_by_slug_key(slug))

def clear_site_settings_cache():
    """Clears the site settings cache."""
    cache.delete(get_site_settings_key())

def clear_delivery_methods_cache():
    """Clears the delivery methods cache."""
    cache.delete(get_delivery_methods_key())
