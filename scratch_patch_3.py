import shutil

# Restore from backup
shutil.copy(r'scratch_5.py', r'views\5_Danh_Gia_KPI.py')

with open(r"views\5_Danh_Gia_KPI.py", "r", encoding="utf-8") as f:
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

# 2. Update Thưởng/Phạt
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

# 3. Insert kpi_tab_quy and replace kpi_tab2
quarterly_block = '''    with kpi_tab_quy:
        st.markdown("#### 📊 Báo cáo Tổng kết KPI Quý")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            sel_quy = st.selectbox("Chọn Quý", [1, 2, 3, 4], index=(today.month - 1) // 3)
        with col_q2:
            sel_nam = st.selectbox("Chọn Năm (Quý)", [today.year - 1, today.year, today.year + 1], index=1)
        
        st.write(f"Đang hiển thị tổng hợp tiến độ Quý {sel_quy}/{sel_nam}")
        q_months = [sel_quy * 3 - 2, sel_quy * 3 - 1, sel_quy * 3]
        
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

new_yearly = '''    with kpi_tab2:
        st.markdown("#### Tổng kết KPI Cả Năm & Xếp loại thưởng Tháng 13")
        
        k_factor = 1.0
        
        if is_manager_view:
            selected_year_full = st.selectbox("Chọn Năm Tổng Kết", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
            selected_dept_y = st.session_state.manager_dept if st.session_state.get('manager_dept') else "Tất cả phòng ban"
        else:
            col_y1, col_y2 = st.columns(2)
            with col_y1:
                selected_year_full = st.selectbox("Chọn Năm Tổng Kết", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
            with col_y2:
                allowed_depts_y = get_departments_for_company(selected_company, config)
                dept_options_y = ["Tất cả phòng ban"] + allowed_depts_y
                selected_dept_y = st.selectbox("Lọc theo Phòng ban", dept_options_y, key="kpi_y_dept")
    
        if st.button("🔄 Chạy / Cập nhật Báo cáo Tổng kết Năm", type="primary"):
            with st.spinner("Đang tính toán dữ liệu 4 Quý..."):
                import pandas as pd
                from datetime import datetime, date
                all_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                adj_year_df = read_kpi_adjustments()
                adj_year_df = adj_year_df[adj_year_df['Nam'] == selected_year_full]
                if 'TenNhanVien' in adj_year_df.columns:
                    all_personnel.update(adj_year_df['TenNhanVien'].dropna().unique())
            
                company_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                all_personnel = all_personnel.intersection(company_personnel)
            
                all_personnel = list(all_personnel)
                all_personnel = [p for p in all_personnel if str(p).strip()]
                yearly_data = []
                for person in all_personnel:
                    person_df = display_df[display_df['NguoiChuTri'] == person].copy()
                
                    quarters_grades = {}
                    count_a_star = 0
                    count_a = 0
                    count_b = 0
                    count_c = 0
                    count_d = 0
                
                    for q in range(1, 5):
                        q_months = [q*3-2, q*3-1, q*3]
                        if selected_year_full > today.year or (selected_year_full == today.year and q_months[0] > today.month):
                            quarters_grades[f"Quý {q}"] = "-"
                            continue
                    
                        def is_in_q(d):
                            if pd.isna(d): return False
                            if isinstance(d, str):
                                try: d = datetime.strptime(d, "%Y-%m-%d").date()
                                except: return False
                            if isinstance(d, datetime): d = d.date()
                            if isinstance(d, date): return d.month in q_months and d.year == selected_year_full
                            return False
                        
                        q_df = person_df[person_df['Deadline'].apply(is_in_q)] if not person_df.empty else person_df
                        q_adj_df = adj_year_df[(adj_year_df['TenNhanVien'] == person) & (adj_year_df['Thang'] == q) & (adj_year_df['LoaiDieuChinh'].str.contains("Quý", na=False))] if not adj_year_df.empty else pd.DataFrame()
                    
                        if q_df.empty and q_adj_df.empty:
                            quarters_grades[f"Quý {q}"] = "-"
                            continue
                        
                        m_df_copy = q_df.copy()
                        m_df_copy['TyTrongKPI'] = pd.to_numeric(m_df_copy.get('TyTrongKPI', pd.Series(0, index=m_df_copy.index)), errors='coerce').fillna(0)
                    
                        for idx, row in m_df_copy.iterrows():
                            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                            is_late = False
                            dl = row['Deadline']
                            if isinstance(dl, str):
                                try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                                except: pass
                            if isinstance(dl, datetime): dl = dl.date()
                            if isinstance(dl, date): is_late = (dl < today) and not is_comp
                            if is_late and row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                                m_df_copy.at[idx, 'PhanTramHoanThanh'] = 100
                            
                        explicit_weight = m_df_copy[m_df_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                        uw_count = len(m_df_copy[m_df_copy['TyTrongKPI'] <= 0])
                        auto_w = max(0, 100 - explicit_weight) / uw_count if uw_count > 0 else 0
                    
                        def calc_score_for_group_y(grp, auto_w):
                            if grp.empty: return 0
                            score = 0
                            total_w = 0
                            for idx, row in grp.iterrows():
                                is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                                w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                            
                                if is_comp: p = 100
                                else:
                                    if "khách quan" in str(row.get('PhanLoaiTreHan')).lower():
                                        cc = row.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                                        if cc == "Miễn trừ (Loại bỏ KPI)":
                                            w = 0
                                            p = 0
                                        elif cc == "50%": p = 50
                                        elif cc == "80%": p = 80
                                        elif cc == "90%": p = 90
                                        else: p = 0
                                    else: p = 0
                                    
                                if pd.isna(p): p = 0
                                score += (p / 100.0) * w
                                total_w += w
                            
                            if total_w > 0: return (score / total_w) * 100
                            return 0
                        
                        t_score = calc_score_for_group_y(m_df_copy, auto_w)
                        f_score = min(115, max(0, round(t_score + (q_adj_df['DiemDieuChinh'].sum() if not q_adj_df.empty else 0), 2)))
                    
                        if f_score > 100:
                            grade = "A*"
                            count_a_star += 1
                        elif f_score > 91: 
                            grade = "A"
                            count_a += 1
                        elif f_score > 81: 
                            grade = "B"
                            count_b += 1
                        elif f_score > 71:
                            grade = "C"
                            count_c += 1
                        else:
                            if selected_year_full == today.year and q_months[0] > today.month:
                                grade = "-"
                            else:
                                grade = "D"
                                count_d += 1
                        
                        quarters_grades[f"Quý {q}"] = grade
                    
                    if count_a_star >= 3 and count_b == 0 and count_c == 0 and count_d == 0:
                        final_grade = "A*"
                        bonus_val = 120
                    elif (count_a_star + count_a) >= 3 and count_c == 0 and count_d == 0:
                        final_grade = "A"
                        bonus_val = 110
                    elif (count_a_star + count_a + count_b) >= 3 and count_d == 0:
                        final_grade = "B"
                        bonus_val = 105
                    elif (count_a_star + count_a + count_b + count_c) >= 3 and count_d <= 1:
                        final_grade = "C"
                        bonus_val = 100
                    else:
                        final_grade = "D"
                        bonus_val = 90
                    
                    evaluated = count_a_star + count_a + count_b + count_c + count_d
                    if evaluated == 0:
                        final_grade = "-"
                        bonus = "-"
                    elif evaluated < 4 and selected_year_full >= today.year:
                        final_grade = "Đang tích lũy"
                        bonus = "-"
                    else:
                        bonus = f"{bonus_val}%"
                    actual_bonus = f"{int(bonus_val * k_factor)}%" if bonus != "-" else "-"
                        
                    row_data = {
                        "Người thực hiện": person,
                        "Phòng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else ""
                    }
                    row_data.update(quarters_grades)
                    row_data["Xếp loại Năm"] = final_grade
                    row_data["Thực nhận (Sau K)"] = actual_bonus
                    yearly_data.append(row_data)
                
                if yearly_data:
                    yearly_df = pd.DataFrame(yearly_data)
                    if selected_dept_y != "Tất cả phòng ban":
                        yearly_df = yearly_df[yearly_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]
                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Không có dữ liệu.")
'''

start_idx = content.find("if 'kpi_tab2' in locals():")
end_idx = content.find("    with kpi_tab3:", start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + "if 'kpi_tab2' in locals():\n" + quarterly_block + new_yearly + '\n' + content[end_idx:]
    with open(r"views\5_Danh_Gia_KPI.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced correctly!")
else:
    print("Failed to find boundaries.")
