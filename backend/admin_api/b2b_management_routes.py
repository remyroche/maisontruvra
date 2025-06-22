from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.models.b2b_models import B2BUser
from backend.extensions import db
from backend.auth.permissions import permission_required, Permission

b2b_management_bp = Blueprint('b2b_management_bp', __name__, url_prefix='/b2b')

@b2b_management_bp.route('/requests', methods=['GET'])
@jwt_required()
@permission_required(Permission.MANAGE_B2B)
def get_b2b_requests():
    # Returns B2B users awaiting approval
    users = B2BUser.query.filter_by(is_approved=False).all()
    return jsonify([user.to_dict() for user in users])

@b2b_management_bp.route('/requests/<int:user_id>/approve', methods=['POST'])
@jwt_required()
@permission_required(Permission.MANAGE_B2B)
def approve_b2b_request(user_id):
    user = B2BUser.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    # Here you might want to send an email to the user
    return jsonify({'message': f'B2B user {user.email} approved.'})

@b2b_management_bp.route('/users', methods=['GET'])
@jwt_required()
@permission_required(Permission.MANAGE_B2B)
def list_b2b_users():
    users = B2BUser.query.all()
    return jsonify([user.to_dict() for user in users])

@b2b_management_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@permission_required(Permission.MANAGE_B2B)
def update_b2b_user(user_id):
    user = B2BUser.query.get_or_404(user_id)
    data = request.get_json()
    
    user.company_name = data.get('company_name', user.company_name)
    user.is_approved = data.get('is_approved', user.is_approved)
    # Add other fields as necessary
    
    db.session.commit()
    return jsonify({'message': f'B2B user {user.email} updated.'})

@b2b_management_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@permission_required(Permission.MANAGE_B2B)
def delete_b2b_user(user_id):
    user = B2BUser.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'B2B user {user.email} deleted.'})

@b2b_management_routes.route('/b2b/requests/<int:request_id>/reject', methods=['POST'])
@admin_required
def reject_b2b_request(request_id):
    """
    Reject a B2B partnership request.
    """
    try:
        B2BPartnershipService.reject_request(request_id)
        return jsonify({"message": "Request rejected successfully."}), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400


@b2b_management_routes.route('/b2b/users/<int:b2b_user_id>', methods=['PUT'])
@admin_required
def update_b2b_user(b2b_user_id):
    """
    Update B2B user details.
    """
    data = request.get_json()
    try:
        updated_user = B2BPartnershipService.update_b2b_user(b2b_user_id, data)
        return jsonify(updated_user.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400
