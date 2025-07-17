from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    sale_date = db.Column(db.String(20), nullable=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    
    customer = db.relationship('Customer', backref='sales')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'sale_date': self.sale_date,
            'total_amount': self.total_amount,
            'currency': self.currency
        }

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    sale = db.relationship('Sale', backref='items')
    product = db.relationship('Product', backref='sale_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }

