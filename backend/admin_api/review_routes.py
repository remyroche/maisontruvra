"""
This module defines the API endpoints for review management in the admin panel.
It uses the @api_resource_handler for secure and consistent handling of individual
review operations and provides a separate endpoint for paginated listing.
"""

from flask import Blueprint, request, g, jsonify
from ..models import Review
from ..schemas import ReviewSchema, ReviewUpdateSchema
from ..utils.decorators import api_resource_handler, roles_required
from ..services.review_service import ReviewService

# --- Blueprint Setup ---
bp = Blueprint("review_management", __name__, url_prefix="/api/admin/reviews")


@bp.route("/", methods=["GET"])
@roles_required("Admin", "Manager")
def list_reviews():
    """
    Handles listing and pagination of all reviews, with optional filtering.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # Filter by approval status (e.g., /reviews?approved=false)
    is_approved_str = request.args.get("approved", None, type=str)
    filters = {}
    if is_approved_str is not None:
        filters["is_approved"] = is_approved_str.lower() == "true"

    paginated_reviews = ReviewService.get_all_reviews_paginated(
        page=page, per_page=per_page, filters=filters
    )

    return jsonify(
        {
            "data": ReviewSchema(many=True).dump(paginated_reviews.items),
            "total": paginated_reviews.total,
            "pages": paginated_reviews.pages,
            "current_page": paginated_reviews.page,
        }
    )


@bp.route("/<int:review_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("Admin", "Manager")
@api_resource_handler(
    model=Review,
    request_schema=ReviewUpdateSchema,  # For validating PUT data
    response_schema=ReviewSchema,  # For serializing GET/PUT response
    eager_loads=["user", "product"],  # Eager load for performance
    log_action=True,
    allow_hard_delete=True,  # Admins can permanently delete reviews
)
def handle_single_review(review_id=None, is_hard_delete=False):
    """
    Handles viewing, updating (approving), and deleting a single review.
    """
    if request.method == "GET":
        # The decorator has fetched the review and placed it in g.target_object.
        return g.target_object

    elif request.method == "PUT":
        # The decorator has fetched the review (g.target_object) and
        # validated the incoming data (g.validated_data).
        return ReviewService.update_review_status(g.target_object, g.validated_data)

    elif request.method == "DELETE":
        # The decorator has already checked if hard delete is allowed.
        # The service layer should contain the actual deletion logic.
        ReviewService.delete_review(review_id)
        return None  # Decorator provides the success message.
