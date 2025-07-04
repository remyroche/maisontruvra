from sqlalchemy.ext.hybrid import hybrid_property

from backend.database import db
from backend.utils.encryption import decrypt_data, encrypt_data


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    _address_line_1 = db.Column("address_line_1", db.String(255), nullable=False)
    _address_line_2 = db.Column("address_line_2", db.String(255))
    _city = db.Column("city", db.String(100), nullable=False)
    _state_province_region = db.Column(
        "state_province_region", db.String(100), nullable=False
    )
    _postal_code = db.Column("postal_code", db.String(20), nullable=False)
    _country = db.Column("country", db.String(100), nullable=False)
    is_default_shipping = db.Column(db.Boolean, default=False)
    is_default_billing = db.Column(db.Boolean, default=False)

    @hybrid_property
    def address_line_1(self):
        return decrypt_data(self._address_line_1)

    @address_line_1.setter
    def address_line_1(self, value):
        self._address_line_1 = encrypt_data(value)

    @hybrid_property
    def address_line_2(self):
        return decrypt_data(self._address_line_2)

    @address_line_2.setter
    def address_line_2(self, value):
        self._address_line_2 = encrypt_data(value)

    @hybrid_property
    def city(self):
        return decrypt_data(self._city)

    @city.setter
    def city(self, value):
        self._city = encrypt_data(value)

    @hybrid_property
    def state_province_region(self):
        return decrypt_data(self._state_province_region)

    @state_province_region.setter
    def state_province_region(self, value):
        self._state_province_region = encrypt_data(value)

    @hybrid_property
    def postal_code(self):
        return decrypt_data(self._postal_code)

    @postal_code.setter
    def postal_code(self, value):
        self._postal_code = encrypt_data(value)

    @hybrid_property
    def country(self):
        return decrypt_data(self._country)

    @country.setter
    def country(self, value):
        self._country = encrypt_data(value)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state_province_region": self.state_province_region,
            "postal_code": self.postal_code,
            "country": self.country,
            "is_default_shipping": self.is_default_shipping,
            "is_default_billing": self.is_default_billing,
        }
