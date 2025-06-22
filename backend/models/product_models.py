from backend.database import db
from .base import BaseModel

class Product(BaseModel):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    product_type = db.Column(db.String(50), default='standard') # e.g., standard, b2b_exclusive, blog
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    
    category = db.relationship('Category', back_populates='products')
    collection = db.relationship('Collection', back_populates='products')
    images = db.relationship('ProductImage', back_populates='product', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")
    inventory = db.relationship('Inventory', back_populates='product', uselist=False, cascade="all, delete-orphan")
    passport = db.relationship('ProductPassport', back_populates='product', uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': str(self.price),
            'sku': self.sku,
            'category': self.category.name if self.category else None,
            'collection': self.collection.name if self.collection else None,
            'images': [img.url for img in self.images]
        }

class Category(BaseModel):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    products = db.relationship('Product', back_populates='category')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug}

class Collection(BaseModel):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    products = db.relationship('Product', back_populates='collection')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug}
        
class ProductImage(BaseModel):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))
    
    product = db.relationship('Product', back_populates='images')

class Review(BaseModel):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending') # pending, approved, rejected
    
    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'user_name': self.user.first_name,
            'created_at': self.created_at.isoformat()
        }
