# 🚀 دليل الإعداد السريع - البدر للإنارة

## ⚡ تشغيل سريع (5 دقائق)

### 1. تحميل المتطلبات
```bash
# تثبيت Python 3.8+
# تثبيت Node.js 16+
```

### 2. تشغيل الخادم الخلفي
```bash
cd badr_lighting
pip install -r requirements.txt
python src/main.py
```

### 3. تشغيل الواجهة الأمامية
```bash
cd badr-frontend
npm install
npm run dev
```

### 4. فتح البرنامج
- افتح المتصفح على: `http://localhost:5173`
- اسم المستخدم: `admin`
- كلمة المرور: `admin123`

## 🖥️ نسخة سطح المكتب

### تشغيل مباشر
```bash
cd badr-desktop
npm install
npm start
```

### أو استخدام ملفات التشغيل
- **Windows**: انقر مزدوج على `start.bat`
- **Linux**: `./start.sh`

## 📱 المتجر العام
افتح ملف: `public-store/index.html` في المتصفح

## 🔧 إعدادات سريعة

### إشعارات التليجرام
1. اذهب إلى: إعدادات التليجرام
2. أدخل Bot Token و Chat ID
3. فعل الإشعارات المطلوبة

### إعدادات الطباعة
1. اذهب إلى: إعدادات الطباعة
2. أدخل معلومات المحل
3. ارفع شعار المحل

## ❗ مشاكل شائعة

### الخادم لا يعمل
```bash
# تحقق من المنفذ
lsof -i :5001
# أو
netstat -an | grep 5001
```

### الواجهة لا تظهر
```bash
# تحقق من المنفذ
lsof -i :5173
# أعد تثبيت التبعيات
rm -rf node_modules && npm install
```

### قاعدة البيانات فارغة
```bash
cd badr_lighting
python -c "from src.main import db; db.create_all()"
```

## 📞 الدعم
للمساعدة السريعة، راجع ملف `DOCUMENTATION.md` الشامل.

