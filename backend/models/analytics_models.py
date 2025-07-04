from backend.database import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSONB


class PageView(BaseModel):
    __tablename__ = "page_views"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


class SalesAnalytics(BaseModel):
    __tablename__ = "sales_analytics"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_sales = db.Column(db.Numeric(10, 2), nullable=False)
    order_count = db.Column(db.Integer, nullable=False)
    data = db.Column(JSONB)  # For storing aggregated data like top products, etc.
