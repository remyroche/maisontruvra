# FILE: routes/mfa.py
# This Flask blueprint handles the setup and verification process for MFA.
# -----------------------------------------------------------------------------

import io

import pyotp
import qrcode
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity

from backend.database import db
from backend.extensions import cache  # Import the cache instance
from backend.services.email_service import EmailService
from backend.services.monitoring_service import MonitoringService
from backend.utils.decorators import permission_required

# Assume 'db' is a database connection manager and 'encryption_service' is configured

mfa_bp = Blueprint("mfa", __name__)


@mfa_bp.route("/mfa/setup", methods=["POST"])
@permission_required()  # Requires a logged-in user
def setup_mfa():
    """
    Generates a new MFA secret for the user and returns it as a QR code.
    This is the first step of the MFA setup process. The secret is stored
    temporarily and not yet saved as 'active' for the user.
    """
    user_id = get_jwt_identity()
    # In a real app, you would fetch user details like email from the DB
    user_email = "user@example.com"

    # Generate a new TOTP secret
    totp_secret = pyotp.random_base32()

    # Generate the provisioning URI for authenticator apps (like Google Authenticator)
    provisioning_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=user_email, issuer_name="YourAppName"
    )

    # Encrypt the secret before storing it temporarily in the session or a cache
    # DO NOT save it to the user's record until they have verified it.
    # For simplicity here, we will just return it. In a real app, manage this state carefully.

    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save image to a byte stream
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    # Store the un-activated secret securely, e.g., in Redis with a short TTL,
    # associated with the user_id.
    # In a production app, you should encrypt this secret before caching.
    cache.set(f"mfa_setup_{user_id}", totp_secret, timeout=300)  # 5-minute expiry

    # Return the QR code image and the secret (for manual entry)
    # The frontend should display the QR code and also the 'totp_secret' for manual setup.
    return Response(img_io, mimetype="image/png")


@mfa_bp.route("/mfa/verify", methods=["POST"])
@permission_required()
def verify_mfa_setup():
    """
    Verifies the TOTP code provided by the user and, on success,
    permanently enables MFA for their account.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    token = data.get("token")

    # 1. Retrieve the temporarily stored secret for this user from the cache.
    secret = cache.get(f"mfa_setup_{user_id}")
    if not secret:
        return jsonify(
            {"error": "MFA setup session expired. Please start over."}
        ), 408  # 408 Request Timeout

    # 2. Verify the token against the secret.
    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        return jsonify({"error": "Invalid token. Please try again."}), 400

    # 3. On successful verification, save the encrypted secret to the database
    #    and enable MFA for the user. This is a permanent change.
    # In a real app, use a strong encryption service here.
    encrypted_secret_for_db = "encrypted:" + secret  # Placeholder for actual encryption
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET is_mfa_enabled = TRUE, mfa_secret = %s WHERE id = %s",
            (encrypted_secret_for_db, user_id),
        )
        conn.commit()
        # Clean up the temporary secret from the cache
        cache.delete(f"mfa_setup_{user_id}")
        # You should also generate and show the user their one-time recovery codes here.
        EmailService.send_security_alert(
            user_id, "L'authentification à deux facteurs (2FA) a été activée"
        )
        return jsonify({"message": "MFA has been successfully enabled."}), 200
    except Exception as e:
        conn.rollback()
        MonitoringService.log_error(f"Failed to enable MFA for user {user_id}: {e}")
        return jsonify({"error": "Could not enable MFA due to a server error."}), 500
    finally:
        cursor.close()
        conn.close()
