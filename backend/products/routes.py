import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from backend.extensions import cache
from backend.models.product_models import Product, Review
from backend.schemas import ProductSchema, ProductSearchSchema, ReviewSchema
from backend.services.exceptions import NotFoundException, ValidationException
from backend.services.inventory_service import InventoryService
from backend.services.product_service import ProductService
from backend.services.review_service import ReviewService
from backend.utils.decorators import api_resource_handler
from backend.utils.input_sanitizer import InputSanitizer

# --- Blueprint and Service Initialization ---
products_bp = Blueprint("products", __name__, url_prefix="/api/products")
logger = logging.getLogger(__name__)
product_service = ProductService(logger)
review_service = ReviewService(logger)
inventory_service = InventoryService(logger)


# --- Product Routes ---
@products_bp.route("/<uuid:product_id>/recommendations", methods=["GET"])
def get_recommendations(product_id):
    """Gets co-purchased product recommendations for a given product."""
    recommendations = product_service.get_product_recommendations(product_id)
    return jsonify(ProductSchema(many=True).dump(recommendations))


@products_bp.route("/search", methods=["GET"])
def search_products():
    """Endpoint for product search/autocomplete."""
    query = InputSanitizer.sanitize_input(request.args.get("q", ""))
    if len(query) < 2:
        return jsonify([])

    products = product_service.search_products(query)
    return jsonify([{"id": str(p.id), "name": p.name, "sku": p.sku} for p in products])


@products_bp.route("/", methods=["GET"])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_products():
    """Get a list of all available products with filtering and pagination."""
    try:
        validated_params = ProductSearchSchema().load(request.args)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid query parameters",
                    "errors": err.messages,
                }
            ),
            400,
        )

    try:
        products_pagination = product_service.get_all_products_paginated(
            page=validated_params.get("page", 1),
            per_page=validated_params.get("per_page", 24),
            filters=validated_params,
        )
        return jsonify(
            {
                "status": "success",
                "data": ProductSchema(many=True).dump(products_pagination.items),
                "total": products_pagination.total,
                "pages": products_pagination.pages,
                "current_page": products_pagination.page,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An error occurred while fetching products.",
                }
            ),
            500,
        )


@products_bp.route("/<slug>", methods=["GET"])
@api_resource_handler(
    model=Product,
    response_schema=ProductSchema,
    lookup_field="slug",
    eager_loads=["category", "collections", "reviews"],
)
def get_product_by_slug(instance):
    """Get detailed information for a single product by its slug."""
    return instance


@products_bp.route("/<int:product_id>/notify-me", methods=["POST"])
def request_stock_notification(product_id):
    """Endpoint for users to request notification when a product is back in stock."""
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required."}), 400

    try:
        _, message = inventory_service.request_stock_notification(product_id, email)
        return jsonify({"message": message}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception(
            f"Failed to create stock notification for product {product_id}: {e}"
        )
        return jsonify({"error": "An internal error occurred."}), 500


# --- Category and Review Routes ---
@products_bp.route("/categories", methods=["GET"])
@cache.cached(timeout=3600)  # Cache for 1 hour
def get_product_categories():
    """Get a list of all product categories."""
    try:
        categories = product_service.get_all_categories()
        return jsonify({"status": "success", "data": [c.to_dict() for c in categories]})
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An error occurred while fetching categories.",
                }
            ),
            500,
        )


@products_bp.route("/<int:product_id>/reviews", methods=["GET"])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_product_reviews(product_id):
    """Get all approved reviews for a specific product."""
    try:
        reviews = review_service.get_reviews_for_product(product_id)
        return jsonify(
            {"status": "success", "data": ReviewSchema(many=True).dump(reviews)}
        )
    except Exception as e:
        logger.error(
            f"Error fetching reviews for product {product_id}: {e}", exc_info=True
        )
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An error occurred while fetching reviews.",
                }
            ),
            500,
        )


@products_bp.route("/<int:product_id>/reviews", methods=["POST"])
@jwt_required()
@api_resource_handler(
    model=Review,
    request_schema=ReviewSchema,
    response_schema=ReviewSchema,
    cache_timeout=0,
    log_action=True,
)
def create_product_review(validated_data, product_id):
    """Submit a new review for a product. Requires authentication."""
    user_id = get_jwt_identity()
    try:
        review = review_service.submit_review(user_id, product_id, validated_data)
        return review
    except ValueError as e:
        raise ValidationException(str(e)) from e
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
