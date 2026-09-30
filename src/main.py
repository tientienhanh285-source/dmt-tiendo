import streamlit as st
import auth

st.set_page_config(
    page_title="Hệ thống KPI - DMT Group",
    page_icon="⚓",
    layout="wide"
)

if not auth.check_login():
    st.stop()

user = st.session_state.user

st.sidebar.title(f"Xin chào, {user['full_name']}")
st.sidebar.write(f"**Phòng ban:** {user['department_name']}")
st.sidebar.write(f"**Vai trò:** {user['role']}")

if st.sidebar.button("Đăng xuất"):
    auth.logout()

st.title("Trạm kiểm soát KPI - DMT Group")
st.success(f"Chào mừng bạn quay lại! Bạn đang đăng nhập với quyền **{user['role']}**.")

# Navigation logic based on role will be added here
if user['role'] == 'Admin' or user['role'] == 'Manager':
    st.header("Master View - Tổng quan")
    st.write("Khu vực dành cho Lãnh đạo & Quản lý")

st.header("Công việc của tôi")
st.write("Khu vực cập nhật tiến độ công việc hàng ngày")
