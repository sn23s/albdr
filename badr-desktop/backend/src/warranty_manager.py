"""
نظام إدارة الضمان لبرنامج البدر للإنارة
يدعم تتبع فترات الضمان وإدارة طلبات الصيانة
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WarrantyManager:
    """نظام إدارة الضمان"""
    
    def __init__(self, db_path: str = "warranty.sqlite"):
        """
        تهيئة نظام إدارة الضمان
        
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
            
            # جدول الضمانات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warranties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    product_code TEXT,
                    customer_id TEXT,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT,
                    customer_address TEXT,
                    invoice_number TEXT NOT NULL,
                    purchase_date DATE NOT NULL,
                    warranty_start_date DATE NOT NULL,
                    warranty_end_date DATE NOT NULL,
                    warranty_months INTEGER NOT NULL,
                    warranty_terms TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول طلبات الصيانة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warranty_claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    warranty_id INTEGER NOT NULL,
                    claim_date DATE NOT NULL,
                    issue_description TEXT NOT NULL,
                    claim_status TEXT DEFAULT 'pending',
                    resolution_date DATE,
                    resolution_description TEXT,
                    technician_name TEXT,
                    cost DECIMAL(10,2) DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (warranty_id) REFERENCES warranties (id)
                )
            ''')
            
            # جدول تجديد الضمان
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warranty_extensions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    warranty_id INTEGER NOT NULL,
                    extension_months INTEGER NOT NULL,
                    new_end_date DATE NOT NULL,
                    reason TEXT,
                    cost DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (warranty_id) REFERENCES warranties (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("تم إنشاء جداول قاعدة بيانات الضمان")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {str(e)}")
            raise
    
    def create_warranty(self, warranty_data: Dict) -> int:
        """
        إنشاء ضمان جديد
        
        Args:
            warranty_data: بيانات الضمان
            
        Returns:
            معرف الضمان المُنشأ
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # حساب تاريخ انتهاء الضمان
            start_date = datetime.strptime(warranty_data['warranty_start_date'], '%Y-%m-%d')
            warranty_months = warranty_data['warranty_months']
            end_date = start_date + timedelta(days=warranty_months * 30)
            
            # إدراج بيانات الضمان
            cursor.execute('''
                INSERT INTO warranties (
                    product_id, product_name, product_code, customer_id, customer_name,
                    customer_phone, customer_address, invoice_number, purchase_date,
                    warranty_start_date, warranty_end_date, warranty_months, warranty_terms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                warranty_data['product_id'],
                warranty_data['product_name'],
                warranty_data.get('product_code', ''),
                warranty_data.get('customer_id', ''),
                warranty_data['customer_name'],
                warranty_data.get('customer_phone', ''),
                warranty_data.get('customer_address', ''),
                warranty_data['invoice_number'],
                warranty_data['purchase_date'],
                warranty_data['warranty_start_date'],
                end_date.strftime('%Y-%m-%d'),
                warranty_months,
                warranty_data.get('warranty_terms', 'ضمان ضد عيوب الصناعة')
            ))
            
            warranty_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء ضمان جديد: {warranty_id}")
            return warranty_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الضمان: {str(e)}")
            raise
    
    def get_warranty_by_id(self, warranty_id: int) -> Optional[Dict]:
        """
        الحصول على ضمان بالمعرف
        
        Args:
            warranty_id: معرف الضمان
            
        Returns:
            بيانات الضمان أو None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM warranties WHERE id = ?', (warranty_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                warranty = dict(zip(columns, row))
                
                # إضافة معلومات إضافية
                warranty['is_active'] = self.is_warranty_active(warranty_id)
                warranty['days_remaining'] = self.get_warranty_days_remaining(warranty_id)
                
                return warranty
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الضمان: {str(e)}")
            return None
    
    def search_warranties(self, search_criteria: Dict) -> List[Dict]:
        """
        البحث في الضمانات
        
        Args:
            search_criteria: معايير البحث
            
        Returns:
            قائمة بالضمانات المطابقة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # بناء استعلام البحث
            query = "SELECT * FROM warranties WHERE 1=1"
            params = []
            
            if search_criteria.get('customer_name'):
                query += " AND customer_name LIKE ?"
                params.append(f"%{search_criteria['customer_name']}%")
            
            if search_criteria.get('customer_phone'):
                query += " AND customer_phone LIKE ?"
                params.append(f"%{search_criteria['customer_phone']}%")
            
            if search_criteria.get('product_name'):
                query += " AND product_name LIKE ?"
                params.append(f"%{search_criteria['product_name']}%")
            
            if search_criteria.get('product_code'):
                query += " AND product_code LIKE ?"
                params.append(f"%{search_criteria['product_code']}%")
            
            if search_criteria.get('invoice_number'):
                query += " AND invoice_number LIKE ?"
                params.append(f"%{search_criteria['invoice_number']}%")
            
            if search_criteria.get('status'):
                query += " AND status = ?"
                params.append(search_criteria['status'])
            
            # ترتيب النتائج
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            # تحويل النتائج إلى قواميس
            columns = [desc[0] for desc in cursor.description]
            warranties = []
            
            for row in rows:
                warranty = dict(zip(columns, row))
                warranty['is_active'] = self.is_warranty_active(warranty['id'])
                warranty['days_remaining'] = self.get_warranty_days_remaining(warranty['id'])
                warranties.append(warranty)
            
            return warranties
            
        except Exception as e:
            logger.error(f"خطأ في البحث في الضمانات: {str(e)}")
            return []
    
    def is_warranty_active(self, warranty_id: int) -> bool:
        """
        التحقق من صلاحية الضمان
        
        Args:
            warranty_id: معرف الضمان
            
        Returns:
            True إذا كان الضمان ساري المفعول، False خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT warranty_end_date, status FROM warranties WHERE id = ?', (warranty_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                end_date_str, status = row
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                current_date = datetime.now()
                
                return status == 'active' and current_date <= end_date
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحية الضمان: {str(e)}")
            return False
    
    def get_warranty_days_remaining(self, warranty_id: int) -> int:
        """
        الحصول على عدد الأيام المتبقية في الضمان
        
        Args:
            warranty_id: معرف الضمان
            
        Returns:
            عدد الأيام المتبقية (سالب إذا انتهى الضمان)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT warranty_end_date FROM warranties WHERE id = ?', (warranty_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                end_date = datetime.strptime(row[0], '%Y-%m-%d')
                current_date = datetime.now()
                delta = end_date - current_date
                
                return delta.days
            
            return 0
            
        except Exception as e:
            logger.error(f"خطأ في حساب الأيام المتبقية: {str(e)}")
            return 0
    
    def create_warranty_claim(self, claim_data: Dict) -> int:
        """
        إنشاء طلب صيانة تحت الضمان
        
        Args:
            claim_data: بيانات طلب الصيانة
            
        Returns:
            معرف طلب الصيانة
        """
        try:
            # التحقق من صلاحية الضمان
            if not self.is_warranty_active(claim_data['warranty_id']):
                raise ValueError("الضمان غير ساري المفعول")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO warranty_claims (
                    warranty_id, claim_date, issue_description, notes
                ) VALUES (?, ?, ?, ?)
            ''', (
                claim_data['warranty_id'],
                claim_data.get('claim_date', datetime.now().strftime('%Y-%m-%d')),
                claim_data['issue_description'],
                claim_data.get('notes', '')
            ))
            
            claim_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء طلب صيانة جديد: {claim_id}")
            return claim_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء طلب الصيانة: {str(e)}")
            raise
    
    def update_warranty_claim(self, claim_id: int, update_data: Dict) -> bool:
        """
        تحديث طلب صيانة
        
        Args:
            claim_id: معرف طلب الصيانة
            update_data: البيانات المحدثة
            
        Returns:
            True إذا تم التحديث بنجاح، False خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # بناء استعلام التحديث
            update_fields = []
            params = []
            
            for field, value in update_data.items():
                if field in ['claim_status', 'resolution_date', 'resolution_description', 
                           'technician_name', 'cost', 'notes']:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(claim_id)
                
                query = f"UPDATE warranty_claims SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
            
            conn.close()
            
            logger.info(f"تم تحديث طلب الصيانة: {claim_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث طلب الصيانة: {str(e)}")
            return False
    
    def get_warranty_claims(self, warranty_id: int) -> List[Dict]:
        """
        الحصول على طلبات الصيانة لضمان معين
        
        Args:
            warranty_id: معرف الضمان
            
        Returns:
            قائمة بطلبات الصيانة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM warranty_claims 
                WHERE warranty_id = ? 
                ORDER BY claim_date DESC
            ''', (warranty_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            claims = [dict(zip(columns, row)) for row in rows]
            
            return claims
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على طلبات الصيانة: {str(e)}")
            return []
    
    def extend_warranty(self, warranty_id: int, extension_months: int, 
                       reason: str = "", cost: float = 0) -> bool:
        """
        تمديد فترة الضمان
        
        Args:
            warranty_id: معرف الضمان
            extension_months: عدد أشهر التمديد
            reason: سبب التمديد
            cost: تكلفة التمديد
            
        Returns:
            True إذا تم التمديد بنجاح، False خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # الحصول على تاريخ انتهاء الضمان الحالي
            cursor.execute('SELECT warranty_end_date FROM warranties WHERE id = ?', (warranty_id,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError("الضمان غير موجود")
            
            current_end_date = datetime.strptime(row[0], '%Y-%m-%d')
            new_end_date = current_end_date + timedelta(days=extension_months * 30)
            
            # تحديث تاريخ انتهاء الضمان
            cursor.execute('''
                UPDATE warranties 
                SET warranty_end_date = ?, updated_at = ? 
                WHERE id = ?
            ''', (new_end_date.strftime('%Y-%m-%d'), datetime.now().isoformat(), warranty_id))
            
            # إضافة سجل التمديد
            cursor.execute('''
                INSERT INTO warranty_extensions (
                    warranty_id, extension_months, new_end_date, reason, cost
                ) VALUES (?, ?, ?, ?, ?)
            ''', (warranty_id, extension_months, new_end_date.strftime('%Y-%m-%d'), reason, cost))
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم تمديد الضمان {warranty_id} لمدة {extension_months} شهر")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تمديد الضمان: {str(e)}")
            return False
    
    def get_expiring_warranties(self, days_ahead: int = 30) -> List[Dict]:
        """
        الحصول على الضمانات التي ستنتهي قريباً
        
        Args:
            days_ahead: عدد الأيام للتنبيه المسبق
            
        Returns:
            قائمة بالضمانات التي ستنتهي
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # حساب التاريخ المستهدف
            target_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT * FROM warranties 
                WHERE warranty_end_date BETWEEN ? AND ? 
                AND status = 'active'
                ORDER BY warranty_end_date ASC
            ''', (current_date, target_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = [desc[0] for desc in cursor.description]
            warranties = []
            
            for row in rows:
                warranty = dict(zip(columns, row))
                warranty['days_remaining'] = self.get_warranty_days_remaining(warranty['id'])
                warranties.append(warranty)
            
            return warranties
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الضمانات المنتهية: {str(e)}")
            return []
    
    def generate_warranty_report(self, start_date: str, end_date: str) -> Dict:
        """
        إنشاء تقرير الضمانات
        
        Args:
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            
        Returns:
            تقرير الضمانات
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إحصائيات عامة
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_warranties,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_warranties,
                    COUNT(CASE WHEN warranty_end_date < date('now') THEN 1 END) as expired_warranties
                FROM warranties 
                WHERE created_at BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            stats = cursor.fetchone()
            
            # طلبات الصيانة
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_claims,
                    COUNT(CASE WHEN claim_status = 'pending' THEN 1 END) as pending_claims,
                    COUNT(CASE WHEN claim_status = 'resolved' THEN 1 END) as resolved_claims,
                    AVG(cost) as avg_claim_cost
                FROM warranty_claims wc
                JOIN warranties w ON wc.warranty_id = w.id
                WHERE wc.created_at BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            claims_stats = cursor.fetchone()
            
            conn.close()
            
            report = {
                'period': {'start_date': start_date, 'end_date': end_date},
                'warranties': {
                    'total': stats[0],
                    'active': stats[1],
                    'expired': stats[2]
                },
                'claims': {
                    'total': claims_stats[0],
                    'pending': claims_stats[1],
                    'resolved': claims_stats[2],
                    'avg_cost': claims_stats[3] or 0
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تقرير الضمانات: {str(e)}")
            return {}


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير الضمان
    warranty_manager = WarrantyManager()
    
    # مثال على إنشاء ضمان
    warranty_data = {
        'product_id': 'PROD-001',
        'product_name': 'لمبة LED 10 واط',
        'product_code': 'LED-10W-001',
        'customer_name': 'علي حسن',
        'customer_phone': '+964 750 123 4567',
        'customer_address': 'الكرادة - بغداد',
        'invoice_number': 'INV-2025-001',
        'purchase_date': '2025-01-09',
        'warranty_start_date': '2025-01-09',
        'warranty_months': 12,
        'warranty_terms': 'ضمان ضد عيوب الصناعة لمدة 12 شهر'
    }
    
    try:
        # إنشاء ضمان
        warranty_id = warranty_manager.create_warranty(warranty_data)
        print(f"تم إنشاء ضمان جديد: {warranty_id}")
        
        # البحث في الضمانات
        search_results = warranty_manager.search_warranties({'customer_name': 'علي'})
        print(f"نتائج البحث: {len(search_results)} ضمان")
        
        # الحصول على الضمانات المنتهية قريباً
        expiring = warranty_manager.get_expiring_warranties(30)
        print(f"ضمانات ستنتهي خلال 30 يوم: {len(expiring)}")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

