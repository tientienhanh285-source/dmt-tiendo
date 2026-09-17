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
    except Exception as e:
        import traceback
        st.error(f"Lỗi khi gọi read_db(): {e}")
        st.code(traceback.format_exc())
        display_df = pd.DataFrame()

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



st.info("💡 **Gợi ý:** Để xem chi tiết hướng dẫn sử dụng phần mềm, bạn hãy nhấp vào mục **📖 Sổ tay Hướng dẫn** ở thanh Menu bên trái nhé!")

st.markdown(f"### 🚀 Bảng theo dõi tiến độ công việc — {selected_company}")


# Calculate stats based on filtered dash_df
dash_df = display_df.copy()
total_dash = len(dash_df)
done_dash = len(dash_df[dash_df['TrangThai'] == 'Hoàn thành'])

# Tính số việc Vướng mắc HOẶC Trễ hạn (không đếm trùng)
is_issue = dash_df['TrangThai'] == 'Có vướng mắc'
is_overdue = (pd.to_datetime(dash_df['Deadline'], errors='coerce') < pd.Timestamp(today)) & (dash_df['TrangThai'] != 'Hoàn thành')
issue_and_overdue_count = len(dash_df[is_issue | is_overdue])

doing_dash = total_dash - done_dash - issue_and_overdue_count
if doing_dash < 0:
    doing_dash = 0
    
# 4 metrics cards
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Tổng số việc", total_dash)
with m_col2:
    st.metric("Đã xong", done_dash)
with m_col3:
    st.metric("Đang làm", doing_dash)
with m_col4:
    st.metric("🔴 Trễ hạn / Vướng mắc", issue_and_overdue_count)

st.markdown("---")

st.markdown("""
    <style>
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 1rem !important;
    }
    button[data-baseweb="tab"] span {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #555555 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] span {
        color: #1976d2 !important;
    }
    </style>
""", unsafe_allow_html=True)

tab_master, tab_report, tab_giaoban, tab_data = st.tabs(["🌟 MASTER VIEW", "📊 CÔNG VIỆC TỚI HẠN", "📢 BÁO CÁO GIAO BAN", "📋 BẢNG THEO DÕI TIẾN ĐỘ CÔNG VIỆC"])

