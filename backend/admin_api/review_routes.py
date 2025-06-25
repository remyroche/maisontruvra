from flask import Blueprint, request, jsonify
from backend.services.review_service import ReviewService # Assumed service
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import admin_required, staff_required, roles_required, permissions_required
from ..utils.decorators import log_admin_action

review_bp = Blueprint('admin_review_routes', __name__, url_prefix='/api/admin/reviews')

# READ all reviews (with pagination and filtering)
@review_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_REVIEWS')
@log_admin_action
@roles_required ('Admin', 'Staff')
@admin_required
def get_reviews():
    """
    Retrieves all product reviews with optional filtering by status.
    """
    status_filter = request.args.get('status')
    reviews = ReviewService.get_all_reviews(status_filter=status_filter)
    return jsonify([review.to_dict() for review in reviews])

@review_bp.route('/<int:review_id>/approve', methods=['PUT'])
@permissions_required('MANAGE_REVIEWS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def approve_review(review_id):
    """
    Approves a pending review.
    """
    review = ReviewService.approve_review(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    return jsonify(review.to_dict())

@review_bp.route('/<int:review_id>', methods=['DELETE'])
@permissions_required('MANAGE_REVIEWS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def delete_review(review_id):
    """
    Deletes a review.
    """
    if ReviewService.delete_review(review_id):
        return jsonify({"message": "Review deleted successfully"})
    return jsonify({"error": "Review not found"}), 404

        
@review_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_REVIEWS')
@log_admin_action
@roles_required ('Admin', 'Manager', 'Support')
@admin_required
def get_reviews():
    """
    Get a paginated and filterable list of all product reviews.
    Query Params:
    - page: The page number to retrieve.
    - per_page: The number of reviews per page.
    - status: Filter by review status (e.g., 'pending', 'approved', 'rejected').
    - product_id: Filter by product ID.
    - user_id: Filter by user ID.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        filters = {
            'status': request.args.get('status', type=str),
            'product_id': request.args.get('product_id', type=int),
            'user_id': request.args.get('user_id', type=int)
        }
        # Remove None values so we don't pass empty filters
        filters = {k: v for k, v in filters.items() if v is not None}
        
        reviews_pagination = ReviewService.get_all_reviews_paginated(page=page, per_page=per_page, filters=filters)
        
        return jsonify({
            "status": "success",
            "data": [review.to_dict() for review in reviews_pagination.items],
            "total": reviews_pagination.total,
            "pages": reviews_pagination.pages,
            "current_page": reviews_pagination.page
        }), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message="An internal error occurred while fetching reviews."), 500

        return jsonify(status="error", message="An internal error occurred while deleting the review."), 500
