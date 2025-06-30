from marshmallow import Schema, fields, validate

# --- Input Validation Schemas (for 'loading' data into the app) ---

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

class UserRegistrationSchema(Schema):
    firstName = fields.Str(required=True, data_key="first_name")
    lastName = fields.Str(required=True, data_key="last_name")
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class AddressSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    street_line_1 = fields.Str(required=True)
    street_line_2 = fields.Str(allow_none=True)
    city = fields.Str(required=True)
    postal_code = fields.Str(required=True)
    country = fields.Str(required=True)

class ContactFormSchema(Schema):
    """Schema for validating contact form submissions."""
    name = fields.Str(required=True, validate=validate.Length(min=2, error="Name is required."))
    email = fields.Email(required=True, error_messages={"required": "A valid email is required."})
    subject = fields.Str(required=True, validate=validate.Length(min=5, error="Subject must be at least 5 characters."))
    message = fields.Str(required=True, validate=validate.Length(min=10, error="Message must be at least 10 characters."))
