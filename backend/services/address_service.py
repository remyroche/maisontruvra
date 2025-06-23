from backend.models.user_models import User
from backend.models.address_models import Address
from backend.database import db

class AddressService:
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
    def update_address(address_id: int, user_id: int, data: dict) -> Address:
        """Updates an existing address, ensuring it belongs to the user."""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
        
        for key, value in data.items():
            # Map camelCase from frontend to snake_case in the model
            model_key = ''.join(['_'+c.lower() if c.isupper() else c for c in key]).lstrip('_')
            if hasattr(address, model_key):
                setattr(address, model_key, value)
        
        db.session.commit()
        return address

    @staticmethod
    def delete_address(address_id: int, user_id: int):
        """Deletes an address, ensuring it belongs to the user."""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first_or_404()
        db.session.delete(address)
        db.session.commit()
