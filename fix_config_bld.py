import json
import streamlit as st
import pandas as pd
from app import get_gsheets_conn, safe_gsheets_read, safe_gsheets_update, load_settings

def force_fix_config():
    # Mock session state
    settings = load_settings()
    if "gsheet_url" in settings:
        st.session_state["gsheet_url"] = settings["gsheet_url"]
        
    conn = get_gsheets_conn()
    if not conn:
        print("No connection")
        return
        
    df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=0)
    if df is None or df.empty:
        print("No config found")
        return
        
    json_str = df.iloc[0]["config_json"]
    data = json.loads(json_str)
    
    if "personnel_by_department" in data:
        data["personnel_by_department"]["Ban Lãnh đạo"] = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
        
        df_save = pd.DataFrame([{"config_json": json.dumps(data, ensure_ascii=False)}])
        success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        if success:
            print("Successfully updated CONFIG in Google Sheets!")
        else:
            print("Failed to save CONFIG.")
    else:
        print("No personnel config found to update.")

if __name__ == "__main__":
    force_fix_config()
