"""
نظام إدارة الثيمات لبرنامج البدر للإنارة
يدعم التبديل بين الوضع الداكن والفاتح
"""

import json
import os
from typing import Dict, Optional
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThemeManager:
    """مدير الثيمات والألوان"""
    
    def __init__(self, config_path: str = "theme_config.json"):
        """
        تهيئة مدير الثيمات
        
        Args:
            config_path: مسار ملف إعدادات الثيم
        """
        self.config_path = config_path
        self.current_theme = "light"
        self.themes = self.load_default_themes()
        self.load_config()
    
    def load_default_themes(self) -> Dict:
        """تحميل الثيمات الافتراضية"""
        return {
            "light": {
                "name": "الوضع الفاتح",
                "colors": {
                    # الألوان الأساسية
                    "primary": "#2563eb",           # أزرق أساسي
                    "primary_hover": "#1d4ed8",     # أزرق داكن عند التمرير
                    "secondary": "#64748b",         # رمادي ثانوي
                    "accent": "#f59e0b",            # أصفر للتمييز
                    
                    # ألوان الخلفية
                    "background": "#ffffff",        # خلفية بيضاء
                    "surface": "#f8fafc",           # سطح فاتح
                    "card": "#ffffff",              # خلفية البطاقات
                    "sidebar": "#f1f5f9",           # الشريط الجانبي
                    
                    # ألوان النصوص
                    "text_primary": "#1e293b",      # نص أساسي داكن
                    "text_secondary": "#64748b",    # نص ثانوي
                    "text_muted": "#94a3b8",        # نص خافت
                    "text_on_primary": "#ffffff",   # نص على الأزرق
                    
                    # ألوان الحدود
                    "border": "#e2e8f0",            # حدود فاتحة
                    "border_focus": "#2563eb",      # حدود عند التركيز
                    "divider": "#f1f5f9",           # خطوط الفصل
                    
                    # ألوان الحالات
                    "success": "#10b981",           # أخضر للنجاح
                    "warning": "#f59e0b",           # أصفر للتحذير
                    "error": "#ef4444",             # أحمر للخطأ
                    "info": "#3b82f6",              # أزرق للمعلومات
                    
                    # ألوان الحالات الفاتحة
                    "success_light": "#d1fae5",     # خلفية خضراء فاتحة
                    "warning_light": "#fef3c7",     # خلفية صفراء فاتحة
                    "error_light": "#fee2e2",       # خلفية حمراء فاتحة
                    "info_light": "#dbeafe",        # خلفية زرقاء فاتحة
                    
                    # ألوان الأزرار
                    "button_primary": "#2563eb",
                    "button_primary_hover": "#1d4ed8",
                    "button_secondary": "#6b7280",
                    "button_secondary_hover": "#4b5563",
                    "button_success": "#10b981",
                    "button_success_hover": "#059669",
                    "button_danger": "#ef4444",
                    "button_danger_hover": "#dc2626",
                    
                    # ألوان الإدخال
                    "input_background": "#ffffff",
                    "input_border": "#d1d5db",
                    "input_focus": "#2563eb",
                    "input_disabled": "#f3f4f6",
                    
                    # ألوان الجداول
                    "table_header": "#f8fafc",
                    "table_row_even": "#ffffff",
                    "table_row_odd": "#f8fafc",
                    "table_row_hover": "#f1f5f9",
                    
                    # ألوان الظلال
                    "shadow_light": "rgba(0, 0, 0, 0.05)",
                    "shadow_medium": "rgba(0, 0, 0, 0.1)",
                    "shadow_heavy": "rgba(0, 0, 0, 0.25)"
                },
                "fonts": {
                    "primary": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    "secondary": "'Arial', sans-serif",
                    "monospace": "'Courier New', monospace"
                },
                "sizes": {
                    "text_xs": "12px",
                    "text_sm": "14px",
                    "text_base": "16px",
                    "text_lg": "18px",
                    "text_xl": "20px",
                    "text_2xl": "24px",
                    "text_3xl": "30px",
                    
                    "spacing_xs": "4px",
                    "spacing_sm": "8px",
                    "spacing_md": "16px",
                    "spacing_lg": "24px",
                    "spacing_xl": "32px",
                    
                    "border_radius": "6px",
                    "border_radius_lg": "12px",
                    "border_width": "1px"
                }
            },
            "dark": {
                "name": "الوضع الداكن",
                "colors": {
                    # الألوان الأساسية
                    "primary": "#3b82f6",           # أزرق فاتح
                    "primary_hover": "#2563eb",     # أزرق متوسط عند التمرير
                    "secondary": "#6b7280",         # رمادي متوسط
                    "accent": "#fbbf24",            # أصفر فاتح للتمييز
                    
                    # ألوان الخلفية
                    "background": "#111827",        # خلفية داكنة جداً
                    "surface": "#1f2937",           # سطح داكن
                    "card": "#374151",              # خلفية البطاقات داكنة
                    "sidebar": "#1f2937",           # الشريط الجانبي داكن
                    
                    # ألوان النصوص
                    "text_primary": "#f9fafb",      # نص أساسي فاتح
                    "text_secondary": "#d1d5db",    # نص ثانوي فاتح
                    "text_muted": "#9ca3af",        # نص خافت
                    "text_on_primary": "#ffffff",   # نص على الأزرق
                    
                    # ألوان الحدود
                    "border": "#374151",            # حدود داكنة
                    "border_focus": "#3b82f6",      # حدود عند التركيز
                    "divider": "#374151",           # خطوط الفصل
                    
                    # ألوان الحالات
                    "success": "#34d399",           # أخضر فاتح للنجاح
                    "warning": "#fbbf24",           # أصفر فاتح للتحذير
                    "error": "#f87171",             # أحمر فاتح للخطأ
                    "info": "#60a5fa",              # أزرق فاتح للمعلومات
                    
                    # ألوان الحالات الداكنة
                    "success_light": "#064e3b",     # خلفية خضراء داكنة
                    "warning_light": "#78350f",     # خلفية صفراء داكنة
                    "error_light": "#7f1d1d",       # خلفية حمراء داكنة
                    "info_light": "#1e3a8a",        # خلفية زرقاء داكنة
                    
                    # ألوان الأزرار
                    "button_primary": "#3b82f6",
                    "button_primary_hover": "#2563eb",
                    "button_secondary": "#6b7280",
                    "button_secondary_hover": "#9ca3af",
                    "button_success": "#34d399",
                    "button_success_hover": "#10b981",
                    "button_danger": "#f87171",
                    "button_danger_hover": "#ef4444",
                    
                    # ألوان الإدخال
                    "input_background": "#374151",
                    "input_border": "#4b5563",
                    "input_focus": "#3b82f6",
                    "input_disabled": "#1f2937",
                    
                    # ألوان الجداول
                    "table_header": "#1f2937",
                    "table_row_even": "#374151",
                    "table_row_odd": "#1f2937",
                    "table_row_hover": "#4b5563",
                    
                    # ألوان الظلال
                    "shadow_light": "rgba(0, 0, 0, 0.3)",
                    "shadow_medium": "rgba(0, 0, 0, 0.5)",
                    "shadow_heavy": "rgba(0, 0, 0, 0.8)"
                },
                "fonts": {
                    "primary": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    "secondary": "'Arial', sans-serif",
                    "monospace": "'Courier New', monospace"
                },
                "sizes": {
                    "text_xs": "12px",
                    "text_sm": "14px",
                    "text_base": "16px",
                    "text_lg": "18px",
                    "text_xl": "20px",
                    "text_2xl": "24px",
                    "text_3xl": "30px",
                    
                    "spacing_xs": "4px",
                    "spacing_sm": "8px",
                    "spacing_md": "16px",
                    "spacing_lg": "24px",
                    "spacing_xl": "32px",
                    
                    "border_radius": "6px",
                    "border_radius_lg": "12px",
                    "border_width": "1px"
                }
            }
        }
    
    def load_config(self):
        """تحميل إعدادات الثيم من الملف"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_theme = config.get('current_theme', 'light')
                    
                    # دمج الثيمات المخصصة إن وجدت
                    custom_themes = config.get('custom_themes', {})
                    self.themes.update(custom_themes)
                    
                logger.info(f"تم تحميل إعدادات الثيم: {self.current_theme}")
            else:
                # إنشاء ملف الإعدادات الافتراضي
                self.save_config()
                
        except Exception as e:
            logger.error(f"خطأ في تحميل إعدادات الثيم: {str(e)}")
            self.current_theme = "light"
    
    def save_config(self):
        """حفظ إعدادات الثيم في الملف"""
        try:
            config = {
                'current_theme': self.current_theme,
                'custom_themes': {k: v for k, v in self.themes.items() 
                                if k not in ['light', 'dark']},
                'last_updated': str(datetime.now())
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info("تم حفظ إعدادات الثيم")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ إعدادات الثيم: {str(e)}")
    
    def set_theme(self, theme_name: str) -> bool:
        """
        تعيين الثيم الحالي
        
        Args:
            theme_name: اسم الثيم
            
        Returns:
            True إذا تم التعيين بنجاح، False خلاف ذلك
        """
        try:
            if theme_name in self.themes:
                self.current_theme = theme_name
                self.save_config()
                logger.info(f"تم تغيير الثيم إلى: {theme_name}")
                return True
            else:
                logger.error(f"الثيم غير موجود: {theme_name}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تعيين الثيم: {str(e)}")
            return False
    
    def toggle_theme(self) -> str:
        """
        التبديل بين الوضع الفاتح والداكن
        
        Returns:
            اسم الثيم الجديد
        """
        try:
            new_theme = "dark" if self.current_theme == "light" else "light"
            self.set_theme(new_theme)
            return new_theme
            
        except Exception as e:
            logger.error(f"خطأ في تبديل الثيم: {str(e)}")
            return self.current_theme
    
    def get_current_theme(self) -> Dict:
        """
        الحصول على الثيم الحالي
        
        Returns:
            بيانات الثيم الحالي
        """
        return self.themes.get(self.current_theme, self.themes['light'])
    
    def get_color(self, color_name: str) -> str:
        """
        الحصول على لون من الثيم الحالي
        
        Args:
            color_name: اسم اللون
            
        Returns:
            قيمة اللون
        """
        theme = self.get_current_theme()
        return theme['colors'].get(color_name, '#000000')
    
    def get_font(self, font_name: str) -> str:
        """
        الحصول على خط من الثيم الحالي
        
        Args:
            font_name: اسم الخط
            
        Returns:
            قيمة الخط
        """
        theme = self.get_current_theme()
        return theme['fonts'].get(font_name, 'Arial, sans-serif')
    
    def get_size(self, size_name: str) -> str:
        """
        الحصول على حجم من الثيم الحالي
        
        Args:
            size_name: اسم الحجم
            
        Returns:
            قيمة الحجم
        """
        theme = self.get_current_theme()
        return theme['sizes'].get(size_name, '16px')
    
    def generate_css(self) -> str:
        """
        إنشاء CSS للثيم الحالي
        
        Returns:
            كود CSS
        """
        try:
            theme = self.get_current_theme()
            css_vars = []
            
            # متغيرات الألوان
            for color_name, color_value in theme['colors'].items():
                css_vars.append(f"  --color-{color_name.replace('_', '-')}: {color_value};")
            
            # متغيرات الخطوط
            for font_name, font_value in theme['fonts'].items():
                css_vars.append(f"  --font-{font_name}: {font_value};")
            
            # متغيرات الأحجام
            for size_name, size_value in theme['sizes'].items():
                css_vars.append(f"  --size-{size_name.replace('_', '-')}: {size_value};")
            
            css = f"""/* ثيم {theme['name']} */
