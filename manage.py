
import os
import click
from flask.cli import with_appcontext
import pyotp
import qrcode
from flask_migrate import Migrate

from backend import create_app, db
from backend.models.user_models import User, UserRole

# Create a minimal app instance for the CLI to work
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_admin(email, password):
    """Creates a new administrator user and generates a TOTP secret."""
    if User.query.filter_by(email=email).first():
        print(f"Error: User with email {email} already exists.")
        return

    # Generate a new TOTP secret
    totp_secret = pyotp.random_base32()

    # Create the new user
    new_admin = User(
        email=email,
        role=UserRole.ADMIN,
        is_active=True,
        email_verified=True, # Admins are trusted by default
        totp_secret=totp_secret # Save the secret
    )
    new_admin.set_password(password)
    
    db.session.add(new_admin)
    db.session.commit()
    
    print(f"✅ Successfully created admin user with email: {email}")

    # Generate the provisioning URI for the authenticator app
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=email,
        issuer_name="Maison Trüvra Admin"
    )

    print("\nScan the QR code below with your authenticator app (e.g., Google Authenticator).")
    
    # Create and print the QR code to the terminal
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    qr.print_tty()

    print(f"\nIf you cannot scan the QR code, manually enter this secret key into your app:")
    print(f"🔑 Secret Key: {totp_secret}\n")


if __name__ == '__main__':
    app.cli()
