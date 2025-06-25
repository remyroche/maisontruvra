from backend.database import db
from .base import BaseModel, SoftDeleteMixin

class BlogCategory(BaseModel, SoftDeleteMixin):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    posts = db.relationship('BlogPost', back_populates='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'is_deleted': self.is_deleted,
        }

class BlogPost(BaseModel, SoftDeleteMixin):
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'author_id': self.author_id,
            'category_id': self.category_id,
            'is_published': self.is_published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'is_deleted': self.is_deleted,
        }
