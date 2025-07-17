# 📚 دليل المطور الشامل - برنامج البدر للإنارة

## 🎯 نظرة عامة

برنامج إدارة محل شامل مطور خصيصاً لمحل "البدر للإنارة" باستخدام أحدث التقنيات:

- **الواجهة الأمامية**: React + Vite + Tailwind CSS
- **الخادم الخلفي**: Python Flask + SQLAlchemy
- **قاعدة البيانات**: SQLite
- **نسخة سطح المكتب**: Electron
- **التصميم**: Material Design + RTL Support

---

## 🏗️ هيكل المشروع

```
badr_lighting_system/
├── 📁 badr_lighting/          # الخادم الخلفي (Backend)
│   ├── 📁 src/
│   │   ├── 📄 main.py         # نقطة البداية
│   │   ├── 📁 models/         # نماذج قاعدة البيانات
│   │   ├── 📁 routes/         # مسارات API
│   │   └── 📁 services/       # الخدمات (التليجرام، إلخ)
│   ├── 📄 database.sql        # هيكل قاعدة البيانات
│   └── 📄 requirements.txt    # متطلبات Python
│
├── 📁 badr-frontend/          # الواجهة الأمامية (Frontend)
│   ├── 📁 src/
│   │   ├── 📄 App.jsx         # المكون الرئيسي
│   │   ├── 📁 components/     # مكونات React
│   │   └── 📁 lib/            # المكتبات المساعدة
│   ├── 📄 package.json        # تبعيات Node.js
│   └── 📄 vite.config.js      # إعدادات Vite
│
├── 📁 badr-desktop/           # نسخة سطح المكتب (Electron)
│   ├── 📄 main.js             # تطبيق Electron الرئيسي
│   ├── 📄 preload.js          # ملف الأمان
│   ├── 📁 backend/            # نسخة من الخادم الخلفي
│   └── 📁 frontend/           # نسخة من الواجهة الأمامية
│
├── 📁 public-store/           # المتجر العام للعملاء
│   └── 📄 index.html          # صفحة المتجر
│
└── 📄 DOCUMENTATION.md        # هذا الملف
```

---

## 🚀 التثبيت والإعداد

### المتطلبات الأساسية

