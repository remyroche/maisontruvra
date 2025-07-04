import uuid
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from backend.models import Inventory, Product
from backend.services.background_task_service import BackgroundTaskService
from backend.services.email_service import EmailService

from .. import db
from ..extensions import cache
from ..models import Inventory, InventoryReservation, Product, StockMovement
from ..models.passport_models import PassportEntry, ProductPassport, SerializedItem
from .exceptions import NotFoundException, ServiceError, ServiceException
from .monitoring_service import MonitoringService

# Updated reservation lifetime to 1 hour (60 minutes)
RESERVATION_LIFETIME_MINUTES = 60

import os

import qrcode
from flask import render_template, url_for

from ..database import db
from ..models.inventory_models import Item
from ..models.product_models import Product
from ..services.exceptions import NotFoundException, ServiceError, ValidationException


class InventoryService:
    """
    Handles the business logic for managing individual inventory items,
    including the generation of their digital passports and QR codes.
    """

    def __init__(self, logger):
        self.logger = logger
        self.background_task_service = BackgroundTaskService(logger)
        self.email_service = EmailService(logger)

    def create_new_item(self, item_data: dict):
        """
        Fonction principale pour la création d'un article unique et de son passeport.
        C'est le processus de "naissance" d'un article.
        """
        product_id = item_data.get("product_id")
        if not product_id:
            raise ValidationException("Un 'product_id' parent est requis.")

        product = (
            self.session.query(Product)
            .filter_by(id=product_id)
            .with_for_update()
            .one_or_none()
        )
        if not product:
            raise NotFoundException(resource_name="Product", resource_id=product_id)

        try:
            was_out_of_stock = product.stock <= 0

            # 1. Créer l'enregistrement de l'article sérialisé
            new_item = SerializedItem(
                product_id=product.id,
                uid=f"{product.sku or 'SKU'}-{uuid.uuid4().hex[:8].upper()}",
                status="in_stock",
                # Ajout des autres champs depuis item_data
                creation_date=item_data.get("creation_date"),
                harvest_date=item_data.get("harvest_date"),
                price=item_data.get("price"),
                producer_notes=item_data.get("producer_notes"),
                pairing_suggestions=item_data.get("pairing_suggestions"),
            )
            self.session.add(new_item)
            self.session.flush()  # Utiliser flush pour obtenir l'ID/UID de new_item avant le commit final

            # 2. Définir les chemins et l'URL pour les actifs numériques
            item_uid_str = str(new_item.uid)
            passport_url = url_for(
                "passport_bp.view_passport", item_uid=item_uid_str, _external=True
            )

            # S'assurer que les répertoires de stockage existent
            html_dir = current_app.config["PASSPORT_HTML_STORAGE_PATH"]
            pdf_dir = current_app.config["PASSPORT_PDF_STORAGE_PATH"]
            qr_dir = current_app.config["QR_CODE_STORAGE_PATH"]
            os.makedirs(html_dir, exist_ok=True)
            os.makedirs(pdf_dir, exist_ok=True)
            os.makedirs(qr_dir, exist_ok=True)

            html_path = os.path.join(html_dir, f"{item_uid_str}.html")
            pdf_path = os.path.join(pdf_dir, f"{item_uid_str}.pdf")
            qr_path = os.path.join(qr_dir, f"{item_uid_str}.png")

            # 3. Générer et sauvegarder le passeport HTML
            rendered_html = render_template(
                "non-email/product_passport.html",
                item=new_item,
                passport_url=passport_url,
            )
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(rendered_html)

            # 4. Générer le PDF à partir du HTML
            self.pdf_service.generate_from_html(html_path, pdf_path)

            # 5. Générer et sauvegarder le QR code
            qr_img = qrcode.make(passport_url)
            qr_img.save(qr_path)

            # 6. Créer l'enregistrement du Passeport Numérique avec les chemins des actifs
            new_passport = ProductPassport(
                serialized_item=new_item,
                html_file_path=html_path,
                pdf_file_path=pdf_path,
                qr_code_file_path=qr_path,
            )
            self.session.add(new_passport)

            # 7. Créer l'entrée "CREATED" dans l'historique du passeport
            entry = PassportEntry(
                passport=new_passport,
                event_type="CREATED",
                details="Item manufactured and stock created.",
            )
            self.session.add(entry)

            # 8. Incrémenter le stock général du produit
            product.stock += 1

            # 9. Enregistrer le mouvement de stock
            log = StockMovement(
                product_id=product.id, quantity_change=1, reason="Item Creation"
            )
            self.session.add(log)

            # 10. Le commit final se fera par la fonction appelante (add_new_stock_batch)

            # Notification si le produit est de nouveau en stock
            if was_out_of_stock and product.stock > 0:
                self.logger.info(
                    f"Product {product.name} is back in stock. Triggering notifications."
                )
                from .notification_service import NotificationService

                notification_service = NotificationService()
                notification_service.notify_users_of_restock.delay(product.id)

            return new_item

        except Exception as e:
            # En cas d'erreur, le rollback est géré par la fonction appelante
            self.logger.error(
                f"Error creating new item for product {product_id}: {e}", exc_info=True
            )
            raise ServiceException("An error occurred during item creation.")

    def add_new_stock_batch(self, item_data: dict, quantity: int):
        """
        Ajoute un lot de nouveaux articles en appelant create_new_item pour chaque unité.
        Gère la transaction pour s'assurer que soit tous les articles sont créés, soit aucun.
        """
        if quantity <= 0:
            raise ValidationException("Quantity must be a positive integer.")

        try:
            created_items = []
            for _ in range(quantity):
                item = self.create_new_item(item_data)
                created_items.append(item)

            # Commit la transaction entière une fois que toutes les créations ont réussi
            self.session.commit()
            self.logger.info(
                f"Successfully created a batch of {quantity} items for product {item_data.get('product_id')}."
            )
            return created_items

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Failed to create item batch. Rolled back transaction. Error: {e}",
                exc_info=True,
            )
            raise ServiceException("Failed to create the batch of items.")

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
            inventory = (
                db.session.query(Inventory).filter_by(product_id=product_id).first()
            )
            if inventory and inventory.quantity >= quantity:
                inventory.quantity -= quantity
                db.session.commit()
                self.logger.info(
                    f"Decreased stock for product {product_id} by {quantity}."
                )
                return inventory
            else:
                raise ValueError("Insufficient stock to decrease.")
        except (SQLAlchemyError, ValueError) as e:
            db.session.rollback()
            self.logger.error(f"Error decreasing stock for product {product_id}: {e}")
            raise

    @staticmethod
    def reserve_stock(product_id: int, quantity_to_reserve: int, user_id: int = None):
        """
        Reserves a specific quantity of a product. This is the core function
        to prevent overselling. It's called when an item is added to a cart.
        """
        inventory_item = (
            Inventory.query.filter_by(product_id=product_id).with_for_update().first()
        )

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
            session_id=session_identifier,
        ).first()

        if reservation:
            reservation.quantity += quantity_to_reserve
            reservation.expires_at = datetime.utcnow() + timedelta(
                minutes=RESERVATION_LIFETIME_MINUTES
            )
        else:
            reservation = InventoryReservation(
                inventory_id=inventory_item.id,
                user_id=user_id,
                session_id=session_identifier,
                quantity=quantity_to_reserve,
                expires_at=datetime.utcnow()
                + timedelta(minutes=RESERVATION_LIFETIME_MINUTES),
            )
            db.session.add(reservation)

        cache.delete(f"view//api/products/{product_id}")
        cache.delete("view//api/products")

        db.session.commit()
        return reservation

    @staticmethod
    def release_stock(product_id: int, quantity_to_release: int, user_id: int = None):
        """
        Releases a reservation. Called when an item is removed from the cart.
        """
        inventory_item = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory_item:
            return  # Fails silently if inventory doesn't exist

        session_identifier = db.session.sid if not user_id else None

        reservation = InventoryReservation.query.filter_by(
            inventory_id=inventory_item.id,
            user_id=user_id,
            session_id=session_identifier,
        ).first()

        if reservation:
            reservation.quantity -= quantity_to_release
            if reservation.quantity <= 0:
                db.session.delete(reservation)

            cache.delete(f"view//api/products/{product_id}")
            cache.delete("view//api/products")

            db.session.commit()

    @staticmethod
    def convert_reservation_to_sale(order):
        """
        Called when an order is successfully placed. This converts the reservation
        into a permanent stock decrement.
        """
        session_identifier = db.session.sid if not order.user_id else None

        for item in order.items:
            inventory_item = (
                Inventory.query.filter_by(product_id=item.product_id)
                .with_for_update()
                .first()
            )
            if inventory_item:
                inventory_item.quantity -= item.quantity

                reservation = InventoryReservation.query.filter_by(
                    inventory_id=inventory_item.id,
                    user_id=order.user_id,
                    session_id=session_identifier,
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
            raise ServiceError(
                "A valid user ID is required to release all reservations.", 400
            )

        try:
            # Find which products will be affected before deleting the reservations
            reservations_to_delete = (
                InventoryReservation.query.filter_by(user_id=user_id)
                .join(Inventory)
                .all()
            )
            product_ids_to_clear = {
                res.inventory.product_id for res in reservations_to_delete
            }

            # Use synchronize_session=False for a more efficient bulk delete,
            # as the session is being managed by the calling service (CartService).
            num_deleted = InventoryReservation.query.filter_by(user_id=user_id).delete(
                synchronize_session=False
            )
            # This does not commit the session; the calling service is responsible for the commit.
            if num_deleted > 0:
                MonitoringService.log_info(
                    f"Released {num_deleted} total reservations for user {user_id} as part of a larger transaction.",
                    "InventoryService",
                )
                for pid in product_ids_to_clear:
                    cache.delete(f"view//api/products/{pid}")
                cache.delete("view//api/products")

        except Exception as e:
            # The calling service should handle rollback.
            MonitoringService.log_error(
                f"Error releasing all reservations for user {user_id}: {str(e)}",
                "InventoryService",
                exc_info=True,
            )
            # Re-raise the exception to ensure the calling service's transaction fails.
            raise ServiceError(
                f"Could not release all inventory reservations for user {user_id}."
            )

    @staticmethod
    def release_expired_reservations():
        """
        A cleanup function to be run periodically by a background task.
        It finds and deletes all expired reservations.
        """
        # First, find which products will be affected by the expiration
        reservations_to_expire = (
            InventoryReservation.query.filter(
                InventoryReservation.expires_at <= datetime.utcnow()
            )
            .join(Inventory)
            .all()
        )

        if not reservations_to_expire:
            return 0

        product_ids_to_clear = {
            res.inventory.product_id for res in reservations_to_expire
        }
        reservation_ids = [res.id for res in reservations_to_expire]

        # Perform the bulk delete
        expired_count = InventoryReservation.query.filter(
            InventoryReservation.id.in_(reservation_ids)
        ).delete(synchronize_session=False)

        db.session.commit()

        if expired_count > 0:
            MonitoringService.log_info(
                f"Released {expired_count} expired inventory reservations.",
                "InventoryService",
            )
            for pid in product_ids_to_clear:
                cache.delete(f"view//api/products/{pid}")
            cache.delete("view//api/products")
        return expired_count
