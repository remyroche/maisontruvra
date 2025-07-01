"""
This module defines the API endpoints for collection management in the admin panel.
"""
from flask import Blueprint, request, g, jsonify
from ..models import Collection
from ..schemas import CollectionSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService

bp = Blueprint('collection_management', __name__, url_prefix='/api/admin/collections')

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:collection_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('Admin', 'Manager')
@api_resource_handler(
    model=Collection, 
    request_schema=CollectionSchema,
    response_schema=CollectionSchema,
    log_action=True
)
def handle_collections(collection_id=None):
    """Handles all CRUD operations for Collections."""
    if request.method == 'GET' and collection_id is None:
        all_collections = ProductService.get_all_collections()
        return jsonify(CollectionSchema(many=True).dump(all_collections))

    if request.method == 'GET':
        return g.target_object
    elif request.method == 'POST':
        return ProductService.create_collection(g.validated_data)
    elif request.method == 'PUT':
        return ProductService.update_collection(collection_id, g.validated_data)
    elif request.method == 'DELETE':
        ProductService.delete_collection(collection_id)
        return None
