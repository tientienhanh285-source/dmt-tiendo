import streamlit as st
import auth

if not auth.check_login():
    st.stop()

user = st.session_state.user

if user['role'] not in ['Admin', 'Manager']:
    st.warning("Trang này chỉ dành cho Quản lý & Lãnh đạo.")
    st.stop()

st.title("✅ Duyệt Việc Khách Quan (DVKQ)")
st.write("Tại đây Quản lý chốt phần trăm (%) hoàn thành cho các Task bị vướng mắc do khách quan.")

st.info("Hiện có 2 công việc đang chờ bạn xét duyệt.")

with st.expander("1. Task: Cập nhật hệ thống máy chủ (Nhân viên: Nguyễn Văn Bồn)"):
    st.write("**Lý do vướng mắc:** Đối tác cung cấp phần cứng giao hàng trễ 3 ngày.")
    st.write("**Khối lượng thực tế đã làm:** Đã backup xong dữ liệu, chỉ chờ cắm ổ cứng mới.")
    st.slider("Chốt tỷ lệ hoàn thành (%)", 0, 100, 80)
    st.button("Xác nhận tỷ lệ", key="btn1")

with st.expander("2. Task: Hoàn thiện hồ sơ thầu (Nhân viên: Phan Thị Mỹ Hạnh)"):
    st.write("**Lý do vướng mắc:** Chờ phản hồi từ CĐT.")
    st.write("**Khối lượng thực tế đã làm:** Hồ sơ đã in xong 90%.")
    st.slider("Chốt tỷ lệ hoàn thành (%)", 0, 100, 90)
    st.button("Xác nhận tỷ lệ", key="btn2")
