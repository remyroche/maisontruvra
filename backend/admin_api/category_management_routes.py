"""
This module defines the API endpoints for category management in the admin panel.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Category
from ..schemas import CategorySchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService

bp = Blueprint('category_management', __name__, url_prefix='/api/admin/categories')

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(
    model=Category, 
    request_schema=CategorySchema,
    response_schema=CategorySchema,
    log_action=True
)
def handle_categories(category_id=None):
    """Handles all CRUD operations for Categories."""
    if request.method == 'GET' and category_id is None:
        all_categories = ProductService.get_all_categories()
        return jsonify(CategorySchema(many=True).dump(all_categories))
    
    if request.method == 'GET':
        return g.target_object
    elif request.method == 'POST':
        return ProductService.create_category(g.validated_data)
    elif request.method == 'PUT':
        return ProductService.update_category(category_id, g.validated_data)
    elif request.method == 'DELETE':
        ProductService.delete_category(category_id)
        return None
