import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Sidebar Role Options
old_roles = 'role_mode = st.sidebar.selectbox("QUYỀN TRUY CẬP", ["Nhân viên", "Quản lý", "Cá nhân (Thử nghiệm)"], index=0)'
new_roles = 'role_mode = st.sidebar.selectbox("QUYỀN TRUY CẬP", ["Nhân viên", "Quản lý", "HR", "Cá nhân (Thử nghiệm)"], index=0)'
content = content.replace(old_roles, new_roles)

# 2. Sidebar Auth Logic
old_auth = """if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False
if "is_personal_authenticated" not in st.session_state:
    st.session_state.is_personal_authenticated = False
if "personal_user" not in st.session_state:
    st.session_state.personal_user = None

if role_mode == "Quản lý":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    if not st.session_state.is_admin_authenticated:
        admin_pwd = st.sidebar.text_input("Nhập Mật khẩu Quản lý", type="password")
        if admin_pwd:
            if admin_pwd == "admindmt123":
                st.session_state.is_admin_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mật khẩu không đúng!")
    
    if st.session_state.is_admin_authenticated:
        st.sidebar.success("Đã xác thực quyền Quản lý!")
        
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_admin_authenticated = False
            st.rerun()

elif role_mode == "Cá nhân (Thử nghiệm)":
    st.session_state.is_admin_authenticated = False
    if not st.session_state.is_personal_authenticated:
        pers_pwd = st.sidebar.text_input("Nhập MÃ PIN cá nhân (Mặc định: 1234)", type="password")
        if pers_pwd:
            if pers_pwd == "1234":
                st.session_state.is_personal_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("MÃ PIN không đúng!")
    
    if st.session_state.is_personal_authenticated:
        st.sidebar.success("Đã xác thực quyền Cá nhân!")
        
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_personal_authenticated = False
            st.session_state.personal_user = None
            st.rerun()
else:
    st.session_state.is_admin_authenticated = False
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None"""

new_auth = """if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False
if "is_manager_authenticated" not in st.session_state:
    st.session_state.is_manager_authenticated = False
if "is_personal_authenticated" not in st.session_state:
    st.session_state.is_personal_authenticated = False
if "personal_user" not in st.session_state:
    st.session_state.personal_user = None

if role_mode == "Quản lý":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_admin_authenticated = False
    if not st.session_state.is_manager_authenticated:
        mgr_pwd = st.sidebar.text_input("Nhập Mật khẩu Quản lý", type="password")
        if mgr_pwd:
            if mgr_pwd == "quanly123":
                st.session_state.is_manager_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mật khẩu không đúng!")
    
    if st.session_state.is_manager_authenticated:
        st.sidebar.success("Đã xác thực quyền Quản lý!")
        
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_manager_authenticated = False
            st.rerun()

elif role_mode == "HR":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_manager_authenticated = False
    if not st.session_state.is_admin_authenticated:
        admin_pwd = st.sidebar.text_input("Nhập Mật khẩu HR", type="password")
        if admin_pwd:
            if admin_pwd == "admindmt123":
                st.session_state.is_admin_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mật khẩu không đúng!")
    
    if st.session_state.is_admin_authenticated:
        st.sidebar.success("Đã xác thực toàn quyền (HR)!")
        
        if st.sidebar.button("Đăng xuất", key="logout_hr"):
            st.session_state.is_admin_authenticated = False
            st.rerun()

elif role_mode == "Cá nhân (Thử nghiệm)":
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    if not st.session_state.is_personal_authenticated:
        pers_pwd = st.sidebar.text_input("Nhập MÃ PIN cá nhân (Mặc định: 1234)", type="password")
        if pers_pwd:
            if pers_pwd == "1234":
                st.session_state.is_personal_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("MÃ PIN không đúng!")
    
    if st.session_state.is_personal_authenticated:
        st.sidebar.success("Đã xác thực quyền Cá nhân!")
        
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_personal_authenticated = False
            st.session_state.personal_user = None
            st.rerun()
else:
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None"""

content = content.replace(old_auth, new_auth)

# 3. Form Update check for Mức độ ghi nhận
old_update_check = """                        if u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            if st.session_state.is_admin_authenticated:
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')"""

new_update_check = """                        if u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            if st.session_state.is_admin_authenticated or st.session_state.get('is_manager_authenticated', False):
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')"""

content = content.replace(old_update_check, new_update_check)

# 4. KPI Tab checks
old_kpi_check1 = """    if role_mode == "Quản lý" and st.session_state.is_admin_authenticated:
        kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📊 Đánh giá theo Tháng", "📈 Tổng kết KPI Cả Năm (Tháng 13)", "💰 Thưởng / Phạt Điểm", "📉 Phân tích & Xuất Báo cáo"])
    else:
        kpi_tab1, kpi_tab2 = st.tabs(["📊 Đánh giá theo Tháng", "📈 Tổng kết KPI Cả Năm (Tháng 13)"])"""

new_kpi_check1 = """    if st.session_state.is_admin_authenticated:
        kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📊 Đánh giá theo Tháng", "📈 Tổng kết KPI Cả Năm (Tháng 13)", "💰 Thưởng / Phạt Điểm", "📉 Phân tích & Xuất Báo cáo"])
    else:
        kpi_tab1, kpi_tab2 = st.tabs(["📊 Đánh giá theo Tháng", "📈 Tổng kết KPI Cả Năm (Tháng 13)"])"""
content = content.replace(old_kpi_check1, new_kpi_check1)

old_kpi_check2 = """    if role_mode == "Quản lý" and st.session_state.is_admin_authenticated:
        with kpi_tab3:"""
new_kpi_check2 = """    if st.session_state.is_admin_authenticated:
        with kpi_tab3:"""
content = content.replace(old_kpi_check2, new_kpi_check2)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
