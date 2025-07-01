"""
This module defines Marshmallow schemas for data validation and serialization.
Schemas ensure that data moving in and out of the API is well-structured and secure,
separating input validation from output serialization.
"""
import re
from marshmallow import Schema, fields, validate, ValidationError
from .extensions import ma

# --- Base Schema & Custom Validators ---

class BaseSchema(ma.Schema):
    """Base schema with common configuration."""
    class Meta:
        unknown = 'EXCLUDE'

def validate_password_complexity(password):
    """
    Custom validator for password strength. Ensures at least 8 characters,
    one uppercase, one lowercase, one digit, and one special character.
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[\W_]", password):
        raise ValidationError("Password must contain at least one special character.")

# --- Core Model Schemas ---

class RoleSchema(BaseSchema):
    """Schema for serializing Role data."""
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)

class AddressSchema(BaseSchema):
    """Schema for shipping/billing addresses."""
    id = fields.Int(dump_only=True)
    street = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    country = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    address_type = fields.Str(validate=validate.OneOf(["shipping", "billing"]))
    is_default = fields.Bool(default=False)

class CategorySchema(BaseSchema):
    """Schema for Product Categories."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class TagSchema(BaseSchema):
    """Schema for Product Tags."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class VariantSchema(BaseSchema):
    """Schema for Product Variants."""
    id = fields.Int(dump_only=True)
    sku = fields.Str(required=True)
    price_offset = fields.Decimal(as_string=True, required=True)
    stock = fields.Int(required=True, validate=validate.Range(min=0))

class ProductSchema(BaseSchema):
    """Schema for serializing a full Product object."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    price = fields.Decimal(as_string=True, required=True)
    is_active = fields.Bool(required=True)
    is_featured = fields.Bool(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    category_id = fields.Int(required=True, load_only=True)
    tag_ids = fields.List(fields.Int(), load_only=True, required=False)
    category = fields.Nested(CategorySchema, dump_only=True)
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    variants = fields.List(fields.Nested(VariantSchema), required=True)

class ReviewSchema(BaseSchema):
    """Schema for product reviews."""
    id = fields.Int(dump_only=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    title = fields.Str(required=True, validate=validate.Length(max=100))
    comment = fields.Str(validate=validate.Length(max=1000))
    is_approved = fields.Bool(dump_only=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'first_name'))
    product = fields.Nested(ProductSchema, dump_only=True, only=('id', 'name'))

# --- User & Auth Schemas ---

class UserSchema(BaseSchema):
    """Base User schema for serialization."""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    is_active = fields.Bool(dump_only=True)
    roles = fields.List(fields.Nested(RoleSchema), dump_only=True)

class UserRegistrationSchema(BaseSchema):
    """Schema for new user registration."""
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password_complexity)

class LoginSchema(BaseSchema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserProfileUpdateSchema(BaseSchema):
    """Schema for users updating their own profile."""
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))

class ChangePasswordSchema(BaseSchema):
    """Schema for changing a password."""
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password_complexity)

class PasswordResetRequestSchema(BaseSchema):
    """Schema for requesting a password reset."""
    email = fields.Email(required=True)

class PasswordResetConfirmSchema(BaseSchema):
    """Schema for confirming a password reset with a token."""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate_password_complexity)

# --- Cart & Checkout Schemas ---

class AddToCartSchema(BaseSchema):
    """Schema for adding an item to the cart."""
    variant_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class UpdateCartItemSchema(BaseSchema):
    """Schema for updating an item's quantity in the cart."""
    quantity = fields.Int(required=True, validate=validate.Range(min=0)) # 0 to remove

class ApplyDiscountSchema(BaseSchema):
    """Schema for applying a discount code to the cart."""
    code = fields.Str(required=True)

class CheckoutSchema(BaseSchema):
    """Schema for validating the final checkout payload."""
    shipping_address_id = fields.Int(required=True)
    billing_address_id = fields.Int(required=True)
    delivery_method_id = fields.Int(required=True)
    payment_token = fields.Str(required=True) # From payment provider
    notes = fields.Str(allow_none=True)

# --- Blog Schemas ---

class BlogCategorySchema(BaseSchema):
    """Schema for blog categories."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3))
    slug = fields.Str(dump_only=True)

class BlogPostSchema(BaseSchema):
    """Schema for validating and serializing Blog Posts."""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=5))
    content = fields.Str(required=True)
    slug = fields.Str(dump_only=True)
    is_published = fields.Bool(default=False)
    created_at = fields.DateTime(dump_only=True)
    author_id = fields.Int(load_only=True, required=True)
    category_id = fields.Int(load_only=True, required=True)
    author = fields.Nested(UserSchema, dump_only=True, only=("id", "first_name", "last_name"))
    category = fields.Nested(BlogCategorySchema, dump_only=True)

# --- Admin-Specific Schemas ---

class AdminUserUpdateSchema(BaseSchema):
    """Schema for admins updating user profiles."""
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    is_active = fields.Bool()
    role_ids = fields.List(fields.Int())

class OrderUpdateSchema(BaseSchema):
    """Schema for admins updating an order's status."""
    status = fields.Str(required=True, validate=validate.OneOf(["pending", "processing", "shipped", "delivered", "cancelled"]))
    tracking_number = fields.Str(allow_none=True, validate=validate.Length(max=100))

class DiscountSchema(BaseSchema):
    """Schema for creating/updating discounts."""
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True, validate=validate.Length(min=4, max=50))
    discount_type = fields.Str(required=True, validate=validate.OneOf(['percentage', 'fixed']))
    value = fields.Decimal(as_string=True, required=True, validate=validate.Range(min=0))
    is_active = fields.Bool(default=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_to = fields.DateTime(allow_none=True)
    usage_limit = fields.Int(allow_none=True, validate=validate.Range(min=1))

class DeliveryMethodSchema(BaseSchema):
    """Schema for creating/updating delivery methods."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(allow_none=True)
    price = fields.Decimal(as_string=True, required=True, validate=validate.Range(min=0))
    is_active = fields.Bool(default=True)
    tier_ids = fields.List(fields.Int(), load_only=True, required=False)

# --- Miscellaneous Schemas ---

class ContactFormSchema(BaseSchema):
    """Schema for the public contact form."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    company_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)

class NewsletterSubscriptionSchema(BaseSchema):
    """Schema for newsletter signups."""
    email = fields.Email(required=True)
    first_name = fields.Str(validate=validate.Length(max=50))
    list_type = fields.Str(missing='b2c', validate=validate.OneOf(['b2c', 'b2b']))

class SiteSettingsSchema(Schema):
    """A dynamic schema for updating site settings."""
    settings = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)
