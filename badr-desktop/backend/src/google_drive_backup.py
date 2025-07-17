"""
نظام النسخ الاحتياطي إلى Google Drive لبرنامج البدر للإنارة
يتطلب إعداد Google Drive API
"""

import os
import json
from datetime import datetime
from typing import Optional, List
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDriveBackup:
    """نظام النسخ الاحتياطي إلى Google Drive"""
    
    # نطاقات الصلاحيات المطلوبة
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        تهيئة نظام النسخ الاحتياطي إلى Google Drive
        
        Args:
            credentials_file: ملف بيانات اعتماد Google API
            token_file: ملف رمز الوصول المحفوظ
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("مكتبات Google Drive غير متوفرة. يرجى تثبيتها باستخدام: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.backup_folder_id = None
        
    def authenticate(self) -> bool:
        """
        المصادقة مع Google Drive API
        
        Returns:
            True إذا تمت المصادقة بنجاح، False خلاف ذلك
        """
        try:
            creds = None
            
            # تحميل الرمز المحفوظ إذا كان موجوداً
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # إذا لم تكن هناك بيانات اعتماد صالحة، اطلب من المستخدم تسجيل الدخول
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"ملف بيانات الاعتماد غير موجود: {self.credentials_file}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # حفظ بيانات الاعتماد للاستخدام التالي
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # إنشاء خدمة Google Drive
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("تم تسجيل الدخول إلى Google Drive بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في المصادقة مع Google Drive: {str(e)}")
            return False
    
    def create_backup_folder(self, folder_name: str = "البدر للإنارة - نسخ احتياطية") -> Optional[str]:
        """
        إنشاء مجلد للنسخ الاحتياطية في Google Drive
        
        Args:
            folder_name: اسم المجلد
            
        Returns:
            معرف المجلد إذا تم إنشاؤه بنجاح، None خلاف ذلك
        """
        try:
            if not self.service:
                logger.error("يجب المصادقة أولاً")
                return None
            
            # البحث عن المجلد إذا كان موجوداً
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # المجلد موجود
                folder_id = folders[0]['id']
                logger.info(f"تم العثور على مجلد النسخ الاحتياطية: {folder_id}")
            else:
                # إنشاء مجلد جديد
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                folder_id = folder.get('id')
                logger.info(f"تم إنشاء مجلد النسخ الاحتياطية: {folder_id}")
            
            self.backup_folder_id = folder_id
            return folder_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجلد النسخ الاحتياطية: {str(e)}")
            return None
    
    def upload_file(self, file_path: str, file_name: Optional[str] = None) -> Optional[str]:
        """
        رفع ملف إلى Google Drive
        
        Args:
            file_path: مسار الملف المحلي
            file_name: اسم الملف في Google Drive (اختياري)
            
        Returns:
            معرف الملف إذا تم الرفع بنجاح، None خلاف ذلك
        """
        try:
            if not self.service:
                logger.error("يجب المصادقة أولاً")
                return None
            
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return None
            
            # تحديد اسم الملف
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # إعداد بيانات الملف
            file_metadata = {'name': file_name}
            
            # إضافة الملف إلى مجلد النسخ الاحتياطية إذا كان موجوداً
            if self.backup_folder_id:
                file_metadata['parents'] = [self.backup_folder_id]
            
            # رفع الملف
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"تم رفع الملف بنجاح: {file_name} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            logger.error(f"خطأ في رفع الملف: {str(e)}")
            return None
    
    def upload_backup(self, backup_file_path: str) -> bool:
        """
        رفع ملف نسخة احتياطية إلى Google Drive
        
        Args:
            backup_file_path: مسار ملف النسخة الاحتياطية
            
        Returns:
            True إذا تم الرفع بنجاح، False خلاف ذلك
        """
        try:
            # المصادقة
            if not self.authenticate():
                return False
            
            # إنشاء مجلد النسخ الاحتياطية
            if not self.create_backup_folder():
                return False
            
            # إنشاء اسم ملف مع الطابع الزمني
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = os.path.basename(backup_file_path)
            name_without_ext = os.path.splitext(original_name)[0]
            extension = os.path.splitext(original_name)[1]
            drive_file_name = f"{name_without_ext}_{timestamp}{extension}"
            
            # رفع الملف
            file_id = self.upload_file(backup_file_path, drive_file_name)
            
            if file_id:
                logger.info(f"تم رفع النسخة الاحتياطية إلى Google Drive بنجاح")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"خطأ في رفع النسخة الاحتياطية: {str(e)}")
            return False
    
    def list_backup_files(self) -> List[dict]:
        """
        عرض قائمة ملفات النسخ الاحتياطية في Google Drive
        
        Returns:
            قائمة بمعلومات الملفات
        """
        try:
            if not self.service:
                logger.error("يجب المصادقة أولاً")
                return []
            
            if not self.backup_folder_id:
                logger.error("مجلد النسخ الاحتياطية غير موجود")
                return []
            
            # البحث عن الملفات في مجلد النسخ الاحتياطية
            results = self.service.files().list(
                q=f"'{self.backup_folder_id}' in parents",
                fields="files(id, name, size, createdTime, modifiedTime)",
                orderBy="createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            logger.error(f"خطأ في عرض ملفات النسخ الاحتياطية: {str(e)}")
            return []
    
    def delete_old_backups(self, keep_count: int = 10):
        """
        حذف النسخ الاحتياطية القديمة من Google Drive
        
        Args:
            keep_count: عدد النسخ المراد الاحتفاظ بها
        """
        try:
            files = self.list_backup_files()
            
            if len(files) > keep_count:
                files_to_delete = files[keep_count:]
                
                for file in files_to_delete:
                    self.service.files().delete(fileId=file['id']).execute()
                    logger.info(f"تم حذف النسخة الاحتياطية القديمة: {file['name']}")
                    
        except Exception as e:
            logger.error(f"خطأ في حذف النسخ الاحتياطية القديمة: {str(e)}")


class AutoBackupManager:
    """مدير النسخ الاحتياطي التلقائي"""
    
    def __init__(self, backup_system, google_drive_backup=None):
        """
        تهيئة مدير النسخ الاحتياطي التلقائي
        
        Args:
            backup_system: نظام النسخ الاحتياطي المحلي
            google_drive_backup: نظام النسخ الاحتياطي إلى Google Drive (اختياري)
        """
        self.backup_system = backup_system
        self.google_drive_backup = google_drive_backup
        
    def create_and_upload_backup(self, backup_type: str = "full", upload_to_drive: bool = True) -> bool:
        """
        إنشاء نسخة احتياطية ورفعها إلى Google Drive
        
        Args:
            backup_type: نوع النسخة الاحتياطية
            upload_to_drive: رفع إلى Google Drive
            
        Returns:
            True إذا تمت العملية بنجاح، False خلاف ذلك
        """
        try:
            # إنشاء النسخة الاحتياطية المحلية
            if backup_type == "json":
                backup_file = self.backup_system.backup_database_to_json()
            elif backup_type == "excel":
                backup_file = self.backup_system.backup_database_to_excel()
            elif backup_type == "db":
                backup_file = self.backup_system.backup_database_file()
            else:  # full
                backup_file = self.backup_system.create_full_backup()
            
            # رفع إلى Google Drive إذا كان مطلوباً
            if upload_to_drive and self.google_drive_backup:
                success = self.google_drive_backup.upload_backup(backup_file)
                if success:
                    logger.info("تم رفع النسخة الاحتياطية إلى Google Drive")
                else:
                    logger.warning("فشل في رفع النسخة الاحتياطية إلى Google Drive")
            
            # تنظيف النسخ القديمة
            self.backup_system.cleanup_old_backups()
            if upload_to_drive and self.google_drive_backup:
                self.google_drive_backup.delete_old_backups()
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ورفع النسخة الاحتياطية: {str(e)}")
            return False


# مثال على الاستخدام
if __name__ == "__main__":
    from backup_system import BackupSystem
    
    # إنشاء أنظمة النسخ الاحتياطي
    backup_system = BackupSystem("database.sqlite", "backups")
    
    if GOOGLE_DRIVE_AVAILABLE:
        google_drive_backup = GoogleDriveBackup()
        
        # إنشاء مدير النسخ الاحتياطي التلقائي
        auto_backup = AutoBackupManager(backup_system, google_drive_backup)
        
        # إنشاء ورفع نسخة احتياطية شاملة
        success = auto_backup.create_and_upload_backup("full", upload_to_drive=True)
        
        if success:
            print("تم إنشاء ورفع النسخة الاحتياطية بنجاح")
        else:
            print("فشل في إنشاء أو رفع النسخة الاحتياطية")
    else:
        print("مكتبات Google Drive غير متوفرة. سيتم إنشاء نسخة احتياطية محلية فقط.")
        backup_file = backup_system.create_full_backup()
        print(f"تم إنشاء النسخة الاحتياطية المحلية: {backup_file}")

