import sys
import unicodedata
sys.path.append('.')
from core_logic import load_config
from app import DEPT_LEADS
import json

config = load_config()
personnel = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]["KT"]
dept_leads = DEPT_LEADS.get("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", {}).get("KT", [])

out = {
    "personnel": personnel,
    "personnel_repr": [repr(p) for p in personnel],
    "dept_leads": dept_leads,
    "dept_leads_repr": [repr(p) for p in dept_leads],
    "match": [p for p in personnel if p not in dept_leads]
}

with open("test_repr.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
