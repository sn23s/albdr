from flask import Blueprint, request, jsonify
from src.models.warranty import Warranty, WarrantyTemplate, db
from src.models.sale import SaleItem, Sale
from src.models.product import Product
from src.models.customer import Customer
from src.services.telegram_service import TelegramService
from datetime import datetime, timedelta
import json

warranty_bp = Blueprint('warranty', __name__)

@warranty_bp.route('/warranties', methods=['GET'])
def get_warranties():
    """Get all warranties with filtering options"""
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    product_id = request.args.get('product_id', type=int)
    expiring_days = request.args.get('expiring_days', type=int)
    
    query = Warranty.query
    
    if status:
        query = query.filter(Warranty.status == status)
    if customer_id:
        query = query.filter(Warranty.customer_id == customer_id)
    if product_id:
        query = query.filter(Warranty.product_id == product_id)
    
    warranties = query.all()
    
    # Filter by expiring days if specified
    if expiring_days is not None:
        warranties = [w for w in warranties if w.get_days_remaining() <= expiring_days]
    
    return jsonify([warranty.to_dict() for warranty in warranties])

@warranty_bp.route('/warranties/<int:warranty_id>', methods=['GET'])
def get_warranty(warranty_id):
    """Get specific warranty details"""
    warranty = Warranty.query.get_or_404(warranty_id)
    return jsonify(warranty.to_dict())

