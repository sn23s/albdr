"""
نظام قراءة QR Code و Barcode لبرنامج البدر للإنارة
يدعم قراءة الرموز من الكاميرا والملفات
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional, List, Dict, Tuple
import logging
import json
from datetime import datetime

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRBarcodeScanner:
    """نظام قراءة QR Code و Barcode"""
    
    def __init__(self):
        """تهيئة نظام القراءة"""
        self.camera = None
        self.is_scanning = False
        
    def start_camera(self, camera_index: int = 0) -> bool:
        """
        تشغيل الكاميرا
        
        Args:
            camera_index: فهرس الكاميرا (0 للكاميرا الافتراضية)
            
        Returns:
            True إذا تم تشغيل الكاميرا بنجاح، False خلاف ذلك
        """
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                logger.error("فشل في تشغيل الكاميرا")
                return False
            
            # تحسين إعدادات الكاميرا
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("تم تشغيل الكاميرا بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تشغيل الكاميرا: {str(e)}")
            return False
    
    def stop_camera(self):
        """إيقاف الكاميرا"""
        try:
            if self.camera:
                self.camera.release()
                self.camera = None
                self.is_scanning = False
                logger.info("تم إيقاف الكاميرا")
        except Exception as e:
            logger.error(f"خطأ في إيقاف الكاميرا: {str(e)}")
    
    def scan_from_camera(self, timeout: int = 30) -> Optional[Dict]:
        """
        قراءة رمز من الكاميرا
        
        Args:
            timeout: مهلة زمنية بالثواني للقراءة
            
        Returns:
            معلومات الرمز المقروء أو None
        """
        try:
            if not self.camera:
                logger.error("الكاميرا غير مشغلة")
                return None
            
            self.is_scanning = True
            start_time = datetime.now()
            
            while self.is_scanning:
                # التحقق من انتهاء المهلة الزمنية
                if (datetime.now() - start_time).seconds > timeout:
                    logger.warning("انتهت المهلة الزمنية للقراءة")
                    break
                
                # قراءة إطار من الكاميرا
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # قراءة الرموز من الإطار
                codes = self.decode_frame(frame)
                
                if codes:
                    # تم العثور على رمز
                    code_info = codes[0]  # أخذ أول رمز
                    logger.info(f"تم قراءة رمز: {code_info['data']}")
                    return code_info
                
                # عرض الإطار (اختياري للتطبيقات المرئية)
                cv2.imshow('QR/Barcode Scanner', frame)
                
                # التحقق من الضغط على مفتاح للخروج
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyAllWindows()
            return None
            
        except Exception as e:
            logger.error(f"خطأ في قراءة الرمز من الكاميرا: {str(e)}")
            return None
        finally:
            self.is_scanning = False
    
    def scan_from_file(self, file_path: str) -> List[Dict]:
        """
        قراءة رموز من ملف صورة
        
        Args:
            file_path: مسار ملف الصورة
            
        Returns:
            قائمة بمعلومات الرموز المقروءة
        """
        try:
            # قراءة الصورة
            image = cv2.imread(file_path)
            if image is None:
                logger.error(f"فشل في قراءة الصورة: {file_path}")
                return []
            
            # قراءة الرموز من الصورة
            codes = self.decode_frame(image)
            
            if codes:
                logger.info(f"تم قراءة {len(codes)} رمز من الصورة")
            else:
                logger.warning("لم يتم العثور على أي رموز في الصورة")
            
            return codes
            
        except Exception as e:
            logger.error(f"خطأ في قراءة الرمز من الملف: {str(e)}")
            return []
    
    def decode_frame(self, frame) -> List[Dict]:
        """
        قراءة الرموز من إطار صورة
        
        Args:
            frame: إطار الصورة
            
        Returns:
            قائمة بمعلومات الرموز المقروءة
        """
        try:
            # تحويل الصورة إلى رمادي
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # قراءة الرموز
            decoded_objects = pyzbar.decode(gray)
            
            codes = []
            for obj in decoded_objects:
                # استخراج معلومات الرمز
                code_info = {
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'rect': obj.rect,
                    'polygon': obj.polygon,
                    'timestamp': datetime.now().isoformat()
                }
                codes.append(code_info)
                
                # رسم مربع حول الرمز (للعرض المرئي)
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = np.int0(hull)
                    cv2.drawContours(frame, [hull], -1, (0, 255, 0), 3)
                else:
                    cv2.polylines(frame, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 3)
                
                # إضافة نص الرمز
                x, y, w, h = obj.rect
                cv2.putText(frame, code_info['data'], (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return codes
            
        except Exception as e:
            logger.error(f"خطأ في قراءة الإطار: {str(e)}")
            return []
    
    def stop_scanning(self):
        """إيقاف عملية القراءة"""
        self.is_scanning = False


class QRBarcodeGenerator:
    """نظام إنشاء QR Code و Barcode"""
    
    def __init__(self):
        """تهيئة نظام الإنشاء"""
        pass
    
    def generate_qr_code(self, data: str, size: Tuple[int, int] = (200, 200), 
                        border: int = 4, error_correction: str = 'M') -> Image.Image:
        """
        إنشاء QR Code
        
        Args:
            data: البيانات المراد تشفيرها
            size: حجم الصورة
            border: حجم الحدود
            error_correction: مستوى تصحيح الأخطاء (L, M, Q, H)
            
        Returns:
            صورة QR Code
        """
        try:
            # تحديد مستوى تصحيح الأخطاء
            error_levels = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            
            # إنشاء QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
                box_size=10,
                border=border,
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # إنشاء الصورة
            img = qr.make_image(fill_color="black", back_color="white")
            
            # تغيير حجم الصورة
            img = img.resize(size, Image.LANCZOS)
            
            logger.info(f"تم إنشاء QR Code للبيانات: {data[:50]}...")
            return img
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء QR Code: {str(e)}")
            raise
    
    def generate_product_qr(self, product_info: Dict) -> Image.Image:
        """
        إنشاء QR Code للمنتج
        
        Args:
            product_info: معلومات المنتج
            
        Returns:
            صورة QR Code للمنتج
        """
        try:
            # تحويل معلومات المنتج إلى JSON
            product_json = json.dumps(product_info, ensure_ascii=False)
            
            # إنشاء QR Code
            qr_img = self.generate_qr_code(product_json, size=(300, 300))
            
            # إضافة معلومات المنتج أسفل QR Code
            final_img = Image.new('RGB', (300, 400), 'white')
            final_img.paste(qr_img, (0, 0))
            
            # إضافة نص
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # إضافة اسم المنتج
            product_name = product_info.get('name', 'منتج غير محدد')
            text_width = draw.textlength(product_name, font=font)
            x = (300 - text_width) // 2
            draw.text((x, 310), product_name, fill='black', font=font)
            
            # إضافة الكود
            product_code = product_info.get('code', '')
            if product_code:
                text_width = draw.textlength(f"الكود: {product_code}", font=font)
                x = (300 - text_width) // 2
                draw.text((x, 330), f"الكود: {product_code}", fill='black', font=font)
            
            # إضافة السعر
            price = product_info.get('price', 0)
            if price:
                text_width = draw.textlength(f"السعر: {price} دينار", font=font)
                x = (300 - text_width) // 2
                draw.text((x, 350), f"السعر: {price} دينار", fill='black', font=font)
            
            logger.info(f"تم إنشاء QR Code للمنتج: {product_name}")
            return final_img
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء QR Code للمنتج: {str(e)}")
            raise
    
    def save_qr_code(self, qr_img: Image.Image, file_path: str):
        """
        حفظ QR Code في ملف
        
        Args:
            qr_img: صورة QR Code
            file_path: مسار الملف
        """
        try:
            qr_img.save(file_path)
            logger.info(f"تم حفظ QR Code في: {file_path}")
        except Exception as e:
            logger.error(f"خطأ في حفظ QR Code: {str(e)}")
            raise
    
    def qr_to_base64(self, qr_img: Image.Image) -> str:
        """
        تحويل QR Code إلى Base64
        
        Args:
            qr_img: صورة QR Code
            
        Returns:
            QR Code مُشفر بـ Base64
        """
        try:
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        except Exception as e:
            logger.error(f"خطأ في تحويل QR Code إلى Base64: {str(e)}")
            raise


class ProductCodeManager:
    """مدير أكواد المنتجات"""
    
    def __init__(self):
        """تهيئة مدير الأكواد"""
        self.scanner = QRBarcodeScanner()
        self.generator = QRBarcodeGenerator()
    
    def scan_product_code(self, method: str = "camera", file_path: str = None) -> Optional[Dict]:
        """
        قراءة كود المنتج
        
        Args:
            method: طريقة القراءة (camera أو file)
            file_path: مسار الملف (للقراءة من ملف)
            
        Returns:
            معلومات المنتج المقروءة
        """
        try:
            if method == "camera":
                if not self.scanner.start_camera():
                    return None
                
                code_info = self.scanner.scan_from_camera()
                self.scanner.stop_camera()
                
                if code_info:
                    return self.parse_product_code(code_info['data'])
                
            elif method == "file" and file_path:
                codes = self.scanner.scan_from_file(file_path)
                if codes:
                    return self.parse_product_code(codes[0]['data'])
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في قراءة كود المنتج: {str(e)}")
            return None
    
    def parse_product_code(self, code_data: str) -> Dict:
        """
        تحليل بيانات كود المنتج
        
        Args:
            code_data: بيانات الكود
            
        Returns:
            معلومات المنتج المحللة
        """
        try:
            # محاولة تحليل JSON
            try:
                product_info = json.loads(code_data)
                if isinstance(product_info, dict):
                    return product_info
            except json.JSONDecodeError:
                pass
            
            # إذا لم يكن JSON، اعتبره كود بسيط
            return {
                'code': code_data,
                'type': 'simple_code',
                'scanned_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل كود المنتج: {str(e)}")
            return {
                'code': code_data,
                'type': 'unknown',
                'error': str(e),
                'scanned_at': datetime.now().isoformat()
            }
    
    def generate_product_code(self, product_info: Dict, code_type: str = "qr") -> Image.Image:
        """
        إنشاء كود للمنتج
        
        Args:
            product_info: معلومات المنتج
            code_type: نوع الكود (qr)
            
        Returns:
            صورة الكود
        """
        try:
            if code_type == "qr":
                return self.generator.generate_product_qr(product_info)
            else:
                raise ValueError(f"نوع كود غير مدعوم: {code_type}")
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء كود المنتج: {str(e)}")
            raise


# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير أكواد المنتجات
    product_manager = ProductCodeManager()
    
    # مثال على إنشاء QR Code لمنتج
    product_info = {
        'id': 1,
        'name': 'لمبة LED 10 واط',
        'code': 'LED-10W-001',
        'price': 15000,
        'category': 'إضاءة LED',
        'warranty_months': 12,
        'supplier': 'شركة الإضاءة المتقدمة'
    }
    
    try:
        # إنشاء QR Code
        qr_img = product_manager.generate_product_code(product_info)
        
        # حفظ QR Code
        qr_img.save("product_qr.png")
        print("تم إنشاء QR Code للمنتج وحفظه في product_qr.png")
        
        # قراءة QR Code من الملف
        scanned_info = product_manager.scan_product_code("file", "product_qr.png")
        if scanned_info:
            print(f"تم قراءة المنتج: {scanned_info}")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")
    
    # تنظيف الموارد
    product_manager.scanner.stop_camera()

