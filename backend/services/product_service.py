from backend.models.product_models import Product, Category, Collection
from backend.models.enums import ProductStatus
from backend.database import db
from backend.services.exceptions import NotFoundException, ServiceException
from sqlalchemy import or_

class ProductService:
    @staticmethod
    def get_all_products(category_id=None, collection_id=None, search=None, page=1, per_page=20):
        """Get all products with optional filtering"""
        query = Product.query.filter_by(status=ProductStatus.ACTIVE)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if collection_id:
            query = query.join(Product.collections).filter(Collection.id == collection_id)
        if search:
            query = query.filter(or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            ))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_product_by_id(product_id):
        """Get product by ID"""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with id {product_id} not found")
        return product
    
    @staticmethod
    def get_product_by_slug(slug):
        """Get product by slug"""
        product = Product.query.filter_by(slug=slug).first()
        if not product:
            raise NotFoundException(f"Product with slug {slug} not found")
        return product
    
    @staticmethod
    def create_product(data):
        """Create new product"""
        try:
            product = Product(**data)
            db.session.add(product)
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to create product: {str(e)}")
    
    @staticmethod
    def update_product(product_id, data):
        """Update existing product"""
        product = ProductService.get_product_by_id(product_id)
        try:
            for key, value in data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to update product: {str(e)}")
    
    @staticmethod
    def delete_product(product_id):
        """Delete product"""
        product = ProductService.get_product_by_id(product_id)
        try:
            db.session.delete(product)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to delete product: {str(e)}")
    
    @staticmethod
    def get_all_categories():
        """Get all categories"""
        return Category.query.all()
    
    @staticmethod
    def create_category(data):
        """Create new category"""
        try:
            category = Category(**data)
            db.session.add(category)
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            raise ServiceException(f"Failed to create category: {str(e)}")
    
    @staticmethod
    def get_products_by_type(product_type):
        """Get products by type (for blog posts etc)"""
        return Product.query.filter_by(product_type=product_type).all()