@warranty_bp.route('/warranties', methods=['POST'])
def create_warranty():
    """Create new warranty"""
    data = request.get_json()
    
    try:
        warranty = Warranty(
            sale_item_id=data['sale_item_id'],
            product_id=data['product_id'],
            customer_id=data['customer_id'],
            warranty_type=data.get('warranty_type', 'manufacturer'),
            warranty_period_months=data.get('warranty_period_months', 12),
            start_date=data['start_date'],
            end_date=data['end_date'],
            is_transferable=data.get('is_transferable', False),
            terms_conditions=data.get('terms_conditions', ''),
            coverage_details=data.get('coverage_details', ''),
            exclusions=data.get('exclusions', '')
        )
        
        db.session.add(warranty)
        db.session.commit()
        
        # Send notification
        try:
            telegram = TelegramService()
            customer = Customer.query.get(warranty.customer_id)
            product = Product.query.get(warranty.product_id)
            
            message = f"🛡️ تم إنشاء ضمان جديد\n\n"
            message += f"العميل: {customer.name if customer else 'غير محدد'}\n"
            message += f"المنتج: {product.name if product else 'غير محدد'}\n"
            message += f"نوع الضمان: {warranty.warranty_type}\n"
            message += f"مدة الضمان: {warranty.warranty_period_months} شهر\n"
            message += f"تاريخ الانتهاء: {warranty.end_date}"
            
            telegram.send_notification(message, 'warranty')
        except Exception as e:
            print(f"Failed to send warranty notification: {e}")
        
        return jsonify(warranty.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@warranty_bp.route('/warranties/<int:warranty_id>', methods=['PUT'])
def update_warranty(warranty_id):
    """Update warranty details"""
    warranty = Warranty.query.get_or_404(warranty_id)
    data = request.get_json()
    
    try:
        warranty.warranty_type = data.get('warranty_type', warranty.warranty_type)
        warranty.warranty_period_months = data.get('warranty_period_months', warranty.warranty_period_months)
        warranty.start_date = data.get('start_date', warranty.start_date)
        warranty.end_date = data.get('end_date', warranty.end_date)
        warranty.status = data.get('status', warranty.status)
        warranty.is_transferable = data.get('is_transferable', warranty.is_transferable)
        warranty.terms_conditions = data.get('terms_conditions', warranty.terms_conditions)
        warranty.coverage_details = data.get('coverage_details', warranty.coverage_details)
        warranty.exclusions = data.get('exclusions', warranty.exclusions)
        warranty.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.session.commit()
        return jsonify(warranty.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@warranty_bp.route('/warranties/<int:warranty_id>/claim', methods=['POST'])
def claim_warranty(warranty_id):
    """Process warranty claim"""
    warranty = Warranty.query.get_or_404(warranty_id)
    data = request.get_json()
    
    try:
        claim_details = data.get('claim_details', '')
        warranty.add_claim(claim_details)
        
        db.session.commit()
        
        # Send notification
        try:
            telegram = TelegramService()
            customer = Customer.query.get(warranty.customer_id)
            product = Product.query.get(warranty.product_id)
            
            message = f"⚠️ مطالبة ضمان جديدة\n\n"
            message += f"العميل: {customer.name if customer else 'غير محدد'}\n"
            message += f"الهاتف: {customer.phone if customer else 'غير محدد'}\n"
            message += f"المنتج: {product.name if product else 'غير محدد'}\n"
            message += f"تفاصيل المطالبة: {claim_details}\n"
            message += f"رقم المطالبة: #{warranty.claim_count}"
            
            telegram.send_notification(message, 'warranty')
        except Exception as e:
            print(f"Failed to send warranty claim notification: {e}")
        
        return jsonify(warranty.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@warranty_bp.route('/warranties/<int:warranty_id>', methods=['DELETE'])
def delete_warranty(warranty_id):
    """Delete warranty"""
    warranty = Warranty.query.get_or_404(warranty_id)
    db.session.delete(warranty)
    db.session.commit()
    
    return '', 204

@warranty_bp.route('/warranties/expiring', methods=['GET'])
def get_expiring_warranties():
    """Get warranties expiring within specified days"""
    days_ahead = request.args.get('days', 30, type=int)
    
    warranties = Warranty.query.filter(Warranty.status == 'active').all()
    expiring_warranties = [w for w in warranties if 0 < w.get_days_remaining() <= days_ahead]
    
    return jsonify([warranty.to_dict() for warranty in expiring_warranties])

@warranty_bp.route('/warranties/expired', methods=['GET'])
def get_expired_warranties():
    """Get expired warranties"""
    warranties = Warranty.query.filter(Warranty.status == 'active').all()
    expired_warranties = [w for w in warranties if w.get_days_remaining() == 0]
    
    return jsonify([warranty.to_dict() for warranty in expired_warranties])

@warranty_bp.route('/warranties/customer/<int:customer_id>', methods=['GET'])
def get_customer_warranties(customer_id):
    """Get all warranties for a specific customer"""
    warranties = Warranty.query.filter(Warranty.customer_id == customer_id).all()
    return jsonify([warranty.to_dict() for warranty in warranties])

@warranty_bp.route('/warranties/product/<int:product_id>', methods=['GET'])
def get_product_warranties(product_id):
    """Get all warranties for a specific product"""
    warranties = Warranty.query.filter(Warranty.product_id == product_id).all()
    return jsonify([warranty.to_dict() for warranty in warranties])

@warranty_bp.route('/warranties/stats', methods=['GET'])
def get_warranty_stats():
    """Get warranty statistics"""
    total_warranties = Warranty.query.count()
    active_warranties = Warranty.query.filter(Warranty.status == 'active').count()
    claimed_warranties = Warranty.query.filter(Warranty.status == 'claimed').count()
    
    # Get expiring warranties
    all_active = Warranty.query.filter(Warranty.status == 'active').all()
    expiring_30_days = len([w for w in all_active if 0 < w.get_days_remaining() <= 30])
    expiring_7_days = len([w for w in all_active if 0 < w.get_days_remaining() <= 7])
    expired = len([w for w in all_active if w.get_days_remaining() == 0])
    
    return jsonify({
        'total_warranties': total_warranties,
        'active_warranties': active_warranties,
        'claimed_warranties': claimed_warranties,
        'expiring_30_days': expiring_30_days,
        'expiring_7_days': expiring_7_days,
        'expired': expired
    })

@warranty_bp.route('/warranties/check-notifications', methods=['POST'])
def check_warranty_notifications():
    """Check and send warranty expiration notifications"""
    notifications_sent = 0
    
    try:
        telegram = TelegramService()
        active_warranties = Warranty.query.filter(Warranty.status == 'active').all()
        
        for warranty in active_warranties:
            customer = Customer.query.get(warranty.customer_id)
            product = Product.query.get(warranty.product_id)
            
            # Check for 30-day notification
            if warranty.should_send_notification('30_days'):
                message = f"⏰ تنبيه انتهاء ضمان (30 يوم)\n\n"
                message += f"العميل: {customer.name if customer else 'غير محدد'}\n"
                message += f"الهاتف: {customer.phone if customer else 'غير محدد'}\n"
                message += f"المنتج: {product.name if product else 'غير محدد'}\n"
                message += f"تاريخ انتهاء الضمان: {warranty.end_date}\n"
                message += f"الأيام المتبقية: {warranty.get_days_remaining()}"
                
                if telegram.send_notification(message, 'warranty'):
                    warranty.mark_notification_sent('30_days')
                    notifications_sent += 1
            
            # Check for 7-day notification
            elif warranty.should_send_notification('7_days'):
                message = f"🚨 تنبيه انتهاء ضمان (7 أيام)\n\n"
                message += f"العميل: {customer.name if customer else 'غير محدد'}\n"
                message += f"الهاتف: {customer.phone if customer else 'غير محدد'}\n"
                message += f"المنتج: {product.name if product else 'غير محدد'}\n"
                message += f"تاريخ انتهاء الضمان: {warranty.end_date}\n"
                message += f"الأيام المتبقية: {warranty.get_days_remaining()}"
                
                if telegram.send_notification(message, 'warranty'):
                    warranty.mark_notification_sent('7_days')
                    notifications_sent += 1
            
            # Check for expiration notification
            elif warranty.should_send_notification('expired'):
                message = f"❌ انتهى الضمان\n\n"
                message += f"العميل: {customer.name if customer else 'غير محدد'}\n"
                message += f"الهاتف: {customer.phone if customer else 'غير محدد'}\n"
                message += f"المنتج: {product.name if product else 'غير محدد'}\n"
                message += f"تاريخ انتهاء الضمان: {warranty.end_date}"
                
                if telegram.send_notification(message, 'warranty'):
                    warranty.mark_notification_sent('expired')
                    warranty.status = 'expired'
                    notifications_sent += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'تم إرسال {notifications_sent} إشعار',
            'notifications_sent': notifications_sent
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Warranty Templates Routes
@warranty_bp.route('/warranty-templates', methods=['GET'])
def get_warranty_templates():
    """Get all warranty templates"""
    templates = WarrantyTemplate.query.filter(WarrantyTemplate.is_active == True).all()
    return jsonify([template.to_dict() for template in templates])

@warranty_bp.route('/warranty-templates', methods=['POST'])
def create_warranty_template():
    """Create new warranty template"""
    data = request.get_json()
    
    try:
        template = WarrantyTemplate(
            name=data['name'],
            warranty_type=data['warranty_type'],
            period_months=data['period_months'],
            terms_conditions=data.get('terms_conditions', ''),
            coverage_details=data.get('coverage_details', ''),
            exclusions=data.get('exclusions', ''),
            is_transferable=data.get('is_transferable', False)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@warranty_bp.route('/warranty-templates/<int:template_id>', methods=['PUT'])
def update_warranty_template(template_id):
    """Update warranty template"""
    template = WarrantyTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    try:
        template.name = data.get('name', template.name)
        template.warranty_type = data.get('warranty_type', template.warranty_type)
        template.period_months = data.get('period_months', template.period_months)
        template.terms_conditions = data.get('terms_conditions', template.terms_conditions)
        template.coverage_details = data.get('coverage_details', template.coverage_details)
        template.exclusions = data.get('exclusions', template.exclusions)
        template.is_transferable = data.get('is_transferable', template.is_transferable)
        template.is_active = data.get('is_active', template.is_active)
        
        db.session.commit()
        return jsonify(template.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@warranty_bp.route('/warranty-templates/<int:template_id>', methods=['DELETE'])
def delete_warranty_template(template_id):
    """Delete warranty template"""
    template = WarrantyTemplate.query.get_or_404(template_id)
    template.is_active = False
    db.session.commit()
    
    return '', 204

