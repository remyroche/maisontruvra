from backend.models.product_models import Product, Category, Collection
from backend.models.enums import ProductStatus
from backend.database import db
from backend.services.exceptions import NotFoundException, ServiceException
from sqlalchemy import or_
from backend.services.passport_service import PassportService # Import the new service
from models import db, Product, Category, Collection, Review, WishlistItem, Inventory
from sqlalchemy.orm import joinedload, subqueryload


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


    def get_published_products(self, page, per_page, sort_by, sort_direction, category_name=None, collection_name=None):
        """
        Gets a paginated list of published products, eagerly loading relationships
        to prevent N+1 query problems.
        """
        query = Product.query.filter_by(is_active=True).options(
            joinedload(Product.category),
            joinedload(Product.collection),
            subqueryload(Product.images)
        )

        if category_name:
            query = query.join(Category).filter(Category.name == category_name)
        
        if collection_name:
            query = query.join(Collection).filter(Collection.name == collection_name)

        if sort_direction == 'desc':
            query = query.order_by(db.desc(getattr(Product, sort_by, 'name')))
        else:
            query = query.order_by(db.asc(getattr(Product, sort_by, 'name')))

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_product_by_slug(self, slug):
        """
        Gets a single product by slug, eagerly loading all related data.
        """
        return Product.query.filter_by(slug=slug).options(
            subqueryload(Product.variants),
            subqueryload(Product.images),
            subqueryload(Product.reviews).joinedload(Review.user),
            joinedload(Product.category),
            joinedload(Product.collection)
        ).first()

    def get_all_products_paginated(self, page, per_page, sort_by, sort_direction, category_id=None, collection_id=None):
        """
        Gets a paginated list of all products for the admin, eagerly loading relationships.
        """
        query = Product.query.options(
            joinedload(Product.inventory),
            joinedload(Product.category),
            joinedload(Product.collection)
        )

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if collection_id:
            query = query.filter(Product.collection_id == collection_id)

        if sort_direction == 'desc':
            query = query.order_by(db.desc(getattr(Product, sort_by, 'name')))
        else:
            query = query.order_by(db.asc(getattr(Product, sort_by, 'name')))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
        

    def search_products(self, search_term, limit=10):
        return Product.query.filter(Product.name.ilike(f'%{search_term}%')).limit(limit).all()
        
    @staticmethod
    def get_product_by_id(product_id):
        """Get product by ID"""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with id {product_id} not found")
        return product
    
    @staticmethod
    def create_product(self, data):
        """
        Creates a new product and automatically generates its digital passport.
        This is an atomic operation: if passport creation fails, the entire
        transaction is rolled back, and the product is not created.
        """
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id'],
            # ... other fields
        )
        
        try:
            # Add the new product to the session
            db.session.add(new_product)
            
            # Flush the session to assign an ID to new_product without committing
            db.session.flush()

            # --- Passport Creation Hook (Mandatory) ---
            PassportService.create_for_product(new_product)
            
            # Commit the transaction only if both product and passport are created
            db.session.commit()
            
            return new_product
        except Exception as e:
            # If any part of the process fails, roll back the entire transaction
            db.session.rollback()
            current_app.logger.error(
                f"Failed to create product or its mandatory passport. "
                f"Transaction rolled back. Error: {e}"
            )
            # Re-raise the exception to notify the caller of the failure
            raise

    
    
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
