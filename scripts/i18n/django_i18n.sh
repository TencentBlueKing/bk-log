#!bin/bash

WORK_PATH=`pwd`

# 创建翻译文件及js

django-admin makemessages || exit 1

# 中文自动填充对应中文

python $WORK_PATH/scripts/i18n/fill_po_with_po.py -p $WORK_PATH/locale/zh-cn/LC_MESSAGES/django.po

# 输出需要翻译的位置

echo "可能需要翻译的内容，请检查"
echo -e "\nen.django.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/en/LC_MESSAGES/django.po
grep -n -e 'fuzzy' $WORK_PATH/locale/en/LC_MESSAGES/django.po
echo -e "\nzh-cn.django.po"
grep -n -e 'msgstr ""' $WORK_PATH/locale/zh_hans/LC_MESSAGES/django.po
grep -n -e 'fuzzy' $WORK_PATH/locale/zh-cn/LC_MESSAGES/django.po

read -rsp $'Press translate django.po, then press any key to continue...\n' -n1 key
django-admin compilemessages
