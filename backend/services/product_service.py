# backend/Services/product_service.py
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload

from backend.extensions import cache, db
from backend.models import Category, Collection, Product
from backend.models.b2b_loyalty_models import LoyaltyTier
from backend.models.order_models import OrderItem
from backend.models.product_models import ProductVariant, Stock
from backend.services.audit_log_service import AuditLogService
from backend.services.exceptions import (
    DuplicateProductError,
    InvalidAPIRequestError,
    NotFoundException,
    ProductNotFoundError,
    ServiceError,
    ValidationException,
)
from backend.services.monitoring_service import MonitoringService
from backend.utils.cache_helpers import (
    clear_product_cache,
    get_product_by_id_key,
    get_product_by_slug_key,
    get_product_list_key,
)
from backend.utils.input_sanitizer import InputSanitizer


class ProductService:
    def __init__(self, logger):
        self.logger = logger

    def get_all_products(self, user=None, filters=None, page=1, per_page=20):
        """Retrieves all products from the database, with caching."""
        cache_key = get_product_list_key()
        products = cache.get(cache_key)
        if products is None:
            products = (
                Product.query.options(joinedload(Product.category))
                .order_by(Product.name)
                .all()
            )
            cache.set(cache_key, products, timeout=3600)  # Cache for 1 hour

        # Start with base query
        query = Product.query.options(joinedload(Product.category))

        # --- User-based Filtering (Visibility & Tier Restrictions) ---
        if user:
            # Filter by B2C/B2B visibility
            if hasattr(user, "is_b2b") and user.is_b2b:
                query = query.filter(Product.is_b2b_visible)
            else:
                query = query.filter(Product.is_b2c_visible)

            # Handle tier-specific restrictions
            products_with_restrictions = (
                db.session.query(Product.id).join("restricted_to_tiers").distinct()
            )

            if hasattr(user, "loyalty") and user.loyalty:
                # User has loyalty info, so they can see non-restricted items
                # OR items restricted to their specific tier.
                query = query.filter(
                    ~Product.id.in_(products_with_restrictions)
                    | (
                        Product.id.in_(
                            db.session.query(Product.id)
                            .join("restricted_to_tiers")
                            .filter(LoyaltyTier.id == user.loyalty.tier_id)
                        )
                    )
                )
            else:
                # User has no loyalty info, they can only see non-restricted items
                query = query.filter(~Product.id.in_(products_with_restrictions))
        else:
            # For non-logged-in users, show only public B2C products with no tier restrictions
            query = query.filter(Product.is_b2c_visible)
            products_with_restrictions = (
                db.session.query(Product.id).join("restricted_to_tiers").distinct()
            )
            query = query.filter(~Product.id.in_(products_with_restrictions))

        # --- Standard Filtering ---
        if filters:
            filters = InputSanitizer.sanitize_input(filters)
            # By default, only show non-deleted (active) products unless specified
            if not filters.get("include_deleted", False):
                query = query.filter(Product.deleted_at.is_(None))

            if filters.get("category_id"):
                query = query.filter(Product.category_id == filters["category_id"])

            if filters.get("collection_id"):
                query = query.filter(Product.collection_id == filters["collection_id"])

            if filters.get("is_active") is not None:
                query = query.filter(Product.is_active == filters["is_active"])

            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    db.or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term),
                    )
                )

        return query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_product_by_slug_cached(slug):
        """Retrieves a single product by its slug, with caching."""
        cache_key = get_product_by_slug_key(slug)
        product = cache.get(cache_key)
        if product is None:
            product = Product.query.filter_by(slug=slug).first()
            if product:
                cache.set(cache_key, product, timeout=3600)
                # Also cache by ID for consistency
                cache.set(get_product_by_id_key(product.id), product, timeout=3600)
        return product

    @staticmethod
    def get_all_products():
        """
        Fetches all products.
        """
        # Using options to eagerly load relationships to avoid N+1 query problems.
        return Product.query.options(
            db.joinedload(Product.variants).joinedload(ProductVariant.stock),
            db.joinedload(Product.category),
        ).all()

    @staticmethod
    def get_product_by_id(product_id: int, user=None):
        """
        Get a single product by ID, handling serialization, visibility, and B2B pricing.
        """
        # Eager load all relevant relationships
        product = Product.query.options(
            selectinload(Product.variants).selectinload(ProductVariant.stock),
            joinedload(Product.category),
            selectinload(Product.reviews),
            selectinload(Product.tags),
            selectinload(Product.restricted_to_tiers),
        ).get(product_id)

        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")

        # --- Visibility Check ---
        is_b2b_user = hasattr(user, "is_b2b") and user.is_b2b
        if is_b2b_user and not product.is_b2b_visible:
            raise NotFoundException(f"Product with ID {product_id} not found")
        if not is_b2b_user and not product.is_b2c_visible:
            raise NotFoundException(f"Product with ID {product_id} not found")

        # --- Tier Restriction Check ---
        if product.restricted_to_tiers:
            if not user or not hasattr(user, "loyalty") or not user.loyalty:
                raise NotFoundException(f"Product with ID {product_id} not found")

            user_tier_id = user.loyalty.tier_id
            allowed_tier_ids = {tier.id for tier in product.restricted_to_tiers}
            if user_tier_id not in allowed_tier_ids:
                raise NotFoundException(f"Product with ID {product_id} not found")

        # --- Serialization and Price Calculation ---
        view = "b2b" if is_b2b_user else "public"
        product_data = product.to_dict(view=view)

        # Calculate B2B-specific price if applicable
        if is_b2b_user:
            tier_discount = 0
            if user.loyalty and user.loyalty.tier:
                tier_discount = user.loyalty.tier.discount

            b2b_price = product.price * (1 - tier_discount / 100)
            product_data["b2c_price"] = product.price
            product_data["b2b_price"] = b2b_price

        return product_data

    @staticmethod
    def search_products(query, limit=10):
        """Searches for products by name or SKU for autocomplete."""
        search_term = f"%{query.lower()}%"
        return (
            Product.query.filter(
                (func.lower(Product.name).like(search_term))
                | (func.lower(Product.sku).like(search_term))
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_product_recommendations(product_id, limit=5):
        """
        Gets product recommendations based on co-purchase history.
        "Customers who bought this also bought..."
        """
        # Find orders that contain the target product
        subquery = (
            db.session.query(OrderItem.order_id)
            .filter(OrderItem.product_id == product_id)
            .subquery()
        )

        # Find all other products purchased in those same orders
        recommendations = (
            db.session.query(
                OrderItem.product_id,
                func.count(OrderItem.product_id).label("purchase_count"),
            )
            .filter(
                OrderItem.order_id.in_(subquery),
                OrderItem.product_id != product_id,  # Exclude the original product
            )
            .group_by(OrderItem.product_id)
            .order_by(func.count(OrderItem.product_id).desc())
            .limit(limit)
            .all()
        )

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
            value = str(attributes[key]).upper().replace(" ", "-")
            parts.append(value)
        return "-".join(parts)

    @staticmethod
    def create_product_with_variants(data):
        """
        Creates a new parent product and all its specified variants in a single transaction.
        """
        base_sku = data.get("base_sku")
        variants_data = data.get("variants", [])

        if not base_sku or not data.get("name") or not variants_data:
            raise ServiceError(
                "Name, base_sku, and at least one variant are required.", 400
            )

        # Start a transaction
        try:
            new_product = Product(
                name=data.get("name"),
                description=data.get("description"),
                price=float(data.get("price")),
                stock=int(data.get("stock", 0)),
                sku=data.get("sku"),
                image_url=data.get("image_url"),
                category_id=data.get("category_id"),
                collection_id=data.get("collection_id"),
                passport_hd_image_url=data.get("passport_hd_image_url"),
                sourcing_production_place=data.get("sourcing_production_place"),
                producer_notes=data.get("producer_notes"),
                pairing_suggestions=data.get("pairing_suggestions"),
            )
            db.session.add(new_product)

            for variant_data in variants_data:
                attributes = variant_data.get("attributes")
                if not attributes:
                    raise ServiceError("Each variant must have attributes.", 400)

                generated_sku = ProductService._generate_sku(base_sku, attributes)

                new_variant = ProductVariant(
                    product=new_product,
                    sku=generated_sku,
                    price=variant_data["price"],
                    attributes=attributes,
                )

                # Create an inventory record for the new variant
                initial_stock = int(variant_data.get("stock", 0))
                inventory = OrderItem(
                    variant=new_variant, quantity=initial_stock, status="in_stock"
                )  # Assuming ProductItem is your inventory model
                db.session.add(inventory)

                new_product.variants.append(new_variant)

            db.session.commit()
            MonitoringService.log_info(
                f"Created new product '{new_product.name}' with {len(new_product.variants)} variants.",
                "ProductService",
            )
            return new_product

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to create product with variants: {e}",
                "ProductService",
                exc_info=True,
            )
            raise ServiceError("Product creation failed due to a database error.")

    def create_product_for_quote(self, name, description, price, owner_id=None):
        """
        Creates a new, non-public product specifically for a quote.
        """
        try:
            # Generate a unique SKU for the quote product
            unique_sku = f"QUOTE-{int(db.func.now().timestamp())}"

            quote_product = Product(
                name=name,
                description=description,
                price=price,
                sku=unique_sku,
                is_active=True,  # Active so it can be ordered
                is_quotable_only=True,  # Hidden from public shop
                owner_id=owner_id,  # Assign ownership
            )
            db.session.add(quote_product)
            db.session.commit()
            self.logger.info(f"Created hidden product '{name}' for a quote.")
            return quote_product
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating product for quote: {e}")
            raise

    @staticmethod
    def create_product(product_data: dict):
        """Create a new product with proper validation and logging."""
        # Check for duplicate product name before proceeding.
        if Product.query.filter(Product.name.ilike(product_data["name"])).first():
            raise DuplicateProductError(
                f"Product with name '{product_data['name']}' already exists."
            )

        # Sanitize user-provided string fields to prevent XSS.
        InputSanitizer.sanitize_html(product_data["name"])
        InputSanitizer.sanitize_html(product_data["description"])

        # Verify that the foreign key references are valid.
        if not Category.query.get(product_data["category_id"]):
            raise InvalidAPIRequestError(
                f"Category with id {product_data['category_id']} not found."
            )

        if product_data.get("collection_id") and not Collection.query.get(
            product_data["collection_id"]
        ):
            raise InvalidAPIRequestError(
                f"Collection with id {product_data['collection_id']} not found."
            )

        # Create the main product record.
        new_product = Product(
            name=product_data.get("name"),
            description=product_data.get("description"),
            price=float(product_data.get("price")),
            stock=int(product_data.get("stock", 0)),
            sku=product_data.get("sku"),
            image_url=product_data.get("image_url"),
            category_id=product_data.get("category_id"),
            collection_id=product_data.get("collection_id"),
            passport_hd_image_url=product_data.get("passport_hd_image_url"),
            sourcing_production_place=product_data.get("sourcing_production_place"),
            producer_notes=product_data.get("producer_notes"),
            pairing_suggestions=product_data.get("pairing_suggestions"),
        )
        db.session.add(new_product)
        db.session.flush()  # Flush to get the new_product.id for variant creation.

        # Create variants and their initial stock.
        for variant_data in product_data["variants"]:
            if ProductVariant.query.filter_by(sku=variant_data["sku"]).first():
                db.session.rollback()  # Rollback the transaction to avoid partial creation.
                raise DuplicateProductError(
                    f"Variant with SKU '{variant_data['sku']}' already exists."
                )

            new_variant = ProductVariant(
                product_id=new_product.id,
                sku=variant_data["sku"],
                price_offset=variant_data["price_offset"],
            )
            db.session.add(new_variant)
            db.session.flush()  # Flush to get new_variant.id for stock creation.

            new_stock = Stock(variant_id=new_variant.id, quantity=variant_data["stock"])
            db.session.add(new_stock)

        # Log the administrative action for auditing purposes.
        AuditLogService.log_admin_action(
            action="create_product",
            target_id=new_product.id,
            details=f"Created product '{new_product.name}'",
        )

        db.session.commit()
        clear_product_cache()
        return new_product

    @staticmethod
    def update_product(product_id, data):
        """
        Updates an existing product, including the enhanced passport and descriptive fields.
        `product_id` is the ID of the product to update.
        `data` is a dictionary containing the fields to update.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return None  # Or raise a custom NotFound exception

            # Store original slug for cache invalidation
            original_slug = product.slug if hasattr(product, "slug") else None

            # Track changes for audit log
            changes = {}

            # Update standard fields using .get(key, default_value) to allow partial updates
            if "name" in data and data["name"] != product.name:
                changes["name"] = {"old": product.name, "new": data["name"]}
                product.name = data["name"]

            if "description" in data and data["description"] != product.description:
                changes["description"] = {
                    "old": product.description,
                    "new": data["description"],
                }
                product.description = data["description"]

            if "price" in data and float(data["price"]) != product.price:
                changes["price"] = {"old": product.price, "new": float(data["price"])}
                product.price = float(data["price"])

            if "stock" in data and int(data["stock"]) != product.stock:
                changes["stock"] = {"old": product.stock, "new": int(data["stock"])}
                product.stock = int(data["stock"])

            if "sku" in data and data["sku"] != product.sku:
                changes["sku"] = {"old": product.sku, "new": data["sku"]}
                product.sku = data["sku"]

            if "image_url" in data and data["image_url"] != product.image_url:
                changes["image_url"] = {
                    "old": product.image_url,
                    "new": data["image_url"],
                }
                product.image_url = data["image_url"]

            if "category_id" in data and data["category_id"] != product.category_id:
                changes["category_id"] = {
                    "old": product.category_id,
                    "new": data["category_id"],
                }
                product.category_id = data["category_id"]

            if (
                "collection_id" in data
                and data["collection_id"] != product.collection_id
            ):
                changes["collection_id"] = {
                    "old": product.collection_id,
                    "new": data["collection_id"],
                }
                product.collection_id = data["collection_id"]

            # --- UPDATE NEWLY ADDED FIELDS ---
            if (
                "passport_hd_image_url" in data
                and data["passport_hd_image_url"] != product.passport_hd_image_url
            ):
                changes["passport_hd_image_url"] = {
                    "old": product.passport_hd_image_url,
                    "new": data["passport_hd_image_url"],
                }
                product.passport_hd_image_url = data["passport_hd_image_url"]

            if (
                "sourcing_production_place" in data
                and data["sourcing_production_place"]
                != product.sourcing_production_place
            ):
                changes["sourcing_production_place"] = {
                    "old": product.sourcing_production_place,
                    "new": data["sourcing_production_place"],
                }
                product.sourcing_production_place = data["sourcing_production_place"]

            if (
                "producer_notes" in data
                and data["producer_notes"] != product.producer_notes
            ):
                changes["producer_notes"] = {
                    "old": product.producer_notes,
                    "new": data["producer_notes"],
                }
                product.producer_notes = data["producer_notes"]

            if (
                "pairing_suggestions" in data
                and data["pairing_suggestions"] != product.pairing_suggestions
            ):
                changes["pairing_suggestions"] = {
                    "old": product.pairing_suggestions,
                    "new": data["pairing_suggestions"],
                }
                product.pairing_suggestions = data["pairing_suggestions"]

            if changes:
                AuditLogService.log_action(
                    "PRODUCT_UPDATED",
                    target_id=product.id,
                    details={"changes": changes},
                )

            db.session.commit()

            # Invalidate caches
            clear_product_cache(product_id=product.id, slug=original_slug)
            if (
                original_slug
                and hasattr(product, "slug")
                and original_slug != product.slug
            ):
                clear_product_cache(slug=product.slug)

            MonitoringService.log_info(
                f"Product updated successfully: {product.name} (ID: {product.id})",
                "ProductService",
            )

            return product.to_dict(view="admin")

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to update product {product_id}: {str(e)}",
                "ProductService",
                exc_info=True,
            )
            raise ValidationException(f"Failed to update product: {str(e)}")

    @staticmethod
    def delete_product(product_id: int):
        """Soft delete product with logging."""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundException(f"Product with ID {product_id} not found")

        try:
            product_slug = product.slug
            product.is_active = False
            product.deleted_at = db.func.now()

            db.session.flush()

            AuditLogService.log_action(
                "PRODUCT_DELETED", target_id=product.id, details={"name": product.name}
            )

            db.session.commit()

            # Invalidate all caches related to this product
            clear_product_cache(product_id=product_id, slug=product_slug)

            MonitoringService.log_info(
                f"Product soft deleted: {product.name} (ID: {product.id})",
                "ProductService",
            )

        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to delete product {product_id}: {str(e)}",
                "ProductService",
                exc_info=True,
            )
            raise ValidationException(f"Failed to delete product: {str(e)}")

    @staticmethod
    def get_product_by_id(product_id):
        """
        Fetches a product by its ID.

        Raises:
            ProductNotFoundError: If no product with the given ID is found.
        """
        product = Product.query.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with id {product_id} not found.")
        return product

    @staticmethod
    def get_low_stock_products(threshold: int = 10):
        """Get products with low stock levels."""
        return (
            db.session.query(
                Product,
                ProductVariant,
                db.func.count(OrderItem.id).label("stock_count"),
            )
            .join(ProductVariant)
            .outerjoin(
                OrderItem,
                db.and_(
                    OrderItem.product_variant_id == ProductVariant.id,
                    OrderItem.status == "in_stock",
                ),
            )
            .group_by(Product.id, ProductVariant.id)
            .having(db.func.count(OrderItem.id) <= threshold)
            .all()
        )
