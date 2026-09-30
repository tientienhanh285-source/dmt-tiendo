import sys
import json
sys.path.append('.')
from core_logic import load_config

config = load_config()

out = {}
if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in config.get("companies", {}):
    p = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("personnel_by_department", {})
    out["KT"] = p.get("KT")
    out["Ban Kỹ thuật"] = p.get("Ban Kỹ thuật")
    out["all_keys"] = list(p.keys())

with open("test_db_check.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
