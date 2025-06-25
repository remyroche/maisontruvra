import os
import uuid
from flask import render_template, current_app
from ..models import db, Product
from .exceptions import ServiceError, NotFoundException
from backend.models.passport_models import ProductPassport
from backend.database import db

logger = logging.getLogger(__name__)

class PassportService:

    @staticmethod
    def generate_pdf(passport_id):
        """
        Generates a Product Passport PDF, saves it, and updates the
        passport record in the database.
        This is called by a Celery task.
        """
        logger.info(f"Starting PDF generation for passport_id: {passport_id}")

        # 1. Fetch passport and related product data from the database
        passport = ProductPassport.query.options(
            db.joinedload(ProductPassport.product)
        ).get(passport_id)

        if not passport:
            logger.error(f"Could not generate passport: Passport {passport_id} not found.")
            raise ValueError(f"Passport {passport_id} not found")

        # 2. Build the context dictionary for the template
        template_name = 'non-email/product_passport.html'
        context = {
            'passport': passport,
            'product': passport.product,
            # You can add any other related data the template might need here
        }

        try:
            # 3. Render an HTML template with the context
            html_string = render_template(template_name, **context)

            # 4. Use a library like WeasyPrint to convert the HTML to PDF
            # pdf_file = HTML(string=html_string).write_pdf()

            # 5. Save the PDF (e.g., to a cloud storage bucket) and update the passport record
            filename = f"passports/passport-{passport.id}-{passport.product.sku}.pdf"
            # cloud_storage.save(pdf_file, filename) # Real implementation

            passport.pdf_url = filename
            # Assuming a status field exists on the passport model to track generation
            if hasattr(passport, 'status'):
                passport.status = 'generated'

            db.session.commit()

            logger.info(f"PDF generation for passport {passport.id} completed. Saved to {filename}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"An error occurred during PDF generation for passport {passport_id}: {e}", exc_info=True)
            # The Celery task's autoretry will handle this exception.
            raise

    @staticmethod
    def create_and_render_passport(product_id: int):
        """
        Creates a new ProductPassport entry in the database, then renders its
        corresponding HTML page from a template and saves it.

        Args:
            product_id: The ID of the product for which to create a passport.

        Returns:
            The created ProductPassport object.
        """
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Cannot create passport: Product with ID {product_id} not found.")

        try:
            # 1. Create the database record for the new passport
            # The unique_identifier is generated automatically by the model's default.
            new_passport = ProductPassport(product_id=product.id)
            db.session.add(new_passport)
            
            # We need the ID and unique_identifier, so we flush the session to get them
            # without committing the full transaction yet.
            db.session.flush()

            # 2. Prepare data for the template
            passport_data = {
                'passport_id': new_passport.unique_identifier,
                'product_name': product.name,
                'sku': product.sku,
                'creation_date': new_passport.creation_date.strftime("%d %B %Y"),
                'material': product.material, # Assuming these fields exist on the Product model
                'origin': product.origin,
            }

            # 3. Render the HTML from the Jinja2 template
            rendered_html = render_template('non-email/product_passport.html', **passport_data)

            # 4. Save the rendered HTML to a file
            # The filename is based on the passport's unique ID to prevent collisions.
            passport_filename = f"{new_passport.unique_identifier}.html"
            # Ensure the directory exists
            passports_dir = current_app.config.get('PASSPORTS_STORAGE_PATH', 'instance/passports')
            os.makedirs(passports_dir, exist_ok=True)
            
            file_path = os.path.join(passports_dir, passport_filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)

            # 5. Store the relative path to the HTML file in the database record (optional but good practice)
            # new_passport.html_path = file_path 

            current_app.logger.info(f"Generated passport {new_passport.unique_identifier} for product {product.id}")
            
            return new_passport

        except Exception as e:
            # The calling function should handle the rollback.
            current_app.logger.error(f"Failed to create and render passport for product {product_id}: {e}", exc_info=True)
            raise ServiceError("Passport creation failed.")
