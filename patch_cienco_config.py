import json
from app import load_config, get_gsheets_conn, safe_gsheets_update
import pandas as pd

def update_supabase_config():
    print("Loading config from Supabase...")
    config = load_config()
    
    cienco_name = "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
    
    if "companies" not in config:
        config["companies"] = {}
        
    if cienco_name not in config["companies"]:
        config["companies"][cienco_name] = {}
        
    if "projects_by_category" not in config["companies"][cienco_name]:
        config["companies"][cienco_name]["projects_by_category"] = {}
        
    if "HẠ TẦNG & GIAO THÔNG" not in config["companies"][cienco_name]["projects_by_category"]:
        config["companies"][cienco_name]["projects_by_category"]["HẠ TẦNG & GIAO THÔNG"] = []
        
    projects_to_add = [
        "Tuyến đường Lê Trọng Tấn",
        "Tuyến đường Lê Trọng Tấn - Hoà Nhơn",
        "Tuyến đường Trần Hưng Đạo",
        "Trục 1 Tây Bắc (Đoạn 1)",
        "Trục 1 Tây Bắc (Đoạn 2)",
        "Khu TĐC Hoà Vang",
        "Khu TĐC Hòa Liên 5",
        "Dự án Tam Anh Nam"
    ]
    
    current_projects = config["companies"][cienco_name]["projects_by_category"]["HẠ TẦNG & GIAO THÔNG"]
    for p in projects_to_add:
        if p not in current_projects:
            current_projects.append(p)
            
    config["companies"][cienco_name]["projects_by_category"]["HẠ TẦNG & GIAO THÔNG"] = current_projects
    
    print("Saving config back to Supabase...")
    conn = get_gsheets_conn()
    if conn:
        df_save = pd.DataFrame([{
            "NhanSu": "APP_GLOBAL_CONFIG",
            "PhongBan": "SYSTEM",
            "Role": "SYSTEM",
            "config_json": json.dumps(config, ensure_ascii=False)
        }])
        safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        print("Success!")
    else:
        print("Failed to get connection")

if __name__ == "__main__":
    update_supabase_config()
