from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.review_service import ReviewService
from backend.services.exceptions import ServiceException, NotFoundException

review_routes = Blueprint('review_routes', __name__)

@review_routes.route('/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def submit_review(product_id):
    """
    Submit a review for a product.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    if not rating:
        return jsonify({"error": "Rating is required."}), 400

    try:
        # Check if the user has purchased this product before allowing a review
        if not ReviewService.has_user_purchased_product(user_id, product_id):
             return jsonify({"error": "You can only review products you have purchased."}), 403

        review = ReviewService.create_review(product_id, user_id, rating, comment)
        return jsonify(review.to_dict()), 201
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400
