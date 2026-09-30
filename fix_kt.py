import os

files_to_fix = [
    'app.py',
    'app_fixed.py',
    'app_temp.py',
    'core_logic.py',
    'fix_dept_leads_final.py',
    'patch_core_logic_leads.py',
    'patch_roles_from_image.py'
]

for f in files_to_fix:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('"KT": ["Nguyễn Văn Bồn"]', '"KT": ["Trần Quốc Thể"]')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Fixed {f}")
