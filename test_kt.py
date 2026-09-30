import json
from app_fixed import *
config = load_config()

# Scenario 1: sel_login_dept = 'KT'
sel_login_dept1 = 'KT'
personnel_list1 = get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', sel_login_dept1, config)
dept_leads1 = DEPT_LEADS.get('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', {}).get(sel_login_dept1, [])
nhan_vien_list1 = [p for p in personnel_list1 if p not in dept_leads1]

# Scenario 2: sel_login_dept = 'Ban Kỹ thuật'
sel_login_dept2 = 'Ban Kỹ thuật'
personnel_list2 = get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', sel_login_dept2, config)
dept_leads2 = DEPT_LEADS.get('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', {}).get(sel_login_dept2, [])
nhan_vien_list2 = [p for p in personnel_list2 if p not in dept_leads2]

out = {
    "KT": {
        "personnel": personnel_list1,
        "leads": dept_leads1,
        "nhanvien": nhan_vien_list1
    },
    "Ban Kỹ thuật": {
        "personnel": personnel_list2,
        "leads": dept_leads2,
        "nhanvien": nhan_vien_list2
    },
    "config_dept_list": get_departments_for_company('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', config)
}
with open("test_kt_logic.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
