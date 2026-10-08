import json
import re
from core_logic import load_config, save_config

config = load_config()
da_personnel = ["Nguyễn Quốc Vinh", "Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"]

# CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG
if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in config.get("companies", {}):
    personnel = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("personnel_by_department", {})
    if "Ban Dự án" in personnel or "Ban Dự án" in config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("departments", []):
        personnel["Ban Dự án"] = da_personnel
    if "DA" in personnel:
        personnel["DA"] = da_personnel
    config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"] = personnel

if "personnel_by_department" in config:
    personnel = config["personnel_by_department"]
    if "Ban Dự án" in personnel:
        personnel["Ban Dự án"] = da_personnel
    if "DA" in personnel:
        personnel["DA"] = da_personnel

save_config(config)

with open('core_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'"Ban Dự án":\s*\[.*?\]'
replacement = '"Ban Dự án": ["Nguyễn Quốc Vinh", "Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"]'
content = re.sub(pattern, replacement, content)

with open('core_logic.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored DA personnel")
