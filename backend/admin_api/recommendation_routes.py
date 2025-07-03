# backend/admin_api/recommendation_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..services.recommendation_service import RecommendationService
from ..services.exceptions import NotFoundException, ServiceError
from ..utils.decorators import roles_required
from ..utils.input_sanitizer import InputSanitizer

# Create a Blueprint for admin recommendation routes
admin_recommendation_bp = Blueprint('admin_recommendation_bp', __name__, url_prefix='/api/admin/recommendations')

@admin_recommendation_bp.route('/summary', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def get_recommendations_summary():
    """
    Get a summary of recommendation statistics for the admin dashboard.
    Shows overview of users with/without personalized recommendations and popular categories.
    """
    try:
        summary = RecommendationService.get_recommendations_summary()
        return jsonify(summary), 200
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500

@admin_recommendation_bp.route('/all', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def get_all_customer_recommendations():
    """
    Get recommendations for all customers with pagination.
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 50, max: 100)
    - limit_per_user: Number of recommendations per user (default: 5, max: 10)
    """
    try:
        # Get and validate query parameters
        page = InputSanitizer.sanitize_integer(request.args.get('page', 1))
        per_page = min(InputSanitizer.sanitize_integer(request.args.get('per_page', 50)), 100)
        limit_per_user = min(InputSanitizer.sanitize_integer(request.args.get('limit_per_user', 5)), 10)
        
        # Ensure positive values
        page = max(1, page)
        per_page = max(1, per_page)
        limit_per_user = max(1, limit_per_user)
        
        recommendations = RecommendationService.get_all_customer_recommendations(
            limit_per_user=limit_per_user,
            page=page,
            per_page=per_page
        )
        return jsonify(recommendations), 200
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Invalid request parameters: {str(e)}'}), 400

@admin_recommendation_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def get_user_recommendations(user_id):
    """
    Get detailed recommendations for a specific user.
    Query parameters:
    - limit: Number of recommendations to return (default: 5, max: 20)
    """
    try:
        limit = min(InputSanitizer.sanitize_integer(request.args.get('limit', 5)), 20)
        limit = max(1, limit)
        
        recommendations = RecommendationService.get_admin_recommendations_for_user(user_id, limit)
        return jsonify(recommendations), 200
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Invalid request parameters: {str(e)}'}), 400

@admin_recommendation_bp.route('/bulk', methods=['POST'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def bulk_generate_recommendations():
    """
    Generate recommendations for multiple users at once.
    Request body should contain:
    {
        "user_ids": [1, 2, 3, ...],
        "limit_per_user": 5  // optional, default: 5, max: 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_ids' not in data:
            return jsonify({'error': 'user_ids is required'}), 400
        
        user_ids = data['user_ids']
        if not isinstance(user_ids, list) or not user_ids:
            return jsonify({'error': 'user_ids must be a non-empty list'}), 400
        
        # Limit the number of users that can be processed at once
        if len(user_ids) > 100:
            return jsonify({'error': 'Cannot process more than 100 users at once'}), 400
        
        # Validate and sanitize user IDs
        try:
            user_ids = [InputSanitizer.sanitize_integer(uid) for uid in user_ids]
        except Exception:
            return jsonify({'error': 'All user_ids must be valid integers'}), 400
        
        limit_per_user = min(InputSanitizer.sanitize_integer(data.get('limit_per_user', 5)), 10)
        limit_per_user = max(1, limit_per_user)
        
        results = RecommendationService.bulk_generate_recommendations(user_ids, limit_per_user)
        return jsonify(results), 200
        
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400

@admin_recommendation_bp.route('/export', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def export_recommendations():
    """
    Export recommendations data for analysis or marketing campaigns.
    Query parameters:
    - format: 'json' or 'csv' (default: 'json')
    - limit_per_user: Number of recommendations per user (default: 5, max: 10)
    - page: Page number for pagination (default: 1)
    - per_page: Items per page (default: 100, max: 500)
    """
    try:
        format_type = request.args.get('format', 'json').lower()
        if format_type not in ['json', 'csv']:
            return jsonify({'error': 'Format must be either json or csv'}), 400
        
        page = max(1, InputSanitizer.sanitize_integer(request.args.get('page', 1)))
        per_page = min(max(1, InputSanitizer.sanitize_integer(request.args.get('per_page', 100))), 500)
        limit_per_user = min(max(1, InputSanitizer.sanitize_integer(request.args.get('limit_per_user', 5))), 10)
        
        recommendations_data = RecommendationService.get_all_customer_recommendations(
            limit_per_user=limit_per_user,
            page=page,
            per_page=per_page
        )
        
        if format_type == 'json':
            return jsonify(recommendations_data), 200
        
        elif format_type == 'csv':
            # For CSV export, we'll flatten the data structure
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'User ID', 'User Email', 'User Name', 'Registration Date', 'Last Login',
                'Recommendation Count', 'Product IDs', 'Product Names', 'Product Categories'
            ])
            
            # Write data rows
            for user_rec in recommendations_data['recommendations']:
                product_ids = []
                product_names = []
                product_categories = []
                
                for rec in user_rec['recommendations']:
                    product_ids.append(str(rec.get('id', '')))
                    product_names.append(rec.get('name', ''))
                    product_categories.append(rec.get('category', ''))
                
                writer.writerow([
                    user_rec['user_id'],
                    user_rec['user_email'],
                    user_rec['user_name'],
                    user_rec['registration_date'],
                    user_rec['last_login'],
                    user_rec['recommendation_count'],
                    '; '.join(product_ids),
                    '; '.join(product_names),
                    '; '.join(product_categories)
                ])
            
            output.seek(0)
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=customer_recommendations.csv'}
            )
            
    except ServiceError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@admin_recommendation_bp.route('/users/search', methods=['GET'])
@jwt_required()
@roles_required('Admin', 'Manager', 'Marketing')
def search_users_for_recommendations():
    """
    Search for users to view their recommendations.
    Query parameters:
    - q: Search query (email, name, or user ID)
    - limit: Number of results to return (default: 20, max: 50)
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        limit = min(max(1, InputSanitizer.sanitize_integer(request.args.get('limit', 20))), 50)
        
        from ..models import User
        from sqlalchemy import or_
        
        # Search users by email, name, or ID
        search_filter = or_(
            User.email.ilike(f'%{query}%'),
            User.first_name.ilike(f'%{query}%'),
            User.last_name.ilike(f'%{query}%')
        )
        
        # If query is numeric, also search by ID
        try:
            user_id = int(query)
            search_filter = or_(search_filter, User.id == user_id)
        except ValueError:
            pass
        
        users = User.query.filter(
            User.is_active == True,
            search_filter
        ).limit(limit).all()
        
        results = []
        for user in users:
            try:
                # Get basic recommendation info for each user
                recommendations = RecommendationService.get_recommendations_for_user(user.id, 3)
                results.append({
                    'user_id': user.id,
                    'user_email': user.email,
                    'user_name': f"{user.first_name} {user.last_name}".strip(),
                    'registration_date': user.created_at.isoformat() if user.created_at else None,
                    'has_recommendations': len(recommendations) > 0,
                    'recommendation_preview': recommendations[:2]  # Show first 2 recommendations as preview
                })
            except Exception:
                # If recommendations fail, still include user in results
                results.append({
                    'user_id': user.id,
                    'user_email': user.email,
                    'user_name': f"{user.first_name} {user.last_name}".strip(),
                    'registration_date': user.created_at.isoformat() if user.created_at else None,
                    'has_recommendations': False,
                    'recommendation_preview': []
                })
        
        return jsonify({
            'users': results,
            'total_found': len(results),
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500