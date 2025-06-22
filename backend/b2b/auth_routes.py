from flask import Blueprint, request, jsonify
from backend.services.b2b_partnership_service import B2BPartnershipService
from backend.services.auth_service import AuthService
from backend.services.exceptions import ServiceException
from flask_jwt_extended import create_access_token

auth_routes = Blueprint('b2b_auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def b2b_register_request():
    """
    Submits a request to become a B2B partner.
    This does not create a user account immediately.
    """
    data = request.get_json()
    try:
        partnership_request = B2BPartnershipService.create_request(data)
        return jsonify(partnership_request.to_dict()), 202 # 202 Accepted
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400

@auth_routes.route('/login', methods=['POST'])
def b2b_login():
    """
    Authenticate a B2B user and return an access token.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    try:
        # This authentication must ensure the user is an approved B2B user
        user = AuthService.authenticate_b2b_user(email, password)
        if user:
            access_token = create_access_token(identity=user.id)
            b2b_user_profile = user.b2b_account[0] # A user has one B2B profile
            return jsonify(
                access_token=access_token, 
                user=user.to_dict(),
                b2b_profile=b2b_user_profile.to_dict()
            ), 200
        return jsonify({"msg": "Invalid credentials or not a B2B user"}), 401
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 401