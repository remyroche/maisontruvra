from ..models import Inventory, InventoryReservation
from .. import db
from .exceptions import ServiceError, NotFoundException
from flask import session, current_app
from datetime import datetime, timedelta
from .passport_service import PassportService
from .notification_service import NotificationService
from .monitoring_service import MonitoringService
from ..extensions import cache
from backend.models import db, Inventory, Product, StockNotificationRequest
from backend.services.email_service import EmailService
from backend.services.background_task_service import BackgroundTaskService
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select

# Updated reservation lifetime to 1 hour (60 minutes)
RESERVATION_LIFETIME_MINUTES = 60

import os
import qrcode
from flask import current_app, render_template, url_for
from ..models import db
from ..models.inventory_models import Item
from ..models.product_models import Product
from ..models.passport_models import Passport # Import the Passport model
from ..services.exceptions import NotFoundException, ValidationException, ServiceError
from ..services.pdf_service import PDFService # Import PDFService to generate PDFs

class InventoryService:
    """
    Handles the business logic for managing individual inventory items,
    including the generation of their digital passports and QR codes.
    """


    def __init__(self, logger):
        self.logger = logger
        self.background_task_service = BackgroundTaskService(logger)
        self.email_service = EmailService(logger)

    @staticmethod
    def create_item(data):
        """
        Creates a new inventory Item and its associated digital passport.
        
        This process includes:
        1. Creating the Item record in the database.
        2. Generating an HTML passport from a template.
        3. Generating a PDF version of the passport.
        4. Creating a QR code that links to the passport's public URL.
        5. Saving all asset paths in a new Passport database record.
        """
        product_id = data.get('product_id')
        if not product_id:
            raise ValidationException("A parent product ID is required to create an item.")

        parent_product = Product.query.get(product_id)
        if not parent_product:
            raise NotFoundException(f"Parent product with ID {product_id} not found.")

        try:
            # Create the Item first to get its UID
            new_item = Item(
                product_id=product_id,
                collection_id=data.get('collection_id'),
                stock_quantity=data.get('stock_quantity', 1),
                creation_date=data.get('creation_date'),
                harvest_date=data.get('harvest_date'),
                price=data.get('price'),
                producer_notes=data.get('producer_notes'),
                pairing_suggestions=data.get('pairing_suggestions')
            )
            db.session.add(new_item)
            db.session.commit() # Commit to persist the item and its generated UID

            # --- Post-Creation: Generate Passport and QR Code ---
            
            # 1. Define paths and URL for the assets
            item_uid_str = str(new_item.uid)
            passport_url = url_for('passport_bp.view_passport', item_uid=item_uid_str, _external=True)
            
            # Ensure storage directories exist
            html_dir = current_app.config['PASSPORT_HTML_STORAGE_PATH']
            pdf_dir = current_app.config['PASSPORT_PDF_STORAGE_PATH']
            qr_dir = current_app.config['QR_CODE_STORAGE_PATH']
            os.makedirs(html_dir, exist_ok=True)
            os.makedirs(pdf_dir, exist_ok=True)
            os.makedirs(qr_dir, exist_ok=True)

            html_path = os.path.join(html_dir, f"{item_uid_str}.html")
            pdf_path = os.path.join(pdf_dir, f"{item_uid_str}.pdf")
            qr_path = os.path.join(qr_dir, f"{item_uid_str}.png")

            # 2. Generate and save the HTML passport
            rendered_html = render_template('non-email/product_passport.html', item=new_item)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)

            # 3. Generate and save the PDF passport
            PDFService.generate_from_html(html_path, pdf_path)

            # 4. Generate and save the QR code
            qr_img = qrcode.make(passport_url)
            qr_img.save(qr_path)

            # 5. Create and save the Passport database record
            new_passport = Passport(
                item_id=new_item.id,
                public_url=passport_url,
                html_file_path=html_path,
                pdf_file_path=pdf_path,
                qr_code_file_path=qr_path
            )

            increase_stock(InventoryService, product_id, 1)
            
            db.session.add(new_passport)
            db.session.commit()

            return new_item

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating item and passport: {e}", exc_info=True)
            raise ServiceError("An error occurred while creating the inventory item and its passport.")


    
    @staticmethod
    def get_item_by_id(item_id):
        """Retrieves a single item by its ID."""
        return Item.query.get(item_id)

    @staticmethod
    def get_all_items():
        """Retrieves all inventory items."""
        return Item.query.all()

    def get_stock_level(self, product_id):
        """Gets the current stock level for a product."""
        inventory = db.session.query(Inventory).filter_by(product_id=product_id).first()
        return inventory.quantity if inventory else 0

    def check_stock(self, product_id, quantity_needed):
        """Checks if there is enough stock for a product."""
        return self.get_stock_level(product_id) >= quantity_needed

    def decrease_stock(self, product_id, quantity):
        """Decreases stock for a product."""
        try:
            inventory = db.session.query(Inventory).filter_by(product_id=product_id).first()
            if inventory and inventory.quantity >= quantity:
                inventory.quantity -= quantity
                db.session.commit()
                self.logger.info(f"Decreased stock for product {product_id} by {quantity}.")
                return inventory
            else:
                raise ValueError("Insufficient stock to decrease.")
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error decreasing stock for product {product_id}: {e}")
            raise

    def request_stock_notification(self, product_id, email):
        """Creates a request for a back-in-stock notification."""
        try:
            # Check if product exists
            product = db.session.query(Product).get(product_id)
            if not product:
                raise ValueError("Product not found.")

            # Check if already in stock
            if self.get_stock_level(product_id) > 0:
                return None, "Product is already in stock."

            notification_request = StockNotificationRequest(product_id=product_id, email=email)
            db.session.add(notification_request)
            db.session.commit()
            self.logger.info(f"Stock notification request created for product {product_id} by {email}.")
            return notification_request, "You will be notified when the product is back in stock."
        except IntegrityError:
            db.session.rollback()
            self.logger.warning(f"Duplicate stock notification request for product {product_id} by {email}.")
            return None, "You have already requested a notification for this product."
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error creating stock notification request: {e}")
            raise

    def process_stock_notifications(self, product_id):
        """Sends out back-in-stock emails for a given product."""
        try:
            requests = db.session.query(StockNotificationRequest).filter_by(product_id=product_id, notified_at=None).all()
            if not requests:
                self.logger.info(f"No pending stock notifications to process for product {product_id}.")
                return

            product = db.session.query(Product).get(product_id)
            if not product:
                self.logger.error(f"Cannot process stock notifications for non-existent product {product_id}.")
                return

            self.logger.info(f"Processing {len(requests)} stock notifications for product '{product.name}'.")
            
            subject = f"'{product.name}' is Back in Stock!"
            template = "back_in_stock_notification"
            
            for req in requests:
                context = {"product": product, "user_email": req.email}
                self.email_service.send_email(req.email, subject, template, context)
                req.notified_at = datetime.utcnow()
            
            db.session.commit()
            self.logger.info(f"Finished processing stock notifications for product {product_id}.")

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"An error occurred during stock notification processing for product {product_id}: {e}")


    
    @staticmethod
    def increase_stock(self, product_id, quantity):
        """
        Increases stock for a product, e.g., for a return or cancellation.
        Triggers back-in-stock notifications if the product was previously out of stock.
        """
        try:
            inventory = db.session.query(Inventory).filter_by(product_id=product_id).first()
            if not inventory:
                # This case might happen if a product was created without an inventory record
                inventory = Inventory(product_id=product_id, quantity=0)
                db.session.add(inventory)
            
            was_out_of_stock = inventory.quantity <= 0
            inventory.quantity += quantity
            
            # If the product is now back in stock, process notifications
            if was_out_of_stock and inventory.quantity > 0:
                self.logger.info(f"Product {product_id} is back in stock. Triggering notifications.")
                self.background_task_service.submit_task(self.process_stock_notifications, product_id)

            for _ in range(quantity_to_add):
                PassportService.create_and_render_passport(inventory_item.product_id)

            db.session.commit()
            self.logger.info(f"Increased stock for product {product_id} by {quantity}.")
            return inventory
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error increasing stock for product {product_id}: {e}")
            raise

    

    @staticmethod
    def reserve_stock(product_id: int, quantity_to_reserve: int, user_id: int = None):
        """
        Reserves a specific quantity of a product. This is the core function
        to prevent overselling. It's called when an item is added to a cart.
        """
        inventory_item = Inventory.query.filter_by(product_id=product_id).with_for_update().first()

        if not inventory_item:
            raise ServiceError("Product inventory not found.", 404)

        if inventory_item.available_quantity < quantity_to_reserve:
            raise ServiceError("Insufficient stock available for reservation.", 409)

        # Use either the user_id or the Flask session ID for the reservation
        session_identifier = db.session.sid if not user_id else None
        
        # Check for existing reservation for this user/session to just update it
        reservation = InventoryReservation.query.filter_by(
            inventory_id=inventory_item.id,
            user_id=user_id,
            session_id=session_identifier
        ).first()

        if reservation:
            reservation.quantity += quantity_to_reserve
            reservation.expires_at = datetime.utcnow() + timedelta(minutes=RESERVATION_LIFETIME_MINUTES)
        else:
            reservation = InventoryReservation(
                inventory_id=inventory_item.id,
                user_id=user_id,
                session_id=session_identifier,
                quantity=quantity_to_reserve,
                expires_at=datetime.utcnow() + timedelta(minutes=RESERVATION_LIFETIME_MINUTES)
            )
            db.session.add(reservation)
                    
        cache.delete('view//api/products/{}'.format(product_id)) 
        cache.delete('view//api/products') 

        db.session.commit()
        return reservation

    @staticmethod
    def release_stock(product_id: int, quantity_to_release: int, user_id: int = None):
        """
        Releases a reservation. Called when an item is removed from the cart.
        """
        inventory_item = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory_item:
            return # Fails silently if inventory doesn't exist

        session_identifier = db.session.sid if not user_id else None
        
        reservation = InventoryReservation.query.filter_by(
            inventory_id=inventory_item.id,
            user_id=user_id,
            session_id=session_identifier
        ).first()

        if reservation:
            reservation.quantity -= quantity_to_release
            if reservation.quantity <= 0:
                db.session.delete(reservation)

            cache.delete('view//api/products/{}'.format(product_id)) 
            cache.delete('view//api/products') 

            db.session.commit()

    @staticmethod
    def convert_reservation_to_sale(order):
        """
        Called when an order is successfully placed. This converts the reservation
        into a permanent stock decrement.
        """
        session_identifier = db.session.sid if not order.user_id else None
        
        for item in order.items:
            inventory_item = Inventory.query.filter_by(product_id=item.product_id).with_for_update().first()
            if inventory_item:
                inventory_item.quantity -= item.quantity
                
                reservation = InventoryReservation.query.filter_by(
                    inventory_id=inventory_item.id,
                    user_id=order.user_id,
                    session_id=session_identifier
                ).first()
                if reservation:
                    # Remove the fulfilled part of the reservation
                    reservation.quantity -= item.quantity
                    if reservation.quantity <= 0:
                        db.session.delete(reservation)
        db.session.commit()

    @staticmethod
    def release_all_reservations_for_user(user_id: int):
        """
        Deletes all inventory reservations associated with a specific user.
        This is called by CartService when a user's cart is cleared.
        This method expects to be part of a larger transaction managed by the calling service.
        """
        if not user_id:
            raise ServiceError("A valid user ID is required to release all reservations.", 400)
            
        try:
            # Find which products will be affected before deleting the reservations
            reservations_to_delete = InventoryReservation.query.filter_by(user_id=user_id).join(Inventory).all()
            product_ids_to_clear = {res.inventory.product_id for res in reservations_to_delete}

            # Use synchronize_session=False for a more efficient bulk delete,
            # as the session is being managed by the calling service (CartService).
            num_deleted = InventoryReservation.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            # This does not commit the session; the calling service is responsible for the commit.
            if num_deleted > 0:
                MonitoringService.log_info(
                    f"Released {num_deleted} total reservations for user {user_id} as part of a larger transaction.",
                    "InventoryService"
                )
                for pid in product_ids_to_clear:
                    cache.delete(f'view//api/products/{pid}')
                cache.delete('view//api/products')

        except Exception as e:
            # The calling service should handle rollback.
            MonitoringService.log_error(
                f"Error releasing all reservations for user {user_id}: {str(e)}",
                "InventoryService",
                exc_info=True
            )
            # Re-raise the exception to ensure the calling service's transaction fails.
            raise ServiceError(f"Could not release all inventory reservations for user {user_id}.")


    @staticmethod
    def release_expired_reservations():
        """
        A cleanup function to be run periodically by a background task.
        It finds and deletes all expired reservations.
        """
        # First, find which products will be affected by the expiration
        reservations_to_expire = InventoryReservation.query.filter(
            InventoryReservation.expires_at <= datetime.utcnow()
        ).join(Inventory).all()

        if not reservations_to_expire:
            return 0

        product_ids_to_clear = {res.inventory.product_id for res in reservations_to_expire}
        reservation_ids = [res.id for res in reservations_to_expire]

        # Perform the bulk delete
        expired_count = InventoryReservation.query.filter(
            InventoryReservation.id.in_(reservation_ids)
        ).delete(synchronize_session=False)

        db.session.commit()

        if expired_count > 0:
            MonitoringService.log_info(
                f"Released {expired_count} expired inventory reservations.",
                "InventoryService"
            )
            for pid in product_ids_to_clear:
                cache.delete(f'view//api/products/{pid}')
            cache.delete('view//api/products')
        return expired_count
