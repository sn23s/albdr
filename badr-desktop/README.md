# برنامج البدر للإنارة - نظام إدارة المبيعات والمخزون

## نظرة عامة
برنامج شامل لإدارة مبيعات ومخزون شركة البدر للإنارة، مطور باستخدام Electron مع واجهة حديثة وميزات متقدمة.

## الميزات الرئيسية

### 🛒 إدارة المبيعات
- إنشاء فواتير البيع مع QR Code
- طباعة الفواتير مع معلومات الضمان
- البيع السريع عبر مسح الباركود
- إدارة العملاء والشركات

### 📦 إدارة المخزون
- تتبع المنتجات والكميات
- إضافة صور للمنتجات
- إنشاء باركود مخصص للمنتجات
- تنبيهات المخزون المنخفض

### 🔧 إدارة الضمان
- تتبع فترات الضمان
- إدارة طلبات الصيانة
- تمديد الضمان
- تقارير شاملة

### 👥 إدارة المستخدمين
- نظام صلاحيات متدرج
- أدوار مختلفة (مدير، أمين صندوق، موظف مبيعات، إلخ)
- تسجيل نشاط المستخدمين

### 💰 إدارة الديون
- تتبع ديون الشركات
- سجل المدفوعات
- تذكيرات الدفع
- تقارير مالية

### 📱 الإشعارات
- إشعارات Telegram
- إشعارات WhatsApp
- تخصيص المستقبلين
- قوالب إشعارات جاهزة

### 🎨 واجهة المستخدم
- الوضع الداكن والفاتح
- واجهة عربية بالكامل
- تصميم متجاوب
- سهولة الاستخدام

### 💾 النسخ الاحتياطي
- نسخ احتياطي محلي (JSON, Excel, CSV)
- نسخ احتياطي سحابي (Google Drive)
- استعادة البيانات
- تنظيف النسخ القديمة

## متطلبات النظام
- Windows 10 أو أحدث
- 4 GB RAM أو أكثر
- 500 MB مساحة فارغة
- اتصال بالإنترنت (للإشعارات والنسخ السحابي)

## التثبيت والتشغيل

### للمطورين
```bash
# تثبيت المتطلبات
npm install

# تشغيل البرنامج في وضع التطوير
npm start

# بناء ملف EXE لنظام Windows
npm run build-win
```

### للمستخدمين
1. حمل ملف EXE من صفحة Releases
2. شغل الملف مباشرة (لا يحتاج تثبيت)
3. استخدم البيانات الافتراضية للدخول:
   - اسم المستخدم: admin
   - كلمة المرور: admin123

## البناء التلقائي
يستخدم المشروع GitHub Actions للبناء التلقائي:
- بناء تلقائي مع كل تحديث
- إنشاء إصدارات مع Tags
- تحميل مباشر للملفات

## الدعم الفني
للدعم الفني أو الاستفسارات، يرجى التواصل مع فريق التطوير.

## الترخيص
جميع الحقوق محفوظة لشركة البدر للإنارة © 2025

