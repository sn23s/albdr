"""
نظام النسخ الاحتياطي لبرنامج البدر للإنارة
يدعم النسخ الاحتياطي إلى ملفات محلية وGoogle Drive
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
import shutil
import zipfile
from typing import Dict, List, Optional
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupSystem:
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        """
        تهيئة نظام النسخ الاحتياطي
        
        Args:
            db_path: مسار قاعدة البيانات
            backup_dir: مجلد النسخ الاحتياطي
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.ensure_backup_directory()
        
    def ensure_backup_directory(self):
        """إنشاء مجلد النسخ الاحتياطي إذا لم يكن موجوداً"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"تم إنشاء مجلد النسخ الاحتياطي: {self.backup_dir}")
    
    def get_timestamp(self) -> str:
        """الحصول على طابع زمني للنسخة الاحتياطية"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def backup_database_to_json(self) -> str:
        """
        نسخ احتياطي لقاعدة البيانات بصيغة JSON
        
        Returns:
            مسار ملف النسخة الاحتياطية
        """
        try:
            timestamp = self.get_timestamp()
            backup_filename = f"backup_json_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # الحصول على أسماء الجداول
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            backup_data = {}
            
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # تجاهل جداول النظام
                    # الحصول على بيانات الجدول
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    # الحصول على أسماء الأعمدة
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    # تحويل البيانات إلى قائمة من القواميس
                    table_data = []
                    for row in rows:
                        row_dict = {}
                        for i, value in enumerate(row):
                            row_dict[columns[i]] = value
                        table_data.append(row_dict)
                    
                    backup_data[table_name] = table_data
            
            conn.close()
            
            # حفظ البيانات في ملف JSON
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم إنشاء نسخة احتياطية JSON: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية JSON: {str(e)}")
            raise
    
    def backup_database_to_excel(self) -> str:
        """
        نسخ احتياطي لقاعدة البيانات بصيغة Excel
        
        Returns:
            مسار ملف النسخة الاحتياطية
        """
        try:
            timestamp = self.get_timestamp()
            backup_filename = f"backup_excel_{timestamp}.xlsx"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            
            # الحصول على أسماء الجداول
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # إنشاء ملف Excel مع أوراق متعددة
            with pd.ExcelWriter(backup_path, engine='openpyxl') as writer:
                for table in tables:
                    table_name = table[0]
                    if table_name != 'sqlite_sequence':  # تجاهل جداول النظام
                        # قراءة بيانات الجدول
                        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                        
                        # كتابة البيانات في ورقة منفصلة
                        df.to_excel(writer, sheet_name=table_name, index=False)
            
            conn.close()
            
            logger.info(f"تم إنشاء نسخة احتياطية Excel: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية Excel: {str(e)}")
            raise
    
    def backup_database_to_csv(self) -> List[str]:
        """
        نسخ احتياطي لقاعدة البيانات بصيغة CSV (ملف منفصل لكل جدول)
        
        Returns:
            قائمة بمسارات ملفات النسخ الاحتياطية
        """
        try:
            timestamp = self.get_timestamp()
            csv_dir = os.path.join(self.backup_dir, f"backup_csv_{timestamp}")
            os.makedirs(csv_dir, exist_ok=True)
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            
            # الحصول على أسماء الجداول
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            backup_files = []
            
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # تجاهل جداول النظام
                    # قراءة بيانات الجدول
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    
                    # حفظ البيانات في ملف CSV
                    csv_filename = f"{table_name}.csv"
                    csv_path = os.path.join(csv_dir, csv_filename)
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    backup_files.append(csv_path)
            
            conn.close()
            
            logger.info(f"تم إنشاء نسخ احتياطية CSV في: {csv_dir}")
            return backup_files
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخ الاحتياطية CSV: {str(e)}")
            raise
    
    def backup_database_file(self) -> str:
        """
        نسخ احتياطي مباشر لملف قاعدة البيانات
        
        Returns:
            مسار ملف النسخة الاحتياطية
        """
        try:
            timestamp = self.get_timestamp()
            backup_filename = f"backup_db_{timestamp}.sqlite"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # نسخ ملف قاعدة البيانات
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"تم إنشاء نسخة احتياطية لقاعدة البيانات: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"خطأ في نسخ ملف قاعدة البيانات: {str(e)}")
            raise
    
    def create_full_backup(self) -> str:
        """
        إنشاء نسخة احتياطية شاملة (جميع الصيغ مضغوطة في ملف واحد)
        
        Returns:
            مسار ملف النسخة الاحتياطية المضغوطة
        """
        try:
            timestamp = self.get_timestamp()
            
            # إنشاء النسخ الاحتياطية بجميع الصيغ
            json_backup = self.backup_database_to_json()
            excel_backup = self.backup_database_to_excel()
            csv_backups = self.backup_database_to_csv()
            db_backup = self.backup_database_file()
            
            # إنشاء ملف مضغوط
            zip_filename = f"full_backup_{timestamp}.zip"
            zip_path = os.path.join(self.backup_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # إضافة ملف JSON
                zipf.write(json_backup, os.path.basename(json_backup))
                
                # إضافة ملف Excel
                zipf.write(excel_backup, os.path.basename(excel_backup))
                
                # إضافة ملفات CSV
                for csv_file in csv_backups:
                    arcname = f"csv/{os.path.basename(csv_file)}"
                    zipf.write(csv_file, arcname)
                
                # إضافة ملف قاعدة البيانات
                zipf.write(db_backup, os.path.basename(db_backup))
            
            # حذف الملفات المؤقتة
            os.remove(json_backup)
            os.remove(excel_backup)
            os.remove(db_backup)
            
            # حذف مجلد CSV
            csv_dir = os.path.dirname(csv_backups[0]) if csv_backups else None
            if csv_dir and os.path.exists(csv_dir):
                shutil.rmtree(csv_dir)
            
            logger.info(f"تم إنشاء نسخة احتياطية شاملة: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية الشاملة: {str(e)}")
            raise
    
    def schedule_automatic_backup(self, backup_type: str = "full", interval_hours: int = 24):
        """
        جدولة النسخ الاحتياطي التلقائي
        
        Args:
            backup_type: نوع النسخة الاحتياطية (json, excel, csv, db, full)
            interval_hours: الفترة الزمنية بالساعات بين النسخ الاحتياطية
        """
        # هذه الدالة تحتاج إلى تطبيق مع مكتبة جدولة مثل APScheduler
        # سيتم تطبيقها في الإصدار المتقدم
        pass
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """
        حذف النسخ الاحتياطية القديمة والاحتفاظ بعدد محدد من النسخ الحديثة
        
        Args:
            keep_count: عدد النسخ الاحتياطية المراد الاحتفاظ بها
        """
        try:
            # الحصول على قائمة ملفات النسخ الاحتياطية
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("backup_") or filename.startswith("full_backup_"):
                    file_path = os.path.join(self.backup_dir, filename)
                    if os.path.isfile(file_path):
                        backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # ترتيب الملفات حسب تاريخ التعديل (الأحدث أولاً)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # حذف الملفات الزائدة
            if len(backup_files) > keep_count:
                files_to_delete = backup_files[keep_count:]
                for file_path, _ in files_to_delete:
                    os.remove(file_path)
                    logger.info(f"تم حذف النسخة الاحتياطية القديمة: {file_path}")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف النسخ الاحتياطية القديمة: {str(e)}")
    
    def restore_from_json(self, json_file_path: str):
        """
        استعادة البيانات من ملف JSON
        
        Args:
            json_file_path: مسار ملف JSON
        """
        try:
            # قراءة بيانات JSON
            with open(json_file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # الاتصال بقاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # استعادة البيانات لكل جدول
            for table_name, table_data in backup_data.items():
                if table_data:  # إذا كان الجدول يحتوي على بيانات
                    # حذف البيانات الموجودة
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # إدراج البيانات المستعادة
                    columns = list(table_data[0].keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    
                    for row in table_data:
                        values = [row[col] for col in columns]
                        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم استعادة البيانات من: {json_file_path}")
            
        except Exception as e:
            logger.error(f"خطأ في استعادة البيانات من JSON: {str(e)}")
            raise


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء نظام النسخ الاحتياطي
    backup_system = BackupSystem("database.sqlite", "backups")
    
    # إنشاء نسخة احتياطية شاملة
    backup_file = backup_system.create_full_backup()
    print(f"تم إنشاء النسخة الاحتياطية: {backup_file}")
    
    # تنظيف النسخ القديمة
    backup_system.cleanup_old_backups(keep_count=5)

