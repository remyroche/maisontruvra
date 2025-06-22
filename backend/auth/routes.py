from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.services.user_service import UserService
from backend.services.exceptions import ServiceException, NotFoundException
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('public_auth_routes', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new B2C user.
    """
    data = request.get_json()
    try:
        user = UserService.create_user(data)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, user=user.to_dict()), 201
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handles the initial login with email and password.
    If the user is a staff member with MFA enabled, it returns a temporary
    token prompting for an MFA code instead of a full access token.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 1. Authenticate user by email and password.
    user = User.authenticate(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # 2. Check if the user is staff AND has MFA enabled.
    # The 'is_staff' check should be based on their role (e.g., from RBACService).
    if user.is_staff and user.is_mfa_enabled:
        # User needs to complete the second factor of authentication.
        # Issue a short-lived temporary token that includes a claim indicating
        # that the next step is MFA verification.
        additional_claims = {"mfa_required": True}
        temp_token = create_access_token(
            identity=user.id,
            expires_delta=datetime.timedelta(minutes=5),
            additional_claims=additional_claims
        )
        return jsonify({
            "message": "MFA code required.",
            "mfa_token": temp_token
        }), 202 # 202 Accepted indicates the process is not yet complete.
    
    # 3. For non-MFA users or non-staff, issue a standard access token.
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
@auth_bp.route('/login/verify-mfa', methods=['POST'])
def verify_login_mfa():
    """
    Verifies the MFA token for a staff user.
    Requires the temporary 'mfa_token' from the first login step.
    """
    data = request.get_json()
    mfa_token = data.get('mfa_token')
    totp_code = data.get('totp_code')

    # This endpoint must be accessed with the temporary token.
    # A custom decorator would be ideal here. For simplicity:
    try:
        # Decode the token to verify it and get the user identity.
        decoded_token = decode_token(mfa_token)
        if not decoded_token['mfa_required']:
             return jsonify({"error": "Invalid token for MFA verification."}), 401
        user_id = decoded_token['sub']
    except:
        return jsonify({"error": "Invalid or expired MFA token."}), 401

    # Fetch user's MFA secret from DB
    secret = User.get_mfa_secret(user_id) # This should decrypt the secret
    
    # Verify the code
    totp = pyotp.TOTP(secret)
    if not totp.verify(totp_code):
        return jsonify({"error": "Invalid MFA code."}), 401

    # On success, issue a new, fully-scoped access token.
    # Crucially, this new token contains a claim indicating MFA was completed.
    additional_claims = {"mfa_verified": True}
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims
    )
    return jsonify(access_token=access_token), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint to handle user logout.
    In a token-based system, the client is responsible for discarding the token.
    This endpoint can be used for logging or to manage a token blocklist if implemented.
    """
    # For a simple implementation, we just confirm the action.
    # For a more advanced setup, you could add the token's jti to a blocklist.
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    email = data.get('email')
    try:
        AuthService.send_password_reset_email(email)
        return jsonify({"msg": "If an account with that email exists, a password reset link has been sent."}), 200
    except NotFoundException:
         # Still return a success message to prevent user enumeration
        return jsonify({"msg": "If an account with that email exists, a password reset link has been sent."}), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    try:
        AuthService.reset_password_with_token(token, new_password)
        return jsonify({"msg": "Password has been updated successfully."}), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 400
