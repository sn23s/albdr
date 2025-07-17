from flask import Blueprint, request, jsonify
from src.models.sale import Sale, SaleItem, db
from src.models.product import Product
from src.models.customer import Customer
from src.models.warranty import Warranty
from src.services.telegram_service import telegram_service
from datetime import datetime, timedelta

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/sales', methods=['GET'])
def get_sales():
    sales = Sale.query.all()
    return jsonify([sale.to_dict() for sale in sales])

@sale_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    sale_data = sale.to_dict()
    sale_data['items'] = [item.to_dict() for item in sale.items]
    return jsonify(sale_data)

@sale_bp.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    
    sale = Sale(
        customer_id=data.get('customer_id'),
        total_amount=data['total_amount'],
        currency=data['currency'],
        sale_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    db.session.add(sale)
    db.session.flush()  # Get the sale ID
    
    # Add sale items
    items_for_notification = []
    for item_data in data['items']:
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(sale_item)
        
        # Update product quantity
        product = Product.query.get(item_data['product_id'])
        if product:
            product.quantity -= item_data['quantity']
            
            # إضافة معلومات المنتج للإشعار
            items_for_notification.append({
                'name': product.name,
                'quantity': item_data['quantity'],
                'price': item_data['price']
            })
            
            # تحقق من المخزون القليل وإرسال تنبيه
            if product.quantity <= 5:  # يمكن تعديل هذا الرقم
                telegram_service.send_low_stock_alert({
                    'name': product.name,
                    'quantity': product.quantity,
                    'min_quantity': 5
                })
        
        # Create warranty if specified
        if 'warranty_months' in item_data and item_data['warranty_months'] > 0:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=item_data['warranty_months'] * 30)
            
            warranty = Warranty(
                sale_item_id=sale_item.id,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            db.session.add(warranty)
    
    db.session.commit()
    
    # إرسال إشعار التليجرام للمبيعة الجديدة
    try:
        customer_name = 'زبون عادي'
        if sale.customer_id:
            customer = Customer.query.get(sale.customer_id)
            if customer:
                customer_name = customer.name
        
        sale_notification_data = {
            'customer_name': customer_name,
            'total_amount': sale.total_amount,
            'currency': sale.currency,
            'items': items_for_notification
        }
        
        telegram_service.send_sale_notification(sale_notification_data)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    return jsonify(sale.to_dict()), 201

@sale_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    # Restore product quantities
    for item in sale.items:
        product = Product.query.get(item.product_id)
        if product:
            product.quantity += item.quantity
    
    db.session.delete(sale)
    db.session.commit()
    
    return '', 204

@sale_bp.route('/sales/report', methods=['GET'])
def sales_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    sales = query.all()
    
    total_revenue = sum(sale.total_amount for sale in sales)
    total_sales = len(sales)
    
    return jsonify({
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'sales': [sale.to_dict() for sale in sales]
    })

@sale_bp.route('/sales/daily-summary', methods=['POST'])
def send_daily_summary():
    """إرسال ملخص يومي للمبيعات"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # حساب مبيعات اليوم
        today_sales = Sale.query.filter(Sale.sale_date.like(f'{today}%')).all()
        total_sales = sum(sale.total_amount for sale in today_sales)
        sales_count = len(today_sales)
        
        # يمكن إضافة حساب المصروفات هنا لاحقاً
        total_expenses = 0
        
        summary_data = {
            'total_sales': total_sales,
            'sales_count': sales_count,
            'total_expenses': total_expenses
        }
        
        success = telegram_service.send_daily_summary(summary_data)
        
        if success:
            return jsonify({'success': True, 'message': 'تم إرسال الملخص اليومي بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في إرسال الملخص اليومي'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

