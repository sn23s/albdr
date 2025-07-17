"""
نظام طباعة الفواتير لبرنامج البدر للإنارة
يدعم طباعة فواتير البيع مع معلومات الزبون والضمان
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import logging
import qrcode
from PIL import Image as PILImage
import io

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvoicePrinter:
    """نظام طباعة الفواتير"""
    
    def __init__(self, company_info: Dict = None):
        """
        تهيئة نظام طباعة الفواتير
        
        Args:
            company_info: معلومات الشركة
        """
        self.company_info = company_info or {
            'name': 'محل البدر للإنارة',
            'address': 'بغداد - العراق',
            'phone': '+964 XXX XXX XXXX',
            'email': 'info@albadr-lighting.com',
            'logo_path': None
        }
        
        # إعداد الخطوط العربية
        self.setup_fonts()
        
        # إعداد الأنماط
        self.setup_styles()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل خط عربي
            # يمكن تحميل خطوط عربية مثل Amiri أو Cairo
            # pdfmetrics.registerFont(TTFont('Arabic', 'path/to/arabic/font.ttf'))
            self.arabic_font = 'Helvetica'  # استخدام خط افتراضي
        except Exception as e:
            logger.warning(f"فشل في تحميل الخط العربي: {str(e)}")
            self.arabic_font = 'Helvetica'
    
    def setup_styles(self):
        """إعداد أنماط النصوص"""
        self.styles = getSampleStyleSheet()
        
        # نمط العنوان الرئيسي
        self.styles.add(ParagraphStyle(
            name='ArabicTitle',
            parent=self.styles['Title'],
            fontName=self.arabic_font,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # نمط النص العادي
        self.styles.add(ParagraphStyle(
            name='ArabicNormal',
            parent=self.styles['Normal'],
            fontName=self.arabic_font,
            fontSize=12,
            alignment=TA_RIGHT
        ))
        
        # نمط النص المتوسط
        self.styles.add(ParagraphStyle(
            name='ArabicHeading',
            parent=self.styles['Heading2'],
            fontName=self.arabic_font,
            fontSize=14,
            alignment=TA_RIGHT,
            spaceAfter=10
        ))
    
    def create_invoice(self, invoice_data: Dict, output_path: str = None) -> str:
        """
        إنشاء فاتورة PDF
        
        Args:
            invoice_data: بيانات الفاتورة
            output_path: مسار ملف الإخراج
            
        Returns:
            مسار ملف الفاتورة المُنشأة
        """
        try:
            # تحديد مسار الملف
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                invoice_number = invoice_data.get('invoice_number', 'INV')
                output_path = f"invoice_{invoice_number}_{timestamp}.pdf"
            
            # إنشاء المستند
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # إنشاء محتوى الفاتورة
            story = []
            
            # إضافة رأس الشركة
            story.extend(self.create_company_header())
            
            # إضافة معلومات الفاتورة
            story.extend(self.create_invoice_header(invoice_data))
            
            # إضافة معلومات الزبون
            story.extend(self.create_customer_info(invoice_data))
            
            # إضافة جدول المنتجات
            story.extend(self.create_products_table(invoice_data))
            
            # إضافة الإجمالي
            story.extend(self.create_totals_section(invoice_data))
            
            # إضافة معلومات الضمان
            story.extend(self.create_warranty_section(invoice_data))
            
            # إضافة QR Code
            story.extend(self.create_qr_section(invoice_data))
            
            # إضافة تذييل
            story.extend(self.create_footer())
            
            # بناء المستند
            doc.build(story)
            
            logger.info(f"تم إنشاء الفاتورة: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الفاتورة: {str(e)}")
            raise
    
    def create_company_header(self) -> List:
        """إنشاء رأس الشركة"""
        elements = []
        
        # شعار الشركة (إذا كان متوفراً)
        if self.company_info.get('logo_path') and os.path.exists(self.company_info['logo_path']):
            try:
                logo = Image(self.company_info['logo_path'], width=2*inch, height=1*inch)
                elements.append(logo)
            except Exception as e:
                logger.warning(f"فشل في تحميل الشعار: {str(e)}")
        
        # اسم الشركة
        company_name = Paragraph(self.company_info['name'], self.styles['ArabicTitle'])
        elements.append(company_name)
        
        # معلومات الاتصال
        contact_info = f"""
        {self.company_info.get('address', '')}<br/>
        هاتف: {self.company_info.get('phone', '')}<br/>
        البريد الإلكتروني: {self.company_info.get('email', '')}
        """
        contact_para = Paragraph(contact_info, self.styles['ArabicNormal'])
        elements.append(contact_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_invoice_header(self, invoice_data: Dict) -> List:
        """إنشاء رأس الفاتورة"""
        elements = []
        
        # عنوان الفاتورة
        title = Paragraph("فاتورة بيع", self.styles['ArabicTitle'])
        elements.append(title)
        
        # معلومات الفاتورة
        invoice_info = [
            ['رقم الفاتورة:', invoice_data.get('invoice_number', '')],
            ['التاريخ:', invoice_data.get('date', datetime.now().strftime('%Y-%m-%d'))],
            ['الوقت:', invoice_data.get('time', datetime.now().strftime('%H:%M:%S'))],
            ['البائع:', invoice_data.get('seller', 'غير محدد')]
        ]
        
        # إنشاء جدول معلومات الفاتورة
        invoice_table = Table(invoice_info, colWidths=[3*cm, 4*cm])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_customer_info(self, invoice_data: Dict) -> List:
        """إنشاء معلومات الزبون"""
        elements = []
        
        customer = invoice_data.get('customer', {})
        
        if customer:
            # عنوان قسم الزبون
            customer_title = Paragraph("معلومات الزبون", self.styles['ArabicHeading'])
            elements.append(customer_title)
            
            # معلومات الزبون
            customer_info = [
                ['الاسم:', customer.get('name', 'غير محدد')],
                ['الهاتف:', customer.get('phone', 'غير محدد')],
                ['العنوان:', customer.get('address', 'غير محدد')]
            ]
            
            customer_table = Table(customer_info, colWidths=[3*cm, 6*cm])
            customer_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
            ]))
            
            elements.append(customer_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def create_products_table(self, invoice_data: Dict) -> List:
        """إنشاء جدول المنتجات"""
        elements = []
        
        # عنوان قسم المنتجات
        products_title = Paragraph("المنتجات المباعة", self.styles['ArabicHeading'])
        elements.append(products_title)
        
        # رأس الجدول
        headers = ['المجموع', 'السعر', 'الكمية', 'اسم المنتج', 'الكود', 'ت']
        
        # بيانات المنتجات
        products = invoice_data.get('products', [])
        table_data = [headers]
        
        for i, product in enumerate(products, 1):
            quantity = product.get('quantity', 1)
            price = product.get('price', 0)
            total = quantity * price
            
            row = [
                f"{total:,.0f}",
                f"{price:,.0f}",
                str(quantity),
                product.get('name', 'غير محدد'),
                product.get('code', ''),
                str(i)
            ]
            table_data.append(row)
        
        # إنشاء الجدول
        products_table = Table(table_data, colWidths=[2.5*cm, 2.5*cm, 1.5*cm, 4*cm, 2*cm, 1*cm])
        products_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), self.arabic_font)
        ]))
        
        elements.append(products_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_totals_section(self, invoice_data: Dict) -> List:
        """إنشاء قسم الإجماليات"""
        elements = []
        
        # حساب الإجماليات
        products = invoice_data.get('products', [])
        subtotal = sum(p.get('quantity', 1) * p.get('price', 0) for p in products)
        discount = invoice_data.get('discount', 0)
        tax = invoice_data.get('tax', 0)
        total = subtotal - discount + tax
        
        # جدول الإجماليات
        totals_data = [
            ['المجموع الفرعي:', f"{subtotal:,.0f} دينار"],
            ['الخصم:', f"{discount:,.0f} دينار"],
            ['الضريبة:', f"{tax:,.0f} دينار"],
            ['المجموع الكلي:', f"{total:,.0f} دينار"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*cm, 4*cm])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTNAME', (0, -1), (-1, -1), self.arabic_font)
        ]))
        
        # محاذاة الجدول إلى اليسار
        totals_table.hAlign = 'LEFT'
        
        elements.append(totals_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_warranty_section(self, invoice_data: Dict) -> List:
        """إنشاء قسم الضمان"""
        elements = []
        
        warranty_info = invoice_data.get('warranty', {})
        
        if warranty_info:
            # عنوان قسم الضمان
            warranty_title = Paragraph("معلومات الضمان", self.styles['ArabicHeading'])
            elements.append(warranty_title)
            
            # حساب تاريخ انتهاء الضمان
            start_date = datetime.strptime(invoice_data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
            warranty_months = warranty_info.get('months', 12)
            end_date = start_date + timedelta(days=warranty_months * 30)
            
            warranty_data = [
                ['مدة الضمان:', f"{warranty_months} شهر"],
                ['تاريخ البداية:', start_date.strftime('%Y-%m-%d')],
                ['تاريخ الانتهاء:', end_date.strftime('%Y-%m-%d')],
                ['شروط الضمان:', warranty_info.get('terms', 'ضمان ضد عيوب الصناعة')]
            ]
            
            warranty_table = Table(warranty_data, colWidths=[3*cm, 6*cm])
            warranty_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue)
            ]))
            
            elements.append(warranty_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def create_qr_section(self, invoice_data: Dict) -> List:
        """إنشاء قسم QR Code"""
        elements = []
        
        try:
            # إنشاء QR Code يحتوي على معلومات الفاتورة
            qr_data = {
                'invoice_number': invoice_data.get('invoice_number'),
                'date': invoice_data.get('date'),
                'total': sum(p.get('quantity', 1) * p.get('price', 0) for p in invoice_data.get('products', [])),
                'customer': invoice_data.get('customer', {}).get('name', ''),
                'company': self.company_info['name']
            }
            
            # إنشاء QR Code
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(str(qr_data))
            qr.make(fit=True)
            
            # تحويل إلى صورة
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # حفظ مؤقت
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # إضافة QR Code إلى الفاتورة
            qr_image = Image(qr_buffer, width=1.5*inch, height=1.5*inch)
            qr_image.hAlign = 'LEFT'
            
            elements.append(qr_image)
            
            # نص توضيحي
            qr_text = Paragraph("امسح الكود للتحقق من الفاتورة", self.styles['ArabicNormal'])
            elements.append(qr_text)
            
        except Exception as e:
            logger.warning(f"فشل في إنشاء QR Code: {str(e)}")
        
        return elements
    
    def create_footer(self) -> List:
        """إنشاء تذييل الفاتورة"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        # رسالة شكر
        thank_you = Paragraph("شكراً لتعاملكم معنا", self.styles['ArabicTitle'])
        elements.append(thank_you)
        
        # معلومات إضافية
        footer_text = """
        • يرجى الاحتفاظ بهذه الفاتورة للضمان<br/>
        • لا يمكن استرداد البضاعة إلا خلال 7 أيام من تاريخ الشراء<br/>
        • الضمان لا يشمل الكسر أو سوء الاستخدام
        """
        footer_para = Paragraph(footer_text, self.styles['ArabicNormal'])
        elements.append(footer_para)
        
        return elements
    
    def print_invoice(self, invoice_data: Dict, printer_name: str = None) -> bool:
        """
        طباعة الفاتورة
        
        Args:
            invoice_data: بيانات الفاتورة
            printer_name: اسم الطابعة (اختياري)
            
        Returns:
            True إذا تمت الطباعة بنجاح، False خلاف ذلك
        """
        try:
            # إنشاء ملف PDF
            pdf_path = self.create_invoice(invoice_data)
            
            # طباعة الملف
            if os.name == 'nt':  # Windows
                if printer_name:
                    os.system(f'print /D:"{printer_name}" "{pdf_path}"')
                else:
                    os.startfile(pdf_path, "print")
            else:  # Linux/Mac
                if printer_name:
                    os.system(f'lp -d {printer_name} "{pdf_path}"')
                else:
                    os.system(f'lp "{pdf_path}"')
            
            logger.info(f"تم إرسال الفاتورة للطباعة: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في طباعة الفاتورة: {str(e)}")
            return False


