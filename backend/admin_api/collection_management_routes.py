"""
This module defines the API endpoints for collection management in the admin panel.
"""

from flask import Blueprint, request, g, jsonify
from ..models import Collection
from ..schemas import CollectionSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.product_service import ProductService

bp = Blueprint("collection_management", __name__, url_prefix="/api/admin/collections")


@bp.route("/", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_all_collections():
    """
    Retrieves a list of all product collections.
    Supports including soft-deleted items via a query parameter.
    """
    try:
        include_deleted = request.args.get("include_deleted", "false").lower() == "true"
        collections = ProductService.get_all_collections(
            include_deleted=include_deleted
        )
        return jsonify(CollectionSchema(many=True).dump(collections)), 200
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route("/", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Collection,
    request_schema=CollectionSchema,
    response_schema=CollectionSchema,
    log_action=True,
)
def create_collection():
    """
    Creates a new product collection.
    The decorator handles validation, session management, and response serialization.
    """
    return ProductService.create_collection(g.validated_data)


@bp.route("/<int:collection_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Collection, response_schema=CollectionSchema)
def get_collection(collection_id):
    """
    Retrieves a single collection by its ID.
    The decorator handles fetching and serialization.
    """
    return g.target_object


@bp.route("/<int:collection_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Collection,
    request_schema=CollectionSchema,
    response_schema=CollectionSchema,
    log_action=True,
)
def update_collection(collection_id):
    """
    Updates an existing collection.
    The decorator fetches the collection, validates input, and handles the response.
    """
    return ProductService.update_collection(g.target_object, g.validated_data)


@bp.route("/<int:collection_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Collection, allow_hard_delete=True, log_action=True)
def delete_collection(collection_id):
    """
    Deletes a collection.
    - Soft-delete by default.
    - Use ?hard=true for a permanent, irreversible delete.
    The decorator handles all fetching and deletion logic automatically.
    """
    return None


@bp.route("/<int:collection_id>/restore", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Collection, response_schema=CollectionSchema, log_action=True
)
def restore_collection(collection_id):
    """
    Restores a soft-deleted collection.
    The decorator handles all fetching and restoration logic automatically.
    """
    return g.target_object
