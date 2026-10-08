import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core_logic import get_gsheets_conn, safe_gsheets_read

def inspect_config():
    conn = get_gsheets_conn()
    df = safe_gsheets_read(conn, "CONFIG", ttl=0)
    config_rows = df[df["config_json"].notna()]
    app_row = config_rows[config_rows["NhanSu"] == "APP_GLOBAL_CONFIG"]
    if app_row.empty:
        app_row = config_rows.iloc[0:1]
    
    data = json.loads(app_row.iloc[0]["config_json"])
    comp = data.get("companies", {}).get("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", {})
    personnel = comp.get("personnel_by_department", {})
    
    print("ĐBGT in companies:", personnel.get("ĐBGT"))
    print("Ban Đền bù Giải tỏa in root:", data.get("personnel_by_department", {}).get("Ban Đền bù Giải tỏa"))
    print("ĐBGT in root:", data.get("personnel_by_department", {}).get("ĐBGT"))
    
if __name__ == "__main__":
    inspect_config()
