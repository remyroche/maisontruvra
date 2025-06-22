# FILE: routes/admin_products.py
# New Flask Blueprint to manage the entire product hierarchy via the admin panel.
# -----------------------------------------------------------------------------

from flask import Blueprint, request, jsonify
from backend.services.product_service import ProductService
from backend.services.inventory_service import InventoryService
from backend.services.exceptions import NotFoundException, ServiceException
from backend.auth.permissions import admin_required, permission_required, Permission
from flask_jwt_extended import jwt_required
from backend.models.product_models import Product, Category, Collection
from backend.extensions import db


product_management_routes = Blueprint('product_management_routes', __name__)

@product_management_bp.route('/products', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_PRODUCTS)
def create_product_route():
    data = request.get_json()
    # Basic validation
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': 'Missing name or price'}), 400
    
    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        sku=data.get('sku'),
        # ... other fields
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

@product_management_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
@permission_required(Permission.MANAGE_PRODUCTS)
def update_product_route(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(product.to_dict())

@product_management_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
@permission_required(Permission.MANAGE_PRODUCTS)
def delete_product_route(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})


# Category Routes
@product_management_bp.route('/categories', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_PRODUCTS)
def create_category():
    data = request.get_json()
    new_category = Category(name=data['name'], parent_id=data.get('parent_id'))
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

# Collection Routes
@product_management_bp.route('/collections', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_PRODUCTS)
def create_collection():
    data = request.get_json()
    new_collection = Collection(name=data['name'], description=data.get('description'))
    db.session.add(new_collection)
    db.session.commit()
    return jsonify(new_collection.to_dict()), 201

@product_management_routes.route('/products', methods=['GET'])
@admin_required
def get_products():
    products = ProductService.get_all_products_admin()
    return jsonify([p.to_dict() for p in products]), 200


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
    try:
        inventory_item = InventoryService.update_stock(product_id, quantity)
        return jsonify(inventory_item.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
