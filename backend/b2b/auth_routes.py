from flask import Blueprint, request, jsonify
from backend.services.b2b_service import B2BService # Assumed to handle B2B auth
from backend.utils.sanitization import sanitize_input
from ..services.auth_service import AuthService
from ..services.exceptions import ServiceError
from ..models import db, User
from backend.auth.permissions import admin_required, staff_required
from ..utils.decorators import log_admin_action

b2b_auth_bp = Blueprint('b2b_auth_bp', __name__, url_prefix='/api/b2b/auth')


@admin_auth_bp.route('/reauthenticate', methods=['POST'])
@staff_required
@admin_required # Ensures a user must exist to even attempt re-auth
def reauthenticate():
    """
    Re-authenticates an existing session after a timeout.
    """
    data = request.get_json()
    password = data.get('password')
    
    # Verify password against the currently logged-in user
    if not current_user.check_password(password):
        return jsonify({"error": "Invalid password"}), 401

    # On success, reset the session timers
    now = datetime.utcnow()
    session['login_time'] = now.isoformat()
    session['last_activity_time'] = now.isoformat()
    session.pop('reauth_needed', None) # Remove the re-auth flag
    
    return jsonify({"message": "Re-authentication successful."})


@b2b_auth_bp.route('/forgot-password', methods=['POST'])
def b2b_forgot_password():
    """Endpoint for B2B users to request a password reset email."""
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    data = request.get_json()
    email = data.get('email')
    
    # Assuming B2BAuthService returns the user and a reset token
    user, token = B2BAuthService.issue_password_reset_token(email)
    
    if user and token:
        # --- Send B2B Password Reset Email ---
        EmailService.send_password_reset_email(user, token, is_b2b=True)
        

    AuthService.request_b2b_password_reset(data['email'])
    # Always return a success message to prevent user enumeration
    return jsonify({"message": "If a B2B account with that email exists, a password reset link has been sent."}), 200

@b2b_auth_bp.route('/reset-password', methods=['POST'])
def b2b_reset_password():
    """Endpoint for B2B users to set a new password using a valid token."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required."}), 400

    # Verify using the specific B2B salt
    user = AuthService.verify_password_reset_token(token, salt='b2b-password-reset-salt')

    if not user or not user.is_b2b:
        return jsonify({"error": "Invalid or expired token."}), 401

    try:
        AuthService.reset_user_password(user, new_password)
        return jsonify({"message": "Password has been reset successfully."}), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status_code
        
# B2B User Registration Request
@b2b_auth_bp.route('/register', methods=['POST'])
def b2b_register():
    """
    Submit a B2B account registration request for admin approval.
    """
    data = request.get_json()
    if not data:
        return jsonify(status="error", message="Invalid JSON"), 400

    # Sanitize all incoming data
    sanitized_data = {k: sanitize_input(v) for k, v in data.items()}

    required_fields = [
        'email', 'password', 'first_name', 'last_name', 
        'company_name', 'vat_number', 'phone_number'
    ]
    if not all(field in sanitized_data for field in required_fields):
        missing = [f for f in required_fields if f not in sanitized_data]
        return jsonify(status="error", message=f"Missing required fields: {', '.join(missing)}"), 400

    new_user = B2BAuthService.create_pending_b2b_account(data)
    EmailService.send_b2b_account_pending_email(new_user)

    try:
        # This service creates a B2B account with a 'pending' status
        b2b_account = B2BService.create_b2b_account_request(sanitized_data)
        return jsonify(
            status="success", 
            message="Your registration request has been submitted for approval.",
            data=b2b_account.to_dict()
        ), 201
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 409 # Conflict, e.g., user/company exists
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal server error occurred during registration."), 500

# B2B User Login
@b2b_auth_bp.route('/login', methods=['POST'])
def b2b_login():
    """
    Authenticate a B2B user and return JWT tokens.
    Ensures the user has the 'B2B' role and their account is 'approved'.
    """
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(status="error", message="Email and password are required."), 400

    email = sanitize_input(data.get('email'))
    password = data.get('password') # Do not sanitize

    try:
        # This service method should verify credentials and B2B status
        result = B2BService.login_b2b_user(email, password)
        return jsonify(status="success", **result), 200
    except ValueError as e:
        # Handles cases like wrong password, user not found, account not approved, not a B2B user
        return jsonify(status="error", message=str(e)), 401 # Unauthorized
    except Exception as e:
        # Log error e
        return jsonify(status="error", message="An internal server error occurred."), 500

# Note: B2B password reset could potentially use the same flow as regular users,
# but might require its own endpoints if the logic or email templates differ.
# For now, we assume the main auth password reset flow is sufficient.
