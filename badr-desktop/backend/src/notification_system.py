"""
نظام الإشعارات لبرنامج البدر للإنارة
يدعم إرسال إشعارات عبر Telegram و WhatsApp
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
import sqlite3
import asyncio
import aiohttp
from urllib.parse import quote

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSystem:
    """نظام الإشعارات"""
    
    def __init__(self, db_path: str = "notifications.sqlite"):
        """
        تهيئة نظام الإشعارات
        
        Args:
            db_path: مسار قاعدة البيانات
        """
        self.db_path = db_path
        self.init_database()
        
        # إعدادات Telegram
        self.telegram_bot_token = None
        self.telegram_chat_ids = []
        
        # إعدادات WhatsApp
        self.whatsapp_api_url = None
        self.whatsapp_api_key = None
        self.whatsapp_phone_numbers = []
        
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول إعدادات الإشعارات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, setting_key)
                )
            ''')
            
            # جدول المستقبلين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    recipient_name TEXT,
                    notification_types TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, recipient_id)
                )
            ''')
            
            # جدول سجل الإشعارات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول قوالب الإشعارات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    template_content TEXT NOT NULL,
                    variables TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # إنشاء القوالب الافتراضية
            self.create_default_templates()
            
            logger.info("تم إنشاء جداول قاعدة بيانات الإشعارات")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {str(e)}")
            raise
    
    def create_default_templates(self):
        """إنشاء قوالب الإشعارات الافتراضية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            default_templates = [
                {
                    'name': 'new_sale',
                    'content': '''🛒 عملية بيع جديدة
📋 رقم الفاتورة: {invoice_number}
👤 الزبون: {customer_name}
💰 المبلغ الكلي: {total_amount} دينار
📅 التاريخ: {date}
⏰ الوقت: {time}
👨‍💼 البائع: {seller_name}''',
                    'variables': 'invoice_number,customer_name,total_amount,date,time,seller_name',
                    'description': 'إشعار عملية بيع جديدة'
                },
                {
                    'name': 'new_product',
                    'content': '''📦 منتج جديد
🏷️ اسم المنتج: {product_name}
🔢 الكود: {product_code}
💰 السعر: {price} دينار
📊 الكمية: {quantity}
👤 أضيف بواسطة: {added_by}
📅 التاريخ: {date}''',
                    'variables': 'product_name,product_code,price,quantity,added_by,date',
                    'description': 'إشعار إضافة منتج جديد'
                },
                {
                    'name': 'low_stock',
                    'content': '''⚠️ تنبيه مخزون منخفض
🏷️ المنتج: {product_name}
🔢 الكود: {product_code}
📊 الكمية المتبقية: {remaining_quantity}
📊 الحد الأدنى: {minimum_stock}
⚡ يرجى إعادة التزويد''',
                    'variables': 'product_name,product_code,remaining_quantity,minimum_stock',
                    'description': 'تنبيه مخزون منخفض'
                },
                {
                    'name': 'payment_received',
                    'content': '''💰 دفعة مستلمة
🏢 الشركة: {company_name}
📋 رقم الفاتورة: {invoice_number}
💵 المبلغ المدفوع: {payment_amount} دينار
💳 طريقة الدفع: {payment_method}
📅 التاريخ: {date}
👤 استلمها: {received_by}''',
                    'variables': 'company_name,invoice_number,payment_amount,payment_method,date,received_by',
                    'description': 'إشعار استلام دفعة'
                },
                {
                    'name': 'warranty_expiring',
                    'content': '''⏰ تنبيه انتهاء ضمان
👤 الزبون: {customer_name}
🏷️ المنتج: {product_name}
📋 رقم الفاتورة: {invoice_number}
📅 تاريخ انتهاء الضمان: {warranty_end_date}
📞 هاتف الزبون: {customer_phone}''',
                    'variables': 'customer_name,product_name,invoice_number,warranty_end_date,customer_phone',
                    'description': 'تنبيه انتهاء ضمان'
                }
            ]
            
            for template in default_templates:
                cursor.execute('''
                    INSERT OR IGNORE INTO notification_templates 
                    (template_name, template_content, variables, description)
                    VALUES (?, ?, ?, ?)
                ''', (template['name'], template['content'], template['variables'], template['description']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء القوالب الافتراضية: {str(e)}")
    
    def configure_telegram(self, bot_token: str, chat_ids: List[str]):
        """
        تكوين إعدادات Telegram
        
        Args:
            bot_token: رمز البوت
            chat_ids: قائمة معرفات المحادثات
        """
        try:
            self.telegram_bot_token = bot_token
            self.telegram_chat_ids = chat_ids
            
            # حفظ الإعدادات في قاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings (platform, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', ('telegram', 'bot_token', bot_token))
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings (platform, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', ('telegram', 'chat_ids', json.dumps(chat_ids)))
            
            # إضافة المستقبلين
            for chat_id in chat_ids:
                cursor.execute('''
                    INSERT OR REPLACE INTO notification_recipients 
                    (platform, recipient_id, notification_types)
                    VALUES (?, ?, ?)
                ''', ('telegram', chat_id, 'all'))
            
            conn.commit()
            conn.close()
            
            logger.info("تم تكوين إعدادات Telegram")
            
        except Exception as e:
            logger.error(f"خطأ في تكوين Telegram: {str(e)}")
            raise
    
    def configure_whatsapp(self, api_url: str, api_key: str, phone_numbers: List[str]):
        """
        تكوين إعدادات WhatsApp
        
        Args:
            api_url: رابط API
            api_key: مفتاح API
            phone_numbers: قائمة أرقام الهواتف
        """
        try:
            self.whatsapp_api_url = api_url
            self.whatsapp_api_key = api_key
            self.whatsapp_phone_numbers = phone_numbers
            
            # حفظ الإعدادات في قاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings (platform, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', ('whatsapp', 'api_url', api_url))
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings (platform, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', ('whatsapp', 'api_key', api_key))
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings (platform, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', ('whatsapp', 'phone_numbers', json.dumps(phone_numbers)))
            
            # إضافة المستقبلين
            for phone in phone_numbers:
                cursor.execute('''
                    INSERT OR REPLACE INTO notification_recipients 
                    (platform, recipient_id, notification_types)
                    VALUES (?, ?, ?)
                ''', ('whatsapp', phone, 'all'))
            
            conn.commit()
            conn.close()
            
            logger.info("تم تكوين إعدادات WhatsApp")
            
        except Exception as e:
            logger.error(f"خطأ في تكوين WhatsApp: {str(e)}")
            raise
    
    def load_settings(self):
        """تحميل الإعدادات من قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # تحميل إعدادات Telegram
            cursor.execute('''
                SELECT setting_key, setting_value 
                FROM notification_settings 
                WHERE platform = 'telegram' AND is_active = 1
            ''')
            
            telegram_settings = dict(cursor.fetchall())
            
            if 'bot_token' in telegram_settings:
                self.telegram_bot_token = telegram_settings['bot_token']
            
            if 'chat_ids' in telegram_settings:
                self.telegram_chat_ids = json.loads(telegram_settings['chat_ids'])
            
            # تحميل إعدادات WhatsApp
            cursor.execute('''
                SELECT setting_key, setting_value 
                FROM notification_settings 
                WHERE platform = 'whatsapp' AND is_active = 1
            ''')
            
            whatsapp_settings = dict(cursor.fetchall())
            
            if 'api_url' in whatsapp_settings:
                self.whatsapp_api_url = whatsapp_settings['api_url']
            
            if 'api_key' in whatsapp_settings:
                self.whatsapp_api_key = whatsapp_settings['api_key']
            
            if 'phone_numbers' in whatsapp_settings:
                self.whatsapp_phone_numbers = json.loads(whatsapp_settings['phone_numbers'])
            
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الإعدادات: {str(e)}")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """
        الحصول على قالب إشعار
        
        Args:
            template_name: اسم القالب
            
        Returns:
            محتوى القالب أو None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_content FROM notification_templates 
                WHERE template_name = ?
            ''', (template_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على القالب: {str(e)}")
            return None
    
    def format_message(self, template_name: str, variables: Dict) -> str:
        """
        تنسيق رسالة باستخدام القالب والمتغيرات
        
        Args:
            template_name: اسم القالب
            variables: المتغيرات
            
        Returns:
            الرسالة المنسقة
        """
        try:
            template = self.get_template(template_name)
            if not template:
                return f"قالب غير موجود: {template_name}"
            
            # استبدال المتغيرات
            formatted_message = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                formatted_message = formatted_message.replace(placeholder, str(value))
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق الرسالة: {str(e)}")
            return f"خطأ في تنسيق الرسالة: {str(e)}"
    
    def send_telegram_message(self, message: str, chat_id: str = None) -> bool:
        """
        إرسال رسالة عبر Telegram
        
        Args:
            message: الرسالة
            chat_id: معرف المحادثة (اختياري)
            
        Returns:
            True إذا تم الإرسال بنجاح، False خلاف ذلك
        """
        try:
            if not self.telegram_bot_token:
                logger.error("رمز بوت Telegram غير مكون")
                return False
            
            chat_ids = [chat_id] if chat_id else self.telegram_chat_ids
            
            if not chat_ids:
                logger.error("لا توجد معرفات محادثة Telegram")
                return False
            
            success_count = 0
            
            for cid in chat_ids:
                try:
                    url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                    
                    payload = {
                        'chat_id': cid,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                    
                    response = requests.post(url, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        success_count += 1
                        self.log_notification('telegram', cid, 'message', message, 'sent')
                        logger.info(f"تم إرسال رسالة Telegram إلى {cid}")
                    else:
                        error_msg = f"خطأ HTTP {response.status_code}: {response.text}"
                        self.log_notification('telegram', cid, 'message', message, 'failed', error_msg)
                        logger.error(f"فشل إرسال رسالة Telegram إلى {cid}: {error_msg}")
                
                except Exception as e:
                    error_msg = str(e)
                    self.log_notification('telegram', cid, 'message', message, 'failed', error_msg)
                    logger.error(f"خطأ في إرسال رسالة Telegram إلى {cid}: {error_msg}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة Telegram: {str(e)}")
            return False
    
    def send_whatsapp_message(self, message: str, phone_number: str = None) -> bool:
        """
        إرسال رسالة عبر WhatsApp
        
        Args:
            message: الرسالة
            phone_number: رقم الهاتف (اختياري)
            
        Returns:
            True إذا تم الإرسال بنجاح، False خلاف ذلك
        """
        try:
            if not self.whatsapp_api_url or not self.whatsapp_api_key:
                logger.error("إعدادات WhatsApp API غير مكونة")
                return False
            
            phone_numbers = [phone_number] if phone_number else self.whatsapp_phone_numbers
            
            if not phone_numbers:
                logger.error("لا توجد أرقام هواتف WhatsApp")
                return False
            
            success_count = 0
            
            for phone in phone_numbers:
                try:
                    # تنسيق رقم الهاتف (إزالة الرموز الخاصة)
                    clean_phone = ''.join(filter(str.isdigit, phone))
                    
                    # إعداد الطلب (يعتمد على نوع API المستخدم)
                    headers = {
                        'Authorization': f'Bearer {self.whatsapp_api_key}',
                        'Content-Type': 'application/json'
                    }
                    
                    payload = {
                        'phone': clean_phone,
                        'message': message
                    }
                    
                    response = requests.post(self.whatsapp_api_url, 
                                           headers=headers, 
                                           json=payload, 
                                           timeout=10)
                    
                    if response.status_code == 200:
                        success_count += 1
                        self.log_notification('whatsapp', phone, 'message', message, 'sent')
                        logger.info(f"تم إرسال رسالة WhatsApp إلى {phone}")
                    else:
                        error_msg = f"خطأ HTTP {response.status_code}: {response.text}"
                        self.log_notification('whatsapp', phone, 'message', message, 'failed', error_msg)
                        logger.error(f"فشل إرسال رسالة WhatsApp إلى {phone}: {error_msg}")
                
                except Exception as e:
                    error_msg = str(e)
                    self.log_notification('whatsapp', phone, 'message', message, 'failed', error_msg)
                    logger.error(f"خطأ في إرسال رسالة WhatsApp إلى {phone}: {error_msg}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة WhatsApp: {str(e)}")
            return False
    
    def send_notification(self, template_name: str, variables: Dict, 
                         platforms: List[str] = None) -> Dict:
        """
        إرسال إشعار عبر منصات متعددة
        
        Args:
            template_name: اسم القالب
            variables: المتغيرات
            platforms: قائمة المنصات (telegram, whatsapp)
            
        Returns:
            نتائج الإرسال
        """
        try:
            # تحميل الإعدادات
            self.load_settings()
            
            # تنسيق الرسالة
            message = self.format_message(template_name, variables)
            
            # تحديد المنصات
            if not platforms:
                platforms = ['telegram', 'whatsapp']
            
            results = {}
            
            # إرسال عبر Telegram
            if 'telegram' in platforms:
                results['telegram'] = self.send_telegram_message(message)
            
            # إرسال عبر WhatsApp
            if 'whatsapp' in platforms:
                results['whatsapp'] = self.send_whatsapp_message(message)
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار: {str(e)}")
            return {'error': str(e)}
    
    def log_notification(self, platform: str, recipient_id: str, 
                        notification_type: str, message: str, 
                        status: str, error_message: str = None):
        """
        تسجيل الإشعار في السجل
        
        Args:
            platform: المنصة
            recipient_id: معرف المستقبل
            notification_type: نوع الإشعار
            message: الرسالة
            status: الحالة
            error_message: رسالة الخطأ (اختياري)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sent_at = datetime.now().isoformat() if status == 'sent' else None
            
            cursor.execute('''
                INSERT INTO notification_log 
                (platform, recipient_id, notification_type, message, status, error_message, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (platform, recipient_id, notification_type, message, status, error_message, sent_at))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الإشعار: {str(e)}")
    
    def get_notification_history(self, limit: int = 100) -> List[Dict]:
        """
        الحصول على تاريخ الإشعارات
        
        Args:
            limit: عدد السجلات
            
        Returns:
            قائمة بسجلات الإشعارات
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM notification_log 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            notifications = [dict(zip(columns, row)) for row in rows]
            
            return notifications
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على تاريخ الإشعارات: {str(e)}")
            return []


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء نظام الإشعارات
    notification_system = NotificationSystem()
    
    try:
        # تكوين Telegram (يجب استبدال القيم بالقيم الحقيقية)
        # notification_system.configure_telegram(
        #     bot_token="YOUR_BOT_TOKEN",
        #     chat_ids=["CHAT_ID_1", "CHAT_ID_2"]
        # )
        
        # تكوين WhatsApp (يجب استبدال القيم بالقيم الحقيقية)
        # notification_system.configure_whatsapp(
        #     api_url="https://api.whatsapp.com/send",
        #     api_key="YOUR_API_KEY",
        #     phone_numbers=["+964770123456", "+964750987654"]
        # )
        
        # إرسال إشعار عملية بيع جديدة
        sale_variables = {
            'invoice_number': 'INV-2025-001',
            'customer_name': 'علي حسن',
            'total_amount': '150,000',
            'date': '2025-01-09',
            'time': '14:30',
            'seller_name': 'أحمد محمد'
        }
        
        # results = notification_system.send_notification('new_sale', sale_variables)
        # print(f"نتائج الإرسال: {results}")
        
        print("نظام الإشعارات جاهز للاستخدام")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

