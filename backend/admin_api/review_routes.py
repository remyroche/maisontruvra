from flask import Blueprint, request, jsonify
from backend.services.review_service import ReviewService
from backend.auth.permissions import roles_required, permissions_required
from ..utils.decorators import log_admin_action

review_bp = Blueprint('admin_review_routes', __name__, url_prefix='/api/admin/reviews')

@review_bp.route('/', methods=['GET'])
@log_admin_action
@permissions_required('MANAGE_REVIEWS')
def get_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    filters = {
        'status': request.args.get('status', type=str),
        'include_deleted': request.args.get('include_deleted', 'false').lower() == 'true'
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    reviews_pagination = ReviewService.get_all_reviews_paginated(page=page, per_page=per_page, filters=filters)
    
    return jsonify({
        "status": "success",
        "data": [review.to_admin_dict() for review in reviews_pagination.items],
        "total": reviews_pagination.total,
        "pages": reviews_pagination.pages,
        "current_page": reviews_pagination.page
    })

@review_bp.route('/<int:review_id>/approve', methods=['PUT'])
@log_admin_action
@permissions_required('MANAGE_REVIEWS')
def approve_review(review_id):
    review = ReviewService.approve_review(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    return jsonify(review.to_admin_dict())

@review_bp.route('/<int:review_id>', methods=['DELETE'])
@log_admin_action
@permissions_required('MANAGE_REVIEWS')
def delete_review(review_id):
    hard_delete = request.args.get('hard', 'false').lower() == 'true'
    if hard_delete:
        if ReviewService.hard_delete_review(review_id):
            return jsonify({"message": "Review permanently deleted successfully"})
    else:
        if ReviewService.soft_delete_review(review_id):
            return jsonify({"message": "Review deleted successfully"})
    return jsonify({"error": "Review not found"}), 404

@review_bp.route('/<int:review_id>/restore', methods=['PUT'])
@log_admin_action
@permissions_required('MANAGE_REVIEWS')
def restore_review(review_id):
    if ReviewService.restore_review(review_id):
        return jsonify({"message": "Review restored successfully"})
    return jsonify({"error": "Review not found"}), 404
