"""
This module defines the API endpoints for category management in the admin panel.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Category
from ..schemas import CategorySchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService

bp = Blueprint('category_management', __name__, url_prefix='/api/admin/categories')


@bp.route('/', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
def get_all_categories():
    """
    Retrieves a list of all product categories.
    Supports including soft-deleted items via a query parameter.
    """
    try:
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        categories = ProductService.get_all_categories(include_deleted=include_deleted)
        return jsonify(CategorySchema(many=True).dump(categories)), 200
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route('/', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Category, request_schema=CategorySchema, response_schema=CategorySchema, log_action=True)
def create_category():
    """
    Creates a new product category.
    The decorator handles validation, session management, and response serialization.
    """
    return ProductService.create_category(g.validated_data)


@bp.route('/<int:category_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Category, response_schema=CategorySchema)
def get_category(category_id):
    """
    Retrieves a single category by its ID.
    The decorator handles fetching and serialization.
    """
    return g.target_object


@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Category, request_schema=CategorySchema, response_schema=CategorySchema, log_action=True)
def update_category(category_id):
    """
    Updates an existing category.
    The decorator fetches the category, validates input, and handles the response.
    """
    return ProductService.update_category(g.target_object, g.validated_data)


@bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Category, allow_hard_delete=True, log_action=True)
def delete_category(category_id):
    """
    Deletes a category.
    - Soft-delete by default.
    - Use ?hard=true for a permanent, irreversible delete.
    The decorator handles all fetching and deletion logic automatically.
    """
    return None


@bp.route('/<int:category_id>/restore', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager')
@api_resource_handler(model=Category, response_schema=CategorySchema, log_action=True)
def restore_category(category_id):
    """
    Restores a soft-deleted category.
    The decorator handles all fetching and restoration logic automatically.
    """
    return g.target_object
