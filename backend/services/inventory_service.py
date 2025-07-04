import os
import uuid
import logging
import qrcode
from datetime import datetime, timedelta
from flask import current_app, render_template, url_for
from sqlalchemy.exc import SQLAlchemyError

# FIX: Consolidated all imports into a single, clean block.
# This resolves all F811 (redefinition) and E402 (import not at top) errors.
from backend.database import db
from backend.extensions import cache
from backend.models import (
    Inventory,
    InventoryReservation,
    Product,
    StockMovement,
    SerializedItem,
    ProductPassport,
    PassportEntry,
)
from backend.services.exceptions import (
    NotFoundException,
    ServiceError,
    ValidationException,
    InsufficientStockException,
)
from backend.services.notification_service import NotificationService
from backend.services.pdf_service import PDFService # Assuming a PDF service exists

# CONSTANTS
RESERVATION_LIFETIME_MINUTES = 60

class InventoryService:
    """
    Manages stock levels, reservations, and serialized digital passports for products.
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = db.session
        self.pdf_service = PDFService() # Initialize any dependent services

    def add_new_stock_batch(self, product_id: int, quantity: int, item_details: dict):
        """
        Adds a batch of new serialized items to the inventory for a given product.
        This is a transactional operation.
        """
        if quantity <= 0:
            raise ValidationException("Quantity must be a positive integer.")

        product = self.session.query(Product).with_for_update().get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found.")

        try:
            was_out_of_stock = product.get_available_stock() <= 0
            created_items = []

            for _ in range(quantity):
                item = self._create_serialized_item_and_passport(product, item_details)
                created_items.append(item)
            
            # Increment general stock and log movement
            inventory = self._get_or_create_inventory(product.id)
            inventory.quantity += quantity
            log = StockMovement(
                product_id=product.id, quantity_change=quantity, reason="Batch Creation"
            )
            self.session.add(log)

            self.session.commit()
            self.logger.info(f"Successfully created {quantity} items for product {product_id}.")

            if was_out_of_stock:
                self.logger.info(f"Product {product.name} is back in stock. Triggering notifications.")
                notification_service = NotificationService()
                notification_service.notify_users_of_restock(product.id)

            return created_items
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Failed to create batch for product {product_id}. Rolled back. Error: {e}", exc_info=True)
            # FIX: Correctly raise exception with 'from e'
            raise ServiceError("Failed to create the batch of items.") from e

    def reserve_stock(self, product_id: int, quantity: int, user_id: int):
        """Reserves stock for a user, preventing overselling. Called when adding to cart."""
        inventory = self.session.query(Inventory).filter_by(product_id=product_id).with_for_update().first()
        if not inventory or inventory.get_available_stock() < quantity:
            raise InsufficientStockException("Not enough stock available to reserve.")

        reservation = self.session.query(InventoryReservation).filter_by(
            inventory_id=inventory.id, user_id=user_id
        ).first()

        expires_at = datetime.utcnow() + timedelta(minutes=RESERVATION_LIFETIME_MINUTES)
        if reservation:
            reservation.quantity += quantity
            reservation.expires_at = expires_at
        else:
            reservation = InventoryReservation(
                inventory_id=inventory.id,
                user_id=user_id,
                quantity=quantity,
                expires_at=expires_at,
            )
            self.session.add(reservation)

        cache.delete(f"product_stock_{product_id}")
        self.session.commit()
        return reservation

    def release_stock(self, product_id: int, quantity: int, user_id: int):
        """Releases a user's stock reservation. Called when removing from cart."""
        inventory = self.session.query(Inventory).get(product_id)
        if not inventory: return

        reservation = self.session.query(InventoryReservation).filter_by(
            inventory_id=inventory.id, user_id=user_id
        ).first()

        if reservation:
            reservation.quantity -= quantity
            if reservation.quantity <= 0:
                self.session.delete(reservation)
            
            cache.delete(f"product_stock_{product_id}")
            self.session.commit()
    
    def release_all_reservations_for_user(self, user_id: int):
        """Clears all reservations for a user. Called by CartService.clear_cart."""
        try:
            InventoryReservation.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            self.logger.info(f"Released all reservations for user {user_id}.")
        except Exception as e:
            self.logger.error(f"Error releasing all reservations for user {user_id}: {e}", exc_info=True)
            # FIX: Correctly raise exception with 'from e'
            raise ServiceError(f"Could not release all inventory reservations for user {user_id}.") from e
            
    # --- Private Helper Methods ---

    def _get_or_create_inventory(self, product_id: int) -> Inventory:
        """Internal helper to get or create the main inventory record for a product."""
        inventory = self.session.query(Inventory).filter_by(product_id=product_id).first()
        if not inventory:
            inventory = Inventory(product_id=product_id, quantity=0)
            self.session.add(inventory)
            self.session.flush() # Flush to get ID
        return inventory

    def _create_serialized_item_and_passport(self, product: Product, item_details: dict) -> SerializedItem:
        """Private helper to handle the 'birth' of a single item and its digital assets."""
        try:
            uid = f"{product.sku or 'SKU'}-{uuid.uuid4().hex[:8].upper()}"
            new_item = SerializedItem(product_id=product.id, uid=uid, status="in_stock", **item_details)
            self.session.add(new_item)
            self.session.flush()

            passport_url = url_for("passport_bp.view_passport", item_uid=uid, _external=True)
            html_path, pdf_path, qr_path = self._generate_passport_assets(new_item, passport_url)

            new_passport = ProductPassport(
                serialized_item=new_item,
                html_file_path=html_path,
                pdf_file_path=pdf_path,
                qr_code_file_path=qr_path,
            )
            self.session.add(new_passport)

            entry = PassportEntry(passport=new_passport, event_type="CREATED", details="Item manufactured.")
            self.session.add(entry)

            return new_item
        except Exception as e:
            self.logger.error(f"Error during sub-process of creating item for product {product.id}: {e}", exc_info=True)
            # FIX: Correctly raise exception with 'from e'
            raise ServiceException("An error occurred during item creation.") from e

    def _generate_passport_assets(self, item: SerializedItem, url: str) -> tuple:
        """Generates and saves the HTML, PDF, and QR code for a passport."""
        html_dir = current_app.config["PASSPORT_HTML_STORAGE_PATH"]
        pdf_dir = current_app.config["PASSPORT_PDF_STORAGE_PATH"]
        qr_dir = current_app.config["QR_CODE_STORAGE_PATH"]
        os.makedirs(html_dir, exist_ok=True)
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(qr_dir, exist_ok=True)
        
        html_path = os.path.join(html_dir, f"{item.uid}.html")
        pdf_path = os.path.join(pdf_dir, f"{item.uid}.pdf")
        qr_path = os.path.join(qr_dir, f"{item.uid}.png")

        # Generate HTML
        rendered_html = render_template("non-email/product_passport.html", item=item, passport_url=url)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        
        # Generate PDF
        self.pdf_service.generate_from_html(html_path, pdf_path)
        
        # Generate QR Code
        qrcode.make(url).save(qr_path)
        
        return html_path, pdf_path, qr_path
