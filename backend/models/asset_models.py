from backend.extensions import db

from .base import BaseModel


class Asset(BaseModel):
    """
    Represents an uploaded file (e.g., an image) in the media library.
    """

    __tablename__ = "assets"
    filename = db.Column(db.String(255), nullable=False, unique=True)
    # The public URL to access the file
    url = db.Column(db.String(512), nullable=False)
    # e.g., 'image/jpeg', 'image/png'
    mime_type = db.Column(db.String(100), nullable=False)
    # Could be 'product_image', 'blog_post_hero', 'logo', etc.
    usage_tag = db.Column(db.String(50), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "mime_type": self.mime_type,
            "usage_tag": self.usage_tag,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Asset {self.filename}>"
