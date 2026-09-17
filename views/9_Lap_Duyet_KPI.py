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

if 'display_df' not in locals():
    try:
        display_df = read_db()
    except:
        pass


# Apply Role-based Filtering globally for the view
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        display_df = display_df[display_df['NguoiChuTri'] == st.session_state.personal_user]
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        display_df = display_df[display_df['PhongBan'] == st.session_state.manager_dept]

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



st.markdown(f"### 📝 Lập & Duyệt Kế Hoạch KPI — {selected_company}")

current_month = today.month
current_year = today.year

plans_df = read_kpi_plans()
tasks_df = read_kpi_tasks()

is_manager = role_mode == "Quản lý" and st.session_state.get('is_manager_authenticated', False)
is_hr = role_mode == "HR" and st.session_state.get('is_admin_authenticated', False)

if role_mode == "Nhân viên":
    cu = st.session_state.get('selected_nhan_vien', '')
elif is_manager:
    cu = st.session_state.get('manager_dept', 'QuanLy') # Simplified for demo
else:
    cu = 'HR'
    
if not cu and role_mode == "Nhân viên":
    st.warning("Vui lòng nhập Tên Nhân viên ở thanh bên trái!")
else:
    tab1, tab2 = st.tabs(["👤 KPI Của Tôi (Nhân viên)", "👔 Duyệt & Chấm điểm (Quản lý)"])
    
    with tab1:
        st.subheader("Kế hoạch KPI của tôi")
        month_sel = st.selectbox("Tháng", list(range(1, 13)), index=current_month-1, key='my_kpi_month')
        
        my_plan = plans_df[(plans_df['User']==cu) & (plans_df['Month']==month_sel) & (plans_df['Year']==current_year)]
        status = my_plan['Status'].iloc[0] if not my_plan.empty else 'draft'
        
        if status == 'draft':
            st.info("✍️ Bạn đang ở chế độ Bản nháp. Điều chỉnh tỷ trọng và bấm Gửi duyệt.")
        elif status == 'pending':
            st.warning("⏳ Kế hoạch đang Chờ duyệt. Không thể chỉnh sửa lúc này.")
        else:
            st.success("✅ Kế hoạch đã được Duyệt. Hãy tập trung thực hiện!")
            
        my_tasks = tasks_df[(tasks_df['User']==cu) & (tasks_df['Month']==month_sel) & (tasks_df['Year']==current_year)]
        tot_w = my_tasks['Weight'].sum() if not my_tasks.empty else 0
        
        st.write(f"**Tổng tỷ trọng hiện tại: {round(tot_w, 2)}%**")
        
        if not my_tasks.empty:
            st.dataframe(my_tasks[['Name', 'BSC', 'Type', 'Weight', 'Target', 'Status', 'Score', 'Note']], use_container_width=True)
            
        if status == 'draft' or status == 'approved':
            with st.expander("+ Thêm Công Việc (Phát sinh)" if status=='approved' else "+ Thêm Công Việc"):
                with st.form("add_task_form"):
                    t_name = st.text_input("Tên công việc")
                    
                    t_bsc = st.selectbox("Mảng BSC", ["Vận hành", "Tài chính", "Khách hàng", "Phát triển"])
                    t_w = st.number_input("Tỷ trọng (%)", min_value=1, max_value=100, value=10)
                    t_type = st.selectbox("Loại", ["Định lượng", "Định tính"])
                    t_tgt = st.text_input("Target")
                    
                    if st.form_submit_button("Thêm việc"):
                        import time
                        new_id = int(time.time())
                        new_row = {"id": new_id, "User": cu, "Month": month_sel, "Year": current_year, "Name": t_name, "BSC": t_bsc, "Type": t_type, "Weight": t_w, "Target": t_tgt, "Status": "pending", "Progress": 0, "Score": None, "Note": ""}
                        tasks_df = pd.concat([tasks_df, pd.DataFrame([new_row])], ignore_index=True)
                        
                        tasks_df = auto_scale_tasks(tasks_df, cu, month_sel, current_year)
                        save_kpi_tasks(tasks_df)
                        
                        if status == 'approved':
                            plans_df.loc[(plans_df['User']==cu) & (plans_df['Month']==month_sel), 'Status'] = 'pending'
                            save_kpi_plans(plans_df)
                            
                        st.success("Đã thêm việc!")
                        st.rerun()
                        
        if status == 'draft':
            if st.button("Gửi Duyệt", type="primary"):
                if abs(tot_w - 100) > 0.1:
                    st.error(f"Tổng tỷ trọng phải bằng 100%. Hiện tại là {round(tot_w, 2)}%.")
                else:
                    if my_plan.empty:
                        new_plan = {"User": cu, "Month": month_sel, "Year": current_year, "Status": "pending"}
                        plans_df = pd.concat([plans_df, pd.DataFrame([new_plan])], ignore_index=True)
                    else:
                        plans_df.loc[(plans_df['User']==cu) & (plans_df['Month']==month_sel), 'Status'] = 'pending'
                    save_kpi_plans(plans_df)
                    st.success("Đã gửi duyệt!")
                    st.rerun()
                    
    with tab2:
        st.subheader("Duyệt & Chấm điểm (Quản lý)")
        if not is_manager and not is_hr:
            st.error("Chỉ Quản lý mới có quyền truy cập.")
        else:
            q_month = st.selectbox("Tháng cần duyệt", list(range(1, 13)), index=current_month-1, key='mgr_kpi_month')
            
            st.markdown("#### Đang chờ duyệt")
            pending_plans = plans_df[(plans_df['Month']==q_month) & (plans_df['Status']=='pending')]
            if pending_plans.empty:
                st.info("Không có kế hoạch chờ duyệt.")
            else:
                for idx, row in pending_plans.iterrows():
                    p_user = row['User']
                    p_tasks = tasks_df[(tasks_df['User']==p_user) & (tasks_df['Month']==q_month)]
                    st.write(f"**{p_user}** - Tổng {round(p_tasks['Weight'].sum(), 2)}%")
                    st.dataframe(p_tasks[['Name', 'BSC', 'Weight']], use_container_width=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Duyệt cho {p_user}", key=f"app_{p_user}"):
                            plans_df.loc[(plans_df['User']==p_user) & (plans_df['Month']==q_month), 'Status'] = 'approved'
                            save_kpi_plans(plans_df)
                            st.rerun()
                    with col2:
                        if st.button(f"Từ chối {p_user}", key=f"rej_{p_user}"):
                            plans_df.loc[(plans_df['User']==p_user) & (plans_df['Month']==q_month), 'Status'] = 'draft'
                            save_kpi_plans(plans_df)
                            st.rerun()
                            
            st.markdown("#### Chấm điểm Kế hoạch đã duyệt")
            approved_plans = plans_df[(plans_df['Month']==q_month) & (plans_df['Status']=='approved')]
            if approved_plans.empty:
                st.info("Chưa có kế hoạch nào được duyệt để chấm điểm.")
            else:
                for idx, row in approved_plans.iterrows():
                    p_user = row['User']
                    p_tasks = tasks_df[(tasks_df['User']==p_user) & (tasks_df['Month']==q_month)]
                    
                    # Compute total score
                    tot_score = sum((t_row['Score'] if pd.notnull(t_row['Score']) else 0) * (t_row['Weight'] / 100) for _, t_row in p_tasks.iterrows())
                    
                    with st.expander(f"{p_user} - Tổng điểm: {round(tot_score, 2)}"):
                        for t_idx, t_row in p_tasks.iterrows():
                            c1, c2 = st.columns([3, 1])
                            c1.write(f"{t_row['Name']} (Tỷ trọng: {round(t_row['Weight'], 2)}%)")
                            new_score = c2.number_input("Điểm (0-100)", min_value=0, max_value=100, value=int(t_row['Score']) if pd.notnull(t_row['Score']) else 0, key=f"score_{t_row['id']}")
                            if new_score != (t_row['Score'] if pd.notnull(t_row['Score']) else 0):
                                tasks_df.loc[tasks_df['id']==t_row['id'], 'Score'] = new_score
                                save_kpi_tasks(tasks_df)


