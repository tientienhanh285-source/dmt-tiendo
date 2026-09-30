import sys
import json
sys.path.append('.')
from core_logic import load_config, save_config

config = load_config()

# Update for CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG
if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in config.get("companies", {}):
    if "personnel_by_department" in config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]:
        # Update both full name and abbreviation just in case
        if "Ban Kỹ thuật" in config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]:
            config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]["Ban Kỹ thuật"] = ["Trần Quốc Thể", "Nguyễn Văn Bồn"]
        if "KT" in config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]:
            config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]["KT"] = ["Trần Quốc Thể", "Nguyễn Văn Bồn"]
        
        # If it's missing entirely from the dict, add it
        if "KT" not in config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]:
             config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"]["KT"] = ["Trần Quốc Thể", "Nguyễn Văn Bồn"]

save_config(config)
print("Updated config in DB")
