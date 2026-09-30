import streamlit as st
import auth
import kpi_engine
from datetime import date

if not auth.check_login():
    st.stop()

user = st.session_state.user

st.title("📊 Báo Cáo KPI & Bảng Lương")
st.write("Hệ thống tự động chấm điểm dựa trên nguyên tắc **100 điểm trừ**.")

col1, col2 = st.columns([1, 3])
with col1:
    selected_month = st.selectbox("Chọn tháng", [8, 9, 10, 11, 12], index=1)
    selected_year = st.selectbox("Chọn năm", [2026], index=0)
    
if st.button("Tính điểm KPI tháng này", type="primary"):
    with st.spinner("Đang tổng hợp dữ liệu tiến độ & duyệt việc khách quan..."):
        df_kpi = kpi_engine.calculate_kpi(selected_month, selected_year)
        
        st.success(f"Đã tính xong KPI tháng {selected_month}/{selected_year}!")
        
        # Format the dataframe display
        st.dataframe(
            df_kpi,
            column_config={
                "Tổng Điểm": st.column_config.ProgressColumn(
                    "Tổng Điểm",
                    help="Điểm KPI cuối cùng",
                    format="%f",
                    min_value=0,
                    max_value=120,
                ),
                "Xếp Loại": st.column_config.TextColumn(
                    "Xếp Loại",
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Export logic
        excel_file = kpi_engine.export_kpi_excel(df_kpi, f"BaoCao_KPI_T{selected_month}_{selected_year}.xlsx")
        
        with open(excel_file, "rb") as file:
            st.download_button(
                label="📥 Tải Bảng KPI (Excel)",
                data=file,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.divider()
st.subheader("Cơ chế phân loại")
st.markdown("""
- **A*** (>100 điểm): Hưởng 110 - 120% lương (Vượt trội)
- **A** (92-100 điểm): Hưởng 100% lương
- **B** (82-91 điểm): Hưởng 90% lương
- **C** (72-81 điểm): Hưởng 80% lương
- **D** (<72 điểm): Hưởng 60% lương
""")
