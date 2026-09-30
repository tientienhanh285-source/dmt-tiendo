import os
import re

filepath = r"views\5_Danh_Gia_KPI.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Tabs
old_tabs = '''if is_hr_view:
    kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)", "⚖️ Thưởng / Phạt Điểm", "📈 Phân tích & Xuất Báo cáo"])
elif is_manager_view:
    kpi_tab1, kpi_tab2, kpi_tab3 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)", "⚖️ Thưởng / Phạt Điểm"])
else:
    kpi_tab1, kpi_tab2 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)"])'''

new_tabs = '''if is_hr_view:
    kpi_tab1, kpi_tab_quy, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📅 Đánh giá theo Tháng", "📊 Tổng kết Quý", "🏅 Tổng kết Năm", "⚖️ Thưởng / Phạt Điểm", "📈 Phân tích & Xuất Báo cáo"])
elif is_manager_view:
    kpi_tab1, kpi_tab_quy, kpi_tab2, kpi_tab3 = st.tabs(["📅 Đánh giá theo Tháng", "📊 Tổng kết Quý", "🏅 Tổng kết Năm", "⚖️ Thưởng / Phạt Điểm"])
else:
    kpi_tab1, kpi_tab_quy, kpi_tab2 = st.tabs(["📅 Đánh giá theo Tháng", "📊 Tổng kết Quý", "🏅 Tổng kết Năm"])'''

content = content.replace(old_tabs, new_tabs)

# 2. Add kpi_tab_quy block before kpi_tab2
# We find "with kpi_tab2:" and insert before it.
quarterly_block = '''
with kpi_tab_quy:
    st.markdown("#### 📊 Báo cáo Tổng kết KPI Quý")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        sel_quy = st.selectbox("Chọn Quý", [1, 2, 3, 4], index=(today.month - 1) // 3)
    with col_q2:
        sel_nam = st.selectbox("Chọn Năm (Quý)", [today.year - 1, today.year, today.year + 1], index=1)
    
    st.write(f"Đang hiển thị tổng hợp tiến độ Quý {sel_quy}/{sel_nam}")
    
    # Months in this quarter
    q_months = [sel_quy * 3 - 2, sel_quy * 3 - 1, sel_quy * 3]
    
    # Filter tasks
    if not display_df.empty:
        df_quy = display_df.copy()
        df_quy['Thang_Deadline'] = df_quy['Deadline'].dt.month
        df_quy['Nam_Deadline'] = df_quy['Deadline'].dt.year
        df_quy = df_quy[(df_quy['Thang_Deadline'].isin(q_months)) & (df_quy['Nam_Deadline'] == sel_nam)]
        
        if df_quy.empty:
            st.info(f"Không có công việc nào trong Quý {sel_quy}/{sel_nam}")
        else:
            quy_summary = []
            for p in all_p:
                p_tasks = df_quy[df_quy['NguoiChuTri'] == p]
                if not p_tasks.empty:
                    total_t = len(p_tasks)
                    done_t = len(p_tasks[p_tasks['PhanTramHoanThanh'] == 100])
                    quy_summary.append({
                        "Nhân sự": p,
                        "Tổng việc": total_t,
                        "Đã hoàn thành": done_t,
                        "Tỷ lệ": f"{done_t/total_t*100:.1f}%"
                    })
            if quy_summary:
                st.dataframe(pd.DataFrame(quy_summary), use_container_width=True)
            
            with st.expander("Chi tiết công việc Quý", expanded=False):
                st.dataframe(df_quy[['ID', 'NguoiChuTri', 'TenCongViec', 'Deadline', 'PhanTramHoanThanh', 'TrangThai']], use_container_width=True)
    else:
        st.info("Chưa có dữ liệu.")
'''
content = content.replace('with kpi_tab2:', quarterly_block + '\nwith kpi_tab2:')

# 3. Update Thưởng/Phạt
content = content.replace(
    'adj_type = st.radio("Phân loại hành vi", ["⭐ Thưởng điểm", "🛑 Phạt điểm"], horizontal=True)',
    'adj_type = st.radio("Phân loại hành vi", ["⭐ Thưởng điểm", "🛑 Phạt điểm", "⭐ Thưởng điểm Quý"], horizontal=True)'
)
content = content.replace(
    'actual_val = adj_val if adj_type == "⭐ Thưởng điểm" else -adj_val',
    'actual_val = adj_val if "Thưởng" in adj_type else -adj_val'
)
content = content.replace(
    'LoaiHanhVi=adj_type, DiemDieuChinh=actual_val',
    'LoaiHanhVi=adj_type, DiemDieuChinh=adj_val'
)

# 4. Update Yearly to have 4 Quarters instead of 12 Months
# The current yearly uses a list of 12 months.
# I will create a more advanced python patch script for this.
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Applied initial patch")
