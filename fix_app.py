import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add safe wrappers after get_gsheets_conn
wrapper_code = """
def safe_gsheets_read(conn, worksheet, ttl=0, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    kwargs = {"worksheet": worksheet, "ttl": ttl}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    try:
        df = conn.read(**kwargs)
        return df if df is not None else fallback_df
    except Exception as e:
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        return fallback_df

def safe_gsheets_update(conn, worksheet, data):
    kwargs = {"worksheet": worksheet, "data": data}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    try:
        conn.update(**kwargs)
        return True
    except Exception as e:
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        return False
"""

# Find where to insert wrapper_code
if "def save_config(" in content and "safe_gsheets_read" not in content:
    content = content.replace("def save_config(", wrapper_code + "\ndef save_config(")

# 2. Replace conn.read and conn.update with wrappers
# conn.read(worksheet="CONFIG", ttl=0) -> safe_gsheets_read(conn, worksheet="CONFIG", ttl=0)
content = re.sub(r'conn\.read\((.*?)\)', r'safe_gsheets_read(conn, \1)', content)

# conn.update(worksheet="CONFIG", data=df_save) -> safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
content = re.sub(r'conn\.update\((.*?)\)', r'safe_gsheets_update(conn, \1)', content)

# 3. Add sidebar input for gsheet_url
sidebar_code = """st.sidebar.markdown("---")

# Link Google Sheets Config
st.sidebar.markdown("### 🔗 Kết Nối Google Sheets")
if "gsheet_url" not in st.session_state:
    st.session_state["gsheet_url"] = ""

gsheet_url_input = st.sidebar.text_input(
    "Link Google Sheets (DB chính)", 
    value=st.session_state["gsheet_url"], 
    placeholder="Dán link Google Sheets..."
)

if gsheet_url_input != st.session_state["gsheet_url"]:
    st.session_state["gsheet_url"] = gsheet_url_input
    st.rerun()
"""
if "### 🔗 Kết Nối Google Sheets" not in content:
    content = content.replace('st.sidebar.markdown("---")', sidebar_code, 1)

# 4. Remove st.error and st.warning about google sheets
content = re.sub(r'st\.error\(f"Lỗi lưu cấu hình lên Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.error\(f"Lỗi đọc cấu hình từ Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.error\(f"Lỗi ghi dữ liệu Gantt lên Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.error\(f"Lỗi đọc dữ liệu Gantt từ Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.warning\(f"Lỗi đọc văn bản đến từ Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.error\(f"Lỗi ghi dữ liệu văn bản đến lên Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.warning\(f"Lỗi đọc DB từ Google Sheets: \{e\}"\)', 'pass', content)
content = re.sub(r'st\.error\(f"Lỗi ghi dữ liệu DB lên Google Sheets: \{e\}"\)', 'pass', content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modified app.py successfully!")
