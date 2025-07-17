# دليل نقل التحديثات - برنامج البدر للإنارة

## نظرة عامة

هذا الدليل يوضح كيفية نقل جميع التحديثات والميزات الجديدة التي تم تطويرها إلى النسخة الأصلية من برنامج البدر للإنارة التي تعمل معك حالياً.

## قائمة التحديثات الجديدة

### 1. الملفات المحدثة
- `package.json` - إضافة electron-builder وتبعيات جديدة
- `main.js` - تحسينات وميزات جديدة

### 2. الملفات الجديدة (Python Modules)
- `backup_system.py` - نظام النسخ الاحتياطي
- `google_drive_backup.py` - النسخ السحابي
- `qr_barcode_scanner.py` - قراءة الباركود
- `invoice_printer.py` - طباعة الفواتير
- `product_image_manager.py` - إدارة صور المنتجات
- `warranty_manager.py` - إدارة الضمان
- `user_permissions.py` - صلاحيات المستخدمين
- `debt_management.py` - تسديد الديون
- `notification_system.py` - الإشعارات
- `theme_manager.py` - الثيمات
- `system_reset.py` - إعادة التعيين

### 3. ملفات الواجهة الجديدة
- `theme.css` - أنماط الثيمات
- `notifications.js` - جافاسكريبت الإشعارات
- `barcode-scanner.js` - جافاسكريبت الباركود

## خطوات النقل التفصيلية

### الخطوة 1: تحضير البيئة

1. **إنشاء نسخة احتياطية من المشروع الحالي:**
   ```bash
   # في مجلد المشروع الأصلي
   cd C:\Users\mohammed\Desktop\bdr
   copy badr-desktop badr-desktop-backup
   ```

2. **التأكد من إغلاق البرنامج:**
   - أغلق برنامج البدر للإنارة إذا كان يعمل
   - تأكد من عدم وجود عمليات Node.js في الخلفية

### الخطوة 2: تحديث package.json

1. **افتح ملف package.json الحالي**
2. **استبدل المحتوى بالكامل بهذا:**

```json
{
  "name": "albadr-lighting",
  "version": "2.0.0",
  "description": "نظام إدارة البدر للإنارة - النسخة المحدثة مع جميع الميزات",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build-win": "electron-builder --win",
    "build-mac": "electron-builder --mac",
    "build-linux": "electron-builder --linux",
    "postinstall": "electron-builder install-app-deps"
  },
  "build": {
    "appId": "com.albadr.lighting",
    "productName": "البدر للإنارة",
    "directories": {
      "output": "dist",
      "buildResources": "build"
    },
    "files": [
      "**/*",
      "!**/node_modules/*/{CHANGELOG.md,README.md,README,readme.md,readme}",
      "!**/node_modules/*/{test,__tests__,tests,powered-test,example,examples}",
      "!**/node_modules/*.d.ts",
      "!**/node_modules/.bin",
      "!**/*.{iml,o,hprof,orig,pyc,pyo,rbc,swp,csproj,sln,xproj}",
      "!.editorconfig",
      "!**/._*",
      "!**/{.DS_Store,.git,.hg,.svn,CVS,RCS,SCCS,.gitignore,.gitattributes}",
      "!**/{__pycache__,thumbs.db,.flowconfig,.idea,.vs,.nyc_output}",
      "!**/{appveyor.yml,.travis.yml,circle.yml}",
      "!**/{npm-debug.log,yarn.lock,.yarn-integrity,.yarn-metadata.json}"
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ],
      "icon": "icon.ico",
      "requestedExecutionLevel": "asInvoker"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "allowElevation": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "البدر للإنارة",
      "uninstallDisplayName": "البدر للإنارة",
      "license": "license.txt",
      "installerIcon": "icon.ico",
      "uninstallerIcon": "icon.ico"
    }
  },
  "devDependencies": {
    "electron": "^22.3.27",
    "electron-builder": "^24.6.4"
  },
  "dependencies": {
    "sqlite3": "^5.1.6",
    "qrcode": "^1.5.3",
    "jsqr": "^1.4.0",
    "jspdf": "^2.5.1",
    "html2canvas": "^1.4.1",
    "axios": "^1.6.0",
    "node-telegram-bot-api": "^0.64.0",
    "googleapis": "^128.0.0",
    "multer": "^1.4.5-lts.1",
    "sharp": "^0.32.6",
    "pdf-lib": "^1.17.1",
    "canvas": "^2.11.2",
    "qr-scanner": "^1.4.2"
  },
  "author": "البدر للإنارة",
  "license": "MIT",
  "homepage": "https://albadr-lighting.com",
  "repository": {
    "type": "git",
    "url": "https://github.com/albadr-lighting/desktop-app.git"
  }
}
```

### الخطوة 3: إنشاء هيكل المجلدات الجديد

```bash
# في مجلد المشروع
mkdir modules
mkdir styles
mkdir scripts
mkdir assets
mkdir templates
mkdir config
```

### الخطوة 4: إضافة الملفات الجديدة

