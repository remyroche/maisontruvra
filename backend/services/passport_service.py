import os
import uuid
from flask import render_template, current_app
from ..models import db, ProductPassport, Product
from .exceptions import ServiceError, NotFoundException

class PassportService:
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
