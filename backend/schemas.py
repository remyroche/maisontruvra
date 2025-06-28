from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    price = fields.Decimal(as_string=True, required=True)
    sku = fields.Str(required=True)
    image_url = fields.URL(dump_only=True)
    
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
