import json
from app_fixed import *
config = load_config()

bld = get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'BLĐ', config)
with open("test_hoang.json", "w", encoding="utf-8") as f:
    json.dump(bld, f, ensure_ascii=False, indent=2)
