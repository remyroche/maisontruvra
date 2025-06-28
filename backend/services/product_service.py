from sqlalchemy import func
from backend.database import db
from backend.models.product_models import Product, ProductVariant, ProductCategory, LoyaltyTier, OrderItem
from backend.models.inventory_models import ProductItem
from backend.services.exceptions import NotFoundException, ValidationException, ServiceError
from backend.utils.sanitization import sanitize_input
from backend.services.audit_log_service import AuditLogService
from flask import current_app, request
from flask_jwt_extended import get_jwt_identity
from backend.models.user_models import User



class ProductService:

    @staticmethod
    def get_all_products(user=None):
        """
        Gets all products, filtering based on the user's role and loyalty tier.
        """
        query = Product.query
        
        if user:
            # Filter by B2C/B2B visibility
            if hasattr(user, 'is_b2b') and user.is_b2b:
                query = query.filter(Product.is_b2b_visible == True)
            else:
                query = query.filter(Product.is_b2c_visible == True)

            # Handle tier-specific restrictions
            # A subquery finds products that have *any* tier restrictions
            products_with_restrictions = db.session.query(Product.id).join(
                'restricted_to_tiers'
            ).distinct()
            
            # Filter products: either they have no restrictions, OR the user's tier is in their allowed list
            if hasattr(user, 'loyalty') and user.loyalty:
                query = query.filter(
                    ~Product.id.in_(products_with_restrictions) |
                    (Product.id.in_(
                        db.session.query(Product.id).join('restricted_to_tiers').filter(LoyaltyTier.id == user.loyalty.tier_id)
                    ))
                )
            else:
                # If user has no loyalty info, they can only see non-restricted items
                query = query.filter(~Product.id.in_(products_with_restrictions))
        else:
            # For non-logged-in users, only show public B2C products with no tier restrictions
            query = query.filter(Product.is_b2c_visible == True)
            # Find products that have any tier restrictions and exclude them
            products_with_restrictions = db.session.query(Product.id).join('restricted_to_tiers').distinct()
            query = query.filter(~Product.id.in_(products_with_restrictions))
            
        return query.all()

    @staticmethod
    def search_products(query, limit=10):
        """Searches for products by name or SKU for autocomplete."""
        search_term = f"%{query.lower()}%"
        return Product.query.filter(
            (func.lower(Product.name).like(search_term)) |
            (func.lower(Product.sku).like(search_term))
        ).limit(limit).all()

    @staticmethod
    def get_product_recommendations(product_id, limit=5):
        """
        Gets product recommendations based on co-purchase history.
        "Customers who bought this also bought..."
        """
        # Find orders that contain the target product
        subquery = db.session.query(OrderItem.order_id).filter(OrderItem.product_id == product_id).subquery()

        # Find all other products purchased in those same orders
        recommendations = db.session.query(
            OrderItem.product_id,
            func.count(OrderItem.product_id).label('purchase_count')
        ).filter(
            OrderItem.order_id.in_(subquery),
            OrderItem.product_id != product_id  # Exclude the original product
        ).group_by(
            OrderItem.product_id
        ).order_by(
            func.count(OrderItem.product_id).desc()
        ).limit(limit).all()

        recommended_product_ids = [rec.product_id for rec in recommendations]
        if not recommended_product_ids:
            return []

        # Fetch the full product objects for the recommended IDs
        return Product.query.filter(Product.id.in_(recommended_product_ids)).all()

    @staticmethod
    def _generate_sku(base_sku, attributes):
        """
        Generates a unique SKU for a variant based on its attributes.
        Example: base='SHIRT', attrs={'color': 'Blue', 'size': 'L'} -> 'SHIRT-BLUE-L'
        """
        parts = [base_sku]
        # Sort keys to ensure consistent SKU generation (e.g., color always before size)
        for key in sorted(attributes.keys()):
            # Sanitize attribute value for SKU (uppercase, no spaces)
            value = str(attributes[key]).upper().replace(' ', '-')
            parts.append(value)
        return '-'.join(parts)

    @staticmethod
    def create_product_with_variants(data):
        """
        Creates a new parent product and all its specified variants in a single transaction.
        """
        base_sku = data.get('base_sku')
        variants_data = data.get('variants', [])

        if not base_sku or not data.get('name') or not variants_data:
            raise ServiceError("Name, base_sku, and at least one variant are required.", 400)

        # Start a transaction
        try:
            new_product = Product(
                name=data['name'],
                description=data.get('description', ''),
                base_sku=base_sku,
                category_id=data['category_id']
            )
            db.session.add(new_product)

            for variant_data in variants_data:
                attributes = variant_data.get('attributes')
                if not attributes:
                    raise ServiceError("Each variant must have attributes.", 400)
                
                generated_sku = ProductService._generate_sku(base_sku, attributes)

                new_variant = ProductVariant(
                    product=new_product,
                    sku=generated_sku,
                    price=variant_data['price'],
                    attributes=attributes
                )
                
                # Create an inventory record for the new variant
                initial_stock = int(variant_data.get('stock', 0))
                inventory = ProductItem(variant=new_variant, quantity=initial_stock, status='in_stock') # Assuming ProductItem is your inventory model
                db.session.add(inventory)
                
                new_product.variants.append(new_variant)

            db.session.commit()
            current_app.logger.info(f"Created new product '{new_product.name}' with {len(new_product.variants)} variants.")
            return new_product

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create product with variants: {e}", exc_info=True)
            raise ServiceError("Product creation failed due to a database error.")

    @staticmethod
    def get_b2b_product_by_id(product_id, user_id):
        """Fetch a product with B2B-specific pricing for a given user."""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")

        # Fetch user and their tier discount
        user = User.query.get(user_id)
        tier_discount = 0
        if user and user.loyalty and user.loyalty.tier:
            tier_discount = user.loyalty.tier.discount

        # Calculate B2B price
        b2b_price = product.price * (1 - tier_discount / 100)

        product_data = product.to_dict(view='b2b')
        product_data['b2c_price'] = product.price
        product_data['b2b_price'] = b2b_price

        return product_data

    @staticmethod
    def get_b2b_products_paginated(user_id, page, per_page, **filters):
        """Fetch paginated products with B2B pricing."""
        query = Product.query.filter(Product.is_b2b_visible == True)

        # Apply filters if any
        if filters.get('category'):
            query = query.filter(Product.category_id == filters['category'])
        if filters.get('collection'):
            query = query.filter(Product.collection_id == filters['collection'])
        if filters.get('search_term'):
            search_term = f"%{filters['search_term']}%"
            query = query.filter(Product.name.ilike(search_term))

        # Fetch user and their tier discount
        user = User.query.get(user_id)
        tier_discount = 0
        if user and user.loyalty and user.loyalty.tier:
            tier_discount = user.loyalty.tier.discount

        # Paginate and calculate B2B prices
        products_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products_data = []
        for product in products_pagination.items:
            b2b_price = product.price * (1 - tier_discount / 100)
            product_data = product.to_dict(view='b2b')
            product_data['b2c_price'] = product.price
            product_data['b2b_price'] = b2b_price
            products_data.append(product_data)

        return products_data, products_pagination.total, products_pagination.pages, products_pagination.page


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

        # Handle soft-deleted filter
        if filters and not filters.get('include_deleted', False):
            # By default, only show non-deleted (active) products
            query = query.filter(Product.deleted_at.is_(None))
        
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
            
            current_app.logger.info(f"Product created successfully: {product.name} (ID: {product.id})")
            return product.to_dict(context='admin')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create product: {str(e)}")
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
            
            current_app.logger.info(f"Product updated successfully: {product.name} (ID: {product.id})")
            return product.to_dict(context='admin')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update product {product_id}: {str(e)}")
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
            
            current_app.logger.info(f"Product soft deleted: {product.name} (ID: {product.id})")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to delete product {product_id}: {str(e)}")
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
