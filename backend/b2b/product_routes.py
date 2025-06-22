@b2b_user_required
def get_b2b_products():
    """
    Get all products with B2B-specific pricing.
    """
    user_id = get_jwt_identity()
    products = ProductService.get_all_products()
    
    # Apply B2B pricing logic
    products_with_b2b_price = B2BPricingService.apply_b2b_prices(products, user_id)
    
    return jsonify(products_with_b2b_price), 200

@product_routes.route('/products/<string:product_sku>', methods=['GET'])
@b2b_user_required
def get_b2b_product_detail(product_sku):
    """
    Get a single product with B2B-specific pricing.
    """
    user_id = get_jwt_identity()
    product = ProductService.get_product_by_sku(product_sku)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    product_with_b2b_price = B2BPricingService.apply_b2b_prices([product], user_id)[0]

    return jsonify(product_with_b2b_price), 200
