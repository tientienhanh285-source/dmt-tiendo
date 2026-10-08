import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core_logic import get_gsheets_conn, safe_gsheets_read, safe_gsheets_update

def update_supabase_config():
    conn = get_gsheets_conn()
    df = safe_gsheets_read(conn, "CONFIG", ttl=0)
    config_rows = df[df["config_json"].notna()]
    app_row = config_rows[config_rows["NhanSu"] == "APP_GLOBAL_CONFIG"]
    if app_row.empty:
        app_row = config_rows.iloc[0:1]
        
    data = json.loads(app_row.iloc[0]["config_json"])
    modified = False
    
    if "personnel_by_department" in data:
        data["personnel_by_department"]["Xí nghiệp DTBD"] = ["Mai Văn Châu"]
        data["personnel_by_department"]["Sàn GDBĐS"] = ["Ngô Thị Tâm"]
        data["personnel_by_department"]["XN DTBD"] = ["Mai Văn Châu"]
        modified = True
                
    if "companies" in data and "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG" in data["companies"]:
        comp_data = data["companies"]["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]
        if "personnel_by_department" not in comp_data:
            comp_data["personnel_by_department"] = {}
        comp_data["personnel_by_department"]["Xí nghiệp DTBD"] = ["Mai Văn Châu"]
        comp_data["personnel_by_department"]["Sàn GDBĐS"] = ["Ngô Thị Tâm"]
        comp_data["personnel_by_department"]["XN DTBD"] = ["Mai Văn Châu"]
        modified = True
                
    if not modified:
        print("No modifications made!")
        return
        
    new_json_str = json.dumps(data, ensure_ascii=False)
    idx = app_row.index[0]
    df.at[idx, "config_json"] = new_json_str
    
    print("Updating Supabase...")
    safe_gsheets_update(conn, "CONFIG", df)
    print("Done!")

if __name__ == "__main__":
    update_supabase_config()
