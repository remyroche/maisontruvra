"""
Token utilities for authentication and security operations.
"""

from flask import current_app
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer


def generate_token(data, salt="default-salt", expiry_hours=24):
    """
    Generate a secure token for the given data.

    Args:
        data: Data to encode in the token
        salt: Salt for token generation
        expiry_hours: Token expiry time in hours

    Returns:
        str: Generated token
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(data, salt=salt)


def verify_token(token, salt="default-salt", max_age_hours=24):
    """
    Verify and decode a token.

    Args:
        token: Token to verify
        salt: Salt used for token generation
        max_age_hours: Maximum age of token in hours

    Returns:
        Data encoded in the token

    Raises:
        Exception: If token is invalid or expired
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    max_age = max_age_hours * 3600  # Convert to seconds

    try:
        data = serializer.loads(token, salt=salt, max_age=max_age)
        return data
    except (SignatureExpired, BadTimeSignature) as e:
        raise Exception("Invalid or expired token") from e


def generate_password_reset_token(email):
    """Generate a password reset token."""
    return generate_token(email, salt="password-reset", expiry_hours=1)


def verify_password_reset_token(token):
    """Verify a password reset token."""
    return verify_token(token, salt="password-reset", max_age_hours=1)


def generate_email_verification_token(email):
    """Generate an email verification token."""
    return generate_token(email, salt="email-verification", expiry_hours=24)


def verify_email_verification_token(token):
    """Verify an email verification token."""
    return verify_token(token, salt="email-verification", max_age_hours=24)


def generate_magic_link_token(user_id):
    """Generate a magic link token."""
    return generate_token(user_id, salt="magic-link", expiry_hours=1)


def verify_magic_link_token(token):
    """Verify a magic link token."""
    return verify_token(token, salt="magic-link", max_age_hours=1)
