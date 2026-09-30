import streamlit as st
import auth

if not auth.check_login():
    st.stop()

user = st.session_state.user

if user['role'] != 'Admin':
    st.error("Truy cập bị từ chối. Trang này chỉ dành riêng cho Ban Hành Chính Nhân Sự (Admin).")
    st.stop()

st.title("⚙️ Trạm Quản Trị HCNS")
st.write("Khu vực cấu hình hệ thống, quản lý dữ liệu gốc và điều chỉnh KPI dành riêng cho bộ phận Nhân sự.")

tab1, tab2, tab3 = st.tabs(["1. Quản lý Kế Hoạch Năm", "2. Quản lý Nhân Sự", "3. Phạt/Thưởng Kỷ Luật"])

with tab1:
    st.subheader("Nhập Kế Hoạch / Chỉ Tiêu Năm")
    st.info("HCNS sẽ nhập danh sách các Chỉ tiêu lớn của từng Ban vào đây để làm gốc cho nhân viên tạo việc.")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Chọn Phòng Ban", ["Ban Kế hoạch Đầu tư", "Ban Kỹ thuật", "Ban Tài chính"])
        st.text_input("Tên Chỉ tiêu mới")
    with col2:
        st.number_input("Năm áp dụng", value=2026)
        st.button("Thêm Chỉ Tiêu", type="primary")

with tab2:
    st.subheader("Quản lý Danh sách Nhân viên")
    st.write("Thay vì sửa code như trước, HCNS có thể thêm/xóa nhân viên hoặc đổi Quyền (Manager/Employee) trực tiếp tại đây.")
    st.button("Thêm nhân viên mới")
    
with tab3:
    st.subheader("Cập nhật Điểm Thưởng/Phạt (Ngoài lề)")
    st.write("Dùng để trừ điểm KPI khi vi phạm nội quy công ty (đi trễ, không mặc đồng phục...) hoặc thưởng đột xuất.")
    st.selectbox("Chọn Nhân viên", ["Nguyễn Văn A", "Trần Thị B"])
    st.radio("Loại điều chỉnh", ["Thưởng (+5)", "Phạt (-5)", "Phạt Nặng (-10)"])
    st.text_input("Lý do cụ thể")
    st.button("Cập nhật vào hệ thống")
