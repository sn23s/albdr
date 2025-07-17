from flask import Blueprint, request, jsonify
from src.models.order import Order, OrderItem, db
from src.models.product import Product
from src.services.telegram_service import telegram_service
from datetime import datetime, timedelta

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    """الحصول على جميع الطلبات"""
    status = request.args.get('status')
    order_type = request.args.get('order_type')
    
    query = Order.query
    if status:
        query = query.filter(Order.status == status)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    
    orders = query.order_by(Order.order_date.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """الحصول على طلب محدد"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@order_bp.route('/orders', methods=['POST'])
def create_order():
    """إنشاء طلب جديد"""
    data = request.get_json()
    
    # إنشاء الطلب
    order = Order(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_address=data.get('customer_address', ''),
        total_amount=data['total_amount'],
        currency=data.get('currency', 'IQD'),
        order_type=data.get('order_type', 'pickup'),
        status='pending',
        notes=data.get('notes', ''),
        order_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        delivery_date=data.get('delivery_date'),
        delivery_fee=data.get('delivery_fee', 0)
    )
    
    db.session.add(order)
    db.session.flush()  # للحصول على معرف الطلب
    
    # إضافة عناصر الطلب
    items_for_notification = []
    for item_data in data['items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)
        
        # إضافة معلومات المنتج للإشعار
        product = Product.query.get(item_data['product_id'])
        if product:
            items_for_notification.append({
                'name': product.name,
                'quantity': item_data['quantity'],
                'price': item_data['price']
            })
    
    db.session.commit()
    
    # إرسال إشعار التليجرام للطلب الجديد
    try:
        order_type_text = 'استلام من المحل' if order.order_type == 'pickup' else 'توصيل'
        
        message = f"""
🛍️ <b>طلب جديد</b>

👤 <b>العميل:</b> {order.customer_name}
📱 <b>الهاتف:</b> {order.customer_phone}
🏠 <b>العنوان:</b> {order.customer_address or 'غير محدد'}
💰 <b>المبلغ:</b> {order.total_amount:,.2f} {order.currency}
🚚 <b>نوع الطلب:</b> {order_type_text}
📦 <b>عدد المنتجات:</b> {len(items_for_notification)}
📅 <b>التاريخ:</b> {order.order_date}

🏪 <i>البدر للإنارة</i>
        """.strip()
        
        telegram_service.send_message(message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    return jsonify(order.to_dict()), 201

@order_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """تحديث حالة الطلب"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    old_status = order.status
    new_status = data.get('status')
    
    if new_status:
        order.status = new_status
        db.session.commit()
        
        # إرسال إشعار تغيير الحالة
        try:
            status_text = {
                'pending': 'في الانتظار',
                'confirmed': 'مؤكد',
                'preparing': 'قيد التحضير',
                'ready': 'جاهز للاستلام',
                'delivered': 'تم التوصيل',
                'cancelled': 'ملغي'
            }.get(new_status, new_status)
            
            message = f"""
📋 <b>تحديث حالة الطلب #{order.id}</b>

👤 <b>العميل:</b> {order.customer_name}
📱 <b>الهاتف:</b> {order.customer_phone}
🔄 <b>الحالة الجديدة:</b> {status_text}
💰 <b>المبلغ:</b> {order.total_amount:,.2f} {order.currency}

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            telegram_service.send_message(message)
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")
    
    return jsonify(order.to_dict())

@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """حذف طلب"""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    
    return '', 204

@order_bp.route('/orders/stats', methods=['GET'])
def get_orders_stats():
    """إحصائيات الطلبات"""
    total_orders = Order.query.count()
    pending_orders = Order.query.filter(Order.status == 'pending').count()
    confirmed_orders = Order.query.filter(Order.status == 'confirmed').count()
    delivered_orders = Order.query.filter(Order.status == 'delivered').count()
    
    # إحصائيات اليوم
    today = datetime.now().strftime('%Y-%m-%d')
    today_orders = Order.query.filter(Order.order_date.like(f'{today}%')).all()
    today_revenue = sum(order.total_amount for order in today_orders)
    
    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'delivered_orders': delivered_orders,
        'today_orders': len(today_orders),
        'today_revenue': today_revenue
    })

@order_bp.route('/public/products', methods=['GET'])
def get_public_products():
    """عرض المنتجات للعملاء (واجهة عامة)"""
    products = Product.query.filter(Product.quantity > 0).all()
    
    # تحويل المنتجات إلى تنسيق مناسب للعرض العام
    public_products = []
    for product in products:
        public_product = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'selling_price': product.selling_price,
            'currency': product.currency,
            'quantity': product.quantity,
            'available': product.quantity > 0,
            'image_url': f'/api/products/{product.id}/image' if hasattr(product, 'image_path') else None
        }
        public_products.append(public_product)
    
    return jsonify(public_products)

@order_bp.route('/public/order', methods=['POST'])
def create_public_order():
    """إنشاء طلب من الواجهة العامة"""
    data = request.get_json()
    
    # التحقق من توفر المنتجات
    for item in data['items']:
        product = Product.query.get(item['product_id'])
        if not product or product.quantity < item['quantity']:
            return jsonify({
                'error': f'المنتج غير متوفر بالكمية المطلوبة: {product.name if product else "منتج غير موجود"}'
            }), 400
    
    # إنشاء الطلب
    order = Order(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_address=data.get('customer_address', ''),
        total_amount=data['total_amount'],
        currency=data.get('currency', 'IQD'),
        order_type=data.get('order_type', 'pickup'),
        status='pending',
        notes=data.get('notes', ''),
        order_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        delivery_date=data.get('delivery_date'),
        delivery_fee=data.get('delivery_fee', 0)
    )
    
    db.session.add(order)
    db.session.flush()
    
    # إضافة عناصر الطلب
    for item_data in data['items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # إرسال إشعار
    try:
        order_type_text = 'استلام من المحل' if order.order_type == 'pickup' else 'توصيل'
        
        message = f"""
🛍️ <b>طلب جديد من الموقع</b>

👤 <b>العميل:</b> {order.customer_name}
📱 <b>الهاتف:</b> {order.customer_phone}
🏠 <b>العنوان:</b> {order.customer_address or 'غير محدد'}
💰 <b>المبلغ:</b> {order.total_amount:,.2f} {order.currency}
🚚 <b>نوع الطلب:</b> {order_type_text}
📦 <b>عدد المنتجات:</b> {len(data['items'])}

🌐 <i>طلب من الموقع الإلكتروني</i>
🏪 <i>البدر للإنارة</i>
        """.strip()
        
        telegram_service.send_message(message)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'message': 'تم إرسال طلبك بنجاح! سنتواصل معك قريباً.'
    }), 201

