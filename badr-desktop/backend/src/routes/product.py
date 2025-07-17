from flask import Blueprint, request, jsonify, send_from_directory
from src.models.product import Product, ProductCategory, db
from src.services.telegram_service import telegram_service
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import os
import uuid
import json

product_bp = Blueprint('product', __name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 800)):
    """Resize image to maximum dimensions while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize image
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

@product_bp.route('/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    if category:
        query = query.filter(Product.category == category)
    if status == 'low_stock':
        query = query.filter(Product.quantity <= Product.min_stock_level)
    elif status == 'out_of_stock':
        query = query.filter(Product.quantity <= 0)
    elif status == 'active':
        query = query.filter(Product.is_active == True)
    
    products = query.all()
    return jsonify([product.to_dict() for product in products])

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@product_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    try:
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            cost_price=data['cost_price'],
            selling_price=data['selling_price'],
            quantity=data['quantity'],
            qr_code=data.get('qr_code'),
            currency=data['currency'],
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            model=data.get('model', ''),
            color=data.get('color', ''),
            size=data.get('size', ''),
            weight=data.get('weight'),
            dimensions=data.get('dimensions', ''),
            min_stock_level=data.get('min_stock_level', 5),
            max_stock_level=data.get('max_stock_level', 100),
            reorder_point=data.get('reorder_point', 10),
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False)
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Send notification
        try:
            message = f"📦 تم إضافة منتج جديد\n\n"
            message += f"الاسم: {product.name}\n"
            message += f"السعر: {product.selling_price} {product.currency}\n"
            message += f"الكمية: {product.quantity}\n"
            if product.category:
                message += f"الفئة: {product.category}\n"
            
            telegram_service.send_notification(message, 'product')
        except Exception as e:
            print(f"Failed to send product notification: {e}")
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    try:
        old_quantity = product.quantity
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.cost_price = data.get('cost_price', product.cost_price)
        product.selling_price = data.get('selling_price', product.selling_price)
        product.quantity = data.get('quantity', product.quantity)
        product.qr_code = data.get('qr_code', product.qr_code)
        product.currency = data.get('currency', product.currency)
        product.category = data.get('category', product.category)
        product.brand = data.get('brand', product.brand)
        product.model = data.get('model', product.model)
        product.color = data.get('color', product.color)
        product.size = data.get('size', product.size)
        product.weight = data.get('weight', product.weight)
        product.dimensions = data.get('dimensions', product.dimensions)
        product.min_stock_level = data.get('min_stock_level', product.min_stock_level)
        product.max_stock_level = data.get('max_stock_level', product.max_stock_level)
        product.reorder_point = data.get('reorder_point', product.reorder_point)
        product.is_active = data.get('is_active', product.is_active)
        product.is_featured = data.get('is_featured', product.is_featured)
        product.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.session.commit()
        
        # Send notification for low stock
        if old_quantity > product.min_stock_level and product.quantity <= product.min_stock_level:
            try:
                message = f"⚠️ تنبيه مخزون قليل\n\n"
                message += f"المنتج: {product.name}\n"
                message += f"الكمية المتبقية: {product.quantity}\n"
                message += f"الحد الأدنى: {product.min_stock_level}"
                
                telegram_service.send_notification(message, 'inventory')
            except Exception as e:
                print(f"Failed to send low stock notification: {e}")
        
        return jsonify(product.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Delete associated images
    images_to_delete = product.get_images_list()
    for image_path in images_to_delete:
        try:
            full_path = os.path.join(UPLOAD_FOLDER, image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting image {image_path}: {e}")
    
    db.session.delete(product)
    db.session.commit()
    
    return '', 204

@product_bp.route('/products/<int:product_id>/upload-image', methods=['POST'])
def upload_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    file = request.files['image']
    is_main = request.form.get('is_main', 'false').lower() == 'true'
    
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'نوع الملف غير مدعوم'}), 400
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create upload path
        upload_path = os.path.join(UPLOAD_FOLDER, 'products')
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Resize image
        if not resize_image(file_path):
            os.remove(file_path)
            return jsonify({'error': 'فشل في معالجة الصورة'}), 500
        
        # Update product
        relative_path = f"products/{unique_filename}"
        product.add_image(relative_path, is_main)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم رفع الصورة بنجاح',
            'image_path': relative_path,
            'product': product.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>/remove-image', methods=['DELETE'])
def remove_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    image_path = data.get('image_path')
    if not image_path:
        return jsonify({'error': 'مسار الصورة مطلوب'}), 400
    
    try:
        # Remove from filesystem
        full_path = os.path.join(UPLOAD_FOLDER, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        
        # Remove from product
        product.remove_image(image_path)
        db.session.commit()
        
        return jsonify({
            'message': 'تم حذف الصورة بنجاح',
            'product': product.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@product_bp.route('/products/stats', methods=['GET'])
def get_product_stats():
    total_products = Product.query.count()
    active_products = Product.query.filter(Product.is_active == True).count()
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_stock_level).count()
    out_of_stock_products = Product.query.filter(Product.quantity <= 0).count()
    
    # Calculate total inventory value
    products = Product.query.all()
    total_cost_value = sum(p.cost_price * p.quantity for p in products)
    total_selling_value = sum(p.selling_price * p.quantity for p in products)
    
    return jsonify({
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_cost_value': total_cost_value,
        'total_selling_value': total_selling_value,
        'potential_profit': total_selling_value - total_cost_value
    })

# Product Categories Routes
@product_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = ProductCategory.query.filter(ProductCategory.is_active == True).all()
    return jsonify([category.to_dict() for category in categories])

@product_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    
    try:
        category = ProductCategory(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@product_bp.route('/categories/<int:category_id>/upload-image', methods=['POST'])
def upload_category_image(category_id):
    category = ProductCategory.query.get_or_404(category_id)
    
    if 'image' not in request.files:
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'نوع الملف غير مدعوم'}), 400
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"category_{category_id}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create upload path
        upload_path = os.path.join(UPLOAD_FOLDER, 'categories')
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Resize image
        if not resize_image(file_path):
            os.remove(file_path)
            return jsonify({'error': 'فشل في معالجة الصورة'}), 500
        
        # Update category
        relative_path = f"categories/{unique_filename}"
        category.image = relative_path
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم رفع الصورة بنجاح',
            'image_path': relative_path,
            'category': category.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

