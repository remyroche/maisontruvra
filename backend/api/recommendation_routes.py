# backend/api/recommendation_routes.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.recommendation_service import RecommendationService
from ..services.exceptions import NotFoundException, ServiceError
from ..utils.decorators import roles_required

# Create a Blueprint for recommendation routes
recommendation_bp = Blueprint('recommendation_bp', __name__, url_prefix='/api')

@recommendation_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_user_recommendations():
    """
    Get personalized product recommendations for the current logged-in user.
    """
    user_id = get_jwt_identity()
    try:
        recommendations = RecommendationService.get_recommendations_for_user(user_id)
        return jsonify(recommendations), 200
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/admin/users/<int:user_id>/recommendations', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def get_admin_recommendations_for_user(user_id):
    """
    Admin endpoint to get personalized recommendations for a specific user.
    This is useful for personalizing marketing communications.
    
    DEPRECATED: Please use /api/admin/recommendations/user/<user_id> instead.
    This endpoint is maintained for backward compatibility.
    """
    try:
        recommendations = RecommendationService.get_admin_recommendations_for_user(user_id)
        
        # Add deprecation notice in response headers
        from flask import make_response
        response = make_response(jsonify(recommendations), 200)
        response.headers['X-Deprecated'] = 'true'
        response.headers['X-Deprecated-Message'] = 'Use /api/admin/recommendations/user/<user_id> instead'
        return response
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
