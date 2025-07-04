import pyotp
import qrcode
from io import BytesIO
import base64


class MfaService:
    @staticmethod
    def generate_secret():
        """Generates a new MFA secret key."""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(user_email: str, secret: str) -> str:
        """Generates the provisioning URI for the QR code."""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email, issuer_name="Maison Truvra"
        )

    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Generates a QR code from a URI and returns it as a base64 data URI."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verifies a user-provided MFA token against the secret."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
