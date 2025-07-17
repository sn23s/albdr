"""
نظام إعادة التعيين المحمي بكلمة مرور لبرنامج البدر للإنارة
يدعم إعادة تعيين البيانات مع حماية بكلمة مرور خاصة
"""

import os
import sqlite3
import hashlib
import secrets
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import json

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemResetManager:
    """مدير إعادة تعيين النظام"""
    
    def __init__(self, config_path: str = "reset_config.json"):
        """
        تهيئة مدير إعادة التعيين
        
        Args:
            config_path: مسار ملف إعدادات إعادة التعيين
        """
        self.config_path = config_path
        self.master_password_hash = None
        self.salt = None
        self.reset_history = []
        self.load_config()
        
        # قائمة قواعد البيانات والملفات المراد إعادة تعيينها
        self.database_files = [
            "products.sqlite",
            "sales.sqlite", 
            "customers.sqlite",
            "inventory.sqlite",
            "users.sqlite",
            "debts.sqlite",
            "warranty.sqlite",
            "notifications.sqlite"
        ]
        
        self.data_directories = [
            "product_images",
            "invoices",
            "backups",
            "temp",
            "logs"
        ]
        
        self.config_files = [
            "theme_config.json",
            "app_settings.json",
            "notification_settings.json"
        ]
    
    def load_config(self):
        """تحميل إعدادات إعادة التعيين"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.master_password_hash = config.get('master_password_hash')
                    self.salt = config.get('salt')
                    self.reset_history = config.get('reset_history', [])
                    
                logger.info("تم تحميل إعدادات إعادة التعيين")
            else:
                # إنشاء كلمة مرور افتراضية
                self.set_master_password("AlBadr2025!")
                logger.info("تم إنشاء كلمة مرور افتراضية: AlBadr2025!")
                
        except Exception as e:
            logger.error(f"خطأ في تحميل إعدادات إعادة التعيين: {str(e)}")
            # إنشاء كلمة مرور افتراضية في حالة الخطأ
            self.set_master_password("AlBadr2025!")
    
    def save_config(self):
        """حفظ إعدادات إعادة التعيين"""
        try:
            config = {
                'master_password_hash': self.master_password_hash,
                'salt': self.salt,
                'reset_history': self.reset_history,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info("تم حفظ إعدادات إعادة التعيين")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ إعدادات إعادة التعيين: {str(e)}")
    
    def hash_password(self, password: str, salt: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def set_master_password(self, password: str) -> bool:
        """
        تعيين كلمة المرور الرئيسية
        
        Args:
            password: كلمة المرور الجديدة
            
        Returns:
            True إذا تم التعيين بنجاح، False خلاف ذلك
        """
        try:
            # التحقق من قوة كلمة المرور
            if len(password) < 8:
                raise ValueError("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
            
            # إنشاء salt جديد
            self.salt = secrets.token_hex(16)
            
            # تشفير كلمة المرور
            self.master_password_hash = self.hash_password(password, self.salt)
            
            # حفظ الإعدادات
            self.save_config()
            
            logger.info("تم تعيين كلمة المرور الرئيسية")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تعيين كلمة المرور: {str(e)}")
            return False
    
    def verify_master_password(self, password: str) -> bool:
        """
        التحقق من كلمة المرور الرئيسية
        
        Args:
            password: كلمة المرور للتحقق
            
        Returns:
            True إذا كانت كلمة المرور صحيحة، False خلاف ذلك
        """
        try:
            if not self.master_password_hash or not self.salt:
                logger.error("كلمة المرور الرئيسية غير مكونة")
                return False
            
            password_hash = self.hash_password(password, self.salt)
            return password_hash == self.master_password_hash
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من كلمة المرور: {str(e)}")
            return False
    
    def create_backup_before_reset(self) -> str:
        """
        إنشاء نسخة احتياطية قبل إعادة التعيين
        
        Returns:
            مسار النسخة الاحتياطية
        """
        try:
            # إنشاء مجلد النسخ الاحتياطية
            backup_dir = "reset_backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # اسم النسخة الاحتياطية مع الوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_before_reset_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # إنشاء مجلد النسخة الاحتياطية
            os.makedirs(backup_path)
            
            # نسخ قواعد البيانات
            db_backup_dir = os.path.join(backup_path, "databases")
            os.makedirs(db_backup_dir)
            
            for db_file in self.database_files:
                if os.path.exists(db_file):
                    shutil.copy2(db_file, db_backup_dir)
                    logger.info(f"تم نسخ قاعدة البيانات: {db_file}")
            
            # نسخ المجلدات
            for data_dir in self.data_directories:
                if os.path.exists(data_dir):
                    dest_dir = os.path.join(backup_path, data_dir)
                    shutil.copytree(data_dir, dest_dir)
                    logger.info(f"تم نسخ المجلد: {data_dir}")
            
            # نسخ ملفات الإعدادات
            config_backup_dir = os.path.join(backup_path, "config")
            os.makedirs(config_backup_dir)
            
            for config_file in self.config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, config_backup_dir)
                    logger.info(f"تم نسخ ملف الإعدادات: {config_file}")
            
            # إنشاء ملف معلومات النسخة الاحتياطية
            backup_info = {
                'created_at': datetime.now().isoformat(),
                'backup_type': 'before_reset',
                'databases': [f for f in self.database_files if os.path.exists(f)],
                'directories': [d for d in self.data_directories if os.path.exists(d)],
                'config_files': [c for c in self.config_files if os.path.exists(c)]
            }
            
            with open(os.path.join(backup_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم إنشاء نسخة احتياطية: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
            return ""
    
    def reset_databases(self) -> bool:
        """
        إعادة تعيين قواعد البيانات
        
        Returns:
            True إذا تم الإعادة بنجاح، False خلاف ذلك
        """
        try:
            reset_count = 0
            
            for db_file in self.database_files:
                if os.path.exists(db_file):
                    try:
                        # حذف قاعدة البيانات
                        os.remove(db_file)
                        logger.info(f"تم حذف قاعدة البيانات: {db_file}")
                        reset_count += 1
                        
                    except Exception as e:
                        logger.error(f"خطأ في حذف قاعدة البيانات {db_file}: {str(e)}")
            
            logger.info(f"تم إعادة تعيين {reset_count} قاعدة بيانات")
            return reset_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين قواعد البيانات: {str(e)}")
            return False
    
    def reset_data_directories(self) -> bool:
        """
        إعادة تعيين مجلدات البيانات
        
        Returns:
            True إذا تم الإعادة بنجاح، False خلاف ذلك
        """
        try:
            reset_count = 0
            
            for data_dir in self.data_directories:
                if os.path.exists(data_dir):
                    try:
                        # حذف المجلد وإعادة إنشاؤه
                        shutil.rmtree(data_dir)
                        os.makedirs(data_dir)
                        logger.info(f"تم إعادة تعيين المجلد: {data_dir}")
                        reset_count += 1
                        
                    except Exception as e:
                        logger.error(f"خطأ في إعادة تعيين المجلد {data_dir}: {str(e)}")
            
            logger.info(f"تم إعادة تعيين {reset_count} مجلد")
            return reset_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين مجلدات البيانات: {str(e)}")
            return False
    
    def reset_config_files(self, keep_reset_config: bool = True) -> bool:
        """
        إعادة تعيين ملفات الإعدادات
        
        Args:
            keep_reset_config: الاحتفاظ بإعدادات إعادة التعيين
            
        Returns:
            True إذا تم الإعادة بنجاح، False خلاف ذلك
        """
        try:
            reset_count = 0
            
            for config_file in self.config_files:
                # تجاهل ملف إعدادات إعادة التعيين إذا طُلب الاحتفاظ به
                if keep_reset_config and config_file == self.config_path:
                    continue
                
                if os.path.exists(config_file):
                    try:
                        os.remove(config_file)
                        logger.info(f"تم حذف ملف الإعدادات: {config_file}")
                        reset_count += 1
                        
                    except Exception as e:
                        logger.error(f"خطأ في حذف ملف الإعدادات {config_file}: {str(e)}")
            
            logger.info(f"تم إعادة تعيين {reset_count} ملف إعدادات")
            return reset_count > 0
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تعيين ملفات الإعدادات: {str(e)}")
            return False
    
    def perform_full_reset(self, password: str, create_backup: bool = True) -> Dict:
        """
        تنفيذ إعادة تعيين كاملة للنظام
        
        Args:
            password: كلمة المرور الرئيسية
            create_backup: إنشاء نسخة احتياطية قبل الإعادة
            
        Returns:
            نتائج عملية الإعادة
        """
        try:
            # التحقق من كلمة المرور
            if not self.verify_master_password(password):
                return {
                    'success': False,
                    'error': 'كلمة المرور غير صحيحة',
                    'timestamp': datetime.now().isoformat()
                }
            
            reset_results = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'backup_path': '',
                'databases_reset': False,
                'directories_reset': False,
                'config_reset': False,
                'errors': []
            }
            
            # إنشاء نسخة احتياطية
            if create_backup:
                backup_path = self.create_backup_before_reset()
                reset_results['backup_path'] = backup_path
                
                if not backup_path:
                    reset_results['errors'].append('فشل في إنشاء النسخة الاحتياطية')
            
            # إعادة تعيين قواعد البيانات
            try:
                reset_results['databases_reset'] = self.reset_databases()
            except Exception as e:
                reset_results['errors'].append(f'خطأ في إعادة تعيين قواعد البيانات: {str(e)}')
            
            # إعادة تعيين مجلدات البيانات
            try:
                reset_results['directories_reset'] = self.reset_data_directories()
            except Exception as e:
                reset_results['errors'].append(f'خطأ في إعادة تعيين المجلدات: {str(e)}')
            
            # إعادة تعيين ملفات الإعدادات (مع الاحتفاظ بإعدادات إعادة التعيين)
            try:
                reset_results['config_reset'] = self.reset_config_files(keep_reset_config=True)
            except Exception as e:
                reset_results['errors'].append(f'خطأ في إعادة تعيين ملفات الإعدادات: {str(e)}')
            
            # تسجيل عملية الإعادة في التاريخ
            reset_record = {
                'timestamp': reset_results['timestamp'],
                'backup_created': bool(reset_results['backup_path']),
                'backup_path': reset_results['backup_path'],
                'databases_reset': reset_results['databases_reset'],
                'directories_reset': reset_results['directories_reset'],
                'config_reset': reset_results['config_reset'],
                'errors_count': len(reset_results['errors'])
            }
            
            self.reset_history.append(reset_record)
            
            # الاحتفاظ بآخر 10 سجلات فقط
            if len(self.reset_history) > 10:
                self.reset_history = self.reset_history[-10:]
            
            # حفظ التاريخ المحدث
            self.save_config()
            
            # تحديد نجاح العملية الإجمالي
            reset_results['success'] = (
                reset_results['databases_reset'] or 
                reset_results['directories_reset'] or 
                reset_results['config_reset']
            ) and len(reset_results['errors']) == 0
            
            if reset_results['success']:
                logger.info("تم تنفيذ إعادة التعيين الكاملة بنجاح")
            else:
                logger.warning(f"تم تنفيذ إعادة التعيين مع أخطاء: {reset_results['errors']}")
            
            return reset_results
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ إعادة التعيين: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_reset_history(self) -> List[Dict]:
        """
        الحصول على تاريخ عمليات إعادة التعيين
        
        Returns:
            قائمة بسجلات إعادة التعيين
        """
        return self.reset_history.copy()
    
    def get_system_status(self) -> Dict:
        """
        الحصول على حالة النظام
        
        Returns:
            معلومات حالة النظام
        """
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'databases': {},
                'directories': {},
                'config_files': {},
                'total_size': 0
            }
            
            # فحص قواعد البيانات
            for db_file in self.database_files:
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    status['databases'][db_file] = {
                        'exists': True,
                        'size': size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(db_file)).isoformat()
                    }
                    status['total_size'] += size
                else:
                    status['databases'][db_file] = {'exists': False}
            
            # فحص المجلدات
            for data_dir in self.data_directories:
                if os.path.exists(data_dir):
                    # حساب حجم المجلد
                    total_size = 0
                    file_count = 0
                    
                    for dirpath, dirnames, filenames in os.walk(data_dir):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                size = os.path.getsize(filepath)
                                total_size += size
                                file_count += 1
                            except:
                                pass
                    
                    status['directories'][data_dir] = {
                        'exists': True,
                        'size': total_size,
                        'file_count': file_count,
                        'modified': datetime.fromtimestamp(os.path.getmtime(data_dir)).isoformat()
                    }
                    status['total_size'] += total_size
                else:
                    status['directories'][data_dir] = {'exists': False}
            
            # فحص ملفات الإعدادات
            for config_file in self.config_files:
                if os.path.exists(config_file):
                    size = os.path.getsize(config_file)
                    status['config_files'][config_file] = {
                        'exists': True,
                        'size': size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(config_file)).isoformat()
                    }
                    status['total_size'] += size
                else:
                    status['config_files'][config_file] = {'exists': False}
            
            return status
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة النظام: {str(e)}")
            return {'error': str(e)}
    
    def create_reset_confirmation_dialog(self) -> str:
        """
        إنشاء HTML لنافذة تأكيد إعادة التعيين
        
        Returns:
            كود HTML
        """
        return '''
<div id="resetConfirmationModal" class="modal" style="display: none;">
    <div class="modal-content">
        <div class="modal-header">
            <h2>⚠️ تأكيد إعادة تعيين النظام</h2>
            <span class="close" onclick="closeResetModal()">&times;</span>
        </div>
        <div class="modal-body">
            <div class="warning-message">
                <p><strong>تحذير:</strong> هذه العملية ستقوم بحذف جميع البيانات نهائياً!</p>
                <p>سيتم حذف:</p>
                <ul>
                    <li>جميع المنتجات والمبيعات</li>
                    <li>بيانات الزبائن والشركات</li>
                    <li>سجلات الضمان والديون</li>
                    <li>صور المنتجات والفواتير</li>
                    <li>إعدادات النظام</li>
                </ul>
            </div>
            
            <div class="backup-option">
                <label>
                    <input type="checkbox" id="createBackupBeforeReset" checked>
                    إنشاء نسخة احتياطية قبل الحذف
                </label>
            </div>
            
            <div class="password-input">
                <label for="masterPassword">كلمة المرور الرئيسية:</label>
                <input type="password" id="masterPassword" placeholder="أدخل كلمة المرور الرئيسية">
                <small>كلمة المرور الافتراضية: AlBadr2025!</small>
            </div>
            
            <div class="confirmation-text">
                <label for="confirmationText">اكتب "إعادة تعيين" للتأكيد:</label>
                <input type="text" id="confirmationText" placeholder="إعادة تعيين">
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="closeResetModal()">إلغاء</button>
            <button type="button" class="btn btn-danger" onclick="performSystemReset()" id="confirmResetBtn" disabled>
                تأكيد إعادة التعيين
            </button>
        </div>
    </div>
</div>

<style>
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background-color: var(--color-card);
    border-radius: var(--size-border-radius-lg);
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 20px var(--color-shadow-heavy);
}

.modal-header {
    padding: var(--size-spacing-lg);
    border-bottom: var(--size-border-width) solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    color: var(--color-error);
}

.close {
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
    color: var(--color-text-muted);
}

.close:hover {
    color: var(--color-error);
}

.modal-body {
    padding: var(--size-spacing-lg);
}

.warning-message {
    background-color: var(--color-error-light);
    border: var(--size-border-width) solid var(--color-error);
    border-radius: var(--size-border-radius);
    padding: var(--size-spacing-md);
    margin-bottom: var(--size-spacing-lg);
}

.warning-message ul {
    margin: var(--size-spacing-sm) 0;
    padding-right: var(--size-spacing-lg);
}

.backup-option,
.password-input,
.confirmation-text {
    margin-bottom: var(--size-spacing-lg);
}

.backup-option label {
    display: flex;
    align-items: center;
    gap: var(--size-spacing-sm);
}

.password-input label,
.confirmation-text label {
    display: block;
    margin-bottom: var(--size-spacing-sm);
    font-weight: 600;
}

.password-input input,
.confirmation-text input {
    width: 100%;
    padding: var(--size-spacing-sm);
    border: var(--size-border-width) solid var(--color-border);
    border-radius: var(--size-border-radius);
    font-size: var(--size-text-base);
}

.password-input small {
    display: block;
    margin-top: var(--size-spacing-xs);
    color: var(--color-text-muted);
    font-size: var(--size-text-sm);
}

.modal-footer {
    padding: var(--size-spacing-lg);
    border-top: var(--size-border-width) solid var(--color-border);
    display: flex;
    justify-content: flex-end;
    gap: var(--size-spacing-md);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>'''
    
    def create_reset_javascript(self) -> str:
        """
        إنشاء JavaScript لإدارة إعادة التعيين
        
        Returns:
            كود JavaScript
        """
        return '''
// إدارة نافذة إعادة التعيين
function showResetModal() {
    document.getElementById('resetConfirmationModal').style.display = 'flex';
    
    // إعادة تعيين الحقول
    document.getElementById('masterPassword').value = '';
    document.getElementById('confirmationText').value = '';
    document.getElementById('confirmResetBtn').disabled = true;
    
    // إضافة مستمعي الأحداث
    document.getElementById('masterPassword').addEventListener('input', validateResetForm);
    document.getElementById('confirmationText').addEventListener('input', validateResetForm);
}

function closeResetModal() {
    document.getElementById('resetConfirmationModal').style.display = 'none';
}

function validateResetForm() {
    const password = document.getElementById('masterPassword').value;
    const confirmation = document.getElementById('confirmationText').value;
    const confirmBtn = document.getElementById('confirmResetBtn');
    
    // التحقق من أن كلمة المرور والتأكيد مدخلان
    const isValid = password.length > 0 && confirmation === 'إعادة تعيين';
    
    confirmBtn.disabled = !isValid;
    
    if (isValid) {
        confirmBtn.style.backgroundColor = 'var(--color-error)';
    } else {
        confirmBtn.style.backgroundColor = 'var(--color-button-secondary)';
    }
}

async function performSystemReset() {
    const password = document.getElementById('masterPassword').value;
    const createBackup = document.getElementById('createBackupBeforeReset').checked;
    
    // تأكيد أخير
    if (!confirm('هل أنت متأكد من رغبتك في إعادة تعيين النظام؟ هذه العملية لا يمكن التراجع عنها!')) {
        return;
    }
    
    // إظهار مؤشر التحميل
    const confirmBtn = document.getElementById('confirmResetBtn');
    const originalText = confirmBtn.textContent;
    confirmBtn.textContent = 'جاري إعادة التعيين...';
    confirmBtn.disabled = true;
    
    try {
        // إرسال طلب إعادة التعيين إلى الخادم
        const response = await fetch('/api/system/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                password: password,
                create_backup: createBackup
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('تم إعادة تعيين النظام بنجاح!\\n\\n' + 
                  (result.backup_path ? `تم إنشاء نسخة احتياطية في: ${result.backup_path}` : ''));
            
            // إعادة تحميل الصفحة
            window.location.reload();
        } else {
            alert('فشل في إعادة تعيين النظام: ' + (result.error || 'خطأ غير معروف'));
        }
        
    } catch (error) {
        console.error('خطأ في إعادة التعيين:', error);
        alert('حدث خطأ أثناء إعادة التعيين: ' + error.message);
    } finally {
        // إعادة تعيين الزر
        confirmBtn.textContent = originalText;
        confirmBtn.disabled = false;
        closeResetModal();
    }
}

// إغلاق النافذة عند النقر خارجها
window.onclick = function(event) {
    const modal = document.getElementById('resetConfirmationModal');
    if (event.target === modal) {
        closeResetModal();
    }
}

// إضافة اختصار لوحة المفاتيح لإعادة التعيين (Ctrl+Shift+R)
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.shiftKey && event.key === 'R') {
        event.preventDefault();
        showResetModal();
    }
});

// دالة للحصول على حالة النظام
async function getSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const status = await response.json();
        return status;
    } catch (error) {
        console.error('خطأ في الحصول على حالة النظام:', error);
        return null;
    }
}

// دالة لعرض تاريخ إعادة التعيين
async function showResetHistory() {
    try {
        const response = await fetch('/api/system/reset-history');
        const history = await response.json();
        
        if (history.length === 0) {
            alert('لا يوجد تاريخ لعمليات إعادة التعيين');
            return;
        }
        
        let historyText = 'تاريخ عمليات إعادة التعيين:\\n\\n';
        
        history.forEach((record, index) => {
            const date = new Date(record.timestamp).toLocaleString('ar-EG');
            historyText += `${index + 1}. ${date}\\n`;
            historyText += `   - نسخة احتياطية: ${record.backup_created ? 'نعم' : 'لا'}\\n`;
            historyText += `   - قواعد البيانات: ${record.databases_reset ? 'تم' : 'لم يتم'}\\n`;
            historyText += `   - المجلدات: ${record.directories_reset ? 'تم' : 'لم يتم'}\\n`;
            historyText += `   - الإعدادات: ${record.config_reset ? 'تم' : 'لم يتم'}\\n`;
            if (record.errors_count > 0) {
                historyText += `   - أخطاء: ${record.errors_count}\\n`;
            }
            historyText += '\\n';
        });
        
        alert(historyText);
        
    } catch (error) {
        console.error('خطأ في الحصول على تاريخ إعادة التعيين:', error);
        alert('حدث خطأ أثناء الحصول على التاريخ');
    }
}'''


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير إعادة التعيين
    reset_manager = SystemResetManager()
    
    try:
        print("نظام إعادة التعيين جاهز")
        print(f"كلمة المرور الافتراضية: AlBadr2025!")
        
        # عرض حالة النظام
        status = reset_manager.get_system_status()
        print(f"حالة النظام: {len(status.get('databases', {}))} قاعدة بيانات")
        
        # عرض تاريخ إعادة التعيين
        history = reset_manager.get_reset_history()
        print(f"تاريخ إعادة التعيين: {len(history)} عملية")
        
        # مثال على تغيير كلمة المرور
        # reset_manager.set_master_password("NewPassword123!")
        
        # مثال على إعادة التعيين (تحتاج كلمة مرور صحيحة)
        # result = reset_manager.perform_full_reset("AlBadr2025!", create_backup=True)
        # print(f"نتيجة إعادة التعيين: {result}")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

