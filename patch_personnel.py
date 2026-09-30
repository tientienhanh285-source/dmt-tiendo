# -*- coding: utf-8 -*-
import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py', 'r', 'utf-8') as f:
    content = f.read()

target = '''    else:
        # Fallback to global config if any, or empty list
        personnel_list = config.get("personnel_by_department", {}).get(dept, [])
        
    # Map dept name to abbr
    abbr = DEPT_ABBR.get(dept, dept)
        
    # Exclude managers from the personnel list
    dept_leads = DEPT_LEADS.get(company, {}).get(abbr, [])
    if isinstance(dept_leads, str):
        dept_leads = [dept_leads] if dept_leads else []
        
    return [p for p in personnel_list if p not in dept_leads]'''

replacement = '''    else:
        # Fallback to global config if any, or empty list
        personnel_list = config.get("personnel_by_department", {}).get(dept, [])
        
    return personnel_list'''

# Fix line endings just in case
content = content.replace('\r\n', '\n')
target = target.replace('\r\n', '\n')
replacement = replacement.replace('\r\n', '\n')

if target in content:
    content = content.replace(target, replacement)
    with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py', 'w', 'utf-8') as f:
        f.write(content)
    print('Replaced')
else:
    print('Target not found')
