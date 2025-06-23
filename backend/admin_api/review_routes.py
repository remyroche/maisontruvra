from flask import Blueprint, request, jsonify
from backend.services.review_service import ReviewService # Assumed service
from backend.utils.sanitization import sanitize_input
from backend.auth.permissions import permissions_required

review_management_bp = Blueprint('review_management_bp', __name__, url_prefix='/admin/reviews')

# READ all reviews (with pagination and filtering)
@review_management_bp.route('/', methods=['GET'])
@permissions_required('MANAGE_REVIEWS')
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

# READ a single review by ID
@review_management_bp.route('/<int:review_id>', methods=['GET'])
@permissions_required('MANAGE_REVIEWS')
def get_review(review_id):
    """
    Get a single review by its ID.
    """
    review = ReviewService.get_review_by_id(review_id)
    if review:
        return jsonify(status="success", data=review.to_dict()), 200
    return jsonify(status="error", message="Review not found"), 404

# UPDATE an existing review
@review_management_bp.route('/<int:review_id>', methods=['PUT'])
@permissions_required('MANAGE_REVIEWS')
def update_review(review_id):
    """
    Update a review's content or status.
    This can be used to approve, reject, or edit a review.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400

    if not ReviewService.get_review_by_id(review_id):
        return jsonify(status="error", message="Review not found"), 404

    sanitized_data = sanitize_input(data)

    try:
        updated_review = ReviewService.update_review(review_id, sanitized_data)
        return jsonify(status="success", data=updated_review.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message="An internal error occurred while updating the review."), 500

# DELETE a review
@review_management_bp.route('/<int:review_id>', methods=['DELETE'])
@permissions_required('MANAGE_REVIEWS')
def delete_review(review_id):
    """
    Delete a review.
    """
    if not ReviewService.get_review_by_id(review_id):
        return jsonify(status="error", message="Review not found"), 404

    try:
        ReviewService.delete_review(review_id)
        return jsonify(status="success", message="Review deleted successfully"), 200
    except Exception as e:
        # Proper logging should be implemented here
        return jsonify(status="error", message="An internal error occurred while deleting the review."), 500
