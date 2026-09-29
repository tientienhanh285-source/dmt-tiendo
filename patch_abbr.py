import codecs
import re

core_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py'
with codecs.open(core_file, 'r', 'utf-8') as f:
    content = f.read()

replacement = """def get_personnel_for_company_dept(company, dept, config):
    companies = config.get("companies", {})
    personnel_list = []
    if company in companies:
        personnel_list = companies[company].get("personnel_by_department", {}).get(dept, [])
    else:
        # Fallback to global config if any, or empty list
        personnel_list = config.get("personnel_by_department", {}).get(dept, [])
        
    # Map dept name to abbr
    abbr = DEPT_ABBR.get(dept, dept)
        
    # Exclude managers from the personnel list
    dept_leads = DEPT_LEADS.get(company, {}).get(abbr, [])
    if isinstance(dept_leads, str):
        dept_leads = [dept_leads] if dept_leads else []
        
    return [p for p in personnel_list if p not in dept_leads]"""

content = re.sub(r'def get_personnel_for_company_dept\(company, dept, config\):[\s\S]*?return \[p for p in personnel_list if p not in dept_leads\]', replacement, content, count=1)

with codecs.open(core_file, 'w', 'utf-8') as f:
    f.write(content)
print('Patched core_logic.py')
