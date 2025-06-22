from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from backend.models.user_models import User
from backend.extensions import db, bcrypt
from backend.utils.auth_helpers import send_password_reset_email
from backend.extensions import limiter
from backend.utils.sanitization import sanitize_input

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10/hour")
def register():
    """User registration route."""
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10/hour")
def login():
    """User login route."""
    data = sanitize_input(request.get_json())
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200

    return jsonify({"msg": "Bad email or password"}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh token route."""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5/hour")
def forgot_password():
    """Forgot password route."""
    data = sanitize_input(request.get_json())
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        send_password_reset_email(user)

    # Return a generic message to prevent user enumeration
    return jsonify({"msg": "If your email is in our system, you will receive a password reset link."}), 200

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5/hour")
def reset_password():
    """Reset password route."""
    data = sanitize_input(request.get_json())
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"msg": "Token and new password are required"}), 400

    user = User.verify_reset_password_token(token)

    if not user:
        return jsonify({"msg": "Invalid or expired token"}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"msg": "Password has been reset successfully"}), 200
    
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


