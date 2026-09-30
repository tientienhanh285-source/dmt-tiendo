import sys
import os
import json
sys.path.append('.')
from core_logic import load_config
from app import DEPT_ABBR, get_departments_for_company

config = load_config()

# App.py logic
for comp_name, comp_data in config.get("companies", {}).items():
    if "departments" in comp_data:
        comp_data["departments"] = [DEPT_ABBR.get(d, d) for d in comp_data["departments"]]
    if "personnel_by_department" in comp_data:
        new_personnel = {}
        for d, p in comp_data["personnel_by_department"].items():
            new_personnel[DEPT_ABBR.get(d, d)] = p
        comp_data["personnel_by_department"] = new_personnel

valid_depts = get_departments_for_company("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", config)

out = {
    "valid_depts": valid_depts
}

with open("test_depts.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
