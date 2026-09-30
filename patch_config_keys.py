# -*- coding: utf-8 -*-
import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py', 'r', 'utf-8') as f:
    content = f.read()

target = '        # Map departments to abbreviations to ensure consistency across the app'
replacement = '''        # Migrate old company names to new standardized names
        companies_data = data.get("companies", {})
        if "CTY CP Ð?U TU ÐÀ N?NG - MI?N TRUNG" in companies_data:
            companies_data["CÔNG TY CP Ð?U TU ÐÀ N?NG"] = companies_data.pop("CTY CP Ð?U TU ÐÀ N?NG - MI?N TRUNG")
        if "CTY CP XÂY D?NG CÔNG TRÌNH GIAO THÔNG ÐN-MT" in companies_data:
            companies_data["CÔNG TY CP XÂY D?NG CÔNG TRÌNH GIAO THÔNG ÐN-MT"] = companies_data.pop("CTY CP XÂY D?NG CÔNG TRÌNH GIAO THÔNG ÐN-MT")

        # Map departments to abbreviations to ensure consistency across the app'''

if target in content:
    content = content.replace(target, replacement)
    with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py', 'w', 'utf-8') as f:
        f.write(content)
    print('Replaced')
else:
    print('Target not found')
