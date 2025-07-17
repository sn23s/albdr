from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class Warranty(db.Model):
    __tablename__ = 'warranties'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Warranty details
    warranty_type = db.Column(db.String(50), nullable=False, default='manufacturer')  # manufacturer, store, extended
    warranty_period_months = db.Column(db.Integer, nullable=False, default=12)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    
    # Status and tracking
    status = db.Column(db.String(20), nullable=False, default='active')  # active, expired, claimed, void
    is_transferable = db.Column(db.Boolean, default=False)
    
    # Claim information
    claim_count = db.Column(db.Integer, default=0)
    last_claim_date = db.Column(db.String(20))
    claim_history = db.Column(db.Text)  # JSON string of claim history
    
    # Terms and conditions
    terms = db.Column(db.Text)
    coverage_details = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    
    # Contact and service info
    service_center = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    
    # Additional info
    serial_number = db.Column(db.String(100))
    purchase_price = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Relationships
    product = db.relationship('Product', backref='warranties')
    customer = db.relationship('Customer', backref='warranties')
    sale = db.relationship('Sale', backref='warranties')
    
    def get_days_remaining(self):
        """Get number of days remaining in warranty"""
        try:
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
            today = datetime.now()
            delta = end_date - today
            return max(0, delta.days)
        except:
            return 0
    
    def is_expired(self):
        """Check if warranty has expired"""
        return self.get_days_remaining() == 0
    
    def is_expiring_soon(self, days=30):
        """Check if warranty is expiring within specified days"""
        remaining = self.get_days_remaining()
        return 0 < remaining <= days
    
    def get_status_info(self):
        """Get warranty status with color and message"""
        if self.status == 'void':
            return {'status': 'void', 'message': 'ملغية', 'color': 'gray'}
        elif self.status == 'claimed':
            return {'status': 'claimed', 'message': 'مطالب بها', 'color': 'blue'}
        elif self.is_expired():
            return {'status': 'expired', 'message': 'منتهية', 'color': 'red'}
        elif self.is_expiring_soon(7):
            return {'status': 'expiring_soon', 'message': 'تنتهي قريباً', 'color': 'orange'}
        elif self.is_expiring_soon(30):
            return {'status': 'expiring_month', 'message': 'تنتهي خلال شهر', 'color': 'yellow'}
        else:
            return {'status': 'active', 'message': 'سارية', 'color': 'green'}
    
    def add_claim(self, claim_details):
        """Add a new warranty claim"""
        claim_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'details': claim_details,
            'claim_number': self.claim_count + 1
        }
        
        # Update claim history
        history = []
        if self.claim_history:
            try:
                history = json.loads(self.claim_history)
            except:
                history = []
        
        history.append(claim_data)
        self.claim_history = json.dumps(history)
        self.claim_count += 1
        self.last_claim_date = claim_data['date']
        self.status = 'claimed'
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_claim_history(self):
        """Get warranty claim history"""
        if not self.claim_history:
            return []
        
        try:
            return json.loads(self.claim_history)
        except:
            return []
    
    def extend_warranty(self, additional_months, reason=''):
        """Extend warranty period"""
        try:
            current_end = datetime.strptime(self.end_date, '%Y-%m-%d')
            new_end = current_end + timedelta(days=additional_months * 30)
            self.end_date = new_end.strftime('%Y-%m-%d')
            self.warranty_period_months += additional_months
            self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Add to notes
            extension_note = f"تم تمديد الضمان {additional_months} شهر في {datetime.now().strftime('%Y-%m-%d')}"
            if reason:
                extension_note += f" - السبب: {reason}"
            
            if self.notes:
                self.notes += f"\n{extension_note}"
            else:
                self.notes = extension_note
                
            return True
        except:
            return False
    
    def to_dict(self):
        status_info = self.get_status_info()
        
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'customer_id': self.customer_id,
            
            # Product and customer info (if relationships are loaded)
            'product_name': self.product.name if self.product else None,
            'customer_name': self.customer.name if self.customer else None,
            'customer_phone': self.customer.phone if self.customer else None,
            
            # Warranty details
            'warranty_type': self.warranty_type,
            'warranty_period_months': self.warranty_period_months,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'days_remaining': self.get_days_remaining(),
            
            # Status
            'status': self.status,
            'status_info': status_info,
            'is_transferable': self.is_transferable,
            'is_expired': self.is_expired(),
            'is_expiring_soon': self.is_expiring_soon(),
            
            # Claims
            'claim_count': self.claim_count,
            'last_claim_date': self.last_claim_date,
            'claim_history': self.get_claim_history(),
            
            # Terms and service
            'terms': self.terms,
            'coverage_details': self.coverage_details,
            'exclusions': self.exclusions,
            'service_center': self.service_center,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            
            # Additional info
            'serial_number': self.serial_number,
            'purchase_price': self.purchase_price,
            'notes': self.notes,
            
            # Timestamps
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class WarrantyTemplate(db.Model):
    __tablename__ = 'warranty_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    warranty_type = db.Column(db.String(50), nullable=False)
    period_months = db.Column(db.Integer, nullable=False)
    terms = db.Column(db.Text)
    coverage_details = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'warranty_type': self.warranty_type,
            'period_months': self.period_months,
            'terms': self.terms,
            'coverage_details': self.coverage_details,
            'exclusions': self.exclusions,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

