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



st.markdown('<div class="main-title">📊 Quản trị BSC - KPI (Top-Down)</div>', unsafe_allow_html=True)

if not (st.session_state.is_admin_authenticated or st.session_state.is_manager_authenticated):
    st.warning("🔒 Chức năng này chỉ dành cho Quản lý (Trưởng bộ phận) và HR. Vui lòng đăng nhập từ menu bên trái.")
else:
    st.info("💡 Module này giúp Quản lý thiết lập Kế hoạch năm, rã thành Mục tiêu Quý/Tháng, sau đó giao việc và gắn tỷ trọng KPI trực tiếp cho nhân viên.")
    
    if "bsc_data" not in st.session_state:
        st.session_state.bsc_data = load_bsc_config()
        
    bsc_data = st.session_state.bsc_data
    
    tab1, tab2, tab3 = st.tabs(["1. Thiết lập Kế hoạch Năm & Quý", "2. Phân rã Mục tiêu Tháng", "3. Giao việc từ Mục tiêu"])
    
    with tab1:
        st.subheader("Thiết lập Kế hoạch Năm & Quý")
        st.write("Tại đây, Ban HCNS hoặc Quản lý sẽ thiết lập các mục tiêu lớn trong năm của từng Ban.")
        
        with st.form("form_add_year_goal"):
            col1, col2 = st.columns(2)
            with col1:
                target_year = st.selectbox("Năm", ["2025", "2026", "2027"])
                dept = st.selectbox("Phòng ban", get_departments_for_company(selected_company, config))
            with col2:
                goal_name = st.text_input("Tên Mục tiêu Kế hoạch Năm")
                quarter = st.selectbox("Phân bổ vào Quý", ["Q1", "Q2", "Q3", "Q4", "Cả năm"])
            submit_year = st.form_submit_button("Lưu Kế hoạch")
            
            if submit_year:
                if goal_name:
                    year_key = f"{dept}_{target_year}"
                    if year_key not in bsc_data["years"]:
                        bsc_data["years"][year_key] = []
                    bsc_data["years"][year_key].append({"name": goal_name, "quarter": quarter})
                    if save_bsc_config(bsc_data):
                        st.success("Lưu Kế hoạch năm thành công!")
                        st.rerun()
                    else:
                        st.error("Lỗi khi lưu!")
                else:
                    st.warning("Vui lòng nhập tên Mục tiêu!")
        
        st.write("---")
        st.write("### Danh sách Mục tiêu Năm")
        year_key_sel = f"{dept}_{target_year}"
        if year_key_sel in bsc_data["years"] and bsc_data["years"][year_key_sel]:
            import pandas as pd
            df_y = pd.DataFrame(bsc_data["years"][year_key_sel])
            st.dataframe(df_y, use_container_width=True)
        else:
            st.info("Chưa có kế hoạch năm cho phòng ban này.")
            
    with tab2:
        st.subheader("Phân rã Mục tiêu Tháng")
        st.write("Trưởng bộ phận bóc tách Kế hoạch Năm/Quý thành các mục tiêu cụ thể của Tháng.")
        
        with st.form("form_add_month_goal"):
            col1, col2 = st.columns(2)
            with col1:
                m_year = st.selectbox("Năm ", ["2025", "2026", "2027"])
                m_month = st.selectbox("Tháng", [str(i) for i in range(1, 13)])
                m_dept = st.selectbox("Phòng ban ", get_departments_for_company(selected_company, config))
            with col2:
                m_goal_name = st.text_input("Tên Mục tiêu Tháng (Key Result)")
                m_weight = st.number_input("Tỷ trọng dự kiến của mục tiêu này (%)", min_value=0, max_value=100, value=20)
            submit_month = st.form_submit_button("Lưu Mục tiêu Tháng")
            
            if submit_month:
                if m_goal_name:
                    month_key = f"{m_dept}_{m_year}_{m_month}"
                    if month_key not in bsc_data["months"]:
                        bsc_data["months"][month_key] = []
                    bsc_data["months"][month_key].append({"name": m_goal_name, "weight": m_weight})
                    if save_bsc_config(bsc_data):
                        st.success("Lưu Mục tiêu tháng thành công!")
                        st.rerun()
                    else:
                        st.error("Lỗi khi lưu!")
                else:
                    st.warning("Vui lòng nhập tên Mục tiêu Tháng!")
                    
        st.write("---")
        st.write("### Danh sách Mục tiêu Tháng")
        month_key_sel = f"{m_dept}_{m_year}_{m_month}"
        if month_key_sel in bsc_data["months"] and bsc_data["months"][month_key_sel]:
            import pandas as pd
            df_m = pd.DataFrame(bsc_data["months"][month_key_sel])
            st.dataframe(df_m, use_container_width=True)
        else:
            st.info("Chưa có mục tiêu tháng cho phòng ban này.")
            
    with tab3:
        st.subheader("Giao việc & Tỷ trọng (Từ Mục tiêu)")
        st.write("Trưởng bộ phận chọn Mục tiêu Tháng, và tạo công việc giao cho nhân viên.")
        
        t3_year = st.selectbox("Năm  ", ["2025", "2026", "2027"])
        t3_month = st.selectbox("Tháng ", [str(i) for i in range(1, 13)])
        
        # Use a selectbox so HR or Manager can change the department
        default_t3 = get_departments_for_company(selected_company, config)[0]
        if st.session_state.get('manager_dept') in get_departments_for_company(selected_company, config):
            default_t3 = st.session_state.manager_dept
        t3_dept = st.selectbox("Phòng ban", get_departments_for_company(selected_company, config), index=get_departments_for_company(selected_company, config).index(default_t3) if default_t3 in get_departments_for_company(selected_company, config) else 0)
    
        
        t3_month_key = f"{t3_dept}_{t3_year}_{t3_month}"
        if t3_month_key in bsc_data["months"] and bsc_data["months"][t3_month_key]:
            goals = [g["name"] for g in bsc_data["months"][t3_month_key]]
            selected_goal = st.selectbox("Chọn Mục tiêu Tháng để giao việc:", goals)
            
            with st.form("form_assign_task"):
                st.write(f"**Tạo công việc cho mục tiêu: {selected_goal}**")
                col1, col2 = st.columns(2)
                with col1:
                    task_name = st.text_input("Tên công việc")
                    assignee = st.selectbox("Giao cho nhân viên", get_personnel_for_company_dept(selected_company, t3_dept, config))
                    dl = st.date_input("Hạn chót")
                with col2:
                    kpi_weight = 0
                    project = st.selectbox("Dự án liên quan", [""] + get_filtered_projects(selected_company, config, [], department=global_active_dept))
                
                submit_task = st.form_submit_button("Giao việc lên Hệ thống")
                
                if submit_task:
                    if task_name and assignee:
                        import uuid
                        from datetime import date
                        new_task = {
                            "ID": str(uuid.uuid4())[:8],
                            "DonVi": selected_company,
                            "PhongBan": t3_dept,
                            "NguoiChuTri": assignee,
                            "TenCongViec": task_name,
                            "GiaiTrinhDeXuat": f"[Mục tiêu Tháng {t3_month}: {selected_goal}]",
                            "TyTrongKPI": kpi_weight,
                            "Deadline": dl.strftime("%Y-%m-%d"),
                            "NgayBatDau": date.today().strftime("%Y-%m-%d"),
                            "TrangThai": "Đang thực hiện",
                            "NgayCapNhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "TenDuAn": project,
                            "NguonGiaoViec": "Công việc được giao / định kì",
                            "ChuKyTheoDoi": "Theo dự án / Tự do",
                            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
                            "MucDoGhiNhan": "Chưa đánh giá",
                            "PhanTramHoanThanh": 0
                        }
                        new_id = insert_task(new_task)
                        if new_id:
                            st.success(f"Đã giao việc cho {assignee} thành công!")
                        else:
                            st.error("Lỗi khi lưu công việc!")
                    else:
                        st.warning("Vui lòng nhập tên công việc và chọn người nhận!")
        else:
            st.info("Hãy tạo Mục tiêu Tháng trước khi giao việc!")



