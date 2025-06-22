from flask_jwt_extended import jwt_required, get_jwt_identity,create_access_token
from backend.services.user_service import UserService
from backend.services.order_service import OrderService
from backend.services.exceptions import ServiceException
from backend.auth.permissions import permission_required
import datetime


account_bp = Blueprint('account_bp', __name__)

@account_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500


@account_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    try:
        orders = OrderService.get_orders_by_user(user_id)
        return jsonify([order.to_dict() for order in orders]), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500

@account_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_user_order_detail(order_id):
    user_id = get_jwt_identity()
    try:
        order = OrderService.get_order_details(order_id, user_id)
        if not order:
             return jsonify({"msg": "Order not found or access denied"}), 404
        return jsonify(order.to_dict_detailed()), 200
    except ServiceException as e:
        return jsonify({"msg": str(e)}), 500


# --- User Registration ---

@account_bp.route('/register', methods=['POST'])
def create_account():
    """
    Creates a new B2C user account.
    B2B registration would likely have a separate, more complex flow.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not all([email, password, name]):
        return jsonify({"error": "Email, password, and name are required."}), 400

    if User.find_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    try:
        # The create method on the User model should handle password hashing.
        user = User.create(name=name, email=email, password=password, role='B2C')
        
        # Add a job to the queue to send a welcome email.
        queue.enqueue('worker.send_email', {'type': 'welcome', 'recipient': user.email})

        return jsonify({"message": f"Account for {user.email} created successfully."}), 201

    except Exception as e:
        logger.error(f"Error during account registration for {email}: {e}")
        return jsonify({"error": "An internal error occurred during registration."}), 500

# --- Password Reset Flow ---

@account_bp.route('/password/request-reset', methods=['POST'])
def request_password_reset():
    """
    Initiates the password reset process for a user.
    Generates a secure, single-use token and sends it to the user's email.
    """
    data = request.get_json()
    email = data.get('email')
    user = User.find_by_email(email)

    if user:
        try:
            # Generate a secure token and its expiration.
            token = PasswordResetToken.generate(user.id)
            reset_link = f"https://yourfrontend.com/reset-password?token={token}"
            
            # Queue an email to be sent with the reset link.
            queue.enqueue(
                'worker.send_email',
                {
                    'type': 'password_reset',
                    'recipient': user.email,
                    'context': {'reset_link': reset_link}
                }
            )
        except Exception as e:
            logger.error(f"Error generating password reset token for {email}: {e}")
            # Do not expose the error to the user for security reasons.

    # Always return a success message to prevent user enumeration attacks.
    return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200

@account_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """
    Resets the user's password using a valid token.
    """
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not all([token, new_password]):
        return jsonify({"error": "Token and new_password are required."}), 400

    # The service method should validate the token, check its expiry,
    # find the user, update the password, and invalidate the token.
    success = PasswordResetToken.use_token_to_reset_password(token, new_password)

    if success:
        return jsonify({"message": "Your password has been reset successfully."}), 200
    else:
        return jsonify({"error": "Invalid or expired token."}), 400

# --- Profile Management ---

@account_bp.route('/profile', methods=['PUT'])
@permission_required() # Requires a logged-in user
def update_profile():
    """
    Allows a logged-in user to update their personal information.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Define which fields are updatable to prevent unwanted changes.
    updatable_fields = ['name', 'shipping_address', 'phone_number']
    update_data = {key: value for key, value in data.items() if key in updatable_fields}

    if not update_data:
        return jsonify({"error": "No updatable fields provided."}), 400

    try:
        user = User.update(user_id, update_data)
        return jsonify({"message": "Profile updated successfully.", "user": user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