:root {{
{chr(10).join(css_vars)}
}}

/* الأنماط الأساسية */
body {{
  background-color: var(--color-background);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--size-text-base);
  margin: 0;
  padding: 0;
  transition: background-color 0.3s ease, color 0.3s ease;
}}

/* الأزرار */
.btn {{
  padding: var(--size-spacing-sm) var(--size-spacing-md);
  border: var(--size-border-width) solid transparent;
  border-radius: var(--size-border-radius);
  font-family: var(--font-primary);
  font-size: var(--size-text-base);
  cursor: pointer;
  transition: all 0.3s ease;
}}

.btn-primary {{
  background-color: var(--color-button-primary);
  color: var(--color-text-on-primary);
}}

.btn-primary:hover {{
  background-color: var(--color-button-primary-hover);
}}

.btn-secondary {{
  background-color: var(--color-button-secondary);
  color: var(--color-text-on-primary);
}}

.btn-secondary:hover {{
  background-color: var(--color-button-secondary-hover);
}}

.btn-success {{
  background-color: var(--color-button-success);
  color: var(--color-text-on-primary);
}}

.btn-success:hover {{
  background-color: var(--color-button-success-hover);
}}

.btn-danger {{
  background-color: var(--color-button-danger);
  color: var(--color-text-on-primary);
}}

