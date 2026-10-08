import json
import os

filepath = 'OUTPUT/CONFIG_PROJECTS.json'

with open(filepath, 'r', encoding='utf-8') as f:
    config = json.load(f)

# The user wants to:
# 1. Remove Thắng from DA manager (if any)
# 2. Remove Thể from KHĐT, CBĐT, KT managers
# 3. Remove Nữ from TCKT managers

# Wait, in the JSON it's probably just a dict mapping department names to manager lists or personnel lists.
# Let's clean it up recursively.
def remove_person(d, dept, person):
    if dept in d:
        if isinstance(d[dept], list):
            if person in d[dept]:
                d[dept].remove(person)
        elif isinstance(d[dept], str):
            if d[dept] == person:
                d[dept] = []
        elif isinstance(d[dept], dict):
            pass # ignore

def clean_dict(data):
    # Remove Thắng from DA
    remove_person(data, "DA", "Nguyễn Đình Thắng")
    remove_person(data, "Ban Dự án", "Nguyễn Đình Thắng")
    
    # Remove Thể from KHĐT, CBĐT, KT
    remove_person(data, "KHĐT", "Trần Quốc Thể")
    remove_person(data, "Ban Kế hoạch Đầu tư", "Trần Quốc Thể")
    
    remove_person(data, "CBĐT", "Trần Quốc Thể")
    remove_person(data, "Ban Chuẩn bị Đầu tư", "Trần Quốc Thể")
    
    remove_person(data, "KT", "Trần Quốc Thể")
    remove_person(data, "Ban Kỹ thuật", "Trần Quốc Thể")
    
    # Remove Nữ from TCKT
    remove_person(data, "TCKT", "Đoàn Thị Ngọc Nữ")
    remove_person(data, "Ban Tài chính Kế toán", "Đoàn Thị Ngọc Nữ")

# Check global personnel_by_department if any
if "personnel_by_department" in config:
    clean_dict(config["personnel_by_department"])

# Check DEPT_LEADS if any
if "DEPT_LEADS" in config:
    clean_dict(config["DEPT_LEADS"])

# Check inside companies
if "companies" in config:
    for comp, comp_data in config["companies"].items():
        if "personnel_by_department" in comp_data:
            clean_dict(comp_data["personnel_by_department"])
        if "DEPT_LEADS" in comp_data:
            clean_dict(comp_data["DEPT_LEADS"])

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print("Patched CONFIG_PROJECTS.json successfully.")
