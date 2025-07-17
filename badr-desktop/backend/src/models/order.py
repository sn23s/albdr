from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='IQD')
    order_type = db.Column(db.String(20), nullable=False, default='pickup')  # pickup, delivery
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, preparing, ready, delivered, cancelled
    notes = db.Column(db.Text, nullable=True)
    order_date = db.Column(db.String(20), nullable=False)
    delivery_date = db.Column(db.String(20), nullable=True)
    delivery_fee = db.Column(db.Float, nullable=True, default=0)
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'order_type': self.order_type,
            'status': self.status,
            'notes': self.notes,
            'order_date': self.order_date,
            'delivery_date': self.delivery_date,
            'delivery_fee': self.delivery_fee,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'items': [item.to_dict() for item in self.items] if self.items else []
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        # Import here to avoid circular imports
        from src.models.product import Product
        product = Product.query.get(self.product_id)
        
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'total': self.total,
            'product_name': product.name if product else None,
            'product_description': product.description if product else None
        }

