from flask import Blueprint, request, jsonify
from src.models.expense import Expense, db
from src.services.telegram_service import telegram_service
from datetime import datetime

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([expense.to_dict() for expense in expenses])

@expense_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    return jsonify(expense.to_dict())

@expense_bp.route('/expenses', methods=['POST'])
def create_expense():
    data = request.get_json()
    
    expense = Expense(
        description=data['description'],
        amount=data['amount'],
        currency=data['currency'],
        expense_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    db.session.add(expense)
    db.session.commit()
    
    # إرسال إشعار التليجرام للمصروف الجديد
    try:
        expense_notification_data = {
            'description': expense.description,
            'amount': expense.amount,
            'currency': expense.currency,
            'category': data.get('category', 'عام')  # يمكن إضافة حقل الفئة لاحقاً
        }
        telegram_service.send_expense_notification(expense_notification_data)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    
    return jsonify(expense.to_dict()), 201

@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    data = request.get_json()
    
    expense.description = data.get('description', expense.description)
    expense.amount = data.get('amount', expense.amount)
    expense.currency = data.get('currency', expense.currency)
    
    db.session.commit()
    
    return jsonify(expense.to_dict())

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    
    return '', 204

@expense_bp.route('/expenses/report', methods=['GET'])
def expenses_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Expense.query
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    
    expenses = query.all()
    
    total_expenses = sum(expense.amount for expense in expenses)
    
    return jsonify({
        'total_expenses': total_expenses,
        'expenses': [expense.to_dict() for expense in expenses]
    })

@expense_bp.route('/expenses/daily-summary', methods=['POST'])
def send_expenses_summary():
    """إرسال ملخص يومي للمصروفات"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # حساب مصروفات اليوم
        today_expenses = Expense.query.filter(Expense.expense_date.like(f'{today}%')).all()
        total_expenses = sum(expense.amount for expense in today_expenses)
        expenses_count = len(today_expenses)
        
        if expenses_count > 0:
            message = f"""
📊 <b>ملخص مصروفات اليوم</b>

💸 <b>إجمالي المصروفات:</b> {total_expenses:,.2f} IQD
📝 <b>عدد المصروفات:</b> {expenses_count}
📅 <b>التاريخ:</b> {today}

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            success = telegram_service.send_message(message)
            
            if success:
                return jsonify({'success': True, 'message': 'تم إرسال ملخص المصروفات بنجاح'})
            else:
                return jsonify({'success': False, 'message': 'فشل في إرسال ملخص المصروفات'}), 400
        else:
            return jsonify({'success': True, 'message': 'لا توجد مصروفات اليوم'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

