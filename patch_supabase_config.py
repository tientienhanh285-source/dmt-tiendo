import json
from core_logic import load_config, save_config

config = load_config()

# CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG
if "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in config.get("companies", {}):
    personnel = config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"].get("personnel_by_department", {})
    
    # 1. Ban Hành chính Nhân sự
    if "Ban Hành chính Nhân sự" in personnel:
        personnel["Ban Hành chính Nhân sự"] = [p for p in personnel["Ban Hành chính Nhân sự"] if p != "Đặng Ngọc Hoàng"]
    if "HCNS" in personnel:
        personnel["HCNS"] = [p for p in personnel["HCNS"] if p != "Đặng Ngọc Hoàng"]

    # 2. Ban Chuẩn bị Đầu tư
    cbdt = ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"]
    if "Ban Chuẩn bị Đầu tư" in personnel:
        personnel["Ban Chuẩn bị Đầu tư"] = cbdt
    if "CBĐT" in personnel:
        personnel["CBĐT"] = cbdt

    # 3. Ban Kế hoạch Đầu tư
    khdt = ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc"]
    if "Ban Kế hoạch Đầu tư" in personnel:
        personnel["Ban Kế hoạch Đầu tư"] = khdt
    if "KHĐT" in personnel:
        personnel["KHĐT"] = khdt

    config["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]["personnel_by_department"] = personnel

# Also check global personnel_by_department if it exists
if "personnel_by_department" in config:
    personnel = config["personnel_by_department"]
    if "Ban Hành chính Nhân sự" in personnel:
        personnel["Ban Hành chính Nhân sự"] = [p for p in personnel["Ban Hành chính Nhân sự"] if p != "Đặng Ngọc Hoàng"]
    if "HCNS" in personnel:
        personnel["HCNS"] = [p for p in personnel["HCNS"] if p != "Đặng Ngọc Hoàng"]
        
    cbdt = ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"]
    if "Ban Chuẩn bị Đầu tư" in personnel:
        personnel["Ban Chuẩn bị Đầu tư"] = cbdt
    if "CBĐT" in personnel:
        personnel["CBĐT"] = cbdt

    khdt = ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc"]
    if "Ban Kế hoạch Đầu tư" in personnel:
        personnel["Ban Kế hoạch Đầu tư"] = khdt
    if "KHĐT" in personnel:
        personnel["KHĐT"] = khdt

save_config(config)
print("Config saved to Supabase.")
