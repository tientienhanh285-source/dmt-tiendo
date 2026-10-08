import re
import json

with open('core_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update Ban Kế hoạch Đầu tư to have Lợi, Tin, Cúc, Thức
# Let's just use regex to replace it
pattern = r'"Ban Kế hoạch Đầu tư":\s*\[.*?\]'
replacement = '"Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc"]'
content = re.sub(pattern, replacement, content)

with open('core_logic.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Update app_dept_leads.json
with open('app_dept_leads.json', 'r', encoding='utf-8') as f:
    leads = json.load(f)

if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in leads:
    leads["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["KHĐT"] = ["Nguyễn Trần Thức"]

with open('app_dept_leads.json', 'w', encoding='utf-8') as f:
    json.dump(leads, f, ensure_ascii=False, indent=2)

print("Updated KHDT personnel and manager.")
