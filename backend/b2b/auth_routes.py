from flask import Blueprint, request, jsonify
from backend.services.b2b_partnership_service import B2BPartnershipService
from backend.services.auth_service import AuthService
from backend.services.exceptions import ServiceException
from flask_jwt_extended import create_access_token
import pyotp
import datetime

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

@b2b_auth_bp.route('/pro/login', methods=['POST'])
@limiter.limit("5 per minute") # Apply rate limiting to prevent brute-force attacks
def b2b_login():
    """
    Handles the initial B2B login with email and password.
    This is the first step and checks for MFA requirements.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    # 1. Authenticate user via a dedicated B2B authentication service.
    #    This service would handle password validation against the hash in the DB.
    try:
        # This service method should find the user by email, ensure their role is 'B2B',
        # and verify their password. It returns a user object on success.
        user = AuthService.authenticate_b2b_user(email, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"B2B authentication error for {email}: {e}")
        return jsonify({"error": "Invalid credentials"}), 401

    # 2. Check if the authenticated B2B user has MFA enabled.
    if user.is_mfa_enabled:
        # Issue a short-lived temporary token that requires MFA verification as the next step.
        additional_claims = {"mfa_required": True, "is_b2b": True}
        temp_token = create_access_token(
            identity=user.id,
            expires_delta=datetime.timedelta(minutes=5),
            additional_claims=additional_claims
        )
        return jsonify({
            "message": "MFA code required.",
            "mfa_token": temp_token
        }), 202 # 202 Accepted: The request is valid but the process is not complete.

    # 3. For B2B users without MFA, issue a standard access token.
    access_token = create_access_token(identity=user.id, additional_claims={"is_b2b": True})
    return jsonify(access_token=access_token), 200


@b2b_auth_bp.route('/pro/login/verify-mfa', methods=['POST'])
@limiter.limit("10 per minute") # Also rate-limit the verification step
def b2b_verify_login_mfa():
    """
    Verifies the MFA TOTP code for a B2B user.
    This is the second step of the login process.
    """
    data = request.get_json()
    # The frontend must send the temporary token from the first step.
    mfa_token = request.headers.get('Authorization').split()[1]
    totp_code = data.get('totp_code')

    if not totp_code:
        return jsonify({"error": "MFA code (totp_code) is required."}), 400

    # A custom decorator would be ideal here to verify the temp token.
    # For clarity, the logic is shown inline:
    try:
        decoded_token = decode_token(mfa_token) # Assumes a JWT decoding utility
        if not decoded_token.get('mfa_required'):
             return jsonify({"error": "Invalid token type for MFA verification."}), 401
        user_id = decoded_token['sub']
    except Exception:
        return jsonify({"error": "Invalid or expired MFA token."}), 401

    # Fetch user's decrypted MFA secret from the DB via a service
    mfa_secret = AuthService.get_user_mfa_secret(user_id)
    if not mfa_secret:
        return jsonify({"error": "MFA not configured correctly for user."}), 500

    # Verify the provided TOTP code.
    totp = pyotp.TOTP(mfa_secret)
    if not totp.verify(totp_code):
        return jsonify({"error": "Invalid MFA code."}), 401

    # On success, issue a new, fully-scoped access token.
    # This token confirms the user is a B2B user AND has passed MFA.
    additional_claims = {"mfa_verified": True, "is_b2b": True}
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims
    )
    return jsonify(access_token=access_token), 200
