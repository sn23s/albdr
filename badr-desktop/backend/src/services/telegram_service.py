import requests
import json
from datetime import datetime
import os

class TelegramService:
    def __init__(self):
        # يمكن تعديل هذه القيم من ملف الإعدادات أو متغيرات البيئة
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.enabled = bool(self.bot_token and self.chat_id)
        
    def send_message(self, message):
        """إرسال رسالة إلى التليجرام"""
        if not self.enabled:
            print(f"Telegram not configured. Message: {message}")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_sale_notification(self, sale_data):
        """إرسال إشعار عملية بيع"""
        try:
            customer_name = sale_data.get('customer_name', 'زبون عادي')
            total_amount = sale_data.get('total_amount', 0)
            currency = sale_data.get('currency', 'IQD')
            sale_date = datetime.now().strftime('%Y/%m/%d %H:%M')
            items_count = len(sale_data.get('items', []))
            
            message = f"""
🛒 <b>عملية بيع جديدة</b>

👤 <b>الزبون:</b> {customer_name}
💰 <b>المبلغ:</b> {total_amount:,.2f} {currency}
📦 <b>عدد المنتجات:</b> {items_count}
📅 <b>التاريخ:</b> {sale_date}

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending sale notification: {e}")
            return False
    
    def send_product_notification(self, product_data, action='add'):
        """إرسال إشعار إضافة/تعديل منتج"""
        try:
            product_name = product_data.get('name', 'منتج غير محدد')
            quantity = product_data.get('quantity', 0)
            price = product_data.get('selling_price', 0)
            currency = product_data.get('currency', 'IQD')
            date_time = datetime.now().strftime('%Y/%m/%d %H:%M')
            
            action_text = {
                'add': '➕ إضافة منتج جديد',
                'update': '✏️ تعديل منتج',
                'delete': '🗑️ حذف منتج'
            }.get(action, '📦 عملية منتج')
            
            message = f"""
{action_text}

📦 <b>اسم المنتج:</b> {product_name}
📊 <b>الكمية:</b> {quantity}
💵 <b>سعر البيع:</b> {price:,.2f} {currency}
📅 <b>التاريخ:</b> {date_time}

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending product notification: {e}")
            return False
    
    def send_expense_notification(self, expense_data):
        """إرسال إشعار مصروف جديد"""
        try:
            description = expense_data.get('description', 'مصروف غير محدد')
            amount = expense_data.get('amount', 0)
            currency = expense_data.get('currency', 'IQD')
            category = expense_data.get('category', 'عام')
            date_time = datetime.now().strftime('%Y/%m/%d %H:%M')
            
            message = f"""
💸 <b>مصروف جديد</b>

📝 <b>الوصف:</b> {description}
🏷️ <b>الفئة:</b> {category}
💰 <b>المبلغ:</b> {amount:,.2f} {currency}
📅 <b>التاريخ:</b> {date_time}

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending expense notification: {e}")
            return False
    
    def send_low_stock_alert(self, product_data):
        """إرسال تنبيه مخزون قليل"""
        try:
            product_name = product_data.get('name', 'منتج غير محدد')
            current_quantity = product_data.get('quantity', 0)
            min_quantity = product_data.get('min_quantity', 5)
            
            message = f"""
⚠️ <b>تنبيه: مخزون قليل</b>

📦 <b>المنتج:</b> {product_name}
📊 <b>الكمية الحالية:</b> {current_quantity}
📉 <b>الحد الأدنى:</b> {min_quantity}

🔄 <i>يُنصح بإعادة التخزين</i>

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending low stock alert: {e}")
            return False
    
    def send_warranty_expiry_alert(self, warranty_data):
        """إرسال تنبيه انتهاء ضمان"""
        try:
            customer_name = warranty_data.get('customer_name', 'زبون غير محدد')
            product_name = warranty_data.get('product_name', 'منتج غير محدد')
            expiry_date = warranty_data.get('expiry_date', '')
            days_remaining = warranty_data.get('days_remaining', 0)
            
            message = f"""
⏰ <b>تنبيه: انتهاء ضمان</b>

👤 <b>الزبون:</b> {customer_name}
📦 <b>المنتج:</b> {product_name}
📅 <b>تاريخ انتهاء الضمان:</b> {expiry_date}
⏳ <b>الأيام المتبقية:</b> {days_remaining} يوم

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending warranty expiry alert: {e}")
            return False
    
    def send_daily_summary(self, summary_data):
        """إرسال ملخص يومي"""
        try:
            date = datetime.now().strftime('%Y/%m/%d')
            total_sales = summary_data.get('total_sales', 0)
            sales_count = summary_data.get('sales_count', 0)
            total_expenses = summary_data.get('total_expenses', 0)
            net_profit = total_sales - total_expenses
            
            message = f"""
📊 <b>الملخص اليومي - {date}</b>

💰 <b>إجمالي المبيعات:</b> {total_sales:,.2f} IQD
🛒 <b>عدد المبيعات:</b> {sales_count}
💸 <b>إجمالي المصروفات:</b> {total_expenses:,.2f} IQD
📈 <b>صافي الربح:</b> {net_profit:,.2f} IQD

🏪 <i>البدر للإنارة</i>
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Error sending daily summary: {e}")
            return False

# إنشاء مثيل عام للخدمة
telegram_service = TelegramService()

