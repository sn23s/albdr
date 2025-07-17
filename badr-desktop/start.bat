@echo off
title البدر للإنارة - تشغيل البرنامج

REM --- Configuration ---
set PYTHON_EXE="C:\Users\mohammed\AppData\Local\Programs\Python\Python313\python.exe"
set NPM_CMD="C:\Program Files\nodejs\npm.cmd"
REM --- End Configuration ---


echo ========================================
echo    البدر للإنارة - نظام إدارة المحل
echo ========================================
echo.
echo جاري تشغيل الخادم الخلفي (Python Backend)...

REM Start the backend in a separate window
start "Badr Backend" cmd /k "%PYTHON_EXE% ..\badr_lighting\src\main.py"

echo جاري تشغيل خادم الواجهة الأمامية (React Frontend)...

REM Start the frontend development server in a separate window
start "Badr Frontend" cmd /k "cd ..\badr-frontend && %NPM_CMD% run dev"

echo جاري تشغيل تطبيق سطح المكتب (Electron App)...

REM Start the Electron app in a separate window
start "Badr Desktop App" cmd /k "%NPM_CMD% start"

echo.
echo تم تشغيل جميع مكونات البرنامج. يرجى التحقق من النوافذ الجديدة.
echo.
pause
