import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import auth

if not auth.check_login():
    st.stop()

user = st.session_state.user

if user['role'] not in ['Admin', 'Manager']:
    st.warning("Bạn không có quyền truy cập trang này. Dành riêng cho Quản lý & Lãnh đạo.")
    st.stop()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #1E3A8A; /* Navy blue */
    }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    /* Section Headers */
    h2, h3 {
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Master View - Kế Hoạch Tổng Thể")
st.write(f"Chào sếp **{user['full_name']}**, dưới đây là tiến độ Kế hoạch của **{user['department_name']}**")

# --- MOCK DATA cho Biểu đồ (Sẽ nối DB thật ở bước sau) ---
data_tien_do = pd.DataFrame({
    "Chỉ tiêu": ["Doanh thu Q4", "Hoàn thiện Trạm Bơm", "Hồ sơ Thầu Xây Lắp", "Tuyển dụng Nhân sự", "Triển khai phần mềm KPI"],
    "Tiến độ (%)": [45, 85, 20, 100, 75],
    "Trạng thái": ["Đang làm", "Sắp xong", "Trễ hạn", "Hoàn thành", "Đang làm"]
})

# --- HÀNG 1: THỐNG KÊ TỔNG QUAN (METRICS) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Tổng Chỉ Tiêu", "5")
with col2:
    st.metric("✅ Hoàn thành", "1", "20%")
with col3:
    st.metric("🔥 Trễ hạn / Vướng", "1", "-1", delta_color="inverse")
with col4:
    st.metric("📝 Chờ DVKQ", "3")

st.divider()

# --- HÀNG 2: BIỂU ĐỒ TRỰC QUAN ---
st.subheader("Bức tranh Toàn cảnh Dự án")
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    # Biểu đồ thanh ngang (Gantt-style/Bar)
    fig_bar = px.bar(
        data_tien_do, 
        x="Tiến độ (%)", 
        y="Chỉ tiêu", 
        orientation='h',
        color="Trạng thái",
        color_discrete_map={
            "Hoàn thành": "#10B981", 
            "Đang làm": "#3B82F6", 
            "Sắp xong": "#F59E0B",
            "Trễ hạn": "#EF4444"
        },
        title="Tiến độ hoàn thành từng Chỉ tiêu"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    # Biểu đồ tròn
    status_counts = data_tien_do["Trạng thái"].value_counts().reset_index()
    status_counts.columns = ["Trạng thái", "Số lượng"]
    fig_pie = px.pie(
        status_counts, 
        values='Số lượng', 
        names='Trạng thái',
        hole=0.4,
        color='Trạng thái',
        color_discrete_map={
            "Hoàn thành": "#10B981", 
            "Đang làm": "#3B82F6", 
            "Sắp xong": "#F59E0B",
            "Trễ hạn": "#EF4444"
        }
    )
    fig_pie.update_layout(title_text="Phân bổ Trạng thái")
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# --- HÀNG 3: BÁO CÁO GIAO BAN ---
st.subheader("Báo cáo Giao ban (Bộ lọc thông minh)")
st.write("Dùng công cụ này để trích xuất nhanh các việc cần họp giao ban.")

filter_status = st.multiselect(
    "Lọc theo trạng thái", 
    ["Đang làm", "Sắp xong", "Trễ hạn", "Hoàn thành"],
    default=["Trễ hạn", "Sắp xong"]
)

# Lọc data hiển thị
filtered_df = data_tien_do[data_tien_do["Trạng thái"].isin(filter_status)]
st.dataframe(
    filtered_df,
    column_config={
        "Tiến độ (%)": st.column_config.ProgressColumn(
            "Tiến độ (%)", format="%f", min_value=0, max_value=100
        )
    },
    use_container_width=True,
    hide_index=True
)
