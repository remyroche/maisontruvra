from flask import Blueprint, jsonify, request
from backend.services.review_service import ReviewService
from backend.auth.permissions import admin_required
from backend.services.exceptions import NotFoundException

review_routes = Blueprint('admin_review_routes', __name__)

@review_routes.route('/reviews', methods=['GET'])
@admin_required
def get_all_reviews():
    reviews = ReviewService.get_all_reviews()
    return jsonify([r.to_dict() for r in reviews]), 200

@review_routes.route('/reviews/pending', methods=['GET'])
@admin_required
def get_pending_reviews():
    reviews = ReviewService.get_reviews_by_status('pending')
    return jsonify([r.to_dict() for r in reviews]), 200

@review_routes.route('/reviews/<int:review_id>/approve', methods=['POST'])
@admin_required
def approve_review(review_id):
    try:
        review = ReviewService.update_review_status(review_id, 'approved')
        return jsonify(review.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@review_routes.route('/reviews/<int:review_id>/reject', methods=['POST'])
@admin_required
def reject_review(review_id):
    try:
        review = ReviewService.update_review_status(review_id, 'rejected')
        return jsonify(review.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404

@review_routes.route('/reviews/<int:review_id>', methods=['DELETE'])
@admin_required
def delete_review(review_id):
    try:
        ReviewService.delete_review(review_id)
        return jsonify({"message": "Review deleted"}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404