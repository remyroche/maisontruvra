import qrcode
import uuid
from io import BytesIO
import base64
from flask import current_app, render_template

from backend.models.passport_models import ProductPassport
from backend.database import db

class PassportService:
    @staticmethod
    def create_for_product(product):
        """
        Creates a new ProductPassport for a given product instance.
        Generates a unique ID and a QR code for the passport URL.
        """
        if not product or not product.id:
            raise ValueError("A valid product is required to create a passport.")

        # 1. Generate a unique identifier for the passport
        passport_uid = str(uuid.uuid4())
        
        # 2. Construct the URL for the passport
        base_url = current_app.config.get('BASE_URL')
        passport_url = f"{base_url}/passeport/{passport_uid}"

        # 3. Generate the QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(passport_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to a buffer and encode as base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        qr_code_data_uri = f"data:image/png;base64,{qr_code_base64}"

        # 4. Create and save the passport instance
        new_passport = ProductPassport(
            uid=passport_uid,
            product_id=product.id,
            qr_code_url=qr_code_data_uri,
            # We can pre-generate the static HTML here or render it on-the-fly
        )
        
        db.session.add(new_passport)
        db.session.commit()
        
        return new_passport

    @staticmethod
    def get_passport_page_by_uid(uid: str) -> str:
        """
        Retrieves passport data and renders the HTML page.
        """
        passport = ProductPassport.query.filter_by(uid=uid).first_or_404()
        product = passport.product # Assumes relationship is set up
        
        # Render the HTML template with the product and passport data
        return render_template('product-passport.html', product=product, passport=passport)
