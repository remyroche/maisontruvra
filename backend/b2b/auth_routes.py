from flask import Blueprint, request, jsonify
from backend.services.b2b_service import B2BService # Assumed to handle B2B auth
from backend.utils.sanitization import sanitize_input

b2b_auth_bp = Blueprint('b2b_auth_bp', __name__, url_prefix='/api/b2b/auth')

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