with tab_master:
    st.markdown("### 🌟 BẢNG THEO DÕI TIẾN ĐỘ CHỈ TIÊU (MASTER VIEW)")
    st.info("Bảng tổng hợp tiến độ Kế hoạch của các Dự án dựa trên đánh giá và nghiệm thu của Lãnh đạo Ban.")
    
    project_targets = load_project_targets()
    
    active_dept = None
    if role_mode == "Quản lý" and st.session_state.is_manager_authenticated:
        active_dept = st.session_state.get("manager_dept")
    elif role_mode == "Nhân viên" and st.session_state.get('is_personal_authenticated'):
        active_dept = st.session_state.get("auth_user_dept")
        
    if active_dept:
        project_targets = [t for t in project_targets if t.get("department") == active_dept]
        
    if not project_targets:
        if active_dept:
            st.warning(f"Ban {active_dept} chưa có Dự án/Chỉ tiêu nào được thiết lập.")
        else:
            st.warning("Chưa có Chỉ tiêu nào được thiết lập. Vui lòng thiết lập trong file project_targets.json")
    else:
        # Group targets by Project
        projects_dict = {}
        for t in project_targets:
            p_name = t.get("project_name", "Không tên")
            if p_name not in projects_dict:
                projects_dict[p_name] = []
            projects_dict[p_name].append(t)
            
        df_tasks = display_df if not display_df.empty else pd.DataFrame()
        
        for p_name, targets in projects_dict.items():
            with st.expander(f"📁 DỰ ÁN: {p_name.upper()} ({len(targets)} Chỉ tiêu)", expanded=False):
                for t in targets:
                    t_name = t.get("target_name")
                    t_id = t.get("target_id")
                    t_dept = t.get("department")
                    t_approved = t.get("approved", False)
                    
                    budget_2026 = t.get("budget_2026", 0)
                    disbursed = 0.0
                    
                    # Calculate progress
                    progress = 100 if t_approved else 0
                    associated_tasks = pd.DataFrame()
                    
                    if not t_approved:
                        if "SanPhamBanGiao" in df_tasks.columns:
                            associated_tasks = df_tasks[df_tasks["SanPhamBanGiao"] == t_name]
                        
                        if len(associated_tasks) > 0:
                            import re
                            for _, r in associated_tasks.iterrows():
                                giai_trinh = str(r.get("GiaiTrinhDeXuat", ""))
                                matches = re.findall(r'\[GIẢI NGÂN:\s*([\d\.]+)\s*TỶ\]', giai_trinh)
                                for m in matches:
                                    try:
                                        disbursed += float(m)
                                    except:
                                        pass
                            
                            if budget_2026 > 0:
                                progress = min(int((disbursed / budget_2026) * 100), 99)
                            else:
                                total_tasks = len(associated_tasks)
                                if total_tasks >= 1 and total_tasks <= 5:
                                    progress = 30
                                elif total_tasks >= 6 and total_tasks <= 10:
                                    progress = 50
                                elif total_tasks > 10:
                                    progress = 80
                            
                    color = "green" if progress == 100 else ("orange" if progress > 0 else "gray")
                    
                    col1, col2, col3 = st.columns([5, 3, 2])
                    with col1:
                        st.markdown(f"**🎯 {t_name}**")
                        caption_text = f"Ban phụ trách: {t_dept} | Hạn: {t.get('deadline')}"
                        if budget_2026 > 0 or disbursed > 0:
                            caption_text += f"<br/>💰 Kế hoạch: <b style='color:#d97706;'>{budget_2026} Tỷ</b> | Đã giải ngân: <b style='color:#16a34a;'>{disbursed:.2f} Tỷ</b>"
                        st.markdown(f"<span style='color:gray; font-size: 0.85em;'>{caption_text}</span>", unsafe_allow_html=True)
                    with col2:
                        st.progress(progress / 100.0)
                        st.markdown(f"<p style='text-align: center; color: {color}; font-weight: bold;'>{progress}%</p>", unsafe_allow_html=True)
                    with col3:
                        if role_mode in ["Quản lý", "Admin"] and not t_approved:
                            if st.button(f"✅ Nghiệm thu", key=f"approve_{t_id}"):
                                # Update JSON
                                import json
                                for pt in project_targets:
                                    if pt["target_id"] == t_id:
                                        pt["approved"] = True
                                        pt["progress"] = 100
                                        break
                                with open('project_targets.json', 'w', encoding='utf-8') as f:
                                    json.dump(project_targets, f, ensure_ascii=False, indent=2)
                                st.success("Đã nghiệm thu!")
                                st.rerun()
                        elif t_approved:
                            st.markdown("<span style='color:green;font-weight:bold;'>Đã Nghiệm Thu</span>", unsafe_allow_html=True)

                    # Hiển thị các công việc con bên trong
                    if len(associated_tasks) > 0:
                        with st.expander(f"📋 Chi tiết {len(associated_tasks)} công việc đang triển khai"):
                            st.dataframe(
                                associated_tasks[['TenCongViec', 'NguoiChuTri', 'TrangThai', 'Deadline']].rename(columns={
                                    'TenCongViec': 'Tên công việc',
                                    'NguoiChuTri': 'Người phụ trách',
                                    'TrangThai': 'Trạng thái',
                                    'Deadline': 'Hạn chót'
                                }), 
                                use_container_width=True, 
                                hide_index=True
                            )
                    st.markdown("---")


