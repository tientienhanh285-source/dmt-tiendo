import streamlit as st
import auth

if not auth.check_login():
    st.stop()

user = st.session_state.user

if user['role'] not in ['Admin', 'Manager']:
    st.error("Truy cập bị từ chối. Tính năng AI chỉ dành cho Quản lý & HCNS.")
    st.stop()

st.title("🤖 Trợ Lý AI - Rà Soát Mô Tả Công Việc (JD)")
st.write("Sử dụng Trí Tuệ Nhân Tạo (Gemini AI) để so sánh khối lượng công việc thực tế của nhân viên với Bản Mô Tả Công Việc gốc.")

st.info("Tính năng này giúp phát hiện nhân viên đang bị giao sai việc, làm lấn sân chuyên môn hoặc đang quá tải so với chức danh.")

col1, col2 = st.columns(2)
with col1:
    nhan_vien = st.selectbox("Chọn nhân viên cần rà soát", ["Nguyễn Văn Bồn", "Phan Thị Mỹ Hạnh"])
with col2:
    thang = st.selectbox("Tháng rà soát", [8, 9, 10, 11, 12])

st.divider()

col_file1, col_file2 = st.columns(2)
with col_file1:
    st.subheader("1. File Mô Tả Công Việc (JD)")
    st.file_uploader("Tải lên file Word/PDF JD của nhân sự này")

with col_file2:
    st.subheader("2. Dữ liệu công việc thực tế")
    st.write(f"Hệ thống sẽ tự động trích xuất toàn bộ các Task mà **{nhan_vien}** đã làm trong tháng {thang}.")
    st.button("Trích xuất dữ liệu", type="secondary")

if st.button("🚀 Kích hoạt AI Phân Tích", type="primary"):
    with st.spinner("AI đang đọc tài liệu và phân tích sự sai lệch..."):
        # Mocking AI response for demonstration
        import time
        time.sleep(2)
        
        st.success("AI đã phân tích xong!")
        
        st.subheader("Báo Cáo Đánh Giá Từ AI")
        st.markdown(f"""
        **Nhân sự:** {nhan_vien}
        **Độ khớp chuyên môn (JD Match):** 85%
        
        **Nhận xét tự động:**
        - ✅ Đa số công việc (85%) đi đúng hướng với chức danh Kỹ thuật viên/Chuyên viên.
        - ⚠️ **Cảnh báo sai lệch:** Có 2 công việc liên quan đến "Hành chính văn thư" (Đi gửi bưu điện, làm thủ tục đóng dấu) không nằm trong JD Kỹ thuật. Đề nghị Quản lý xem xét lại việc giao task hoặc điều chỉnh lại định biên phòng ban.
        """)
