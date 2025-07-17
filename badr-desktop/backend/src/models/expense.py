from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.String(20), nullable=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    currency = db.Column(db.String(10), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'expense_date': self.expense_date,
            'currency': self.currency
        }

