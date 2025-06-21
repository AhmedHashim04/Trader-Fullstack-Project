#!/bin/bash

# ادخل مجلد المشروع الرئيسي
cd /home/ahmed/Desktop/project/src

# نبحث عن كل ملفات test_*.py داخل مجلدات tests
find . -type f -path "*/tests/test_*.py" | while read filepath; do
    # استخراج اسم الملف الحالي بدون المسار
    filename=$(basename "$filepath")
    
    # استخراج اسم التطبيق من المسار (المجلد اللي قبل /tests/)
    appname=$(echo "$filepath" | awk -F'/' '{for(i=1;i<=NF;i++){if($i=="tests"){print $(i-1); exit}}}')

    # التحقق إذا كان الاسم يحتوي فعلاً على اسم التطبيق (لتجنب التكرار)
    if [[ "$filename" != *"_$appname.py" ]]; then
        # الاسم الجديد
        newname=$(echo "$filename" | sed "s/.py/_$appname.py/")
        newpath=$(dirname "$filepath")/$newname
        echo "Renaming $filepath -> $newpath"
        mv "$filepath" "$newpath"
    fi
done


