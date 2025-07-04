from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.models import Collection
from backend.schemas import CollectionSchema
from backend.services.exceptions import ServiceException
from backend.services.product_service import ProductService
from backend.utils.decorators import api_resource_handler, roles_required

# Blueprint for collection management
bp = Blueprint("collection_management", __name__, url_prefix="/api/admin/collections")


@bp.route("/", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_all_collections():
    """
    Retrieves all product collections.
    An optional `include_deleted` query parameter can be used.
    """
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    try:
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
def create_collection(validated_data):
    """
    Creates a new product collection.
    The decorator handles validation, creation, and response.
    """
    return validated_data  # The decorator returns the created object


@bp.route("/<int:collection_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Collection, response_schema=CollectionSchema)
def get_collection(instance):
    """
    Retrieves a single collection by its ID.
    The decorator handles fetching and serialization.
    """
    return instance


@bp.route("/<int:collection_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Collection,
    request_schema=CollectionSchema,
    response_schema=CollectionSchema,
    log_action=True,
)
def update_collection(instance, validated_data):
    """
    Updates an existing collection.
    The decorator handles fetching, validation, updating, and response.
    """
    return instance


@bp.route("/<int:collection_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Collection, allow_hard_delete=True, log_action=True)
def delete_collection(instance):
    """
    Deletes a collection.
    The decorator handles fetching and deletion.
    """
    return {"message": "Collection deleted successfully"}


@bp.route("/<int:collection_id>/restore", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Collection, response_schema=CollectionSchema, log_action=True
)
def restore_collection(instance):
    """
    Restores a soft-deleted collection.
    The decorator handles fetching and restoration logic.
    """
    instance.deleted_at = None
    return instance
