import json
import app_fixed

config = app_fixed.config
hcns = app_fixed.get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'HCNS', config)
tckt = app_fixed.get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'TCKT', config)
bld = app_fixed.get_personnel_for_company_dept('CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'BLĐ', config)

out = {
    "HCNS": hcns,
    "TCKT": tckt,
    "BLD": bld,
    "CONFIG_COMPANIES": list(config.get("companies", {}).keys())
}

with open("test_final.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
