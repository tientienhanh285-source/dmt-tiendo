import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



# 1. Hide Streamlit UI elements for a clean dashboard view
st.markdown("""
    <style>
        
        
        
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"### 📊 Bảng Tổng Quan (View) — {selected_company}")

col_f1, col_f2, col_f3, col_auto = st.columns([2, 2, 2, 1])
with col_f1:
    db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
    merged_projs = get_filtered_projects(selected_company, config, db_projs, department=global_active_dept)
    proj_options = ["Tất cả dự án"] + merged_projs
    sel_proj = st.selectbox("Lọc Dự án", proj_options, key="tv_proj")
with col_f2:
    dept_options = ["Tất cả phòng ban"] + get_departments_for_company(selected_company, config)
    sel_dept = st.selectbox("Lọc Phòng ban", dept_options, key="tv_dept")
with col_f3:
    status_options = ["Đang thực hiện", "Sắp tới hạn / Trễ hạn", "Hoàn thành", "Vướng mắc", "Tất cả trạng thái"]
    sel_status = st.selectbox("Lọc Trạng thái", status_options, key="tv_status", index=1)
with col_auto:
    auto_refresh = st.checkbox("🔄 Auto-refresh (5p)", value=True, help="Tự động tải lại trang sau mỗi 5 phút")
    mobile_mode = st.checkbox("📱 Chế độ Điện thoại", value=False, help="Hiển thị dạng thẻ dọc để xem trên mobile")
    if auto_refresh:
        import streamlit.components.v1 as components
        components.html("""
            <script>
                setTimeout(function(){
                    window.parent.location.reload();
                }, 300000);
            </script>
        """, height=0, width=0)
        
# Apply filters
table_df = display_df.copy()
if sel_proj != "Tất cả dự án":
    clean_proj = clean_proj_name(sel_proj)
    table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
if sel_dept != "Tất cả phòng ban":
    table_df = table_df[table_df['PhongBan'] == sel_dept]
    
def get_days_left(d):
    if pd.notna(d) and hasattr(d, 'strftime'):
        if isinstance(d, datetime):
            d = d.date()
        return (d - today).days
    return 999

if sel_status == "Đang thực hiện":
    table_df = table_df[
        (table_df['TrangThai'] != 'Hoàn thành') & 
        (table_df['TrangThai'] != 'Có vướng mắc') & 
        (table_df['Deadline'].apply(get_days_left) > 3)
    ]
elif sel_status == "Sắp tới hạn / Trễ hạn":
    table_df = table_df[
        (table_df['TrangThai'] != 'Hoàn thành') & 
        (table_df['Deadline'].apply(get_days_left) <= 3)
    ]
elif sel_status == "Hoàn thành":
    table_df = table_df[table_df['TrangThai'] == 'Hoàn thành']
elif sel_status == "Vướng mắc":
    table_df = table_df[table_df['TrangThai'] == 'Có vướng mắc']
    
def _get_priority(row):
    st_val = str(row.get('TrangThai', ''))
    if 'Trễ hạn' in st_val or 'Vướng mắc' in st_val or '🔴' in st_val or '⚠️' in st_val:
        return 0
    return 1
    
table_df['SortPriority'] = table_df.apply(_get_priority, axis=1)
if 'NgayCapNhat' in table_df.columns:
    table_df = table_df.sort_values(by=['NgayCapNhat', 'SortPriority', 'ID'], ascending=[False, True, False]).reset_index(drop=True)
else:
    table_df = table_df.sort_values(by=['SortPriority', 'ID'], ascending=[True, False]).reset_index(drop=True)
    
if table_df.empty:
    st.info("Không có công việc nào phù hợp với bộ lọc.")
else:
    df_display = pd.DataFrame()
    df_display['Phòng ban'] = table_df['PhongBan']
    df_display['Người thực hiện'] = table_df['NguoiChuTri']
    df_display['Dự án / Hạng mục'] = table_df['TenDuAn']
    df_display['Tên công việc'] = table_df['TenCongViec']
    df_display['Ngày bắt đầu'] = table_df['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
    df_display['Tỷ trọng KPI'] = table_df.apply(lambda row: f"{int(float(str(row.get('TyTrongKPI', 0)).strip() or 0))}%" if pd.to_numeric(row.get('TyTrongKPI', 0), errors='coerce') > 0 else "Tự chia", axis=1)
    
    def format_dl(row):
        if pd.isna(row['Deadline']) or not isinstance(row['Deadline'], (date, datetime)): return ""
        prog = int(row['PhanTramHoanThanh'])
        date_str = row['Deadline'].strftime('%d/%m/%Y')
        if prog >= 100: return date_str
        days_left = (row['Deadline'] - today).days
        if days_left < 0: return f"🔴 {date_str} (Trễ {abs(days_left)} ngày)"
        elif days_left == 0: return f"⏳ {date_str} (Hạn hôm nay)"
        elif 1 <= days_left <= 3: return f"⚠️ {date_str} (Còn {days_left} ngày)"
        else: return date_str
    df_display['Hạn chót'] = table_df.apply(format_dl, axis=1)
    
    df_display['Tiến độ'] = table_df['PhanTramHoanThanh']
    
    def format_status(row):
        prog = int(row['PhanTramHoanThanh'])
        if prog >= 100: return "✅ Đã xong"
        if pd.notna(row['Deadline']) and row['Deadline'] < today: return "⚠️ Trễ hạn"
        if row['TrangThai'] == 'Có vướng mắc': return "🔴 Vướng mắc"
        from datetime import date, datetime
        if prog == 0 and pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)) and row['NgayBatDau'] > today: return "❌ Chưa bắt đầu"
        if pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)):
            if today >= row['NgayBatDau']: return "⏳ Đang thực hiện"
        return "❌ Chưa bắt đầu"
    df_display['Trạng thái'] = table_df.apply(format_status, axis=1)
    
    def add_prefix_to_name(row):
        prefix = "🌟 [QUẢN LÝ GIAO] " if ("[Mục tiêu" in str(row.get('GiaiTrinhDeXuat', ''))) else ""
        return f"{prefix}{row['TenCongViec']}"
    df_display['Tên công việc'] = table_df.apply(add_prefix_to_name, axis=1)

    ordered_cols = ['Ngày bắt đầu', 'Hạn chót', 'Tiến độ', 'Trạng thái', 'Người thực hiện', 'Phòng ban', 'Dự án / Hạng mục', 'Tên công việc']
    df_display = df_display[ordered_cols]
    
    st.markdown("---")
    if mobile_mode:
        for idx, row in df_display.iterrows():
            prog = int(row['Tiến độ'])
            
            with st.container():
                st.markdown(f"**📌 {row['Tên công việc']}**")
                st.markdown(f"📁 *{row['Dự án / Hạng mục']}* | 👤 *{row['Người thực hiện']}*")
                st.markdown(f"⏳ **Hạn chót:** {row['Hạn chót']} | Trạng thái: **{row['Trạng thái']}**")
                st.caption(f"Tiến độ: {prog}%")
                st.progress(prog)
                st.markdown("---")
    else:
        st.dataframe(
            df_display,
            column_config={
                "Ngày bắt đầu": st.column_config.TextColumn("Ngày bắt đầu", width=90),
                "Hạn chót": st.column_config.TextColumn("Hạn chót", width=150),
                "Tiến độ": st.column_config.ProgressColumn("Tiến độ", format="%d%%", min_value=0, max_value=100, width=100),
                "Trạng thái": st.column_config.TextColumn("Trạng thái", width=120),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width=150),
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width=80),
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width=200),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large")
            },
            use_container_width=True,
            hide_index=True,
            height=700
        )

# ----------------- 3. THÊM / CẬP NHẬT CÔNG VIỆC -----------------


