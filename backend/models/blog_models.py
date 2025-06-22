from backend.database import db
from .base import BaseModel

class BlogCategory(BaseModel):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    posts = db.relationship('BlogPost', back_populates='category')

class BlogPost(BaseModel):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    
    author = db.relationship('User')
    category = db.relationship('BlogCategory', back_populates='posts')
