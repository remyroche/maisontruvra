from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.product_models import Product, Review
from backend.models.user_models import User
from backend.extensions import db
from backend.utils.decorators import permissions_required, api_resource_handler
from backend.utils.input_sanitizer import InputSanitizer
from backend.schemas import ReviewSchema

review_bp = Blueprint('review_bp', __name__)

@review_bp.route('/<int:product_id>/reviews', methods=['POST'])
@api_resource_handler(Product, schema=ReviewSchema())
@jwt_required()
def submit_review(product_id):
    """
    Allows a logged-in user to submit a review for a product.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Product is already validated and available as g.product
    product = g.product

    # Optional: Check if user has purchased the product before reviewing
    # This would require linking orders to users and products.

    review = Review(
        product_id=product.id,
        user_id=user.id,
        rating=g.validated_data['rating'],
        comment=g.validated_data.get('comment')
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({"msg": "Review submitted successfully"}), 201

@review_bp.route('/<int:product_id>/reviews', methods=['GET'])
@api_resource_handler(Product)
def get_reviews(product_id):
    """
    Get all reviews for a specific product.
    """
    # Product is already validated and available as g.product
    product = g.product
        
    reviews = Review.query.filter_by(product_id=product.id).all()
    
    return jsonify([{
        'id': r.id,
        'rating': r.rating,
        'comment': r.comment,
        'user': r.user.first_name, # or some user identifier
        'created_at': r.created_at.isoformat()
    } for r in reviews]), 200
