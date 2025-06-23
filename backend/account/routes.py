from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.user_service import UserService
from backend.utils.sanitization import sanitize_input

account_bp = Blueprint('account_bp', __name__, url_prefix='/api/account')

# GET current user's profile
@account_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get the profile information for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify(status="error", message="User not found"), 404
    
    return jsonify(status="success", data=user.to_dict()), 200

# UPDATE current user's profile
@account_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update the profile information for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid or missing JSON body"), 400
    
    sanitized_data = sanitize_input(data)

    # For security, certain fields should not be updatable via this endpoint.
    sanitized_data.pop('password', None)
    sanitized_data.pop('email', None) # Email changes should have a separate, verified flow.
    sanitized_data.pop('role', None) # Role should only be changed by an admin.
    sanitized_data.pop('is_mfa_enabled', None)

    try:
        updated_user = UserService.update_user(user_id, sanitized_data)
        if not updated_user:
             return jsonify(status="error", message="User not found or update failed"), 404
        return jsonify(status="success", data=updated_user.to_dict()), 200
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred while updating the profile."), 500

# UPDATE current user's password
@account_bp.route('/password', methods=['PUT'])
@jwt_required()
def update_password():
    """
    Update the password for the currently authenticated user.
    Requires the old password for verification.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify(status="error", message="Both old_password and new_password are required."), 400

    old_password = data['old_password'] # Do not sanitize passwords
    new_password = data['new_password']

    try:
        # The service should handle verification of the old password
        if UserService.update_password(user_id, old_password, new_password):
            return jsonify(status="success", message="Password updated successfully."), 200
        else:
            return jsonify(status="error", message="Invalid current password or failed to update."), 400
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An internal error occurred."), 500

# GET current user's order history
@account_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_order_history():
    """
    Get the order history for the currently authenticated user.
    """
    user_id = get_jwt_identity()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        # Assumes a service method to get orders for a specific user
        orders_pagination = UserService.get_user_orders_paginated(user_id, page=page, per_page=per_page)
        
        return jsonify({
            "status": "success",
            "data": [order.to_dict_for_user() for order in orders_pagination.items], # Use a user-safe serializer
            "total": orders_pagination.total,
            "pages": orders_pagination.pages,
            "current_page": orders_pagination.page
        }), 200
    except Exception as e:
        # Log the error e
        return jsonify(status="error", message="An error occurred while fetching order history."), 500
