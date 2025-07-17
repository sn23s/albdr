@echo off
echo تشغيل برنامج البدر للإنارة...
echo.

cd /d "%~dp0"

echo تفعيل البيئة الافتراضية...
call venv\Scripts\activate

echo تشغيل الخادم...
python src\main.py

pause

