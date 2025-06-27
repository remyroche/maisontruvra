from backend.database import db
from .base import BaseModel, SoftDeleteMixin

class StockNotificationRequest(Base):
    __tablename__ = 'stock_notification_requests'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    
    user = db.relationship('User')
    product = db.relationship('Product')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)


class Product(BaseModel, SoftDeleteMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    base_sku = db.Column(db.String(100), nullable=False, unique=True)
    is_published = db.Column(db.Boolean, default=True)
    product_type = db.Column(db.String(50), default='standard') # e.g., standard, b2b_exclusive, blog
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    images = db.relationship('ProductImage', back_populates='product', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")
    inventory = db.relationship('Inventory', back_populates='product', uselist=False, cascade="all, delete-orphan")
    stock = db.Column(db.Integer, default=0)
    passport = db.relationship('ProductPassport', back_populates='product', uselist=False, cascade="all, delete-orphan")
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    # --- New Fields ---
    internal_note = db.Column(db.Text, nullable=True) # Note for staff
    
    # Visibility Rules
    is_b2c_visible = db.Column(db.Boolean, default=True)
    is_b2b_visible = db.Column(db.Boolean, default=True)
    
    # Many-to-Many relationship for tier-specific visibility
    # If a product is linked to any tiers here, it's ONLY visible to those tiers.
    # If this relationship is empty, it's visible to all users (respecting the b2c/b2b flags).
    restricted_to_tiers = db.relationship(
        'LoyaltyTier', 
        secondary=product_tier_visibility,
        backref=db.backref('visible_products', lazy='dynamic')
    )
    
    def to_public_dict(self, include_variants=False, include_reviews=False):
        """Public view of a product."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': self.price,
            'images': [image.url for image in self.images],
            'category': self.category.name if self.category else None,
            'collection': self.collection.name if self.collection else None,
            'base_sku': self.base_sku,
            'is_deleted': self.is_deleted,
        }
        if include_variants:
            data['variants'] = [v.to_dict() for v in self.variants]
        if include_reviews:
            data['reviews'] = [r.to_public_dict() for r in self.reviews]
        return data
    
    def to_admin_dict(self):
        """Admin view of a product."""
        data = self.to_public_dict(include_variants=True, include_reviews=True)
        data.update({
            'is_active': self.is_active,
            'base_sku': self.base_sku,
            'inventory': self.inventory.quantity if self.inventory else 0,
            'is_b2c_visible': self.is_b2c_visible,
            'is_b2b_visible': self.is_b2b_visible,
            'restricted_to_tier_ids': [str(tier.id) for tier in self.restricted_to_tiers],
            'internal_note': self.internal_note
        })
        return data

    def to_b2b_dict(self):
        """B2B customer view of a product."""
        data = self.to_public_dict(include_variants=True)
        return data

    def to_dict(self, view='public', **kwargs):
        """Routes to the correct serialization based on view."""
        if view == 'admin':
            return self.to_admin_dict()
        if view == 'b2b':
            return self.to_b2b_dict()
        return self.to_public_dict(**kwargs)

class ProductVariant(db.Model, SoftDeleteMixin):
    """
    Represents a specific, purchasable version of a Product.
    This model holds the unique SKU, price, and inventory for each variation.
    """
    __tablename__ = 'product_variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # The full, unique SKU for this specific variant (e.g., 'TR-OIL-100ML')
    sku = db.Column(db.String(150), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Attributes that define this variant (e.g., {"size": "100ml", "color": "black"})
    attributes = db.Column(db.JSON, nullable=False)

    # Each variant has its own inventory record
    inventory = db.relationship('Inventory', backref='variant', uselist=False, cascade="all, delete-orphan")

    # The parent product
    product = db.relationship('Product', back_populates='variants')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'sku': self.sku,
            'price': str(self.price), # Return as string for consistency
            'attributes': self.attributes,
            'available_stock': self.inventory.available_quantity if self.inventory else 0,
            'is_deleted': self.is_deleted,
        }

    def __repr__(self):
        return f'<ProductVariant {self.sku}>'

class Category(BaseModel, SoftDeleteMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    products = db.relationship('Product', back_populates='category')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug, 'is_deleted': self.is_deleted}

class Collection(BaseModel, SoftDeleteMixin):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    products = db.relationship('Product', back_populates='collection')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug, 'is_deleted': self.is_deleted}
        
class ProductImage(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))
    
    product = db.relationship('Product', back_populates='images')

class Review(BaseModel, SoftDeleteMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending') # pending, approved, rejected
    
    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User')

    def to_public_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'title': self.title,
            'text': self.text,
            'author': self.user.first_name,
            'created_at': self.created_at.isoformat(),
            'is_deleted': self.is_deleted,
        }

    def to_admin_dict(self):
        data = self.to_public_dict()
        data['user'] = self.user.to_public_dict()
        data['product_id'] = self.product_id
        data['approved'] = self.approved
        return data

    def to_dict(self, view='public'):
        if view == 'admin':
            return self.to_admin_dict()
        return self.to_public_dict()
