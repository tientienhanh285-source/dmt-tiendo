import sys
import os
import json
sys.path.append('.')
from core_logic import load_config
from app import DEPT_LEADS

config = load_config()
selected_company = "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"
sel_login_dept = "KT"

def get_personnel_for_company_dept(company, dept, config):
    companies = config.get("companies", {})
    personnel_list = []
    if company in companies:
        personnel_list = companies[company].get("personnel_by_department", {}).get(dept, [])
    else:
        personnel_list = config.get("personnel_by_department", {}).get(dept, [])
    return personnel_list

personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])

out = {
    "personnel_list": personnel_list,
    "dept_leads": dept_leads,
    "selected_company": selected_company
}

with open("test_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
