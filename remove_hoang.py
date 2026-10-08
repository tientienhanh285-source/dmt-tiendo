import json

# 1. Update app_dept_leads.json
with open('app_dept_leads.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

if "HCNS" in d and "Đặng Ngọc Hoàng" in d["HCNS"]:
    d["HCNS"].remove("Đặng Ngọc Hoàng")

with open('app_dept_leads.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# 2. Update core_logic.py
with open('core_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# We need to replace Đặng Ngọc Hoàng in HCNS but only inside core_logic.py
# Let's just find and remove it.
new_content = re.sub(r'("HCNS":\s*\[\s*"Nguyễn Thị Hạnh Tiên",\s*)"Đặng Ngọc Hoàng"\s*\]', r'\1]', content)

with open('core_logic.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Hoang removed from HCNS")
