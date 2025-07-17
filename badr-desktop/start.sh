#!/bin/bash

echo "========================================"
echo "   البدر للإنارة - نظام إدارة المحل"
echo "========================================"
echo ""
echo "جاري تشغيل البرنامج..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "خطأ: Node.js غير مثبت على النظام"
    echo "يرجى تثبيت Node.js من: https://nodejs.org"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "خطأ: Python غير مثبت على النظام"
    echo "يرجى تثبيت Python من: https://python.org"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "تثبيت التبعيات..."
    npm install
fi

# Start the application
echo "تشغيل البرنامج..."
npm start

