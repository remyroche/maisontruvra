from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService
from backend.services.inventory_service import InventoryService
from backend.services.exceptions import NotFoundException, ServiceException
from backend.auth.permissions import admin_required

product_management_routes = Blueprint('product_management_routes', __name__)

@product_management_routes.route('/products', methods=['POST'])
@admin_required
def create_product():
    data = request.get_json()
    try:
        product = ProductService.create_product(data)
        return jsonify(product.to_dict()), 201
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@product_management_routes.route('/products', methods=['GET'])
@admin_required
def get_products():
    products = ProductService.get_all_products_admin()
    return jsonify([p.to_dict() for p in products]), 200

@product_management_routes.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    data = request.get_json()
    try:
        product = ProductService.update_product(product_id, data)
        return jsonify(product.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

@product_management_routes.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    try:
        ProductService.delete_product(product_id)
        return jsonify({"message": "Product deleted"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

# Routes for Categories and Collections
@product_management_routes.route('/categories', methods=['POST', 'GET'])
@admin_required
def manage_categories():
    if request.method == 'POST':
        data = request.get_json()
        category = ProductService.create_category(data)
        return jsonify(category.to_dict()), 201
    else:
        categories = ProductService.get_all_categories()
        return jsonify([c.to_dict() for c in categories]), 200

@product_management_routes.route('/collections', methods=['POST', 'GET'])
@admin_required
def manage_collections():
    if request.method == 'POST':
        data = request.get_json()
        collection = ProductService.create_collection(data)
        return jsonify(collection.to_dict()), 201
    else:
        collections = ProductService.get_all_collections()
        return jsonify([c.to_dict() for c in collections]), 200

# Routes for Inventory
@product_management_routes.route('/inventory/<int:product_id>', methods=['PUT'])
@admin_required
def update_inventory(product_id):
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({"error": "Quantity is required"}), 400
    try:
        inventory_item = InventoryService.update_stock(product_id, quantity)
        return jsonify(inventory_item.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404