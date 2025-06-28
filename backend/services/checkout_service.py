from backend.database import db
from backend.models.user_models import User, Address
from backend.models.order_models import DeliveryMethod
from backend.services.exceptions import NotFoundException, ValidationException

class CheckoutService:
    """
    Handles business logic related to the checkout process.
    """

    @staticmethod
    def get_user_addresses(user_id: int):
        """Fetches all addresses for a given user."""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user.addresses

    @staticmethod
    def add_user_address(user_id: int, data: dict):
        """Adds a new address for a user and handles the 'is_default' flag."""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundException("User not found")

        if data.get('is_default'):
            # If this new address is set as default, unset any other default addresses.
            Address.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

        new_address = Address(user_id=user_id, **data)
        db.session.add(new_address)
        db.session.commit()
        return new_address

    @staticmethod
    def update_user_address(user_id: int, address_id: int, data: dict):
        """Updates an existing address for a user."""
        address = db.session.get(Address, address_id)
        if not address or address.user_id != user_id:
            raise NotFoundException("Address not found or permission denied")

        if data.get('is_default'):
            # Unset other default addresses if this one is being set as default.
            Address.query.filter(Address.id != address_id, Address.user_id == user_id, Address.is_default == True).update({"is_default": False})

        for key, value in data.items():
            setattr(address, key, value)
        
        db.session.commit()
        return address

    @staticmethod
    def get_available_delivery_methods(address: dict, cart_total: float):
        """
        Fetches available delivery methods.
        This is a placeholder for more complex logic that might depend on address, weight, or cart value.
        """
        # For now, return all active delivery methods.
        return DeliveryMethod.query.filter_by(is_active=True).order_by(DeliveryMethod.price).all()