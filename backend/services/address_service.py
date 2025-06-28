from backend.models.user_models import User
from backend.models.address_models import Address
from backend.database import db
from backend.utils.input_sanitizer import InputSanitizer


class AddressService:
def create_address(self, user_id, address_data):
    """
    Creates a new address for a user after sanitizing the input data.
    """
    sanitized_data = {key: InputSanitizer.clean_html(value) if isinstance(value, str) else value for key, value in address_data.items()}
    
    address = Address(user_id=user_id, **sanitized_data)
    db.session.add(address)
    db.session.commit()
    return address

    
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

    @staticmethod
    def update_address(self, address_id, address_data):
        """
        Updates an existing address after sanitizing the input data.
        """
        address = self.get_address_by_id(address_id)
        if address:
            sanitized_data = {key: InputSanitizer.clean_html(value) if isinstance(value, str) else value for key, value in address_data.items()}
            for key, value in sanitized_data.items():
                setattr(address, key, value)
            db.session.commit()
        return address

    @staticmethod
    def delete_address(address_id: int, user_id: int):
        """Deletes an address, ensuring it belongs to the user."""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
        db.session.delete(address)
        db.session.commit()