with tab_report:
    st.markdown(f"### 📊 Dashboard Tổng Quan — {selected_company}")

    pass
    
    # Overdue and due today/tomorrow alerts scanning (Group 1 & 2)
    def get_badge_and_urgency(deadline_val, today_dt):
        if pd.isna(deadline_val):
            return None, None
        if not isinstance(deadline_val, date):
            if isinstance(deadline_val, datetime):
                deadline_val = deadline_val.date()
            else:
                return None, None
        if deadline_val < today_dt:
            days_late = (today_dt - deadline_val).days
            return f"🔴 [⚠️ Trễ {days_late} ngày]", 1
        elif deadline_val == today_dt:
            return "⏳ [Hạn hôm nay]", 2
        elif deadline_val == today_dt + timedelta(days=1):
            return "⚠️ [Hạn ngày mai]", 3
        return None, None

    alert_list = []
    for _, row in dash_df[dash_df['TrangThai'] != 'Hoàn thành'].iterrows():
        badge, urgency = get_badge_and_urgency(row['Deadline'], today)
        if badge:
            row_copy = row.copy()
            row_copy['Badge'] = badge
            row_copy['Urgency'] = urgency
            alert_list.append(row_copy)

    if alert_list:
        alert_df_show = pd.DataFrame(alert_list)
        if 'NgayCapNhat' in alert_df_show.columns:
            alert_df_show = alert_df_show.sort_values(by=["Urgency", "NgayCapNhat", "ID"], ascending=[True, False, False])
        else:
            alert_df_show = alert_df_show.sort_values(by=["Urgency", "Deadline"])
        st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(alert_df_show)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")        
    st.markdown("---")

    # Critical alert panel
    st.markdown("### ⚠️ Hạng mục cần lưu ý (Trễ hạn hoặc Sắp đến hạn)")

    if alert_list:
        alert_df_show = pd.DataFrame(alert_list)
        if 'NgayCapNhat' in alert_df_show.columns:
            alert_df_show = alert_df_show.sort_values(by=["Urgency", "NgayCapNhat", "ID"], ascending=[True, False, False])
        else:
            alert_df_show = alert_df_show.sort_values(by=["Urgency", "Deadline"])
        crit_display = pd.DataFrame()
        crit_display['Ngày bắt đầu'] = alert_df_show['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        crit_display['Hạn chót'] = alert_df_show['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        crit_display['Tiến độ'] = alert_df_show['PhanTramHoanThanh'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "0%")
        crit_display['Trạng thái thực tế'] = alert_df_show['Badge']
        crit_display['Người thực hiện'] = alert_df_show['NguoiChuTri']
        crit_display['Phòng ban'] = alert_df_show['PhongBan']
        crit_display['Dự án / Hạng mục'] = alert_df_show['TenDuAn']
        crit_display['Tên công việc'] = alert_df_show['TenCongViec']
        crit_display['Ghi chú / Giải trình vướng mắc'] = alert_df_show['GiaiTrinhDeXuat']
    
        st.dataframe(
            crit_display,
            column_config={
                "Ngày bắt đầu": st.column_config.TextColumn("Ngày bắt đầu", width=90),
                "Hạn chót": st.column_config.TextColumn("Hạn chót", width=150),
                "Tiến độ": st.column_config.TextColumn("Tiến độ", width=80),
                "Trạng thái thực tế": st.column_config.TextColumn("Trạng thái thực tế", width=120),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width=150),
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width=80),
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width=200),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Ghi chú / Giải trình vướng mắc": st.column_config.TextColumn("Ghi chú / Giải trình vướng mắc", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 Đảm bảo tiến độ: Không có công việc nào bị trễ hạn hoặc sắp đến hạn cần lưu ý!")
    
    st.markdown("---")



