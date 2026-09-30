import json
from app import load_config, get_gsheets_conn, safe_gsheets_update
import pandas as pd

def fix_cienco_departments():
    config = load_config()
    cienco_name = "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
    
    if "companies" not in config:
        config["companies"] = {}
    if cienco_name not in config["companies"]:
        config["companies"][cienco_name] = {}
        
    cienco_config = config["companies"][cienco_name]
    
    # Ensure departments list exists
    if "departments" not in cienco_config:
        cienco_config["departments"] = [
            "Ban Lãnh đạo",
            "Ban Hành chính Nhân sự",
            "Ban Tài chính Kế toán",
            "Ban Kế hoạch Đầu tư",
            "Ban Chuẩn bị Đầu tư",
            "Ban Kỹ thuật",
            "Ban Đền bù Giải tỏa",
            "Tổ KPI"
        ]
    else:
        # Append if missing
        missing = ["Ban Kế hoạch Đầu tư", "Ban Kỹ thuật"]
        for d in missing:
            if d not in cienco_config["departments"]:
                cienco_config["departments"].append(d)
                
    if "personnel_by_department" not in cienco_config:
        cienco_config["personnel_by_department"] = {}
        
    if "Ban Kế hoạch Đầu tư" not in cienco_config["personnel_by_department"]:
        cienco_config["personnel_by_department"]["Ban Kế hoạch Đầu tư"] = []
    if "Ban Kỹ thuật" not in cienco_config["personnel_by_department"]:
        cienco_config["personnel_by_department"]["Ban Kỹ thuật"] = []

    config["companies"][cienco_name] = cienco_config
    
    conn = get_gsheets_conn()
    if conn:
        df_save = pd.DataFrame([{
            "NhanSu": "APP_GLOBAL_CONFIG",
            "PhongBan": "SYSTEM",
            "Role": "SYSTEM",
            "config_json": json.dumps(config, ensure_ascii=False)
        }])
        safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        print("Success! Added KHĐT and KT for CIENCO.")

if __name__ == "__main__":
    fix_cienco_departments()
