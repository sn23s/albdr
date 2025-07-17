#!/bin/bash

echo "تشغيل برنامج البدر للإنارة..."
echo

cd "$(dirname "$0")"

echo "تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo "تشغيل الخادم..."
python src/main.py

