from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.product_models import Product, Review
from backend.models.user_models import User
from backend.extensions import db
from backend.utils.decorators import permissions_required, api_resource_handler
from backend.services.exceptions import NotFoundException
from backend.utils.input_sanitizer import InputSanitizer
from backend.schemas import ReviewSchema

review_bp = Blueprint('review_bp', __name__)

@review_bp.route('/<int:product_id>/reviews', methods=['POST'])
@api_resource_handler(
    model=Review,
    request_schema=ReviewSchema,
    response_schema=ReviewSchema,
    ownership_exempt_roles=None,  # Public endpoint, but requires auth
    cache_timeout=0,  # No caching for review creation
    log_action=True  # Log review creation
)
@jwt_required()
def submit_review(product_id):
    """
    Allows a logged-in user to submit a review for a product.
    """
    user_id = get_jwt_identity()
    
    # Verify product exists
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found.")
    
    # Create new review with validated data
    review = Review()
    review.user_id = user_id
    review.product_id = product_id
    for key, value in g.validated_data.items():
        if hasattr(review, key):
            setattr(review, key, value)
    
    db.session.add(review)
    return review

@review_bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    """
    Get all reviews for a specific product.
    """
    # Verify product exists
    product = Product.query.get(product_id)
    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found.")
        
    # Get reviews for the product
    reviews = Review.query.filter_by(product_id=product.id).all()
    
    # Serialize reviews using schema
    review_schema = ReviewSchema(many=True)
    return jsonify(review_schema.dump(reviews)), 200
