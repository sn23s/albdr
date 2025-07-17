"""
نظام تسديد الديون للشركات لبرنامج البدر للإنارة
يدعم إدارة ديون الشركات وتتبع المدفوعات
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
from decimal import Decimal

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebtManagementSystem:
    """نظام إدارة ديون الشركات"""
    
    def __init__(self, db_path: str = "debts.sqlite"):
        """
        تهيئة نظام إدارة الديون
        
        Args:
            db_path: مسار قاعدة البيانات
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول الشركات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    tax_number TEXT,
                    credit_limit DECIMAL(15,2) DEFAULT 0,
                    payment_terms_days INTEGER DEFAULT 30,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الديون
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    invoice_number TEXT NOT NULL,
                    invoice_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    total_amount DECIMAL(15,2) NOT NULL,
                    paid_amount DECIMAL(15,2) DEFAULT 0,
                    remaining_amount DECIMAL(15,2) NOT NULL,
                    status TEXT DEFAULT 'pending',
                    description TEXT,
                    products_json TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            ''')
            
            # جدول المدفوعات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debt_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debt_id INTEGER NOT NULL,
                    payment_date DATE NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    payment_method TEXT DEFAULT 'cash',
                    reference_number TEXT,
                    notes TEXT,
                    received_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (debt_id) REFERENCES company_debts (id)
                )
            ''')
            
            # جدول تذكيرات الدفع
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debt_id INTEGER NOT NULL,
                    reminder_date DATE NOT NULL,
                    reminder_type TEXT DEFAULT 'email',
                    message TEXT,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (debt_id) REFERENCES company_debts (id)
                )
            ''')
            
            # جدول سجل التفاعلات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debt_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debt_id INTEGER NOT NULL,
                    interaction_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (debt_id) REFERENCES company_debts (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("تم إنشاء جداول قاعدة بيانات الديون")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {str(e)}")
            raise
    
    def add_company(self, company_data: Dict) -> int:
        """
        إضافة شركة جديدة
        
        Args:
            company_data: بيانات الشركة
            
        Returns:
            معرف الشركة المُضافة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO companies (
                    name, contact_person, phone, email, address, tax_number,
                    credit_limit, payment_terms_days, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_data['name'],
                company_data.get('contact_person', ''),
                company_data.get('phone', ''),
                company_data.get('email', ''),
                company_data.get('address', ''),
                company_data.get('tax_number', ''),
                company_data.get('credit_limit', 0),
                company_data.get('payment_terms_days', 30),
                company_data.get('notes', '')
            ))
            
            company_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إضافة شركة جديدة: {company_data['name']}")
            return company_id
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الشركة: {str(e)}")
            raise
    
    def create_debt(self, debt_data: Dict) -> int:
        """
        إنشاء دين جديد
        
        Args:
            debt_data: بيانات الدين
            
        Returns:
            معرف الدين المُنشأ
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # حساب تاريخ الاستحقاق
            invoice_date = datetime.strptime(debt_data['invoice_date'], '%Y-%m-%d')
            
            # الحصول على شروط الدفع للشركة
            cursor.execute('SELECT payment_terms_days FROM companies WHERE id = ?', (debt_data['company_id'],))
            company_result = cursor.fetchone()
            payment_terms = company_result[0] if company_result else 30
            
            due_date = invoice_date + timedelta(days=payment_terms)
            
            # تحويل قائمة المنتجات إلى JSON
            products_json = json.dumps(debt_data.get('products', []), ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO company_debts (
                    company_id, invoice_number, invoice_date, due_date,
                    total_amount, remaining_amount, description, products_json, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                debt_data['company_id'],
                debt_data['invoice_number'],
                debt_data['invoice_date'],
                due_date.strftime('%Y-%m-%d'),
                debt_data['total_amount'],
                debt_data['total_amount'],  # المبلغ المتبقي = المبلغ الكلي في البداية
                debt_data.get('description', ''),
                products_json,
                debt_data.get('created_by')
            ))
            
            debt_id = cursor.lastrowid
            
            # تسجيل التفاعل
            self.log_debt_interaction(debt_id, 'debt_created', 'تم إنشاء دين جديد', debt_data.get('created_by'))
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء دين جديد: {debt_data['invoice_number']}")
            return debt_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الدين: {str(e)}")
            raise
    
    def record_payment(self, payment_data: Dict) -> int:
        """
        تسجيل دفعة
        
        Args:
            payment_data: بيانات الدفعة
            
        Returns:
            معرف الدفعة المُسجلة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود الدين
            cursor.execute('SELECT remaining_amount FROM company_debts WHERE id = ?', (payment_data['debt_id'],))
            debt_result = cursor.fetchone()
            
            if not debt_result:
                raise ValueError("الدين غير موجود")
            
            remaining_amount = float(debt_result[0])
            payment_amount = float(payment_data['amount'])
            
            if payment_amount > remaining_amount:
                raise ValueError("مبلغ الدفعة أكبر من المبلغ المتبقي")
            
            # تسجيل الدفعة
            cursor.execute('''
                INSERT INTO debt_payments (
                    debt_id, payment_date, amount, payment_method,
                    reference_number, notes, received_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_data['debt_id'],
                payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
                payment_amount,
                payment_data.get('payment_method', 'cash'),
                payment_data.get('reference_number', ''),
                payment_data.get('notes', ''),
                payment_data.get('received_by')
            ))
            
            payment_id = cursor.lastrowid
            
            # تحديث المبلغ المدفوع والمتبقي في الدين
            cursor.execute('''
                UPDATE company_debts 
                SET paid_amount = paid_amount + ?,
                    remaining_amount = remaining_amount - ?,
                    status = CASE 
                        WHEN remaining_amount - ? <= 0 THEN 'paid'
                        ELSE 'partial'
                    END,
                    updated_at = ?
                WHERE id = ?
            ''', (payment_amount, payment_amount, payment_amount, 
                  datetime.now().isoformat(), payment_data['debt_id']))
            
            # تسجيل التفاعل
            self.log_debt_interaction(
                payment_data['debt_id'], 
                'payment_received', 
                f"تم استلام دفعة بمبلغ {payment_amount:,.0f} دينار",
                payment_data.get('received_by')
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم تسجيل دفعة بمبلغ {payment_amount:,.0f} دينار")
            return payment_id
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الدفعة: {str(e)}")
            raise
    
    def get_company_debts(self, company_id: int, status: str = None) -> List[Dict]:
        """
        الحصول على ديون شركة معينة
        
        Args:
            company_id: معرف الشركة
            status: حالة الدين (اختياري)
            
        Returns:
            قائمة بديون الشركة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT cd.*, c.name as company_name
                FROM company_debts cd
                JOIN companies c ON cd.company_id = c.id
                WHERE cd.company_id = ?
            '''
            params = [company_id]
            
            if status:
                query += ' AND cd.status = ?'
                params.append(status)
            
            query += ' ORDER BY cd.invoice_date DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            debts = []
            
            for row in rows:
                debt = dict(zip(columns, row))
                
                # تحويل JSON المنتجات إلى قائمة
                if debt['products_json']:
                    try:
                        debt['products'] = json.loads(debt['products_json'])
                    except:
                        debt['products'] = []
                else:
                    debt['products'] = []
                
                # حساب الأيام المتبقية للاستحقاق
                due_date = datetime.strptime(debt['due_date'], '%Y-%m-%d')
                today = datetime.now()
                debt['days_until_due'] = (due_date - today).days
                debt['is_overdue'] = debt['days_until_due'] < 0
                
                debts.append(debt)
            
            return debts
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ديون الشركة: {str(e)}")
            return []
    
    def get_all_debts(self, status: str = None, overdue_only: bool = False) -> List[Dict]:
        """
        الحصول على جميع الديون
        
        Args:
            status: حالة الدين (اختياري)
            overdue_only: الديون المتأخرة فقط
            
        Returns:
            قائمة بجميع الديون
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT cd.*, c.name as company_name, c.contact_person, c.phone
                FROM company_debts cd
                JOIN companies c ON cd.company_id = c.id
                WHERE 1=1
            '''
            params = []
            
            if status:
                query += ' AND cd.status = ?'
                params.append(status)
            
            if overdue_only:
                query += ' AND cd.due_date < date("now")'
            
            query += ' ORDER BY cd.due_date ASC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            debts = []
            
            for row in rows:
                debt = dict(zip(columns, row))
                
                # تحويل JSON المنتجات إلى قائمة
                if debt['products_json']:
                    try:
                        debt['products'] = json.loads(debt['products_json'])
                    except:
                        debt['products'] = []
                else:
                    debt['products'] = []
                
                # حساب الأيام المتبقية للاستحقاق
                due_date = datetime.strptime(debt['due_date'], '%Y-%m-%d')
                today = datetime.now()
                debt['days_until_due'] = (due_date - today).days
                debt['is_overdue'] = debt['days_until_due'] < 0
                
                debts.append(debt)
            
            return debts
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الديون: {str(e)}")
            return []
    
    def get_debt_payments(self, debt_id: int) -> List[Dict]:
        """
        الحصول على دفعات دين معين
        
        Args:
            debt_id: معرف الدين
            
        Returns:
            قائمة بدفعات الدين
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM debt_payments 
                WHERE debt_id = ? 
                ORDER BY payment_date DESC
            ''', (debt_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            payments = [dict(zip(columns, row)) for row in rows]
            
            return payments
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على دفعات الدين: {str(e)}")
            return []
    
    def search_debts(self, search_criteria: Dict) -> List[Dict]:
        """
        البحث في الديون
        
        Args:
            search_criteria: معايير البحث
            
        Returns:
            قائمة بالديون المطابقة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT cd.*, c.name as company_name, c.contact_person, c.phone
                FROM company_debts cd
                JOIN companies c ON cd.company_id = c.id
                WHERE 1=1
            '''
            params = []
            
            if search_criteria.get('company_name'):
                query += ' AND c.name LIKE ?'
                params.append(f"%{search_criteria['company_name']}%")
            
            if search_criteria.get('invoice_number'):
                query += ' AND cd.invoice_number LIKE ?'
                params.append(f"%{search_criteria['invoice_number']}%")
            
            if search_criteria.get('status'):
                query += ' AND cd.status = ?'
                params.append(search_criteria['status'])
            
            if search_criteria.get('date_from'):
                query += ' AND cd.invoice_date >= ?'
                params.append(search_criteria['date_from'])
            
            if search_criteria.get('date_to'):
                query += ' AND cd.invoice_date <= ?'
                params.append(search_criteria['date_to'])
            
            if search_criteria.get('amount_min'):
                query += ' AND cd.total_amount >= ?'
                params.append(search_criteria['amount_min'])
            
            if search_criteria.get('amount_max'):
                query += ' AND cd.total_amount <= ?'
                params.append(search_criteria['amount_max'])
            
            query += ' ORDER BY cd.invoice_date DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            debts = []
            
            for row in rows:
                debt = dict(zip(columns, row))
                
                # تحويل JSON المنتجات إلى قائمة
                if debt['products_json']:
                    try:
                        debt['products'] = json.loads(debt['products_json'])
                    except:
                        debt['products'] = []
                else:
                    debt['products'] = []
                
                # حساب الأيام المتبقية للاستحقاق
                due_date = datetime.strptime(debt['due_date'], '%Y-%m-%d')
                today = datetime.now()
                debt['days_until_due'] = (due_date - today).days
                debt['is_overdue'] = debt['days_until_due'] < 0
                
                debts.append(debt)
            
            return debts
            
        except Exception as e:
            logger.error(f"خطأ في البحث في الديون: {str(e)}")
            return []
    
    def get_companies_summary(self) -> List[Dict]:
        """
        الحصول على ملخص ديون الشركات
        
        Returns:
            قائمة بملخص ديون كل شركة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    c.id,
                    c.name,
                    c.contact_person,
                    c.phone,
                    COUNT(cd.id) as total_debts,
                    COALESCE(SUM(cd.total_amount), 0) as total_amount,
                    COALESCE(SUM(cd.paid_amount), 0) as paid_amount,
                    COALESCE(SUM(cd.remaining_amount), 0) as remaining_amount,
                    COUNT(CASE WHEN cd.status = 'pending' THEN 1 END) as pending_debts,
                    COUNT(CASE WHEN cd.due_date < date('now') AND cd.status != 'paid' THEN 1 END) as overdue_debts
                FROM companies c
                LEFT JOIN company_debts cd ON c.id = cd.company_id
                WHERE c.is_active = 1
                GROUP BY c.id, c.name, c.contact_person, c.phone
                HAVING total_debts > 0 OR remaining_amount > 0
                ORDER BY remaining_amount DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            companies = [dict(zip(columns, row)) for row in rows]
            
            return companies
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص الشركات: {str(e)}")
            return []
    
    def log_debt_interaction(self, debt_id: int, interaction_type: str, description: str, user_id: int = None):
        """
        تسجيل تفاعل مع الدين
        
        Args:
            debt_id: معرف الدين
            interaction_type: نوع التفاعل
            description: وصف التفاعل
            user_id: معرف المستخدم
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO debt_interactions (debt_id, interaction_type, description, user_id)
                VALUES (?, ?, ?, ?)
            ''', (debt_id, interaction_type, description, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل التفاعل: {str(e)}")
    
    def generate_debt_report(self, start_date: str, end_date: str) -> Dict:
        """
        إنشاء تقرير الديون
        
        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            
        Returns:
            تقرير الديون
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إحصائيات عامة
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_debts,
                    COALESCE(SUM(total_amount), 0) as total_amount,
                    COALESCE(SUM(paid_amount), 0) as paid_amount,
                    COALESCE(SUM(remaining_amount), 0) as remaining_amount,
                    COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_debts,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_debts,
                    COUNT(CASE WHEN due_date < date('now') AND status != 'paid' THEN 1 END) as overdue_debts
                FROM company_debts 
                WHERE invoice_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            stats = cursor.fetchone()
            
            # أكبر الديون
            cursor.execute('''
                SELECT cd.invoice_number, c.name, cd.total_amount, cd.remaining_amount, cd.status
                FROM company_debts cd
                JOIN companies c ON cd.company_id = c.id
                WHERE cd.invoice_date BETWEEN ? AND ?
                ORDER BY cd.remaining_amount DESC
                LIMIT 10
            ''', (start_date, end_date))
            
            top_debts = cursor.fetchall()
            
            # الشركات الأكثر ديناً
            cursor.execute('''
                SELECT c.name, COUNT(cd.id) as debt_count, 
                       COALESCE(SUM(cd.remaining_amount), 0) as total_remaining
                FROM companies c
                JOIN company_debts cd ON c.id = cd.company_id
                WHERE cd.invoice_date BETWEEN ? AND ?
                GROUP BY c.id, c.name
                ORDER BY total_remaining DESC
                LIMIT 10
            ''', (start_date, end_date))
            
            top_companies = cursor.fetchall()
            
            conn.close()
            
            report = {
                'period': {'start_date': start_date, 'end_date': end_date},
                'summary': {
                    'total_debts': stats[0],
                    'total_amount': float(stats[1]),
                    'paid_amount': float(stats[2]),
                    'remaining_amount': float(stats[3]),
                    'paid_debts': stats[4],
                    'pending_debts': stats[5],
                    'overdue_debts': stats[6],
                    'collection_rate': (float(stats[2]) / float(stats[1]) * 100) if stats[1] > 0 else 0
                },
                'top_debts': [
                    {
                        'invoice_number': row[0],
                        'company_name': row[1],
                        'total_amount': float(row[2]),
                        'remaining_amount': float(row[3]),
                        'status': row[4]
                    } for row in top_debts
                ],
                'top_companies': [
                    {
                        'company_name': row[0],
                        'debt_count': row[1],
                        'total_remaining': float(row[2])
                    } for row in top_companies
                ],
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير الديون: {str(e)}")
            return {}


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء نظام إدارة الديون
    debt_system = DebtManagementSystem()
    
    try:
        # إضافة شركة جديدة
        company_data = {
            'name': 'شركة الإنارة المتقدمة',
            'contact_person': 'محمد أحمد',
            'phone': '+964 770 123 4567',
            'email': 'info@advanced-lighting.com',
            'address': 'شارع الرشيد - بغداد',
            'credit_limit': 5000000,
            'payment_terms_days': 45
        }
        
        company_id = debt_system.add_company(company_data)
        print(f"تم إضافة شركة جديدة: {company_id}")
        
        # إنشاء دين جديد
        debt_data = {
            'company_id': company_id,
            'invoice_number': 'INV-COMP-001',
            'invoice_date': '2025-01-09',
            'total_amount': 1500000,
            'description': 'بيع كشافات LED للشركة',
            'products': [
                {'name': 'كشاف LED 50 واط', 'quantity': 20, 'price': 75000}
            ]
        }
        
        debt_id = debt_system.create_debt(debt_data)
        print(f"تم إنشاء دين جديد: {debt_id}")
        
        # تسجيل دفعة
        payment_data = {
            'debt_id': debt_id,
            'amount': 500000,
            'payment_method': 'bank_transfer',
            'notes': 'دفعة أولى'
        }
        
        payment_id = debt_system.record_payment(payment_data)
        print(f"تم تسجيل دفعة: {payment_id}")
        
        # الحصول على ملخص الشركات
        companies_summary = debt_system.get_companies_summary()
        print(f"ملخص الشركات: {len(companies_summary)} شركة")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

