from marshmallow import Schema, fields, validate, ValidationError
import re

# --- Input Validation Schemas (for 'loading' data into the app) ---


def validate_password_complexity(password):
    """
    Validates that the password has at least 8 characters, one uppercase, one lowercase, one digit, and one special character.
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[\W_]", password): # Non-alphanumeric
        raise ValidationError("Password must contain at least one special character.")

# --- High-Priority Schemas ---

class UserRegistrationSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50, error="First name is required."))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50, error="Last name is required."))
    email = fields.Email(required=True, error="A valid email is required.")
    password = fields.Str(required=True, validate=validate_password_complexity)

class UserProfileUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    email = fields.Email()

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password_complexity)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password_complexity)

class AddressSchema(Schema):
    street = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    country = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    address_type = fields.Str(required=True, validate=validate.OneOf(["shipping", "billing"]))
    is_default = fields.Bool(missing=False)

class AdminUserUpdateSchema(UserProfileUpdateSchema):
    is_active = fields.Bool()
    roles = fields.List(fields.Str())

# --- Medium-Priority Schemas ---

class BlogPostSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True)
    author_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    slug = fields.Str(validate=validate.Length(max=255), allow_none=True)
    is_published = fields.Bool(missing=False)

class ProductReviewSchema(Schema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5, error="Rating must be between 1 and 5."))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    comment = fields.Str(required=True, validate=validate.Length(min=1, max=1000))

class ContactFormSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    company_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)

class SiteSettingsSchema(Schema):
    site_name = fields.Str(validate=validate.Length(min=1, max=100))
    contact_email = fields.Email()
    # This can be expanded with more site settings
    class Meta:
        unknown = fields.INCLUDE


# --- Low-Priority Schemas ---

class CheckoutSchema(Schema):
    shipping_address_id = fields.Int(required=True)
    billing_address_id = fields.Int(required=True)
    payment_method_id = fields.Str(required=True)

class DiscountSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    discount_type = fields.Str(required=True, validate=validate.OneOf(["percentage", "fixed_amount"]))
    value = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    expires_at = fields.DateTime(allow_none=True)
    max_uses = fields.Int(allow_none=True, validate=validate.Range(min=1))
    min_purchase_amount = fields.Decimal(allow_none=True, places=2, validate=validate.Range(min=0))


class ProductVariantInputSchema(Schema):
    """Schema for validating product variants when creating or updating a product."""
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100, error="SKU must be between 1 and 100 characters."))
    price_offset = fields.Decimal(required=True, places=2, error_messages={"required": "Price offset is required."})
    stock = fields.Int(required=True, validate=validate.Range(min=0, error="Stock cannot be negative."))

class CreateProductInputSchema(Schema):
    """
    Schema for validating the incoming payload for creating a new product.
    This is used for 'loading' data.
    """
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255, error="Name must be between 3 and 255 characters."))
    description = fields.Str(required=True, validate=validate.Length(min=10, error="Description must be at least 10 characters long."))
    price = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01, error="Price must be greater than 0."))
    category_id = fields.Int(required=True, error_messages={"required": "Category ID is required."})
    collection_id = fields.Int(required=False, allow_none=True)
    is_active = fields.Bool(required=True)
    is_featured = fields.Bool(required=True)
    variants = fields.List(fields.Nested(ProductVariantInputSchema), required=True, validate=validate.Length(min=1, error="At least one product variant is required."))


# --- Output Serialization Schemas (for 'dumping' data out of the app) ---

class ProductVariantOutputSchema(Schema):
    """Schema for serializing a single product variant for API responses."""
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    price_offset = fields.Decimal(as_string=True)
    stock = fields.Int(source="stock.quantity") # Nested object access

class ProductOutputSchema(Schema):
    """
    Schema for serializing a full Product object for API responses.
    This is used for 'dumping' data. It includes nested variants.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    price = fields.Decimal(as_string=True)
    image_url = fields.URL(dump_only=True) # Assuming a method/property `image_url` exists on the model
    is_active = fields.Bool()
    is_featured = fields.Bool()
    category = fields.Nested('CategorySchema', only=('id', 'name')) # Example of nesting a related model
    variants = fields.List(fields.Nested(ProductVariantOutputSchema))

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    
class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    total_amount = fields.Decimal(as_string=True, required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    
class B2BUserSchema(Schema):
    id = fields.Int(dump_only=True)
    company_name = fields.Str(required=True)
    vat_number = fields.Str()
    user_id = fields.Int(required=True)

class BlogCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class BlogPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    slug = fields.Str(required=True)
    category_id = fields.Int(required=True)
    author_id = fields.Int(required=True)
    published = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


# Additional schemas for API resource handler decorator
class UpdateUserSchema(Schema):
    """Schema for updating user information."""
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    language = fields.Str(validate=validate.OneOf(['en', 'fr', 'es', 'de']))

class UpdatePasswordSchema(Schema):
    """Schema for updating user password."""
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

class AddToWishlistSchema(Schema):
    """Schema for adding items to wishlist."""
    product_id = fields.Int(required=True, validate=validate.Range(min=1))

class ReviewSchema(Schema):
    """Schema for product reviews."""
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))

class OrderStatusUpdateSchema(Schema):
    """Schema for updating order status."""
    status = fields.Str(required=True, validate=validate.OneOf(['pending', 'processing', 'shipped', 'delivered', 'cancelled']))

class InvoiceSignatureSchema(Schema):
    """Schema for invoice signature."""
    signature_data = fields.Str(required=True)

