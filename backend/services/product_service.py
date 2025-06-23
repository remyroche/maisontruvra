
from backend.database import db
from backend.models.product_models import Product, ProductVariant, ProductCategory
from backend.models.inventory_models import ProductItem
from backend.services.exceptions import NotFoundException, ValidationException
from backend.utils.sanitization import sanitize_input
from backend.services.audit_log_service import AuditLogService
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def get_product_by_id(product_id: int, context: str = 'public'):
        """Get product by ID with different serialization contexts."""
        # Optimize query to avoid N+1 problem
        product = Product.query.options(
            db.selectinload(Product.variants).selectinload(ProductVariant.items),
            db.selectinload(Product.category),
            db.selectinload(Product.reviews)
        ).get(product_id)
        
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")
        
        return product.to_dict(context=context)
    
    @staticmethod
    def get_all_products_paginated(page: int, per_page: int, filters: dict = None):
        """Get paginated products with N+1 optimization."""
        query = Product.query.options(
            db.selectinload(Product.variants),
            db.selectinload(Product.category)
        )
        
        if filters:
            filters = sanitize_input(filters)
            if filters.get('category_id'):
                query = query.filter(Product.category_id == filters['category_id'])
            if filters.get('is_active') is not None:
                query = query.filter(Product.is_active == filters['is_active'])
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    db.or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term)
                    )
                )
        
        return query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def create_product(product_data: dict):
        """Create a new product with proper validation and logging."""
        product_data = sanitize_input(product_data)
        
        # Validate required fields
        required_fields = ['name', 'description', 'category_id']
        for field in required_fields:
            if not product_data.get(field):
                raise ValidationException(f"Field '{field}' is required")
        
        try:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                category_id=product_data['category_id'],
                is_active=product_data.get('is_active', True),
                metadata=product_data.get('metadata', {})
            )
            
            db.session.add(product)
            db.session.flush()
            
            # Log the action
            AuditLogService.log_action(
                'PRODUCT_CREATED',
                target_id=product.id,
                details={'name': product.name, 'category_id': product.category_id}
            )
            
            db.session.commit()
            
            logger.info(f"Product created successfully: {product.name} (ID: {product.id})")
            return product.to_dict(context='admin')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create product: {str(e)}")
            raise ValidationException(f"Failed to create product: {str(e)}")
    
    @staticmethod
    def update_product(product_id: int, update_data: dict):
        """Update product with proper validation and logging."""
        update_data = sanitize_input(update_data)
        
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")
        
        try:
            original_data = {
                'name': product.name,
                'description': product.description,
                'is_active': product.is_active
            }
            
            # Update fields
            if 'name' in update_data:
                product.name = update_data['name']
            if 'description' in update_data:
                product.description = update_data['description']
            if 'category_id' in update_data:
                product.category_id = update_data['category_id']
            if 'is_active' in update_data:
                product.is_active = update_data['is_active']
            if 'metadata' in update_data:
                product.metadata = update_data['metadata']
            
            db.session.flush()
            
            # Log changes
            changes = {}
            for key, original_value in original_data.items():
                current_value = getattr(product, key)
                if original_value != current_value:
                    changes[key] = {'from': original_value, 'to': current_value}
            
            if changes:
                AuditLogService.log_action(
                    'PRODUCT_UPDATED',
                    target_id=product.id,
                    details={'changes': changes}
                )
            
            db.session.commit()
            
            logger.info(f"Product updated successfully: {product.name} (ID: {product.id})")
            return product.to_dict(context='admin')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            raise ValidationException(f"Failed to update product: {str(e)}")
    
    @staticmethod
    def delete_product(product_id: int):
        """Soft delete product with logging."""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")
        
        try:
            product.is_active = False
            product.deleted_at = db.func.now()
            
            db.session.flush()
            
            AuditLogService.log_action(
                'PRODUCT_DELETED',
                target_id=product.id,
                details={'name': product.name}
            )
            
            db.session.commit()
            
            logger.info(f"Product soft deleted: {product.name} (ID: {product.id})")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete product {product_id}: {str(e)}")
            raise ValidationException(f"Failed to delete product: {str(e)}")
    
    @staticmethod
    def get_low_stock_products(threshold: int = 10):
        """Get products with low stock levels."""
        return db.session.query(Product, ProductVariant, db.func.count(ProductItem.id).label('stock_count'))\
            .join(ProductVariant)\
            .outerjoin(ProductItem, db.and_(
                ProductItem.product_variant_id == ProductVariant.id,
                ProductItem.status == 'in_stock'
            ))\
            .group_by(Product.id, ProductVariant.id)\
            .having(db.func.count(ProductItem.id) <= threshold)\
            .all()
