from ..models import Inventory, InventoryReservation
from .. import db
from .exceptions import ServiceError
from flask import session, current_app
from datetime import datetime, timedelta
from .passport_service import PassportService

# Updated reservation lifetime to 1 hour (60 minutes)
RESERVATION_LIFETIME_MINUTES = 60

class InventoryService:

    @staticmethod
    def add_stock(inventory_id: int, quantity_to_add: int):
        """
        Adds a specific quantity of stock to an inventory item and generates
        a new product passport for each individual item added.
        This entire process is a single atomic transaction.
        """
        if quantity_to_add <= 0:
            raise ServiceError("Quantity to add must be positive.", 400)

        inventory_item = Inventory.query.with_for_update().get(inventory_id)
        if not inventory_item:
            raise NotFoundException("Inventory item not found.")
            
        try:
            # 1. Update the total stock quantity
            inventory_item.quantity += quantity_to_add

            # 2. Loop to create a passport for each new item
            for _ in range(quantity_to_add):
                PassportService.create_and_render_passport(inventory_item.product_id)

            # 3. Commit the entire transaction
            db.session.commit()
            current_app.logger.info(f"Added {quantity_to_add} units to inventory for product {inventory_item.product_id}. {quantity_to_add} passports created.")

            cache.delete('view//api/products/{}'.format(product_id)) 
            cache.delete('view//api/products')
            
        except Exception as e:
            # If any part fails (e.g., file write error), roll back everything.
            # No quantity will be updated, and no passports will be saved.
            db.session.rollback()
            current_app.logger.error(f"Failed to add stock for inventory {inventory_id}: {e}", exc_info=True)
            raise ServiceError("Failed to add stock and create passports.")

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
        session_identifier = session.sid if not user_id else None
        
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

        session_identifier = session.sid if not user_id else None
        
        reservation = InventoryReservation.query.filter_by(
            inventory_id=inventory_item.id,
            user_id=user_id,
            session_id=session_identifier
        ).first()

        if reservation:
            reservation.quantity -= quantity_to_release
            if reservation.quantity <= 0:
                db.session.delete(reservation)
            db.session.commit()

    @staticmethod
    def convert_reservation_to_sale(order):
        """
        Called when an order is successfully placed. This converts the reservation
        into a permanent stock decrement.
        """
        session_identifier = session.sid if not order.user_id else None
        
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
            # Use synchronize_session=False for a more efficient bulk delete,
            # as the session is being managed by the calling service (CartService).
            num_deleted = InventoryReservation.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            
            # This does not commit the session; the calling service is responsible for the commit.
            current_app.logger.info(f"Released {num_deleted} total reservations for user {user_id} as part of a larger transaction.")

        except Exception as e:
            # The calling service should handle rollback.
            current_app.logger.error(f"Error releasing all reservations for user {user_id}: {str(e)}", exc_info=True)
            # Re-raise the exception to ensure the calling service's transaction fails.
            raise ServiceError(f"Could not release all inventory reservations for user {user_id}.")


    @staticmethod
    def release_expired_reservations():
        """
        A cleanup function to be run periodically by a background task.
        It finds and deletes all expired reservations.
        """
        expired_count = InventoryReservation.query.filter(InventoryReservation.expires_at <= datetime.utcnow()).delete()
        db.session.commit()
        if expired_count > 0:
            current_app.logger.info(f"Released {expired_count} expired inventory reservations.")
        return expired_count
