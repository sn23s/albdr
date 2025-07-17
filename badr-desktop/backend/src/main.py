import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.models.product import Product
from src.models.customer import Customer
from src.models.sale import Sale, SaleItem
from src.models.expense import Expense
from src.models.warranty import Warranty
from src.models.order import Order, OrderItem
from src.routes.user import user_bp
from src.routes.product import product_bp
from src.routes.customer import customer_bp
from src.routes.sale import sale_bp
from src.routes.expense import expense_bp
from src.routes.warranty import warranty_bp
from src.routes.order import order_bp
from src.services.telegram_service import telegram_service

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# إعدادات التليجرام (يمكن تعديلها من متغيرات البيئة)
# لتفعيل التليجرام، قم بتعديل هذه القيم:
# os.environ['TELEGRAM_BOT_TOKEN'] = 'YOUR_BOT_TOKEN_HERE'
# os.environ['TELEGRAM_CHAT_ID'] = 'YOUR_CHAT_ID_HERE'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(sale_bp, url_prefix='/api')
app.register_blueprint(expense_bp, url_prefix='/api')
app.register_blueprint(warranty_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')

# إضافة route لإعدادات التليجرام
@app.route('/api/telegram/settings', methods=['GET', 'POST'])
def telegram_settings():
    if request.method == 'GET':
        return jsonify({
            'enabled': telegram_service.enabled,
            'bot_token_configured': bool(telegram_service.bot_token),
            'chat_id_configured': bool(telegram_service.chat_id)
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        bot_token = data.get('bot_token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        
        if bot_token:
            os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
            telegram_service.bot_token = bot_token
        
        if chat_id:
            os.environ['TELEGRAM_CHAT_ID'] = chat_id
            telegram_service.chat_id = chat_id
        
        telegram_service.enabled = bool(telegram_service.bot_token and telegram_service.chat_id)
        
        return jsonify({
            'success': True,
            'enabled': telegram_service.enabled,
            'message': 'تم حفظ إعدادات التليجرام بنجاح'
        })

@app.route('/api/telegram/test', methods=['POST'])
def test_telegram():
    """اختبار إرسال رسالة تجريبية للتليجرام"""
    if not telegram_service.enabled:
        return jsonify({
            'success': False,
            'message': 'التليجرام غير مفعل. يرجى إعداد البوت أولاً.'
        }), 400
    
    test_message = """
🧪 <b>رسالة اختبار</b>

✅ تم تكوين بوت التليجرام بنجاح!
📱 النظام جاهز لإرسال الإشعارات

🏪 <i>البدر للإنارة</i>
    """.strip()
    
    success = telegram_service.send_message(test_message)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'تم إرسال رسالة الاختبار بنجاح!'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'فشل في إرسال رسالة الاختبار. تحقق من إعدادات البوت.'
        }), 400

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
