# backend/products/review_routes.py

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.review_service import ReviewService
from ..services.exceptions import NotFoundException, ValidationException, ServiceError
from ..utils.decorators import api_resource_handler # Assuming this is the path
from ..models.review_models import Review # Assuming this is the path
from ..schemas import ReviewSchema # Assuming this exists for validation

# Create a Blueprint for review routes, nested under products
review_bp = Blueprint('review_bp', __name__, url_prefix='/api/products/<int:product_id>/reviews')

@review_bp.route('/', methods=['GET'])
def get_reviews(product_id):
    """
    Get all reviews for a specific product.
    This is a public endpoint.
    """
    try:
        reviews = ReviewService.get_reviews_for_product(product_id)
        # Manually serialize the response as this is a custom query
        schema = ReviewSchema(many=True)
        return jsonify(schema.dump(reviews)), 200
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/', methods=['POST'])
@jwt_required()
@api_resource_handler(model=Review, request_schema=ReviewSchema)
def submit_review(product_id):
    """
    Submit a new review for a specific product.
    The decorator handles validation, creation, and response.
    Expects {'rating': <int>, 'comment': <str>} in the request body.
    """
    user_id = get_jwt_identity()
    # g.validated_data is populated by the decorator
    rating = g.validated_data.get('rating')
    comment = g.validated_data.get('comment')
    
    # The service layer contains the core business logic
    new_review = ReviewService.submit_review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )
    # The decorator will serialize this object using the response_schema
    return new_review

