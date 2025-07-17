from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    qr_code = db.Column(db.String(255), unique=True)
    currency = db.Column(db.String(10), nullable=False)
    
    # Image fields
    main_image = db.Column(db.String(500))  # Main product image path
    images = db.Column(db.Text)  # JSON array of additional image paths
    
    # Additional product information
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(100))  # e.g., "10x20x30 cm"
    
    # Inventory management
    min_stock_level = db.Column(db.Integer, default=5)
    max_stock_level = db.Column(db.Integer, default=100)
    reorder_point = db.Column(db.Integer, default=10)
    
    # Product status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def get_images_list(self):
        """Get list of all product images"""
        images_list = []
        
        # Add main image if exists
        if self.main_image:
            images_list.append(self.main_image)
        
        # Add additional images
        if self.images:
            try:
                additional_images = json.loads(self.images)
                if isinstance(additional_images, list):
                    images_list.extend(additional_images)
            except:
                pass
        
        return images_list
    
    def add_image(self, image_path, is_main=False):
        """Add an image to the product"""
        if is_main:
            self.main_image = image_path
        else:
            current_images = []
            if self.images:
                try:
                    current_images = json.loads(self.images)
                    if not isinstance(current_images, list):
                        current_images = []
                except:
                    current_images = []
            
            if image_path not in current_images:
                current_images.append(image_path)
                self.images = json.dumps(current_images)
        
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def remove_image(self, image_path):
        """Remove an image from the product"""
        if self.main_image == image_path:
            self.main_image = None
        
        if self.images:
            try:
                current_images = json.loads(self.images)
                if isinstance(current_images, list) and image_path in current_images:
                    current_images.remove(image_path)
                    self.images = json.dumps(current_images)
            except:
                pass
        
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_stock_status(self):
        """Get stock status information"""
        if self.quantity <= 0:
            return {'status': 'out_of_stock', 'message': 'نفد المخزون', 'color': 'red'}
        elif self.quantity <= self.min_stock_level:
            return {'status': 'low_stock', 'message': 'مخزون قليل', 'color': 'yellow'}
        elif self.quantity <= self.reorder_point:
            return {'status': 'reorder_needed', 'message': 'يحتاج إعادة طلب', 'color': 'orange'}
        else:
            return {'status': 'in_stock', 'message': 'متوفر', 'color': 'green'}
    
    def get_profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            profit = self.selling_price - self.cost_price
            margin = (profit / self.cost_price) * 100
            return round(margin, 2)
        return 0
    
    def to_dict(self):
        stock_status = self.get_stock_status()
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'quantity': self.quantity,
            'qr_code': self.qr_code,
            'currency': self.currency,
            
            # Images
            'main_image': self.main_image,
            'images': self.get_images_list(),
            
            # Additional info
            'category': self.category,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'size': self.size,
            'weight': self.weight,
            'dimensions': self.dimensions,
            
            # Inventory
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'reorder_point': self.reorder_point,
            
            # Status
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'stock_status': stock_status,
            'profit_margin': self.get_profit_margin(),
            
            # Timestamps
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