# مثال على الاستخدام
if __name__ == "__main__":
    # بيانات الشركة
    company_info = {
        'name': 'محل البدر للإنارة',
        'address': 'شارع الرشيد - بغداد - العراق',
        'phone': '+964 770 123 4567',
        'email': 'info@albadr-lighting.com'
    }
    
    # إنشاء نظام الطباعة
    printer = InvoicePrinter(company_info)
    
    # بيانات الفاتورة
    invoice_data = {
        'invoice_number': 'INV-2025-001',
        'date': '2025-01-09',
        'time': '14:30:00',
        'seller': 'أحمد محمد',
        'customer': {
            'name': 'علي حسن',
            'phone': '+964 750 987 6543',
            'address': 'الكرادة - بغداد'
        },
        'products': [
            {
                'code': 'LED-10W-001',
                'name': 'لمبة LED 10 واط - أبيض دافئ',
                'quantity': 5,
                'price': 15000
            },
            {
                'code': 'SPOT-20W-002',
                'name': 'كشاف LED 20 واط - خارجي',
                'quantity': 2,
                'price': 45000
            }
        ],
        'discount': 5000,
        'tax': 0,
        'warranty': {
            'months': 12,
            'terms': 'ضمان ضد عيوب الصناعة فقط'
        }
    }
    
    try:
        # إنشاء الفاتورة
        pdf_path = printer.create_invoice(invoice_data)
        print(f"تم إنشاء الفاتورة: {pdf_path}")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