.btn-danger:hover {{
  background-color: var(--color-button-danger-hover);
}}

/* البطاقات */
.card {{
  background-color: var(--color-card);
  border: var(--size-border-width) solid var(--color-border);
  border-radius: var(--size-border-radius-lg);
  padding: var(--size-spacing-lg);
  box-shadow: 0 2px 4px var(--color-shadow-light);
  transition: box-shadow 0.3s ease;
}}

.card:hover {{
  box-shadow: 0 4px 8px var(--color-shadow-medium);
}}

/* حقول الإدخال */
.input {{
  background-color: var(--color-input-background);
  border: var(--size-border-width) solid var(--color-input-border);
  border-radius: var(--size-border-radius);
  padding: var(--size-spacing-sm) var(--size-spacing-md);
  font-family: var(--font-primary);
  font-size: var(--size-text-base);
  color: var(--color-text-primary);
  transition: border-color 0.3s ease;
}}

.input:focus {{
  outline: none;
  border-color: var(--color-input-focus);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}}

.input:disabled {{
  background-color: var(--color-input-disabled);
  cursor: not-allowed;
}}

/* الجداول */
.table {{
  width: 100%;
  border-collapse: collapse;
  background-color: var(--color-card);
  border-radius: var(--size-border-radius);
  overflow: hidden;
}}

