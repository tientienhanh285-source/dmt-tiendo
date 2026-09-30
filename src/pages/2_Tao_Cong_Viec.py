import streamlit as st
import auth
import db_handler

if not auth.check_login():
    st.stop()

user = st.session_state.user

st.title("➕ Tạo Công Việc Mới")
st.write("Tuân thủ Nguyên tắc: Mọi công việc phải thuộc về 1 Chỉ tiêu Kế hoạch năm.")

# Fetch real plans for this user's department
plans = db_handler.get_master_plans_by_dept(user['department_id'])
plan_options = {p['name']: p['id'] for p in plans}

# Form 3 bước
with st.container(border=True):
    st.subheader("Bước 1: Chọn Kế Hoạch / Dự Án")
    if not plans:
        st.error("Phòng ban của bạn chưa có Kế hoạch năm nào. Vui lòng liên hệ HCNS để thêm.")
        st.stop()
        
    project_name = st.selectbox("Dự án của phòng ban", list(plan_options.keys()))
    project_id = plan_options[project_name]
    
    st.subheader("Bước 2: Chọn Chỉ tiêu")
    indicators = db_handler.get_indicators_by_plan(project_id)
    if not indicators:
        st.warning("Dự án này chưa có Chỉ tiêu chi tiết.")
        indicator_options = {}
    else:
        indicator_options = {i['name']: i['id'] for i in indicators}
        
    indicator_name = st.selectbox("Chỉ tiêu tương ứng", list(indicator_options.keys()) if indicator_options else ["Không có dữ liệu"])
    
    st.subheader("Bước 3: Nhập thông tin Công việc")
    task_name = st.text_input("Tên công việc cụ thể")
    deadline = st.date_input("Hạn chót (Deadline)")
    
    if st.button("Tạo công việc", type="primary"):
        if task_name and indicator_options:
            indicator_id = indicator_options[indicator_name]
            db_handler.create_task(task_name, indicator_id, user['id'], deadline)
            st.success("Tạo công việc thành công! Hệ thống đã ghi nhận vào Cơ sở dữ liệu.")
        else:
            st.error("Vui lòng nhập tên công việc và đảm bảo đã chọn Chỉ tiêu hợp lệ!")

st.divider()
st.subheader("🔁 Tái tạo Công việc định kỳ")
st.write("Chọn các công việc định kỳ từ tháng trước mà bạn muốn tiếp tục làm trong tháng này:")

# Danh sách mẫu các công việc định kỳ của tháng trước
viec_thang_truoc = [
    "Chấm công và tính lương tháng (Ban HCNS)",
    "Bảo trì hệ thống Server định kỳ",
    "Lập báo cáo tài chính nội bộ"
]

viec_can_tai_tao = st.multiselect("Các công việc sẽ được tái tạo:", viec_thang_truoc, default=viec_thang_truoc)

if st.button("Tái tạo việc đã chọn"):
    if viec_can_tai_tao:
        st.success(f"Đã tái tạo thành công {len(viec_can_tai_tao)} công việc sang tháng mới!")
    else:
        st.warning("Vui lòng chọn ít nhất 1 công việc để tái tạo.")
