import streamlit as st
import pandas as pd
import json
from datetime import datetime
from core_logic import get_gsheets_conn

st.set_page_config(page_title="Nhật ký Hệ thống", page_icon="🕵️‍♂️", layout="wide")

if not st.session_state.get('is_admin_authenticated', False):
    st.error("🚫 Bạn không có quyền truy cập trang này. Dành riêng cho Admin/BLĐ.")
    st.stop()

st.title("🕵️‍♂️ Nhật ký Hệ thống (Audit Log)")
st.markdown("Tra cứu lịch sử thao tác của người dùng trên hệ thống (Truy vết).")

@st.cache_data(ttl=30, show_spinner="Đang tải dữ liệu log...")
def fetch_logs():
    conn = get_gsheets_conn()
    if not conn:
        return pd.DataFrame()
    try:
        res = conn.table("kpi_config").select("*").eq("LoaiCauHinh", "AUDIT_LOG").execute()
        if not res.data:
            return pd.DataFrame()
        
        parsed_logs = []
        for row in res.data:
            cjson = row.get("config_json", "{}")
            try:
                cdata = json.loads(cjson)
                parsed_logs.append({
                    "Người thao tác": cdata.get("user", "Unknown"),
                    "Hành động": cdata.get("action", ""),
                    "Thời gian": cdata.get("time", "")
                })
            except:
                pass
                
        df = pd.DataFrame(parsed_logs)
        if not df.empty:
            # Sắp xếp theo thời gian mới nhất (nếu format YYYY-MM-DD HH:MM:SS)
            df = df.sort_values(by="Thời gian", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Lỗi truy xuất Log: {e}")
        return pd.DataFrame()

df_logs = fetch_logs()

if df_logs.empty:
    st.info("Chưa có bản ghi nhật ký nào trong hệ thống.")
else:
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        users = ["Tất cả"] + sorted(list(df_logs["Người thao tác"].unique()))
        sel_user = st.selectbox("Lọc theo Tài khoản", users)
    with col2:
        search_kw = st.text_input("Tìm kiếm thao tác...")
        
    filtered_df = df_logs.copy()
    if sel_user != "Tất cả":
        filtered_df = filtered_df[filtered_df["Người thao tác"] == sel_user]
    if search_kw.strip():
        filtered_df = filtered_df[filtered_df["Hành động"].str.contains(search_kw.strip(), case=False, na=False)]
        
    st.markdown(f"**Tổng số:** {len(filtered_df)} bản ghi.")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 Làm mới Log"):
        fetch_logs.clear()
        st.rerun()