.table th {{
  background-color: var(--color-table-header);
  color: var(--color-text-primary);
  padding: var(--size-spacing-md);
  text-align: right;
  font-weight: 600;
}}

.table td {{
  padding: var(--size-spacing-md);
  border-bottom: var(--size-border-width) solid var(--color-border);
}}

.table tr:nth-child(even) {{
  background-color: var(--color-table-row-even);
}}

.table tr:nth-child(odd) {{
  background-color: var(--color-table-row-odd);
}}

.table tr:hover {{
  background-color: var(--color-table-row-hover);
}}

/* الشريط الجانبي */
.sidebar {{
  background-color: var(--color-sidebar);
  border-right: var(--size-border-width) solid var(--color-border);
  transition: background-color 0.3s ease;
}}

/* النصوص */
.text-primary {{
  color: var(--color-text-primary);
}}

.text-secondary {{
  color: var(--color-text-secondary);
}}

.text-muted {{
  color: var(--color-text-muted);
}}

/* الحالات */
.text-success {{
  color: var(--color-success);
}}

.text-warning {{
  color: var(--color-warning);
}}

.text-error {{
  color: var(--color-error);
}}

.text-info {{
  color: var(--color-info);
}}

/* خلفيات الحالات */
.bg-success {{
  background-color: var(--color-success-light);
  color: var(--color-success);
}}

.bg-warning {{
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}}

.bg-error {{
  background-color: var(--color-error-light);
  color: var(--color-error);
}}

.bg-info {{
  background-color: var(--color-info-light);
  color: var(--color-info);
}}

/* زر تبديل الثيم */
.theme-toggle {{
  position: fixed;
  top: var(--size-spacing-lg);
  left: var(--size-spacing-lg);
  background-color: var(--color-card);
  border: var(--size-border-width) solid var(--color-border);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px var(--color-shadow-medium);
  transition: all 0.3s ease;
  z-index: 1000;
}}

.theme-toggle:hover {{
  transform: scale(1.1);
  box-shadow: 0 4px 12px var(--color-shadow-heavy);
}}

.theme-toggle svg {{
  width: 24px;
  height: 24px;
  fill: var(--color-text-primary);
}}

/* الرسوم المتحركة */
@keyframes fadeIn {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}

@keyframes slideIn {{
  from {{ transform: translateY(-10px); opacity: 0; }}
  to {{ transform: translateY(0); opacity: 1; }}
}}

.fade-in {{
  animation: fadeIn 0.3s ease;
}}