1. **انسخ جميع ملفات Python إلى مجلد modules:**
   - `backup_system.py`
   - `google_drive_backup.py`
   - `qr_barcode_scanner.py`
   - `invoice_printer.py`
   - `product_image_manager.py`
   - `warranty_manager.py`
   - `user_permissions.py`
   - `debt_management.py`
   - `notification_system.py`
   - `theme_manager.py`
   - `system_reset.py`

2. **أنشئ ملف styles/theme.css:**
```css
/* سيتم إنشاؤه تلقائياً من theme_manager.py */
/* أو انسخ المحتوى من الملف المرفق */
```

3. **أنشئ ملف scripts/app.js للوظائف الجديدة:**
```javascript
// وظائف الباركود والإشعارات والثيمات
// سيتم تفصيلها في الملفات المرفقة
```

### الخطوة 5: تحديث main.js

أضف هذه الأسطر إلى ملف main.js الموجود:

```javascript
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// إضافة معالجات الأحداث الجديدة
ipcMain.handle('scan-barcode', async () => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'qr_barcode_scanner.py'),
        'scan'
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في قراءة الباركود'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('print-invoice', async (event, invoiceData) => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'invoice_printer.py'),
        'print',
        JSON.stringify(invoiceData)
      ]);
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true });
        } else {
          reject(new Error('فشل في طباعة الفاتورة'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('backup-data', async (event, backupType = 'full') => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'backup_system.py'),
        'backup',
        backupType
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في إنشاء النسخة الاحتياطية'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('send-notification', async (event, notificationData) => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'notification_system.py'),
        'send',
        JSON.stringify(notificationData)
      ]);
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true });
        } else {
          reject(new Error('فشل في إرسال الإشعار'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('toggle-theme', async () => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'theme_manager.py'),
        'toggle'
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في تغيير الثيم'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('system-reset', async (event, password) => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'system_reset.py'),
        'reset',
        password
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في إعادة تعيين النظام'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

// إضافة معالج لإدارة المستخدمين
ipcMain.handle('user-management', async (event, action, userData) => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'user_permissions.py'),
        action,
        JSON.stringify(userData)
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في إدارة المستخدمين'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});

// إضافة معالج لإدارة الديون
ipcMain.handle('debt-management', async (event, action, debtData) => {
  try {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'modules', 'debt_management.py'),
        action,
        JSON.stringify(debtData)
      ]);
      
      let result = '';
      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(JSON.parse(result));
        } else {
          reject(new Error('فشل في إدارة الديون'));
        }
      });
    });
  } catch (error) {
    throw error;
  }
});
```

### الخطوة 6: تحديث ملف HTML الرئيسي

أضف هذه الأسطر إلى ملف index.html:

```html
<!-- في قسم head -->
<link rel="stylesheet" href="styles/theme.css">

<!-- في قسم body -->
<div id="themeToggle" class="theme-toggle" onclick="toggleTheme()">
  <svg id="themeIcon" viewBox="0 0 24 24">
    <!-- أيقونات الثيم -->
  </svg>
</div>

<!-- قبل إغلاق body -->
<script src="scripts/app.js"></script>
```

### الخطوة 7: تثبيت التبعيات الجديدة

```bash
# في مجلد المشروع
npm install
```

### الخطوة 8: اختبار التحديثات

```bash
# تشغيل البرنامج للاختبار
npm start
```

### الخطوة 9: بناء ملف EXE

```bash
# بناء النسخة النهائية
npm run build-win
```

## نصائح مهمة للنقل

### 1. احتفظ بالبيانات الموجودة
- لا تحذف ملفات قاعدة البيانات الموجودة
- احتفظ بمجلد الصور
- احفظ ملفات الإعدادات

### 2. اختبر كل ميزة
- اختبر قراءة الباركود
- اختبر طباعة الفواتير
- اختبر النسخ الاحتياطي
- اختبر الإشعارات

### 3. تعامل مع الأخطاء
- إذا فشل npm install، احذف node_modules وأعد المحاولة
- إذا فشل البناء، تأكد من تثبيت Python
- إذا لم تعمل الميزات، تحقق من مسارات الملفات

### 4. النسخ الاحتياطي
- احتفظ بنسخة من المشروع الأصلي
- اعمل نسخة احتياطية بعد كل خطوة ناجحة
- احفظ ملفات البيانات منفصلة

## استكشاف الأخطاء

### خطأ "Module not found"
```bash
npm install --save [اسم الحزمة المفقودة]
```

### خطأ "Python not found"
- تأكد من تثبيت Python 3.x
- أضف Python إلى PATH
- أعد تشغيل Command Prompt

### خطأ في البناء
```bash
# نظف الملفات المؤقتة
npm run clean
# أو احذف مجلد dist
rmdir /s dist
# ثم أعد البناء
npm run build-win
```

## الخلاصة

بعد تطبيق هذه الخطوات، ستحصل على:

✅ برنامج محدث بجميع الميزات الجديدة
✅ ملف EXE قابل للتوزيع
✅ جميع البيانات الموجودة محفوظة
✅ واجهة محسنة مع الثيمات
✅ نظام نسخ احتياطي متطور
✅ إشعارات Telegram/WhatsApp
✅ نظام صلاحيات متكامل

**الوقت المطلوب:** 2-3 ساعات للتطبيق الكامل والاختبار