# ----------------- 1.5. BÁO CÁO GIAO BAN -----------------
with tab_giaoban:
    st.markdown(f"### 📢 Báo cáo Giao ban — {selected_company}")
    
    # Thêm filters
    col_f1, col_f2 = st.columns([1, 2.5])
    with col_f1:
        month_opts = ["Tất cả các tháng"] + [f"Tháng {i}" for i in range(1, 13)]
        gb_month = st.selectbox("Lọc theo Tháng", month_opts, index=0)
    with col_f2:
        gb_status = st.radio("Lọc trạng thái", ["Tất cả", "🔴 Cần chú ý gấp", "🟡 Sắp tới hạn (≤3 ngày)", "🔵 Đang thực hiện", "✅ Hoàn thành"], horizontal=True)
        
    # Lọc các công việc có nguồn giao việc là "Giao ban"
    gb_df = display_df[display_df['NguonGiaoViec'].astype(str).str.contains("Giao ban", na=False, case=False)].copy()
    
    if not gb_df.empty:
        def _get_deadline_status(row):
            st_val = str(row.get('TrangThai', ''))
            if st_val == 'Hoàn thành': return "✅ Hoàn thành"
            if st_val == 'Có vướng mắc': return "🔥 Đang vướng mắc"
            
            dl = row.get('Deadline')
            if pd.isna(dl) or dl == "": return "🔵 Đang thực hiện"
            try:
                if isinstance(dl, str): dl_date = datetime.strptime(dl, "%Y-%m-%d").date()
                else: dl_date = dl.date() if isinstance(dl, datetime) else dl
                diff = (dl_date - today).days
                if diff < 0: return f"🔴 Quá hạn {-diff} ngày"
                if diff <= 3: return f"🟡 Sắp tới hạn ({diff} ngày)"
                return "🔵 Đang thực hiện"
            except:
                return "🔵 Đang thực hiện"
        
        gb_df['Tình trạng'] = gb_df.apply(_get_deadline_status, axis=1)
        
        if gb_month != "Tất cả các tháng":
            m_num = int(gb_month.replace("Tháng ", ""))
            def _match_month(dl):
                if pd.isna(dl) or dl == "": return False
                try:
                    if isinstance(dl, str): d = datetime.strptime(dl, "%Y-%m-%d").date()
                    else: d = dl.date() if isinstance(dl, datetime) else dl
                    return d.month == m_num
                except: return False
            gb_df = gb_df[gb_df['Deadline'].apply(_match_month)]
            
        if gb_status == "🔴 Cần chú ý gấp":
            gb_df = gb_df[gb_df['Tình trạng'].str.contains("🔴|🔥", na=False)]
        elif gb_status == "🟡 Sắp tới hạn (≤3 ngày)":
            gb_df = gb_df[gb_df['Tình trạng'].str.contains("🟡", na=False)]
        elif gb_status == "🔵 Đang thực hiện":
            gb_df = gb_df[gb_df['Tình trạng'].str.contains("🔵", na=False)]
        elif gb_status == "✅ Hoàn thành":
            gb_df = gb_df[gb_df['Tình trạng'].str.contains("✅", na=False)]

        def _get_priority_gb(row):
            st_val = str(row.get('Tình trạng', ''))
            if '🔴' in st_val or '🔥' in st_val: return 0
            if '🟡' in st_val: return 1
            if '🔵' in st_val: return 2
            return 3
        gb_df['SortPriority'] = gb_df.apply(_get_priority_gb, axis=1)
        if 'NgayCapNhat' in gb_df.columns:
            gb_df = gb_df.sort_values(by=['SortPriority', 'NgayCapNhat', 'ID'], ascending=[True, False, False]).reset_index(drop=True)
        else:
            gb_df = gb_df.sort_values(by=['SortPriority', 'ID'], ascending=[True, False]).reset_index(drop=True)
    
    if gb_df.empty:
        st.info('Chưa có công việc nào có "Nguồn giao việc" là "Giao ban" phù hợp với bộ lọc.')
        st.write('💡 Nếu chưa có công việc, hãy chọn Nguồn giao việc là **Công việc trong "Giao ban"** khi tạo hoặc cập nhật công việc.')
    else:
        total_gb = len(gb_df)
        done_gb = len(gb_df[gb_df['TrangThai'] == 'Hoàn thành'])
        issue_gb = len(gb_df[gb_df['TrangThai'] == 'Có vướng mắc'])
        
        gb_col1, gb_col2, gb_col3, gb_col4 = st.columns(4)
        gb_col1.metric("📌 Tổng Số Việc Giao Ban", total_gb)
        gb_col2.metric("✅ Đã Hoàn Thành", done_gb)
        gb_col3.metric("🔥 Đang Vướng Mắc", issue_gb)
        gb_col4.metric("⏳ Đang Thực Hiện", total_gb - done_gb - issue_gb)
        
        st.markdown("#### 📋 Danh sách chi tiết:")
        
        # Formatting the table for Giao ban
        gb_display = gb_df[['Deadline', 'NguoiChuTri', 'TenCongViec', 'PhanTramHoanThanh', 'Tình trạng', 'GiaiTrinhDeXuat']]
        
        mobile_mode_gb = st.checkbox("📱 Chế độ Điện thoại", value=False, key="mobile_gb", help="Hiển thị dạng thẻ dọc để xem trên mobile")
        
        if mobile_mode_gb:
            st.markdown("---")
            for idx, row in gb_df.iterrows():
                prog = int(row['PhanTramHoanThanh']) if pd.notna(row['PhanTramHoanThanh']) else 0
                try:
                    dl_str = row['Deadline'].strftime('%d/%m/%Y') if pd.notna(row['Deadline']) and hasattr(row['Deadline'], 'strftime') else str(row['Deadline'])
                except:
                    dl_str = ""
                
                with st.container():
                    st.markdown(f"**📌 {row['TenCongViec']}**")
                    st.markdown(f"👤 *{row['NguoiChuTri']}* | Tình trạng: **{row['Tình trạng']}**")
                    st.markdown(f"⏳ **Hạn chót:** {dl_str} | Giải trình: *{row.get('GiaiTrinhDeXuat', '')}*")
                    st.caption(f"Tiến độ: {prog}%")
                    st.progress(prog)
                    st.markdown("---")
        else:
            st.dataframe(
                gb_display,
                column_config={
                    "Deadline": st.column_config.DateColumn("Hạn chót", format="DD/MM/YYYY"),
                    "NguoiChuTri": "Người phụ trách",
                    "TenCongViec": st.column_config.TextColumn("Tên công việc", width="large"),
                    "PhanTramHoanThanh": st.column_config.ProgressColumn("Tiến độ", format="%d%%", min_value=0, max_value=100),
                    "Tình trạng": st.column_config.TextColumn("Tình trạng"),
                    "GiaiTrinhDeXuat": st.column_config.TextColumn("Vướng mắc / Giải trình", width="medium")
                },
                use_container_width=True,
                hide_index=True
            )

