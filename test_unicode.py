import sys
import json
import unicodedata
sys.path.append('.')
from core_logic import load_config, DEPT_LEADS

config = load_config()
p = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("personnel_by_department", {})
db_kt = p.get("KT", [])

code_kt = DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["KT"]

out = {
    "db_kt_raw": db_kt,
    "code_kt_raw": code_kt,
    "db_kt_bytes": [list(x.encode('utf-8')) for x in db_kt],
    "code_kt_bytes": [list(x.encode('utf-8')) for x in code_kt],
    "db_kt_nfc": [list(unicodedata.normalize('NFC', x).encode('utf-8')) for x in db_kt],
    "code_kt_nfc": [list(unicodedata.normalize('NFC', x).encode('utf-8')) for x in code_kt]
}

with open("test_unicode.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