class QuoteRequestSchema(Schema):
    """Schema for B2B quote requests."""
    request_details = fields.Str(required=True, validate=validate.Length(min=10, max=2000))

class BlogCategorySchema(Schema):
    """Schema for blog categories."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

class LanguageUpdateSchema(Schema):
    """Schema for updating user language."""
    language = fields.Str(required=True, validate=validate.OneOf(['en', 'fr', 'es', 'de']))

class TwoFactorSetupSchema(Schema):
    """Schema for 2FA setup."""
    totp_code = fields.Str(required=True, validate=validate.Length(min=6, max=6))

class TwoFactorVerifySchema(Schema):
    """Schema for 2FA verification."""
    totp_code = fields.Str(required=True, validate=validate.Length(min=6, max=6))

# Cart and Checkout Schemas
class AddToCartSchema(Schema):
    """Schema for adding items to cart."""
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(missing=1, validate=validate.Range(min=1, max=100))

class UpdateCartItemSchema(Schema):
    """Schema for updating cart item quantity."""
    quantity = fields.Int(required=True, validate=validate.Range(min=1, max=100))

class ApplyDiscountSchema(Schema):
    """Schema for applying discount codes."""
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))


class GuestInfoSchema(Schema):
    """Schema for guest checkout information."""
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(validate=validate.Length(max=20))

class CheckoutSchema(Schema):
    cart_id = fields.Int(required=True)
    payment_token = fields.Str(required=True) # Generic token from payment provider
    guest_info = fields.Nested(GuestInfoSchema)
    shipping_address_id = fields.Int()
    billing_address_id = fields.Int()

    # Custom validation to ensure either guest info or address IDs are present
    def validate_checkout_data(self, data, **kwargs):
        is_guest = 'guest_info' in data and data['guest_info']
        is_user = 'shipping_address_id' in data and data['shipping_address_id']
        if not is_guest and not is_user:
            raise ValidationError("Either guest_info or shipping_address_id must be provided.")
        if is_guest and is_user:
            raise ValidationError("Provide either guest_info or address IDs, not both.")
            
# Product Search and Filter Schemas
class ProductSearchSchema(Schema):
    """Schema for product search parameters."""
    q = fields.Str(validate=validate.Length(min=2, max=100))
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=24, validate=validate.Range(min=1, max=100))
    category = fields.Str(validate=validate.Length(max=100))

# Newsletter Schema
class NewsletterSubscriptionSchema(Schema):
    """Schema for newsletter subscription."""
    email = fields.Email(required=True)
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    list_type = fields.Str(missing='b2c', validate=validate.OneOf(['b2c', 'b2b']))

# B2B Schemas
class B2BRegistrationSchema(Schema):
    """Schema for B2B user registration."""
    company_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    vat_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

class B2BQuickOrderSchema(Schema):
    """Schema for B2B quick order."""
    items = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))

# Admin Schemas
class UserManagementSchema(Schema):
    """Schema for admin user management."""
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    is_active = fields.Bool()
    role = fields.Str(validate=validate.OneOf(['user', 'admin', 'manager']))

class ProductManagementSchema(Schema):
    """Schema for admin product management."""
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(min=10))
    price = fields.Decimal(validate=validate.Range(min=0.01), places=2)
    is_active = fields.Bool()
    is_featured = fields.Bool()
    category_id = fields.Int(validate=validate.Range(min=1))

# Inventory Schema
class InventoryUpdateSchema(Schema):
    """Schema for inventory updates."""
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=0))
    location = fields.Str(validate=validate.Length(max=100))

# Delivery Schema
class DeliveryMethodSchema(Schema):
    """Schema for delivery method selection."""
    method_id = fields.Int(required=True, validate=validate.Range(min=1))
    address_id = fields.Int(required=True, validate=validate.Range(min=1))

# MFA Schemas
class MfaVerificationSchema(Schema):
    """Schema for MFA verification during login."""
    user_id = fields.Int(required=True, validate=validate.Range(min=1))
    mfa_token = fields.Str(required=True, validate=validate.Length(min=6, max=6))

# Password Reset Schemas
class PasswordResetRequestSchema(Schema):
    """Schema for password reset request."""
    email = fields.Email(required=True)

class PasswordResetConfirmSchema(Schema):
    """Schema for password reset confirmation."""
    token = fields.Str(required=True, validate=validate.Length(min=1))
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

# Order Creation Schemas
class GuestOrderSchema(Schema):
    """Schema for guest order creation."""
    guest_info = fields.Nested(GuestInfoSchema, required=True)
    shipping_address = fields.Nested(AddressSchema, required=True)
    billing_address = fields.Nested(AddressSchema, required=True)
    payment_token = fields.Str(required=True)
    cart_items = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))

class AuthenticatedOrderSchema(Schema):
    """Schema for authenticated user order creation."""
    shipping_address_id = fields.Int(validate=validate.Range(min=1))
    billing_address_id = fields.Int(validate=validate.Range(min=1))
    shipping_address = fields.Nested(AddressSchema)
    billing_address = fields.Nested(AddressSchema)
    payment_token = fields.Str(required=True)
    cart_items = fields.List(fields.Dict(), validate=validate.Length(min=1))

class CheckoutOrderSchema(Schema):
    """Schema for checkout process."""
    shipping_address = fields.Nested(AddressSchema, required=True)
    billing_address = fields.Nested(AddressSchema, required=True)
    payment_token = fields.Str(required=True)
    delivery_method_id = fields.Int(validate=validate.Range(min=1))
    notes = fields.Str(validate=validate.Length(max=500))