# ----------------- 2. BẢNG TIẾN ĐỘ CHI TIẾT -----------------

with tab_data:
    st.markdown(f"### 📋 Bảng Tiến Độ Công Việc Chi Tiết — {selected_company}")

    # Filter tools for Boss
    is_personal = role_mode == "Nhân viên" and st.session_state.get("is_personal_authenticated", False)
    
    if is_personal:
        col_filter1, col_filter3 = st.columns(2)
        sel_owner_filter = "Tất cả"
    else:
        col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
        merged_projs = get_filtered_projects(selected_company, config, db_projs, department=global_active_dept)
        proj_options = ["Tất cả dự án"] + merged_projs
        sel_proj_filter = st.selectbox("Lọc nhanh theo Dự án / Hạng mục", proj_options)
    
    if not is_personal:
        with col_filter2:
            owners = ["Tất cả"] + sorted(list(display_df['NguoiChuTri'].dropna().astype(str).unique())) if not display_df.empty else ["Tất cả"]
            sel_owner_filter = st.selectbox("Lọc theo Người phụ trách", owners)
        
    with col_filter3:
        months = set()
        if not display_df.empty:
            for _, row in display_df.iterrows():
                if pd.notna(row.get('NgayBatDau')) and hasattr(row['NgayBatDau'], 'strftime'):
                    months.add(row['NgayBatDau'].strftime('%m/%Y'))
                if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                    months.add(row['Deadline'].strftime('%m/%Y'))
        month_options = ["Tất cả các tháng"] + sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        sel_month_filter = st.selectbox("Lọc nhanh theo Tháng", month_options)
    
    # Apply filters
    table_df = display_df.copy()
    if sel_proj_filter != "Tất cả dự án":
        clean_proj = clean_proj_name(sel_proj_filter)
        table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
        
    if sel_owner_filter != "Tất cả":
        table_df = table_df[table_df['NguoiChuTri'] == sel_owner_filter]
    
    if sel_month_filter != "Tất cả các tháng":
        target_month = sel_month_filter
        mask = (
            table_df['NgayBatDau'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
        ) | (
            table_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
        )
        table_df = table_df[mask]
        
    # Sắp xếp: Ghim Trễ hạn/Vướng mắc lên đầu, sau đó mới đến công việc mới cập nhật
    def _get_priority(row):
        st_val = str(row.get('TrangThai', ''))
        if 'Trễ hạn' in st_val or 'Vướng mắc' in st_val or '🔴' in st_val or '⚠️' in st_val:
            return 0
        return 1
        
    table_df['SortPriority'] = table_df.apply(_get_priority, axis=1)
    if 'NgayCapNhat' in table_df.columns:
        table_df = table_df.sort_values(by=['SortPriority', 'NgayCapNhat', 'ID'], ascending=[True, False, False]).reset_index(drop=True)
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
        import pandas as pd
        df_display['Tỷ trọng KPI'] = table_df.apply(lambda row: f"{int(float(str(row.get('TyTrongKPI', 0)).strip() or 0))}%" if pd.to_numeric(row.get('TyTrongKPI', 0), errors='coerce') > 0 else "Tự chia", axis=1)
    
        # Format Hạn chót
        def format_dl(row):
            if pd.isna(row['Deadline']) or not isinstance(row['Deadline'], (date, datetime)): return ""
            prog = int(row['PhanTramHoanThanh'])
            date_str = row['Deadline'].strftime('%d/%m/%Y')
        
            if prog >= 100:
                return date_str
        
            # prog < 100
            days_left = (row['Deadline'] - today).days
            if days_left < 0:
                days_late = abs(days_left)
                return f"🔴 {date_str} (Trễ hạn {days_late} ngày)"
            elif days_left == 0:
                return f"⏳ {date_str} (Hạn hôm nay)"
            elif 1 <= days_left <= 3:
                return f"⚠️ {date_str} (Sắp hạn - Còn {days_left} ngày)"
            else:
                return date_str
        df_display['Hạn chót'] = table_df.apply(format_dl, axis=1)
    
        df_display['Tiến độ'] = table_df['PhanTramHoanThanh']
    
        # Format Trạng thái
        def format_status(row):
            prog = int(row['PhanTramHoanThanh'])
            is_issue = row['TrangThai'] == 'Có vướng mắc'
        
            if prog >= 100:
                return "✅ Đã xong"
            
            # prog < 100
            if pd.notna(row['Deadline']) and row['Deadline'] < today:
                return "⚠️ Trễ hạn"
            
            if is_issue:
                return "🔴 Vướng mắc"
            
            from datetime import date, datetime
            if prog == 0 and pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)) and row['NgayBatDau'] > today:
                return "❌ Chưa bắt đầu"
            
            # Default state based on start date
            if pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)):
                if today >= row['NgayBatDau']:
                    return "⏳ Đang thực hiện"
                else:
                    return "❌ Chưa bắt đầu"
            else:
                return "⏳ Đang thực hiện"
        df_display['Trạng thái'] = table_df.apply(format_status, axis=1)
    
        # Format Nguyên nhân trễ hạn
        def format_late_cause(row):
            is_comp = (row['TrangThai'] == 'Hoàn thành')
            is_late = (pd.notna(row['Deadline']) and row['Deadline'] < today) and not is_comp
            if not is_late:
                return "--"
        
            val = row.get('PhanLoaiTreHan', '')
            if "chủ quan" in str(val).lower():
                return "🔴 [Do chủ quan]"
            elif "khách quan" in str(val).lower():
                explain = row.get('GiaiTrinhDeXuat', '')
                if pd.notna(explain) and str(explain).strip():
                    return f"⚠️ [Do khách quan] - {str(explain).strip()}"
                return "⚠️ [Do khách quan]"
            else:
                return "--"
        df_display['Nguyên nhân trễ hạn'] = table_df.apply(format_late_cause, axis=1)
    
        # Format Kết quả / File đính kèm
        def format_notes(row):
            is_comp = (row['TrangThai'] == 'Hoàn thành')
            if is_comp:
                val = row['LinkKetQua']
                if not val or pd.isna(val):
                    return "Chưa đính kèm kết quả"
                if isinstance(val, str) and val.startswith("OUTPUT"):
                    display_name = os.path.basename(val)
                    if "_" in display_name:
                        display_name = display_name.split("_", 1)[1]
                    return f"📁 {display_name}"
                return str(val)
            else:
                return row['GiaiTrinhDeXuat'] if (isinstance(row['GiaiTrinhDeXuat'], str) and row['GiaiTrinhDeXuat']) else "--"
        df_display['Kết quả / File đính kèm'] = table_df.apply(format_notes, axis=1)
    
        # Reorder columns
        ordered_cols = [
            'Ngày bắt đầu',
            'Hạn chót',
            'Tiến độ',
            'Trạng thái',
            'Người thực hiện',
            'Phòng ban',
            'Dự án / Hạng mục',
            'Tên công việc',
            'Tỷ trọng KPI',
            'Nguyên nhân trễ hạn',
            'Kết quả / File đính kèm'
        ]
        df_display = df_display[ordered_cols]
    
        # Render clean st.dataframe
        st.dataframe(
            df_display,
            column_config={
                "Ngày bắt đầu": st.column_config.TextColumn("Ngày bắt đầu", width=90),
                "Hạn chót": st.column_config.TextColumn("Hạn chót", width=150),
                "Tiến độ": st.column_config.ProgressColumn(
                    "Tiến độ",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                    width=100
                ),
                "Trạng thái": st.column_config.TextColumn("Trạng thái", width=120),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width=150),
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width=80),
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width=200),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Nguyên nhân trễ hạn": st.column_config.TextColumn("Nguyên nhân trễ hạn", width=150),
                "Kết quả / File đính kèm": st.column_config.LinkColumn(
                    "Kết quả / File đính kèm",
                    max_chars=300,
                    width="medium"
                )
            },
            use_container_width=True,
            hide_index=True
        )