- **Python 3.8+** - [تحميل](https://python.org)
- **Node.js 16+** - [تحميل](https://nodejs.org)
- **Git** - [تحميل](https://git-scm.com)

### 1. إعداد الخادم الخلفي

```bash
cd badr_lighting

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم
python src/main.py
```

### 2. إعداد الواجهة الأمامية

```bash
cd badr-frontend

# تثبيت التبعيات
npm install
# أو
pnpm install

# تشغيل خادم التطوير
npm run dev
# أو
pnpm dev
```

### 3. إعداد نسخة سطح المكتب

```bash
cd badr-desktop

# تثبيت التبعيات
npm install

# تشغيل التطبيق
npm start

# بناء نسخة قابلة للتوزيع
npm run build
```

---

## 🔧 التطوير والتخصيص

### إضافة ميزة جديدة

#### 1. في الخادم الخلفي:

```python
# إنشاء نموذج جديد في models/
class NewModel(db.Model):
    __tablename__ = 'new_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# إنشاء routes جديدة في routes/
@new_bp.route('/api/new', methods=['GET'])
def get_new_items():
    items = NewModel.query.all()
    return jsonify([item.to_dict() for item in items])
```

#### 2. في الواجهة الأمامية:

```jsx
// إنشاء مكون جديد في components/
const NewComponent = () => {
  const [data, setData] = useState([])
  
  useEffect(() => {
    fetch('/api/new')
      .then(res => res.json())
      .then(setData)
  }, [])
  
  return (
    <div className="p-6">
      {/* محتوى المكون */}
    </div>
  )
}
```

### تخصيص التصميم

```css
/* في src/index.css */
:root {
  --primary-color: #4F46E5;
  --secondary-color: #06B6D4;
  --accent-color: #F59E0B;
}

/* استخدام Tailwind CSS للتصميم السريع */
.custom-button {
  @apply bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg;
}
```

---

## 🗄️ قاعدة البيانات

### الجداول الرئيسية

| الجدول | الوصف | الحقول الرئيسية |
|--------|-------|-----------------|
| `users` | المستخدمون | id, username, password, role |
| `products` | المنتجات | id, name, price, quantity, category |
| `customers` | الزبائن | id, name, phone, email, address |
| `sales` | المبيعات | id, customer_id, total, date, currency |
| `expenses` | المصروفات | id, description, amount, date |
| `warranties` | الضمانات | id, product_id, customer_id, start_date, end_date |
| `orders` | الطلبات | id, customer_info, items, status, delivery_type |

### إضافة جدول جديد

```sql
-- في database.sql
CREATE TABLE new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔔 إعداد إشعارات التليجرام

### 1. إنشاء بوت تليجرام

1. تحدث مع [@BotFather](https://t.me/botfather)
2. أرسل `/newbot`
3. اتبع التعليمات للحصول على Token
4. احفظ الـ Token في إعدادات البرنامج

### 2. الحصول على Chat ID

```bash
# أرسل رسالة للبوت ثم استخدم هذا الرابط
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

### 3. إعداد الإشعارات

```python
# في services/telegram_service.py
TELEGRAM_CONFIG = {
    'bot_token': 'YOUR_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID',
    'notifications': {
        'sales': True,
        'low_stock': True,
        'warranty_expiry': True
    }
}
```

---

## 🖨️ إعداد الطباعة

### طابعات الفواتير الحرارية

```javascript
// إعدادات الطباعة في PrintSettings.jsx
const printerSettings = {
  width: '80mm',        // عرض الورق
  fontSize: '12px',     // حجم الخط
  margin: '5mm',        // الهوامش
  logo: true,           // عرض الشعار
  qrCode: true          // رمز QR
}
```

### قوالب الفواتير

- **القالب الكلاسيكي**: للطابعات العادية
- **القالب الحراري**: للطابعات الحرارية 58mm/80mm
- **القالب المبسط**: للطباعة السريعة

---

## 🔐 الأمان والصلاحيات

### مستويات الصلاحيات

| المستوى | الصلاحيات |
|---------|-----------|
| `admin` | جميع الصلاحيات |
| `sales` | المبيعات، الزبائن، التقارير |
| `warehouse` | المنتجات، المخزون |
| `employee` | عرض فقط |

### إضافة مستوى صلاحية جديد

```python
# في models/user.py
ROLES = {
    'admin': 4,
    'manager': 3,      # مستوى جديد
    'sales': 2,
    'employee': 1
}
```

---

## 📱 التطوير للموبايل (مستقبلاً)

### React Native Setup

```bash
# إعداد React Native
npx react-native init BadrMobile
cd BadrMobile

# تثبيت التبعيات المطلوبة
npm install @react-navigation/native
npm install react-native-vector-icons
```

### API Integration

```javascript
// في services/api.js
const API_BASE = 'http://your-server.com:5001/api'

export const apiService = {
  async getProducts() {
    const response = await fetch(`${API_BASE}/products`)
    return response.json()
  }
}
```

---

## 🧪 الاختبار

### اختبار الخادم الخلفي

```bash
# تشغيل الاختبارات
python -m pytest tests/

# اختبار API محدد
curl -X GET http://localhost:5001/api/products
```

### اختبار الواجهة الأمامية

```bash
# تشغيل اختبارات Jest
npm test

# اختبار البناء
npm run build
```

---

## 🚀 النشر والتوزيع

### نشر على خادم

```bash
# بناء الواجهة الأمامية
cd badr-frontend
npm run build

# نسخ الملفات المبنية إلى الخادم
cp -r dist/* /var/www/badr-lighting/

# تشغيل الخادم الخلفي مع Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 src.main:app
```

### إنشاء نسخة محمولة

```bash
# ضغط المشروع كاملاً
tar -czf badr-lighting-portable.tar.gz badr_lighting/ badr-frontend/ badr-desktop/

# إنشاء installer للويندوز
cd badr-desktop
npm run build-win
```

---

## 🔧 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في الاتصال بقاعدة البيانات

```bash
# التحقق من وجود ملف قاعدة البيانات
ls -la *.db

# إعادة إنشاء قاعدة البيانات
python -c "from src.main import db; db.create_all()"
```

#### 2. مشكلة في تثبيت التبعيات

```bash
# تنظيف cache npm
npm cache clean --force

# إعادة تثبيت التبعيات
rm -rf node_modules package-lock.json
npm install
```

#### 3. مشكلة في إشعارات التليجرام

```python
# اختبار الاتصال
import requests
response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe')
print(response.json())
```

---

## 📈 التحسينات المستقبلية

### الميزات المقترحة

- [ ] تطبيق موبايل (React Native)
- [ ] تكامل مع أنظمة الدفع الإلكتروني
- [ ] تحليلات متقدمة وذكاء اصطناعي
- [ ] نظام إدارة المخازن المتعددة
- [ ] تكامل مع منصات التجارة الإلكترونية
- [ ] نظام CRM متقدم
- [ ] تقارير مالية معمقة
- [ ] نظام إدارة الموظفين

### التحسينات التقنية

- [ ] تحسين الأداء (Caching)
- [ ] أمان محسن (JWT, OAuth)
- [ ] نسخ احتياطية تلقائية
- [ ] مراقبة النظام (Monitoring)
- [ ] اختبارات تلقائية شاملة

---

## 📞 الدعم والمساعدة

### للمطورين

- **البريد الإلكتروني**: dev@badr-lighting.com
- **التوثيق التقني**: [docs.badr-lighting.com](https://docs.badr-lighting.com)
- **مستودع الكود**: [github.com/badr-lighting](https://github.com/badr-lighting)

### للمستخدمين

- **دليل المستخدم**: [help.badr-lighting.com](https://help.badr-lighting.com)
- **الدعم التقني**: support@badr-lighting.com
- **التدريب**: training@badr-lighting.com

---

## 📄 الترخيص

هذا البرنامج مطور خصيصاً لمحل البدر للإنارة.
جميع الحقوق محفوظة © 2025

**ملاحظة**: هذا التوثيق يتم تحديثه باستمرار. للحصول على أحدث إصدار، يرجى مراجعة المستودع الرسمي.

---

*تم إنشاء هذا التوثيق بواسطة فريق التطوير - آخر تحديث: يناير 2025*

