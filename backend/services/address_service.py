from backend.models.user_models import User
from backend.models.address_models import Address
from backend.database import db
from backend.utils.input_sanitizer import InputSanitizer, sanitize_input
from flask import current_app



class AddressService:



    @staticmethod
    def get_user_addresses(self, user_id):
        return Address.query.filter_by(user_id=user_id).all()

    @staticmethod
    def create_address(self, user_id, data):
        """ Creates an address after sanitizing string fields. """
        sanitized_data = {key: sanitize_input(value) if isinstance(value, str) else value for key, value in data.items()}
        
        new_address = Address(user_id=user_id, **sanitized_data)
        
        # If this is the new default, unset other defaults
        if new_address.is_default:
            Address.query.filter_by(user_id=user_id, address_type=new_address.address_type).update({Address.is_default: False})

        db.session.add(new_address)
        db.session.commit()
        current_app.logger.info(f"New address created for user_id {user_id}")
        return new_address

    @staticmethod
    def update_address(self, address_id, user_id, data):
        """ Updates an address after sanitizing string fields. """
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            return None

        for key, value in data.items():
            sanitized_value = sanitize_input(value) if isinstance(value, str) else value
            setattr(address, key, sanitized_value)
            
        # Handle default logic on update
        if data.get('is_default'):
            Address.query.filter(
                Address.user_id == user_id,
                Address.address_type == address.address_type,
                Address.id != address_id
            ).update({Address.is_default: False})

        db.session.commit()
        current_app.logger.info(f"Address {address_id} updated for user_id {user_id}")
        return address

    @staticmethod
    def delete_address(self, address_id, user_id):
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if address:
            db.session.delete(address)
            db.session.commit()
            current_app.logger.info(f"Address {address_id} deleted for user_id {user_id}")
            return True
        return False

    
    
    @staticmethod
    def get_addresses_for_user(user_id: int) -> list:
        """Retrieves all addresses for a given user."""
        user = User.query.get_or_404(user_id)
        return [address.to_dict() for address in user.addresses]

    @staticmethod
    def add_address_for_user(user_id: int, data: dict) -> Address:
        """Adds a new address for a user, respecting the 4-address limit."""
        user = User.query.get_or_404(user_id)
        
        # The validation logic is handled by the @validates decorator in the User model.
        
        new_address = Address(
            user_id=user_id,
            label=data['label'],
            address_line_1=data['addressLine1'],
            address_line_2=data.get('addressLine2'),
            city=data['city'],
            postal_code=data['postalCode'],
            country=data['country']
        )
        
        db.session.add(new_address)
        db.session.commit()
        return new_address



