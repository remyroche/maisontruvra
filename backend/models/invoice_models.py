from backend.database import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quote'
    id = db.Column(db.Integer, primary_key=True)
    b2b_account_id = db.Column(db.Integer, db.ForeignKey('b2b_account.id'), nullable=False)
    user_request = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, converted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    b2b_account = db.relationship('B2BAccount', backref=db.backref('quotes', lazy=True))

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    b2b_account_id = db.Column(db.Integer, db.ForeignKey('b2b_account.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='draft', nullable=False) # draft, pending_signature, signed, paid, void
    due_date = db.Column(db.DateTime)
    signature_data = db.Column(db.Text, nullable=True)
    pdf_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    b2b_account = db.relationship('B2BAccount', backref=db.backref('invoices', lazy=True))
    quote = db.relationship('Quote', backref=db.backref('invoice', uselist=False))

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_item'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    invoice = db.relationship('Invoice', backref=db.backref('items', cascade="all, delete-orphan"))
