import json
from core_logic import load_config, save_config

config = load_config()

# CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG
if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in config.get("companies", {}):
    personnel = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("personnel_by_department", {})
    
    # 1. Ban Dự án
    vinh = ["Nguyễn Quốc Vinh"]
    if "Ban Dự án" in personnel:
        personnel["Ban Dự án"] = vinh
    if "DA" in personnel:
        personnel["DA"] = vinh

    config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"] = personnel

# Also check global personnel_by_department if it exists
if "personnel_by_department" in config:
    personnel = config["personnel_by_department"]
    vinh = ["Nguyễn Quốc Vinh"]
    if "Ban Dự án" in personnel:
        personnel["Ban Dự án"] = vinh
    if "DA" in personnel:
        personnel["DA"] = vinh

save_config(config)
print("Config saved to Supabase: Added Nguyễn Quốc Vinh to Ban DA.")
