from flask import Blueprint, jsonify, request
from backend.services.b2b_partnership_service import B2BPartnershipService
from backend.services.exceptions import ServiceException, NotFoundException
from backend.auth.permissions import admin_required

b2b_management_routes = Blueprint('b2b_management_routes', __name__)

@b2b_management_routes.route('/b2b/requests', methods=['GET'])
@admin_required
def get_b2b_requests():
    """
    Get all B2B partnership requests.
    """
    try:
        requests = B2BPartnershipService.get_all_requests()
        return jsonify([req.to_dict() for req in requests]), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500

@b2b_management_routes.route('/b2b/requests/<int:request_id>/approve', methods=['POST'])
@admin_required
def approve_b2b_request(request_id):
    """
    Approve a B2B partnership request.
    """
    try:
        b2b_user = B2BPartnershipService.approve_request(request_id)
        return jsonify(b2b_user.to_dict()), 200
    except NotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except ServiceException as e:
        return jsonify({"error": str(e)}), 400

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

@b2b_management_routes.route('/b2b/users', methods=['GET'])
@admin_required
def get_b2b_users():
    """
    Get all approved B2B users.
    """
    try:
        b2b_users = B2BPartnershipService.get_all_b2b_users()
        return jsonify([user.to_dict() for user in b2b_users]), 200
    except ServiceException as e:
        return jsonify({"error": str(e)}), 500

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