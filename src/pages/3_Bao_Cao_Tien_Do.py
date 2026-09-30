import streamlit as st
import auth

if not auth.check_login():
    st.stop()

st.title("📝 Báo Cáo Tiến Độ")
st.write("Cập nhật trạng thái công việc và đính kèm file kết quả.")

import db_handler

st.subheader("Chọn công việc cần cập nhật")
# Fetch real tasks from DB
tasks = db_handler.get_tasks_by_assignee(user['id'])
if not tasks:
    st.info("Bạn hiện không có công việc nào đang thực hiện.")
    st.stop()

danh_sach_viec = [f"{t['task_name']} (Hạn: {t['deadline']}) - {t['status']}" for t in tasks]
viec_duoc_chon = st.selectbox("Danh sách việc đang đảm nhiệm:", danh_sach_viec)

st.write(f"Đang cập nhật tiến độ cho: **{viec_duoc_chon.split(' (')[0]}**")

with st.expander("✅ Báo cáo Hoàn thành", expanded=True):
    st.file_uploader("Đính kèm file kết quả (Bắt buộc)")
    st.text_area("Ghi chú thêm (Không bắt buộc)")
    st.button("Gửi báo cáo hoàn thành", type="primary")

st.divider()
st.subheader("Báo cáo vướng mắc (Xin gia hạn)")
with st.container(border=True):
    loai_loi = st.radio("Nguyên nhân vướng mắc", ["Do bản thân (Chủ quan)", "Khách quan (Chờ đối tác, lỗi hệ thống...)"])
    st.text_area("Mô tả chi tiết vướng mắc")
    if loai_loi == "Khách quan (Chờ đối tác, lỗi hệ thống...)":
        st.info("Trường hợp vướng mắc khách quan, Quản lý sẽ trực tiếp vào xem xét và chốt % hoàn thành thực tế để tính KPI.")
    st.button("Gửi báo cáo vướng mắc", type="secondary")
