import json
from core_logic import DEPT_LEADS
with open("temp_leads.json", "w", encoding="utf-8") as f:
    json.dump(DEPT_LEADS, f, ensure_ascii=False, indent=2)
