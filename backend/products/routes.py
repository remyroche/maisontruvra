from flask import Blueprint, jsonify, request
from backend.services.product_service import ProductService
from backend.services.recommendation_service import RecommendationService

products_bp = Blueprint('public_product_routes', __name__)

@products_bp.route('/', methods=['GET'])
def get_all_products():
    """
    Get a list of all published products, with optional filtering.
    """
    category_slug = request.args.get('category')
    collection_slug = request.args.get('collection')
    
    products = ProductService.get_all_published_products(
        category_slug=category_slug,
        collection_slug=collection_slug
    )
    return jsonify([p.to_dict() for p in products]), 200

@products_bp.route('/<string:slug>', methods=['GET'])
@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """
    Fetches aggregated data for a single product page.
    This endpoint is designed to provide all necessary information for the frontend
    to display a product and its selectable variants (e.g., sizes, colors).
    """
    # In a real application, database interactions would be handled
    # by a service or data access layer.
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True) # Assuming a MySQL-like connector that returns dicts
    try:
        # 1. Fetch the base product information, joining with its category for context.
        cursor.execute(
            """
            SELECT p.id, p.name, p.description, p.collection, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s AND p.deleted_at IS NULL
            """,
            (product_id,)
        )
        product_data = cursor.fetchone()

        if not product_data:
            return jsonify({'error': 'Product not found'}), 404

        # 2. Fetch all available, non-deleted variants (SKUs) for this product.
        cursor.execute(
            """
            SELECT id as variant_id, sku, price, attributes, inventory_count
            FROM product_variants
            WHERE product_id = %s AND deleted_at IS NULL AND inventory_count > 0
            """,
            (product_id,)
        )
        variants = cursor.fetchall()

        # 3. Combine into a single response object for the frontend.
        product_data['variants'] = variants

        return jsonify(product_data), 200

    except Exception as e:
        logger.error(f"Error fetching product details for {product_id}: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500
    finally:
        cursor.close()
        conn.close()


@products_bp.route('/<int:product_id>/recommendations', methods=['GET'])
def get_recommendations(product_id):
    """
    Get product recommendations related to the given product.
    """
    recommendations = RecommendationService.get_recommendations_for_product(product_id)
    return jsonify([p.to_dict() for p in recommendations]), 200
