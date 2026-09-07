import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_auth_block = """
if "is_admin_authenticated" not in st.session_state:
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
    st.session_state.personal_user = None
"""

lines[1451:1500] = [new_auth_block]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done")
