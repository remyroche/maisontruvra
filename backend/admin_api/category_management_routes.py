from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.models import Category
from backend.schemas import CategorySchema
from backend.services.exceptions import ServiceException
from backend.services.product_service import ProductService
from backend.utils.decorators import api_resource_handler, roles_required

# Blueprint for category management
bp = Blueprint("category_management", __name__, url_prefix="/api/admin/categories")


@bp.route("/", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
def get_all_categories():
    """
    Retrieves all product categories.
    An optional `include_deleted` query parameter can be used.
    """
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    try:
        categories = ProductService.get_all_categories(include_deleted=include_deleted)
        return jsonify(CategorySchema(many=True).dump(categories)), 200
    except ServiceException as e:
        return jsonify(e.to_dict()), e.status_code


@bp.route("/", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Category,
    request_schema=CategorySchema,
    response_schema=CategorySchema,
    log_action=True,
)
def create_category(validated_data):
    """
    Creates a new product category.
    The decorator handles validation, creation, and response.
    """
    return validated_data  # The decorator returns the created object


@bp.route("/<int:category_id>", methods=["GET"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Category, response_schema=CategorySchema)
def get_category(instance):
    """
    Retrieves a single category by its ID.
    The decorator handles fetching and serialization.
    """
    return instance


@bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Category,
    request_schema=CategorySchema,
    response_schema=CategorySchema,
    log_action=True,
)
def update_category(instance, validated_data):
    """
    Updates an existing category.
    The decorator handles fetching, validation, updating, and response.
    """
    return instance


@bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Category, allow_hard_delete=True, log_action=True)
def delete_category(instance):
    """
    Deletes a category.
    The decorator handles fetching and deletion.
    """
    return {"message": "Category deleted successfully"}


@bp.route("/<int:category_id>/restore", methods=["POST"])
@jwt_required()
@roles_required("Admin", "Manager")
@api_resource_handler(model=Category, response_schema=CategorySchema, log_action=True)
def restore_category(instance):
    """
    Restores a soft-deleted category.
    The decorator handles fetching and restoration logic.
    """
    instance.deleted_at = None
    return instance
