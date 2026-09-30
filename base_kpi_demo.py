import streamlit as st
import pandas as pd
import uuid

# --- Cấu hình trang ---
st.set_page_config(page_title="Base Goal & Wework Demo", layout="wide")
st.title("🎯 Demo Mô Hình KPI Liên Kết Mục Tiêu (Theo chuẩn Base.vn)")

# --- Khởi tạo Dữ liệu Giả lập ---
if 'goals' not in st.session_state:
    st.session_state['goals'] = [
        {"id": "G1", "name": "Giải quyết dứt điểm Pháp lý & GPMB Khu TĐC Phước Lý 2", "owner": "Ban ĐBGT"},
        {"id": "G2", "name": "Đạt chỉ tiêu doanh thu Sàn BĐS năm 2026", "owner": "Sàn DMT Land"}
    ]

if 'key_results' not in st.session_state:
    st.session_state['key_results'] = [
        {"id": "KR1", "goal_id": "G1", "name": "Hoàn thành số lượng hồ sơ GPMB", "target": 38, "current": 15, "unit": "Hồ sơ"},
        {"id": "KR2", "goal_id": "G2", "name": "Doanh thu dự án Nam Bàu Mạc", "target": 350, "current": 100, "unit": "Tỷ VNĐ"},
        {"id": "KR3", "goal_id": "G2", "name": "Doanh thu Căn hộ Khách sạn DMT Group", "target": 100, "current": 10, "unit": "Tỷ VNĐ"}
    ]

if 'tasks' not in st.session_state:
    st.session_state['tasks'] = [
        {"id": str(uuid.uuid4()), "name": "Gọi điện vận động 5 hộ dân chưa nhận tiền đền bù", "kr_id": "KR1", "status": "Đã hoàn thành", "assignee": "Nguyễn Văn A"},
        {"id": str(uuid.uuid4()), "name": "Chạy chiến dịch Facebook Ads cho Nam Bàu Mạc", "kr_id": "KR2", "status": "Đang thực hiện", "assignee": "Trần Thị B"}
    ]

# --- Tabs Giao diện ---
tab1, tab2 = st.tabs(["📊 Tầng 1: Base Goal (Mục tiêu Kế hoạch năm)", "📝 Tầng 2: Base Wework (Công việc thực thi)"])

# --- TAB 1: BASE GOAL ---
with tab1:
    st.header("Danh sách Mục tiêu 2026 (Objectives & Key Results)")
    st.markdown("Ở tầng này, Lãnh đạo không xem các công việc lặt vặt. Lãnh đạo chỉ xem **Tiến độ của các Chỉ số Cốt lõi (Key Results)**.")
    
    for goal in st.session_state['goals']:
        with st.expander(f"📌 {goal['name']} (Phụ trách: {goal['owner']})", expanded=True):
            # Tìm các KR thuộc Goal này
            krs = [kr for kr in st.session_state['key_results'] if kr['goal_id'] == goal['id']]
            
            for kr in krs:
                progress = int((kr['current'] / kr['target']) * 100) if kr['target'] > 0 else 0
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**KR:** {kr['name']}")
                    st.progress(progress / 100.0)
                with col2:
                    st.write(f"**Tiến độ:** {kr['current']} / {kr['target']} {kr['unit']}")
                with col3:
                    st.write(f"**KPI Đạt:** {progress}%")
                
                # Nút cập nhật KR
                new_current = st.number_input(f"Cập nhật kết quả ({kr['unit']})", value=kr['current'], key=f"upd_{kr['id']}")
                if st.button("Lưu KR", key=f"btn_{kr['id']}"):
                    kr['current'] = new_current
                    st.rerun()
            
            st.divider()

# --- TAB 2: BASE WEWORK ---
with tab2:
    st.header("Quản lý Công việc & Gắn kết Mục tiêu (Goal-Task Linkage)")
    st.markdown("Quy tắc: Mỗi khi tạo 1 công việc mới, **BẮT BUỘC phải gắn nó vào 1 Key Result (KR)** của công ty. Nếu công việc không đẩy KR lên, công việc đó không sinh ra KPI.")
    
    # Form Thêm công việc
    with st.container(border=True):
        st.subheader("➕ Thêm công việc mới")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            task_name = st.text_input("Tên công việc")
            assignee = st.text_input("Người thực hiện")
        with col_t2:
            # Dropdown để chọn KR liên kết
            kr_options = {kr['id']: f"{kr['name']} ({next(g['name'] for g in st.session_state['goals'] if g['id'] == kr['goal_id'])})" for kr in st.session_state['key_results']}
            selected_kr = st.selectbox("🔗 Gắn vào Mục tiêu / Key Result", options=list(kr_options.keys()), format_func=lambda x: kr_options[x])
            status = st.selectbox("Trạng thái", ["Đang thực hiện", "Có vướng mắc", "Đã hoàn thành"])
        
        if st.button("Tạo công việc", type="primary"):
            if task_name and assignee:
                st.session_state['tasks'].append({
                    "id": str(uuid.uuid4()),
                    "name": task_name,
                    "kr_id": selected_kr,
                    "status": status,
                    "assignee": assignee
                })
                st.success("Đã tạo và liên kết công việc thành công!")
                st.rerun()

    # Danh sách công việc
    st.subheader("📋 Bảng Công việc (Đã được Link với Mục tiêu)")
    if st.session_state['tasks']:
        df_tasks = pd.DataFrame(st.session_state['tasks'])
        # Map KR name
        df_tasks['Mục tiêu Phục vụ (KR)'] = df_tasks['kr_id'].apply(lambda x: next(kr['name'] for kr in st.session_state['key_results'] if kr['id'] == x))
        df_tasks.rename(columns={"name": "Tên công việc", "status": "Trạng thái", "assignee": "Người thực hiện"}, inplace=True)
        st.dataframe(df_tasks[['Tên công việc', 'Người thực hiện', 'Trạng thái', 'Mục tiêu Phục vụ (KR)']], use_container_width=True)
    else:
        st.info("Chưa có công việc nào.")

st.sidebar.markdown("### Về Demo này")
st.sidebar.info(
    "Mô hình Base chia rạch ròi 2 tầng:\n\n"
    "1. **Tầng Mục tiêu (Base Goal):** Đo lường giá trị thực mang lại (số hồ sơ đền bù, doanh thu).\n"
    "2. **Tầng Công việc (Base Wework):** Quản lý hành động. Hành động phải phục vụ Mục tiêu.\n\n"
    "**KPI của nhân sự = % Hoàn thành của Mục tiêu (Goal)**, chứ không tính bằng số lượng Task hoàn thành."
)
