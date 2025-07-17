"""
نظام إدارة صور المنتجات لبرنامج البدر للإنارة
يدعم رفع وتحسين وإدارة صور المنتجات
"""

import os
import shutil
from PIL import Image, ImageEnhance, ImageFilter
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import json
import uuid

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductImageManager:
    """نظام إدارة صور المنتجات"""
    
    def __init__(self, images_dir: str = "product_images"):
        """
        تهيئة نظام إدارة الصور
        
        Args:
            images_dir: مجلد حفظ الصور
        """
        self.images_dir = images_dir
        self.thumbnails_dir = os.path.join(images_dir, "thumbnails")
        self.originals_dir = os.path.join(images_dir, "originals")
        self.processed_dir = os.path.join(images_dir, "processed")
        
        # إنشاء المجلدات
        self.create_directories()
        
        # إعدادات الصور
        self.max_size = (1920, 1080)  # الحد الأقصى لحجم الصورة
        self.thumbnail_size = (300, 300)  # حجم الصورة المصغرة
        self.quality = 85  # جودة الضغط
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
    def create_directories(self):
        """إنشاء مجلدات الصور"""
        directories = [
            self.images_dir,
            self.thumbnails_dir,
            self.originals_dir,
            self.processed_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"تم إنشاء مجلد: {directory}")
    
    def validate_image(self, file_path: str) -> bool:
        """
        التحقق من صحة ملف الصورة
        
        Args:
            file_path: مسار ملف الصورة
            
        Returns:
            True إذا كانت الصورة صالحة، False خلاف ذلك
        """
        try:
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            # التحقق من امتداد الملف
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                logger.error(f"صيغة الملف غير مدعومة: {file_ext}")
                return False
            
            # التحقق من إمكانية فتح الصورة
            with Image.open(file_path) as img:
                img.verify()
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الصورة: {str(e)}")
            return False
    
    def generate_unique_filename(self, original_filename: str, product_id: str = None) -> str:
        """
        إنشاء اسم ملف فريد
        
        Args:
            original_filename: اسم الملف الأصلي
            product_id: معرف المنتج (اختياري)
            
        Returns:
            اسم الملف الفريد
        """
        # الحصول على امتداد الملف
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # إنشاء معرف فريد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if product_id:
            filename = f"product_{product_id}_{timestamp}_{unique_id}{file_ext}"
        else:
            filename = f"image_{timestamp}_{unique_id}{file_ext}"
        
        return filename
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        حساب hash للملف لتجنب التكرار
        
        Args:
            file_path: مسار الملف
            
        Returns:
            hash الملف
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"خطأ في حساب hash الملف: {str(e)}")
            return ""
    
    def resize_image(self, image: Image.Image, max_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> Image.Image:
        """
        تغيير حجم الصورة
        
        Args:
            image: الصورة
            max_size: الحد الأقصى للحجم
            maintain_aspect: الحفاظ على نسبة العرض إلى الارتفاع
            
        Returns:
            الصورة بعد تغيير الحجم
        """
        try:
            if maintain_aspect:
                image.thumbnail(max_size, Image.LANCZOS)
            else:
                image = image.resize(max_size, Image.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"خطأ في تغيير حجم الصورة: {str(e)}")
            return image
    
    def enhance_image(self, image: Image.Image, 
                     brightness: float = 1.0, contrast: float = 1.0, 
                     sharpness: float = 1.0, color: float = 1.0) -> Image.Image:
        """
        تحسين جودة الصورة
        
        Args:
            image: الصورة
            brightness: السطوع (1.0 = طبيعي)
            contrast: التباين (1.0 = طبيعي)
            sharpness: الحدة (1.0 = طبيعي)
            color: التشبع اللوني (1.0 = طبيعي)
            
        Returns:
            الصورة المحسنة
        """
        try:
            # تحسين السطوع
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            
            # تحسين التباين
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            
            # تحسين الحدة
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpness)
            
            # تحسين التشبع اللوني
            if color != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(color)
            
            return image
            
        except Exception as e:
            logger.error(f"خطأ في تحسين الصورة: {str(e)}")
            return image
    
    def add_watermark(self, image: Image.Image, watermark_text: str = None, 
                     watermark_image: str = None, opacity: float = 0.3) -> Image.Image:
        """
        إضافة علامة مائية للصورة
        
        Args:
            image: الصورة
            watermark_text: نص العلامة المائية
            watermark_image: مسار صورة العلامة المائية
            opacity: شفافية العلامة المائية
            
        Returns:
            الصورة مع العلامة المائية
        """
        try:
            # إنشاء نسخة من الصورة
            watermarked = image.copy()
            
            if watermark_text:
                # إضافة علامة مائية نصية
                from PIL import ImageDraw, ImageFont
                
                draw = ImageDraw.Draw(watermarked)
                
                # محاولة استخدام خط مخصص
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except:
                    font = ImageFont.load_default()
                
                # حساب موقع النص
                text_width = draw.textlength(watermark_text, font=font)
                text_height = 36  # تقدير ارتفاع النص
                
                x = watermarked.width - text_width - 20
                y = watermarked.height - text_height - 20
                
                # رسم النص مع شفافية
                overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.text((x, y), watermark_text, font=font, 
                                fill=(255, 255, 255, int(255 * opacity)))
                
                # دمج العلامة المائية مع الصورة
                watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
                watermarked = watermarked.convert('RGB')
            
            elif watermark_image and os.path.exists(watermark_image):
                # إضافة علامة مائية من صورة
                with Image.open(watermark_image) as wm_img:
                    # تغيير حجم العلامة المائية
                    wm_size = (watermarked.width // 4, watermarked.height // 4)
                    wm_img = wm_img.resize(wm_size, Image.LANCZOS)
                    
                    # تطبيق الشفافية
                    if wm_img.mode != 'RGBA':
                        wm_img = wm_img.convert('RGBA')
                    
                    # تعديل الشفافية
                    alpha = wm_img.split()[-1]
                    alpha = alpha.point(lambda p: int(p * opacity))
                    wm_img.putalpha(alpha)
                    
                    # حساب موقع العلامة المائية
                    x = watermarked.width - wm_img.width - 20
                    y = watermarked.height - wm_img.height - 20
                    
                    # لصق العلامة المائية
                    watermarked.paste(wm_img, (x, y), wm_img)
            
            return watermarked
            
        except Exception as e:
            logger.error(f"خطأ في إضافة العلامة المائية: {str(e)}")
            return image
    
    def upload_product_image(self, file_path: str, product_id: str, 
                           enhance_settings: Dict = None, 
                           add_watermark: bool = False) -> Dict:
        """
        رفع صورة منتج
        
        Args:
            file_path: مسار ملف الصورة
            product_id: معرف المنتج
            enhance_settings: إعدادات تحسين الصورة
            add_watermark: إضافة علامة مائية
            
        Returns:
            معلومات الصورة المرفوعة
        """
        try:
            # التحقق من صحة الصورة
            if not self.validate_image(file_path):
                raise ValueError("ملف الصورة غير صالح")
            
            # حساب hash الملف
            file_hash = self.calculate_file_hash(file_path)
            
            # إنشاء اسم ملف فريد
            original_filename = os.path.basename(file_path)
            unique_filename = self.generate_unique_filename(original_filename, product_id)
            
            # مسارات الحفظ
            original_path = os.path.join(self.originals_dir, unique_filename)
            processed_path = os.path.join(self.processed_dir, unique_filename)
            thumbnail_path = os.path.join(self.thumbnails_dir, unique_filename)
            
            # نسخ الملف الأصلي
            shutil.copy2(file_path, original_path)
            
            # فتح الصورة للمعالجة
            with Image.open(file_path) as img:
                # تحويل إلى RGB إذا لزم الأمر
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # تحسين الصورة
                if enhance_settings:
                    img = self.enhance_image(
                        img,
                        brightness=enhance_settings.get('brightness', 1.0),
                        contrast=enhance_settings.get('contrast', 1.0),
                        sharpness=enhance_settings.get('sharpness', 1.0),
                        color=enhance_settings.get('color', 1.0)
                    )
                
                # إضافة علامة مائية
                if add_watermark:
                    img = self.add_watermark(img, watermark_text="البدر للإنارة")
                
                # تغيير حجم الصورة الرئيسية
                processed_img = self.resize_image(img, self.max_size)
                
                # حفظ الصورة المعالجة
                processed_img.save(processed_path, 'JPEG', quality=self.quality, optimize=True)
                
                # إنشاء الصورة المصغرة
                thumbnail_img = self.resize_image(img.copy(), self.thumbnail_size)
                thumbnail_img.save(thumbnail_path, 'JPEG', quality=75, optimize=True)
            
            # معلومات الصورة
            image_info = {
                'id': str(uuid.uuid4()),
                'product_id': product_id,
                'original_filename': original_filename,
                'unique_filename': unique_filename,
                'file_hash': file_hash,
                'original_path': original_path,
                'processed_path': processed_path,
                'thumbnail_path': thumbnail_path,
                'upload_date': datetime.now().isoformat(),
                'file_size': os.path.getsize(processed_path),
                'thumbnail_size': os.path.getsize(thumbnail_path)
            }
            
            # حفظ معلومات الصورة
            self.save_image_metadata(image_info)
            
            logger.info(f"تم رفع صورة المنتج {product_id}: {unique_filename}")
            return image_info
            
        except Exception as e:
            logger.error(f"خطأ في رفع صورة المنتج: {str(e)}")
            raise
    
    def save_image_metadata(self, image_info: Dict):
        """
        حفظ معلومات الصورة في ملف JSON
        
        Args:
            image_info: معلومات الصورة
        """
        try:
            metadata_file = os.path.join(self.images_dir, "images_metadata.json")
            
            # قراءة البيانات الموجودة
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # إضافة معلومات الصورة الجديدة
            metadata[image_info['id']] = image_info
            
            # حفظ البيانات المحدثة
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"خطأ في حفظ معلومات الصورة: {str(e)}")
    
    def get_product_images(self, product_id: str) -> List[Dict]:
        """
        الحصول على صور منتج معين
        
        Args:
            product_id: معرف المنتج
            
        Returns:
            قائمة بصور المنتج
        """
        try:
            metadata_file = os.path.join(self.images_dir, "images_metadata.json")
            
            if not os.path.exists(metadata_file):
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # البحث عن صور المنتج
            product_images = []
            for image_id, image_info in metadata.items():
                if image_info.get('product_id') == product_id:
                    product_images.append(image_info)
            
            # ترتيب حسب تاريخ الرفع
            product_images.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
            
            return product_images
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على صور المنتج: {str(e)}")
            return []
    
    def delete_image(self, image_id: str) -> bool:
        """
        حذف صورة
        
        Args:
            image_id: معرف الصورة
            
        Returns:
            True إذا تم الحذف بنجاح، False خلاف ذلك
        """
        try:
            metadata_file = os.path.join(self.images_dir, "images_metadata.json")
            
            if not os.path.exists(metadata_file):
                return False
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if image_id not in metadata:
                logger.warning(f"الصورة غير موجودة: {image_id}")
                return False
            
            image_info = metadata[image_id]
            
            # حذف الملفات
            files_to_delete = [
                image_info.get('original_path'),
                image_info.get('processed_path'),
                image_info.get('thumbnail_path')
            ]
            
            for file_path in files_to_delete:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"تم حذف الملف: {file_path}")
            
            # حذف من البيانات الوصفية
            del metadata[image_id]
            
            # حفظ البيانات المحدثة
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حذف الصورة: {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف الصورة: {str(e)}")
            return False
    
    def cleanup_orphaned_files(self):
        """تنظيف الملفات المهجورة"""
        try:
            metadata_file = os.path.join(self.images_dir, "images_metadata.json")
            
            if not os.path.exists(metadata_file):
                return
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # الحصول على قائمة الملفات المسجلة
            registered_files = set()
            for image_info in metadata.values():
                registered_files.add(image_info.get('original_path'))
                registered_files.add(image_info.get('processed_path'))
                registered_files.add(image_info.get('thumbnail_path'))
            
            # البحث عن الملفات المهجورة
            directories = [self.originals_dir, self.processed_dir, self.thumbnails_dir]
            
            for directory in directories:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if file_path not in registered_files:
                            os.remove(file_path)
                            logger.info(f"تم حذف الملف المهجور: {file_path}")
                            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات المهجورة: {str(e)}")


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير الصور
    image_manager = ProductImageManager("product_images")
    
    # مثال على رفع صورة منتج
    try:
        # إعدادات تحسين الصورة
        enhance_settings = {
            'brightness': 1.1,
            'contrast': 1.2,
            'sharpness': 1.1,
            'color': 1.0
        }
        
        # رفع صورة (يجب أن يكون لديك ملف صورة للاختبار)
        # image_info = image_manager.upload_product_image(
        #     "path/to/product/image.jpg",
        #     "PROD-001",
        #     enhance_settings=enhance_settings,
        #     add_watermark=True
        # )
        # print(f"تم رفع الصورة: {image_info}")
        
        # الحصول على صور منتج
        # product_images = image_manager.get_product_images("PROD-001")
        # print(f"صور المنتج: {len(product_images)}")
        
        print("نظام إدارة الصور جاهز للاستخدام")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

