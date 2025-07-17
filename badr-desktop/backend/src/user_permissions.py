"""
نظام صلاحيات المستخدمين لبرنامج البدر للإنارة
يدعم إدارة المستخدمين والأدوار والصلاحيات
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging
import json

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserPermissionsManager:
    """نظام إدارة صلاحيات المستخدمين"""
    
    def __init__(self, db_path: str = "users.sqlite"):
        """
        تهيئة نظام إدارة المستخدمين
        
        Args:
            db_path: مسار قاعدة البيانات
        """
        self.db_path = db_path
        self.init_database()
        self.create_default_admin()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    role_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            ''')
            
            # جدول الأدوار
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    is_system_role BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الصلاحيات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول ربط الأدوار بالصلاحيات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES roles (id),
                    FOREIGN KEY (permission_id) REFERENCES permissions (id)
                )
            ''')
            
            # جدول جلسات المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # جدول سجل العمليات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # إنشاء الأدوار والصلاحيات الافتراضية
            self.create_default_roles_and_permissions()
            
            logger.info("تم إنشاء جداول قاعدة بيانات المستخدمين")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {str(e)}")
            raise
    
    def create_default_roles_and_permissions(self):
        """إنشاء الأدوار والصلاحيات الافتراضية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # الصلاحيات الافتراضية
            default_permissions = [
                # إدارة المنتجات
                ('products.view', 'عرض المنتجات', 'products'),
                ('products.add', 'إضافة منتجات', 'products'),
                ('products.edit', 'تعديل المنتجات', 'products'),
                ('products.delete', 'حذف المنتجات', 'products'),
                
                # إدارة المبيعات
                ('sales.view', 'عرض المبيعات', 'sales'),
                ('sales.create', 'إنشاء فاتورة بيع', 'sales'),
                ('sales.edit', 'تعديل فاتورة بيع', 'sales'),
                ('sales.delete', 'حذف فاتورة بيع', 'sales'),
                ('sales.print', 'طباعة الفواتير', 'sales'),
                
                # إدارة المالية
                ('finance.view', 'عرض التقارير المالية', 'finance'),
                ('finance.view_profits', 'عرض الأرباح', 'finance'),
                ('finance.view_costs', 'عرض التكاليف', 'finance'),
                
                # إدارة الزبائن
                ('customers.view', 'عرض الزبائن', 'customers'),
                ('customers.add', 'إضافة زبائن', 'customers'),
                ('customers.edit', 'تعديل بيانات الزبائن', 'customers'),
                ('customers.delete', 'حذف الزبائن', 'customers'),
                
                # إدارة الضمان
                ('warranty.view', 'عرض الضمانات', 'warranty'),
                ('warranty.create', 'إنشاء ضمان', 'warranty'),
                ('warranty.manage', 'إدارة طلبات الصيانة', 'warranty'),
                
                # إدارة المخزون
                ('inventory.view', 'عرض المخزون', 'inventory'),
                ('inventory.manage', 'إدارة المخزون', 'inventory'),
                
                # إدارة النظام
                ('system.backup', 'إنشاء نسخ احتياطية', 'system'),
                ('system.restore', 'استعادة النسخ الاحتياطية', 'system'),
                ('system.settings', 'إعدادات النظام', 'system'),
                ('system.reset', 'إعادة تعيين النظام', 'system'),
                
                # إدارة المستخدمين
                ('users.view', 'عرض المستخدمين', 'users'),
                ('users.add', 'إضافة مستخدمين', 'users'),
                ('users.edit', 'تعديل المستخدمين', 'users'),
                ('users.delete', 'حذف المستخدمين', 'users'),
                ('users.permissions', 'إدارة الصلاحيات', 'users'),
                
                # تسديد الديون
                ('debts.view', 'عرض الديون', 'debts'),
                ('debts.manage', 'إدارة تسديد الديون', 'debts'),
                
                # الإشعارات
                ('notifications.manage', 'إدارة الإشعارات', 'notifications')
            ]
            
            # إدراج الصلاحيات
            for perm_name, perm_desc, perm_category in default_permissions:
                cursor.execute('''
                    INSERT OR IGNORE INTO permissions (name, description, category)
                    VALUES (?, ?, ?)
                ''', (perm_name, perm_desc, perm_category))
            
            # الأدوار الافتراضية
            default_roles = [
                ('admin', 'مدير النظام', True),
                ('manager', 'مدير المحل', False),
                ('cashier', 'أمين الصندوق', False),
                ('sales_employee', 'موظف مبيعات', False),
                ('warehouse_employee', 'موظف مخزن', False)
            ]
            
            # إدراج الأدوار
            for role_name, role_desc, is_system in default_roles:
                cursor.execute('''
                    INSERT OR IGNORE INTO roles (name, description, is_system_role)
                    VALUES (?, ?, ?)
                ''', (role_name, role_desc, is_system))
            
            conn.commit()
            
            # ربط الصلاحيات بالأدوار
            self.assign_default_permissions()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الأدوار والصلاحيات الافتراضية: {str(e)}")
    
    def assign_default_permissions(self):
        """ربط الصلاحيات الافتراضية بالأدوار"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # صلاحيات مدير النظام (جميع الصلاحيات)
            cursor.execute('SELECT id FROM roles WHERE name = "admin"')
            admin_role_id = cursor.fetchone()[0]
            
            cursor.execute('SELECT id FROM permissions')
            all_permissions = cursor.fetchall()
            
            for perm_id in all_permissions:
                cursor.execute('''
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                    VALUES (?, ?)
                ''', (admin_role_id, perm_id[0]))
            
            # صلاحيات مدير المحل
            cursor.execute('SELECT id FROM roles WHERE name = "manager"')
            manager_role_id = cursor.fetchone()[0]
            
            manager_permissions = [
                'products.view', 'products.add', 'products.edit',
                'sales.view', 'sales.create', 'sales.edit', 'sales.print',
                'finance.view', 'finance.view_profits', 'finance.view_costs',
                'customers.view', 'customers.add', 'customers.edit',
                'warranty.view', 'warranty.create', 'warranty.manage',
                'inventory.view', 'inventory.manage',
                'debts.view', 'debts.manage',
                'system.backup'
            ]
            
            for perm_name in manager_permissions:
                cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
                perm_result = cursor.fetchone()
                if perm_result:
                    cursor.execute('''
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                    ''', (manager_role_id, perm_result[0]))
            
            # صلاحيات أمين الصندوق
            cursor.execute('SELECT id FROM roles WHERE name = "cashier"')
            cashier_role_id = cursor.fetchone()[0]
            
            cashier_permissions = [
                'products.view',
                'sales.view', 'sales.create', 'sales.print',
                'customers.view', 'customers.add',
                'warranty.view', 'warranty.create'
            ]
            
            for perm_name in cashier_permissions:
                cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
                perm_result = cursor.fetchone()
                if perm_result:
                    cursor.execute('''
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                    ''', (cashier_role_id, perm_result[0]))
            
            # صلاحيات موظف المبيعات
            cursor.execute('SELECT id FROM roles WHERE name = "sales_employee"')
            sales_role_id = cursor.fetchone()[0]
            
            sales_permissions = [
                'products.view',
                'sales.view', 'sales.create', 'sales.print',
                'customers.view', 'customers.add',
                'warranty.view', 'warranty.create'
            ]
            
            for perm_name in sales_permissions:
                cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
                perm_result = cursor.fetchone()
                if perm_result:
                    cursor.execute('''
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                    ''', (sales_role_id, perm_result[0]))
            
            # صلاحيات موظف المخزن
            cursor.execute('SELECT id FROM roles WHERE name = "warehouse_employee"')
            warehouse_role_id = cursor.fetchone()[0]
            
            warehouse_permissions = [
                'products.view', 'products.add', 'products.edit',
                'inventory.view', 'inventory.manage'
            ]
            
            for perm_name in warehouse_permissions:
                cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
                perm_result = cursor.fetchone()
                if perm_result:
                    cursor.execute('''
                        INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                        VALUES (?, ?)
                    ''', (warehouse_role_id, perm_result[0]))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في ربط الصلاحيات بالأدوار: {str(e)}")
    
    def create_default_admin(self):
        """إنشاء مستخدم مدير افتراضي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # التحقق من وجود مدير
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
            if cursor.fetchone()[0] > 0:
                conn.close()
                return
            
            # الحصول على معرف دور المدير
            cursor.execute('SELECT id FROM roles WHERE name = "admin"')
            admin_role_result = cursor.fetchone()
            if not admin_role_result:
                conn.close()
                return
            
            admin_role_id = admin_role_result[0]
            
            # إنشاء كلمة مرور افتراضية
            default_password = "admin123"
            salt = secrets.token_hex(16)
            password_hash = self.hash_password(default_password, salt)
            
            # إنشاء المستخدم المدير
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, full_name, role_id)
                VALUES (?, ?, ?, ?, ?)
            ''', ("admin", password_hash, salt, "مدير النظام", admin_role_id))
            
            conn.commit()
            conn.close()
            
            logger.info("تم إنشاء مستخدم مدير افتراضي (admin/admin123)")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم المدير: {str(e)}")
    
    def hash_password(self, password: str, salt: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def create_user(self, user_data: Dict) -> int:
        """
        إنشاء مستخدم جديد
        
        Args:
            user_data: بيانات المستخدم
            
        Returns:
            معرف المستخدم المُنشأ
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # التحقق من عدم تكرار اسم المستخدم
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (user_data['username'],))
            if cursor.fetchone()[0] > 0:
                raise ValueError("اسم المستخدم موجود مسبقاً")
            
            # تشفير كلمة المرور
            salt = secrets.token_hex(16)
            password_hash = self.hash_password(user_data['password'], salt)
            
            # إدراج المستخدم
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, full_name, phone, role_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                user_data.get('email'),
                password_hash,
                salt,
                user_data['full_name'],
                user_data.get('phone'),
                user_data['role_id']
            ))
            
            user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء مستخدم جديد: {user_data['username']}")
            return user_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        مصادقة المستخدم
        
        Args:
            username: اسم المستخدم
            password: كلمة المرور
            
        Returns:
            بيانات المستخدم إذا تمت المصادقة بنجاح، None خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.username, u.password_hash, u.salt, u.full_name, 
                       u.role_id, r.name as role_name, u.is_active
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.username = ?
            ''', (username,))
            
            user_row = cursor.fetchone()
            
            if not user_row:
                conn.close()
                return None
            
            user_id, username, stored_hash, salt, full_name, role_id, role_name, is_active = user_row
            
            # التحقق من حالة المستخدم
            if not is_active:
                conn.close()
                return None
            
            # التحقق من كلمة المرور
            password_hash = self.hash_password(password, salt)
            if password_hash != stored_hash:
                conn.close()
                return None
            
            # تحديث آخر تسجيل دخول
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            # إنشاء جلسة
            session_token = self.create_session(user_id)
            
            user_data = {
                'id': user_id,
                'username': username,
                'full_name': full_name,
                'role_id': role_id,
                'role_name': role_name,
                'session_token': session_token,
                'permissions': self.get_user_permissions(user_id)
            }
            
            logger.info(f"تم تسجيل دخول المستخدم: {username}")
            return user_data
            
        except Exception as e:
            logger.error(f"خطأ في مصادقة المستخدم: {str(e)}")
            return None
    
    def create_session(self, user_id: int, duration_hours: int = 24) -> str:
        """
        إنشاء جلسة مستخدم
        
        Args:
            user_id: معرف المستخدم
            duration_hours: مدة الجلسة بالساعات
            
        Returns:
            رمز الجلسة
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إنشاء رمز جلسة فريد
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=duration_hours)
            
            # حذف الجلسات المنتهية الصلاحية
            cursor.execute('DELETE FROM user_sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
            
            # إدراج الجلسة الجديدة
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return session_token
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الجلسة: {str(e)}")
            return ""
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        التحقق من صحة الجلسة
        
        Args:
            session_token: رمز الجلسة
            
        Returns:
            بيانات المستخدم إذا كانت الجلسة صالحة، None خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, u.username, u.full_name, u.role_id, r.name as role_name
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                JOIN roles r ON u.role_id = r.id
                WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1
            ''', (session_token, datetime.now().isoformat()))
            
            session_row = cursor.fetchone()
            
            conn.close()
            
            if session_row:
                user_id, username, full_name, role_id, role_name = session_row
                
                return {
                    'id': user_id,
                    'username': username,
                    'full_name': full_name,
                    'role_id': role_id,
                    'role_name': role_name,
                    'permissions': self.get_user_permissions(user_id)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الجلسة: {str(e)}")
            return None
    
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        الحصول على صلاحيات المستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            مجموعة صلاحيات المستخدم
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.name
                FROM users u
                JOIN roles r ON u.role_id = r.id
                JOIN role_permissions rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.id = ?
            ''', (user_id,))
            
            permissions = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            
            return permissions
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على صلاحيات المستخدم: {str(e)}")
            return set()
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """
        التحقق من وجود صلاحية للمستخدم
        
        Args:
            user_id: معرف المستخدم
            permission: اسم الصلاحية
            
        Returns:
            True إذا كان المستخدم يملك الصلاحية، False خلاف ذلك
        """
        permissions = self.get_user_permissions(user_id)
        return permission in permissions
    
    def logout_user(self, session_token: str) -> bool:
        """
        تسجيل خروج المستخدم
        
        Args:
            session_token: رمز الجلسة
            
        Returns:
            True إذا تم تسجيل الخروج بنجاح، False خلاف ذلك
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
            
            conn.commit()
            conn.close()
            
            logger.info("تم تسجيل خروج المستخدم")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الخروج: {str(e)}")
            return False
    
    def log_user_activity(self, user_id: int, action: str, details: str = "", ip_address: str = ""):
        """
        تسجيل نشاط المستخدم
        
        Args:
            user_id: معرف المستخدم
            action: العملية المنفذة
            details: تفاصيل العملية
            ip_address: عنوان IP
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity_log (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل نشاط المستخدم: {str(e)}")


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير الصلاحيات
    permissions_manager = UserPermissionsManager()
    
    # مثال على إنشاء مستخدم جديد
    try:
        # الحصول على معرف دور أمين الصندوق
        conn = sqlite3.connect(permissions_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM roles WHERE name = "cashier"')
        cashier_role_id = cursor.fetchone()[0]
        conn.close()
        
        # بيانات المستخدم الجديد
        user_data = {
            'username': 'ahmed_cashier',
            'password': 'password123',
            'full_name': 'أحمد محمد',
            'phone': '+964 750 123 4567',
            'email': 'ahmed@albadr.com',
            'role_id': cashier_role_id
        }
        
        # إنشاء المستخدم
        user_id = permissions_manager.create_user(user_data)
        print(f"تم إنشاء مستخدم جديد: {user_id}")
        
        # مصادقة المستخدم
        auth_result = permissions_manager.authenticate_user('ahmed_cashier', 'password123')
        if auth_result:
            print(f"تم تسجيل الدخول: {auth_result['full_name']}")
            print(f"الصلاحيات: {auth_result['permissions']}")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