.slide-in {{
  animation: slideIn 0.3s ease;
}}

/* التخطيط المتجاوب */
@media (max-width: 768px) {{
  .card {{
    padding: var(--size-spacing-md);
  }}
  
  .table th,
  .table td {{
    padding: var(--size-spacing-sm);
    font-size: var(--size-text-sm);
  }}
  
  .theme-toggle {{
    top: var(--size-spacing-md);
    left: var(--size-spacing-md);
    width: 40px;
    height: 40px;
  }}
  
  .theme-toggle svg {{
    width: 20px;
    height: 20px;
  }}
}}"""
            
            return css
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء CSS: {str(e)}")
            return ""
    
    def create_theme_toggle_html(self) -> str:
        """
        إنشاء HTML لزر تبديل الثيم
        
        Returns:
            كود HTML
        """
        return '''
<div class="theme-toggle" id="themeToggle" onclick="toggleTheme()">
  <svg id="themeIcon" viewBox="0 0 24 24">
    <!-- أيقونة الشمس للوضع الفاتح -->
    <g id="sunIcon" style="display: none;">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </g>
    <!-- أيقونة القمر للوضع الداكن -->
    <g id="moonIcon">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </g>
  </svg>
</div>'''
    
    def create_theme_toggle_js(self) -> str:
        """
        إنشاء JavaScript لزر تبديل الثيم
        
        Returns:
            كود JavaScript
        """
        return '''
// إدارة الثيمات
let currentTheme = localStorage.getItem('theme') || 'light';

// تطبيق الثيم عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    applyTheme(currentTheme);
    updateThemeIcon();
});

// تطبيق الثيم
function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    
    // تحديث متغيرات CSS إذا لزم الأمر
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
    } else {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
    }
}

// تبديل الثيم
function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    updateThemeIcon();
    
    // إضافة تأثير انتقالي
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    // إرسال حدث تغيير الثيم
    window.dispatchEvent(new CustomEvent('themeChanged', { 
        detail: { theme: newTheme } 
    }));
}

// تحديث أيقونة الثيم
function updateThemeIcon() {
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');
    
    if (currentTheme === 'dark') {
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    } else {
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    }
}

// الاستماع لتغيير الثيم
window.addEventListener('themeChanged', function(event) {
    console.log('تم تغيير الثيم إلى:', event.detail.theme);
    
    // يمكن إضافة المزيد من الوظائف هنا
    // مثل إعادة تحميل الرسوم البيانية أو تحديث الألوان
});

// تطبيق الثيم على العناصر الديناميكية
function applyThemeToElement(element) {
    element.setAttribute('data-theme', currentTheme);
}

// الحصول على لون من الثيم الحالي
function getThemeColor(colorName) {
    const root = document.documentElement;
    return getComputedStyle(root).getPropertyValue(`--color-${colorName.replace('_', '-')}`).trim();
}

// تحديث ألوان الرسوم البيانية
function updateChartColors() {
    // يمكن استخدام هذه الدالة لتحديث ألوان الرسوم البيانية
    // عند تغيير الثيم
    return {
        primary: getThemeColor('primary'),
        success: getThemeColor('success'),
        warning: getThemeColor('warning'),
        error: getThemeColor('error'),
        info: getThemeColor('info'),
        text: getThemeColor('text_primary'),
        background: getThemeColor('background')
    };
}'''


# مثال على الاستخدام
if __name__ == "__main__":
    from datetime import datetime
    
    # إنشاء مدير الثيمات
    theme_manager = ThemeManager()
    
    try:
        print(f"الثيم الحالي: {theme_manager.current_theme}")
        
        # تبديل الثيم
        new_theme = theme_manager.toggle_theme()
        print(f"الثيم الجديد: {new_theme}")
        
        # الحصول على لون
        primary_color = theme_manager.get_color('primary')
        print(f"اللون الأساسي: {primary_color}")
        
        # إنشاء CSS
        css_content = theme_manager.generate_css()
        print(f"تم إنشاء CSS بطول {len(css_content)} حرف")
        
        # حفظ CSS في ملف
        with open('theme.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print("تم حفظ ملف CSS")
        
    except Exception as e:
        print(f"خطأ: {str(e)}")

