import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



st.markdown(f"### 🏆 Đánh giá KPI & Xếp loại Cá nhân — {selected_company}")

if "success_msg" in st.session_state:
    st.success(st.session_state["success_msg"])
    del st.session_state["success_msg"]

is_hr_view = role_mode == "HR" and st.session_state.get("is_admin_authenticated", False)
is_manager_view = role_mode == "Quản lý" and st.session_state.get('is_manager_authenticated', False)

if is_hr_view:
    kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)", "⚖️ Thưởng / Phạt Điểm", "📈 Phân tích & Xuất Báo cáo"])
elif is_manager_view:
    kpi_tab1, kpi_tab2, kpi_tab3 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)", "⚖️ Thưởng / Phạt Điểm"])
else:
    kpi_tab1, kpi_tab2 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)"])

with kpi_tab1:
    st.markdown("#### Đánh giá và Xếp loại KPI Tháng")
    
    if is_manager_view:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            selected_month = st.selectbox("Chọn Tháng", list(range(1, 13)), index=today.month - 1)
        with col_m2:
            selected_year = st.selectbox("Chọn Năm", [today.year - 1, today.year, today.year + 1], index=1)
        selected_dept_m = st.session_state.manager_dept if st.session_state.get('manager_dept') else "Tất cả phòng ban"
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            selected_month = st.selectbox("Chọn Tháng", list(range(1, 13)), index=today.month - 1)
        with col_m2:
            selected_year = st.selectbox("Chọn Năm", [today.year - 1, today.year, today.year + 1], index=1)
        with col_m3:
            allowed_depts_m = get_departments_for_company(selected_company, config)
            dept_options_m = ["Tất cả phòng ban"] + allowed_depts_m
            selected_dept_m = st.selectbox("Lọc theo Phòng ban", dept_options_m, key="kpi_m_dept")
        
    kpi_df = display_df.copy()
    if 'NguoiChuTri' not in kpi_df.columns:
        kpi_df['NguoiChuTri'] = ''
    
    def is_in_month(d, m, y):
        import pandas as pd
        from datetime import datetime, date
        if pd.isna(d): return False
        if isinstance(d, str):
            try: d = datetime.strptime(d, "%Y-%m-%d").date()
            except: return False
        if isinstance(d, datetime): d = d.date()
        if isinstance(d, date): return d.month == m and d.year == y
        return False
        
    kpi_df = kpi_df[kpi_df['Deadline'].apply(lambda x: is_in_month(x, selected_month, selected_year))] if not kpi_df.empty else kpi_df
    
    adj_df = read_kpi_adjustments()
    adj_df = adj_df[(adj_df['Thang'] == selected_month) & (adj_df['Nam'] == selected_year)]
    
    if kpi_df.empty and adj_df.empty:
        st.info(f"Không có dữ liệu công việc hoặc điểm thưởng/phạt nào trong Tháng {selected_month}/{selected_year}.")
    else:
        import pandas as pd
        from datetime import datetime, date
        personnel_kpi = []
        
        # Find all personnel relevant to THIS company
        company_personnel = set(display_df['NguoiChuTri'].dropna().unique())
        
        all_p = set(kpi_df['NguoiChuTri'].dropna().unique())
        if 'TenNhanVien' in adj_df.columns:
            all_p.update(adj_df['TenNhanVien'].dropna().unique())
        
        # Filter to only keep those who belong to the selected company
        all_p = all_p.intersection(company_personnel)
        
        for person in all_p:
            if not str(person).strip(): continue
            group = kpi_df[kpi_df['NguoiChuTri'] == person]
            total_tasks = len(group)
            done_tasks = len(group[group['TrangThai'] == 'Hoàn thành'])
            
            group_copy = group.copy()
            group_copy['TyTrongKPI'] = pd.to_numeric(group_copy.get('TyTrongKPI', pd.Series(0, index=group_copy.index)), errors='coerce').fillna(0)
            
            for idx, row in group_copy.iterrows():
                is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                is_late = False
                dl = row['Deadline']
                if isinstance(dl, str):
                    try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                    except: pass
                if isinstance(dl, datetime): dl = dl.date()
                if isinstance(dl, date): is_late = (dl < today) and not is_comp
                
                if is_late and row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                    group_copy.at[idx, 'PhanTramHoanThanh'] = 100
                    
            explicit_weight_sum = group_copy[group_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
            unweighted_count = len(group_copy[group_copy['TyTrongKPI'] <= 0])
            remaining_weight = max(0, 100 - explicit_weight_sum)
            auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
            
            # TỔNG ĐIỂM: Tất cả các đầu mục đều chia đều tỷ trọng (100 base)
            
            def calc_score_for_group(grp):
                if grp.empty: return 0
                t_score = 0
                total_w = 0
                for idx, row in grp.iterrows():
                    w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                    
                    if is_local:
                        muc_dat = str(row.get('MucDoGhiNhan', 'Mức 3'))
                        if 'Mức 4' in muc_dat: p = 125
                        elif 'Mức 3' in muc_dat: p = 100
                        elif 'Mức 2' in muc_dat: p = 75
                        elif 'Mức 1' in muc_dat: p = 50
                        elif 'Mức 0' in muc_dat: p = 0
                        elif 'Mức -1' in muc_dat: p = -50
                        elif 'Mức -2' in muc_dat: p = -75
                        elif 'Mức -3' in muc_dat: p = -100
                        else:
                            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                            p = 100 if is_comp else 0
                    else:
                        is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                        p = 100 if is_comp else 0
                        
                        if not is_comp and "khách quan" in str(row.get('PhanLoaiTreHan')).lower():
                            cc = row.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            if cc == "Miễn trừ (Loại bỏ KPI)":
                                w = 0
                                p = 0
                            elif cc == "50%": p = 50
                            elif cc == "80%": p = 80
                            elif cc == "90%": p = 90
                            else: p = 0

                    t_score += (p / 100.0) * w
                    total_w += w
                    
                if total_w > 0:
                    return (t_score / total_w) * 100
                return 0

            task_score = calc_score_for_group(group_copy)

            
            p_adj_df = adj_df[adj_df['TenNhanVien'] == person] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
            adj_score = 0
            if not p_adj_df.empty:
                for _, r in p_adj_df.iterrows():
                    loai = str(r.get('LoaiHanhVi', '')).lower()
                    diem = int(r.get('DiemDieuChinh', 0))
                    if 'thưởng' in loai:
                        adj_score += diem
                    elif 'phạt' in loai:
                        adj_score -= diem
                    else:
                        adj_score += diem
            
            final_score = min(115, max(0, round(task_score + adj_score, 2)))
            
            # Xếp loại mới
            if final_score > 100: grade = "A*"
            elif final_score > 91: grade = "A"
            elif final_score > 81: grade = "B"
            elif final_score > 71: grade = "C"
            else:
                if selected_year == today.year and selected_month == today.month:
                    grade = "-"
                else:
                    grade = "D"
            
            pb = group['PhongBan'].iloc[0] if not group.empty else ""
            
            personnel_kpi.append({
                "Người thực hiện": person,
                "Phòng ban": DEPT_ABBR.get(pb, pb),
                "Số việc": total_tasks,
                "Điểm công việc": round(task_score, 1),
                "Thưởng/Phạt": adj_score,
                "TỔNG ĐIỂM": final_score,
                "Xếp loại": grade
            })
            
        if personnel_kpi:
            kpi_month_df = pd.DataFrame(personnel_kpi)
            if selected_dept_m != "Tất cả phòng ban":
                kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_m, selected_dept_m)]
            st.dataframe(
                kpi_month_df[["Người thực hiện", "Phòng ban", "Số việc", "Điểm công việc", "Thưởng/Phạt", "TỔNG ĐIỂM", "Xếp loại"]],
                column_config={
                    "TỔNG ĐIỂM": st.column_config.ProgressColumn("TỔNG ĐIỂM", format="%f", min_value=0, max_value=100),
                },
                use_container_width=True, hide_index=True
            )
            


            st.markdown("---")
            with st.expander("🔍 Tra cứu chi tiết điểm KPI của từng nhân sự", expanded=False):
                st.info("💡 Tính năng này giúp Quản lý đối chiếu các đầu việc và mức độ hoàn thành của nhân sự để xác minh tính chính xác của điểm số.")
                valid_people = sorted(list(kpi_month_df['Người thực hiện'].unique()))
                if valid_people:
                    det_p = st.selectbox("👤 Chọn nhân sự cần tra cứu", valid_people, key="detail_person_kpi")
                    if det_p:
                        p_info = kpi_month_df[kpi_month_df['Người thực hiện'] == det_p].iloc[0]
                        st.markdown(f"### 🧮 Diễn giải công thức tính điểm của **{det_p}**")
                        task_val = p_info['Điểm công việc']
                        adj_val = p_info['Thưởng/Phạt']
                        final_val = p_info['TỔNG ĐIỂM']
                        
                        st.markdown(f"**📝 Danh sách công việc của {det_p}:**")
                        p_tasks = kpi_df[kpi_df['NguoiChuTri'] == det_p].copy()
                        if p_tasks.empty:
                            st.warning("Không có đầu việc nào được ghi nhận trong tháng.")
                        else:
                            p_tasks['TyTrongKPI'] = pd.to_numeric(p_tasks.get('TyTrongKPI', pd.Series(0, index=p_tasks.index)), errors='coerce').fillna(0)
                            explicit_w = p_tasks[p_tasks['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                            unweighted = len(p_tasks[p_tasks['TyTrongKPI'] <= 0])
                            auto_w = max(0, 100 - explicit_w) / unweighted if unweighted > 0 else 0
                            
                            quy_dois = []
                            w_thuctes = []
                            task_parts = []
                            task_tw = 0.0
                            
                            for idx, row in p_tasks.iterrows():
                                is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                                w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                                if is_comp: 
                                    p = 100
                                    p_tasks.at[idx, 'MucDoGhiNhan'] = "-"
                                elif "khách quan" in str(row.get('PhanLoaiTreHan')).lower():
                                    cc = str(row.get('MucDoGhiNhan', '0%'))
                                    if "Miễn trừ" in cc: w = 0; p = 0
                                    elif "50%" in cc: p = 50
                                    elif "80%" in cc: p = 80
                                    elif "90%" in cc: p = 90
                                    else: p = 0
                                else: 
                                    p = 0
                                    p_tasks.at[idx, 'MucDoGhiNhan'] = "-"
                                
                                quy_dois.append(p)
                                w_round = round(w, 2)
                                w_thuctes.append(w_round)
                                
                                if w_round > 0:
                                    task_parts.append(f"({p} × {w_round}%)")
                                    task_tw += w_round
                                
                            p_tasks['Tỷ trọng (Thực tế) %'] = w_thuctes
                            p_tasks['Điểm quy đổi'] = quy_dois
                            
                            task_math = f"[{' + '.join(task_parts)}] / {round(task_tw,2)}%" if task_parts else "0"
                            
                            st.info(f"**1️⃣ Điểm Công việc ({task_val}):** = {task_math}\n\n"
                                    f"**2️⃣ Điểm Thưởng/Phạt:** {adj_val}\n\n"
                                    f"👉 **TỔNG ĐIỂM ({final_val})** = Điểm Công việc + Thưởng/Phạt = {task_val} + ({adj_val})")

                            p_tasks_disp = p_tasks[['NguonGiaoViec', 'TenDuAn', 'TenCongViec', 'Deadline', 'TrangThai', 'PhanLoaiTreHan', 'MucDoGhiNhan', 'TyTrongKPI', 'Tỷ trọng (Thực tế) %', 'Điểm quy đổi']].copy()
                            p_tasks_disp['Deadline'] = pd.to_datetime(p_tasks_disp['Deadline'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('')
                            st.dataframe(p_tasks_disp, use_container_width=True, hide_index=True)
                            
                        st.markdown(f"**⚖️ Lịch sử Thưởng/Phạt của {det_p}:**")
                        p_adjs = adj_df[adj_df['TenNhanVien'] == det_p][['LoaiHanhVi', 'LyDo', 'DiemDieuChinh']] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
                        if p_adjs.empty:
                            st.success("Không có ghi nhận thưởng/phạt nào.")
                        else:
                            st.dataframe(p_adjs, use_container_width=True, hide_index=True)
        else:
            st.info("Không có dữ liệu cá nhân hợp lệ.")
if 'kpi_tab2' in locals():
    with kpi_tab2:
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
            with st.spinner("Đang tính toán dữ liệu 12 tháng..."):
                import pandas as pd
                from datetime import datetime, date
                all_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                adj_year_df = read_kpi_adjustments()
                adj_year_df = adj_year_df[adj_year_df['Nam'] == selected_year_full]
                if 'TenNhanVien' in adj_year_df.columns:
                    all_personnel.update(adj_year_df['TenNhanVien'].dropna().unique())
            
                # Filter to only keep those who belong to the selected company
                company_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                all_personnel = all_personnel.intersection(company_personnel)
            
                all_personnel = list(all_personnel)
                all_personnel = [p for p in all_personnel if str(p).strip()]
                yearly_data = []
                for person in all_personnel:
                    person_df = display_df[display_df['NguoiChuTri'] == person].copy()
                
                    months_grades = {}
                    count_a_star = 0
                    count_a = 0
                    count_b = 0
                    count_c = 0
                    count_d = 0
                
                    for m in range(1, 13):
                        if selected_year_full > today.year or (selected_year_full == today.year and m > today.month):
                            months_grades[f"Tháng {m}"] = "-"
                            continue
                    
                        def is_in_m(d):
                            if pd.isna(d): return False
                            if isinstance(d, str):
                                try: d = datetime.strptime(d, "%Y-%m-%d").date()
                                except: return False
                            if isinstance(d, datetime): d = d.date()
                            if isinstance(d, date): return d.month == m and d.year == selected_year_full
                            return False
                        
                        m_df = person_df[person_df['Deadline'].apply(is_in_m)] if not person_df.empty else person_df
                        m_adj_df = adj_year_df[(adj_year_df['TenNhanVien'] == person) & (adj_year_df['Thang'] == m)] if 'TenNhanVien' in adj_year_df.columns else pd.DataFrame()
                    
                        if m_df.empty and m_adj_df.empty:
                            months_grades[f"Tháng {m}"] = "-"
                            continue
                        
                        m_df_copy = m_df.copy()
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
                            
                                if is_comp:
                                    p = 100
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
                                    else:
                                        p = 0
                                    
                                if pd.isna(p): p = 0
                                score += (p / 100.0) * w
                                total_w += w
                            
                            if total_w > 0:
                                return (score / total_w) * 100
                            return 0
                        
                        t_score = calc_score_for_group_y(m_df_copy, auto_w)
                    
                        f_score = min(115, max(0, round(t_score + m_adj_df['DiemDieuChinh'].sum(), 2)))
                    
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
                            if selected_year_full == today.year and m == today.month:
                                grade = "-"
                            else:
                                grade = "D"
                                count_d += 1
                        
                        months_grades[f"Tháng {m}"] = grade
                    
                    if is_local:
                        # Logic xếp loại năm Cảng Đà Nẵng
                        evaluated = count_a_star + count_a + count_b + count_c + count_d
                        if evaluated == 0:
                            final_grade = "-"
                            bonus_val = 0
                        elif evaluated < 12 and selected_year_full >= today.year:
                            final_grade = "Đang tích lũy"
                            bonus_val = 0
                        else:
                            # Tính điểm trung bình cả năm để xếp loại Cảng Đà Nẵng
                            t_score = f_score # Lấy điểm tháng gần nhất hoặc trung bình
                            if f_score >= 90:
                                final_grade = "A"
                                bonus_val = 110
                            elif f_score >= 80:
                                final_grade = "B"
                                bonus_val = 105
                            elif f_score >= 70:
                                final_grade = "C"
                                bonus_val = 100
                            elif f_score >= 50:
                                final_grade = "D"
                                bonus_val = 95
                            else:
                                final_grade = "E"
                                bonus_val = 90
                            
                            bonus = f"{bonus_val}%"
                    else:
                        # Logic xếp loại năm cũ
                        if count_a_star >= 8 and count_b == 0 and count_c == 0 and count_d == 0:
                            final_grade = "A+"
                            bonus_val = 120
                        elif (count_a_star + count_a) >= 8 and count_c == 0 and count_d == 0:
                            final_grade = "A"
                            bonus_val = 110
                        elif (count_a_star + count_a + count_b) >= 8 and count_d == 0:
                            final_grade = "B"
                            bonus_val = 105
                        elif (count_a_star + count_a + count_b + count_c) >= 8 and count_d <= 2:
                            final_grade = "C"
                            bonus_val = 100
                        else:
                            final_grade = "D"
                            bonus_val = 90
                        
                        evaluated = count_a_star + count_a + count_b + count_c + count_d
                        if evaluated == 0:
                            final_grade = "-"
                            bonus = "-"
                        elif evaluated < 12 and selected_year_full >= today.year:
                            final_grade = "Đang tích lũy"
                            bonus = "-"
                        else:
                            bonus = f"{bonus_val}%"
                        actual_bonus = f"{int(bonus_val * k_factor)}%"
                        
                    row_data = {
                        "Người thực hiện": person,
                        "Phòng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else ""
                    }
                    row_data.update(months_grades)
                    row_data["Xếp loại Năm"] = final_grade
                    row_data["Mức hưởng T13 (Gốc)"] = bonus
                    row_data["Thực nhận (Sau K)"] = actual_bonus
                    yearly_data.append(row_data)
                
                if yearly_data:
                    yearly_df = pd.DataFrame(yearly_data)
                    if selected_dept_y != "Tất cả phòng ban":
                        yearly_df = yearly_df[yearly_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]
                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                
                    excel_data = kpi_reports.generate_yearly_excel(yearly_df, selected_year_full)
                    st.download_button("📥 Xuất Báo cáo Excel", data=excel_data, file_name=f"TongKet_KPI_{selected_year_full}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.info("Không có dữ liệu.")

is_hr = role_mode == "HR" and st.session_state.get("is_admin_authenticated", False)
is_manager = role_mode == "Quản lý" and st.session_state.get("is_manager_authenticated", False)

if is_hr or is_manager:
    with kpi_tab3:
        st.markdown("#### ⚖️ Điều chỉnh Điểm Thưởng / Phạt")
        all_p_list = []
        
        if is_manager and st.session_state.get('manager_dept'):
            dept = st.session_state.manager_dept
            if selected_company == "Tất cả đơn vị":
                for comp, comp_data in config.get("companies", {}).items():
                    all_p_list.extend(comp_data.get("personnel_by_department", {}).get(dept, []))
                all_p_list.extend(config.get("personnel_by_department", {}).get(dept, []))
            else:
                all_p_list.extend(get_personnel_for_company_dept(selected_company, dept, config))
        else:
            if selected_company == "Tất cả đơn vị":
                for comp, comp_data in config.get("companies", {}).items():
                    for dept, persons in comp_data.get("personnel_by_department", {}).items():
                        all_p_list.extend(persons)
                for dept, persons in config.get("personnel_by_department", {}).items():
                    all_p_list.extend(persons)
            else:
                valid_depts = get_departments_for_company(selected_company, config)
                for dept in valid_depts:
                    persons = get_personnel_for_company_dept(selected_company, dept, config)
                    all_p_list.extend(persons)
                    
                    
        all_p_list = sorted(list(set(all_p_list)))
        if not all_p_list:
            all_p_list = ["(Chưa có nhân sự)"]
            
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            adj_person = st.selectbox("Tên nhân viên", all_p_list)
            adj_month = st.selectbox("Tháng áp dụng", list(range(1, 13)), index=today.month - 1)
            adj_year = st.selectbox("Năm áp dụng", [today.year - 1, today.year, today.year + 1], index=1)
        
        with col_f2:
            template_opts = ["Đi trễ, về sớm", "Quên chấm công", "Lý do khác"] if is_hr else ["Lý do khác"]
            adj_template = st.selectbox("Lý do mẫu", template_opts)
            
            if adj_template == "Đi trễ, về sớm":
                so_lan = st.number_input("Tổng số lần trong tháng", min_value=1, value=1)
                sugg_val = max(0, so_lan - 5) * 2
                
                st.info(f"ℹ️ Bạn đang nhập tổng cộng {so_lan} lần vi phạm trong tháng {adj_month}.")
                if so_lan >= 6:
                    st.warning(f"⚠️ Từ lần 6 trở đi: Đề xuất trừ tổng cộng {sugg_val} điểm.")
                else:
                    st.success("✅ Dưới 6 lần: Chưa bị trừ điểm.")
                    
                adj_type = "🛑 Phạt điểm"
                adj_val = st.number_input("Tổng số điểm trừ", min_value=0, max_value=100, value=sugg_val)
                adj_reason = st.text_input("Ghi chú thêm (Tùy chọn)")
                
            elif adj_template == "Quên chấm công":
                so_lan = st.number_input("Tổng số lần trong tháng", min_value=1, value=1)
                sugg_val = max(0, so_lan - 2) * 1
                
                st.info(f"ℹ️ Bạn đang nhập tổng cộng {so_lan} lần vi phạm trong tháng {adj_month}.")
                if so_lan >= 3:
                    st.warning(f"⚠️ Từ lần 3 trở đi: Đề xuất trừ tổng cộng {sugg_val} điểm.")
                else:
                    st.success("✅ Dưới 3 lần: Chưa bị trừ điểm.")
                    
                adj_type = "🛑 Phạt điểm"
                adj_val = st.number_input("Tổng số điểm trừ", min_value=0, max_value=100, value=sugg_val)
                adj_reason = st.text_input("Ghi chú thêm (Tùy chọn)")
                
            else:
                adj_type = st.radio("Phân loại hành vi", ["⭐ Thưởng điểm", "🛑 Phạt điểm"], horizontal=True)
                adj_val = st.number_input("Số điểm", min_value=0, max_value=15, value=5)
                adj_reason = st.text_area("Lý do chi tiết (Bắt buộc)")
                
        if st.button("Lưu Điểm Điều Chỉnh", type="primary"):
            if adj_template == "Lý do khác" and not adj_reason.strip():
                st.error("⚠️ Vui lòng nhập lý do chi tiết!")
            else:
                actual_val = adj_val if adj_type == "⭐ Thưởng điểm" else -adj_val
                if adj_template != "Lý do khác":
                    final_reason = f"[{adj_template}] ({so_lan} lần) {adj_reason.strip()}".strip()
                else:
                    final_reason = adj_reason.strip()
                add_kpi_adjustment(adj_person, adj_month, adj_year, adj_type, actual_val, final_reason)
                st.session_state["success_msg"] = "🎉 Đã lưu điều chỉnh điểm thành công!"
                st.rerun()

    if 'kpi_tab4' in locals():
        with kpi_tab4:
            st.markdown("### Tùy chọn Xuất Báo Cáo & Phân tích")
            col_x1, col_x2 = st.columns(2)
        
            with col_x1:
                st.markdown("#### 1. Báo Cáo Phòng Ban (Excel)")
                if st.button("Tải Báo cáo Phòng Ban"):
                    data_rows = []
                    for i, person in enumerate(all_p_list):
                        data_rows.append({
                            'HoTen': person, 'ChucVu': 'Nhân viên',
                            'SoLanTre': 0, 'SoLanSom': 0, 'SoLanKhongCC': 0,
                            'DiemTruTre': 0, 'DiemTruSom': 0, 'DiemTruKhongCC': 0,
                            'TongTru': 0, 'DiemConLai': 100, 'XepLoai': 'A', 'GhiChu': ''
                        })
                    excel_data = kpi_reports.generate_department_excel(selected_company, selected_month, selected_year, data_rows)
                    st.download_button("📥 Tải Báo Cáo Excel", data=excel_data, file_name=f"KPI_Thang_{selected_month}_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
            with col_x2:
                st.markdown("#### 2. Phiếu KPI Cá Nhân (Word)")
                st.info(f"Đang xuất dữ liệu của: **Tháng {selected_month}/{selected_year}** (Để xuất tháng khác, vui lòng quay lại tab 'Đánh giá theo Tháng' để chọn).")
                emp_to_export = st.selectbox("Chọn nhân viên", all_p_list, key='emp_export')
                if st.button("Tạo Phiếu Đánh Giá"):
                    # Collect real tasks and penalties
                    emp_tasks = []
                    kpi_score = 100
                    if personnel_kpi:
                        for p in personnel_kpi:
                            if p['Người thực hiện'] == emp_to_export:
                                kpi_score = p['Điểm công việc']
                                break
                
                    e_kpi_df = kpi_df[kpi_df['NguoiChuTri'] == emp_to_export].copy()
                    e_kpi_df['TyTrongKPI'] = pd.to_numeric(e_kpi_df['TyTrongKPI'], errors='coerce').fillna(0)
                    e_kpi_df['PhanTramHoanThanh'] = pd.to_numeric(e_kpi_df['PhanTramHoanThanh'], errors='coerce').fillna(0)
                    # Calc weights again if needed, or just display raw tasks
                    explicit_weight_sum = e_kpi_df[e_kpi_df['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                    unweighted_count = len(e_kpi_df[e_kpi_df['TyTrongKPI'] <= 0])
                    remaining_weight = max(0, 100 - explicit_weight_sum)
                    auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
                
                    for idx, row in e_kpi_df.iterrows():
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        pt = row.get('PhanTramHoanThanh', 0)
                        if pd.isna(pt): pt = 0
                    
                        diem_tru = w - (pt / 100.0 * w)
                        emp_tasks.append({
                            'TenCV': row['TenCongViec'],
                            'TgianYC': str(row['Deadline']),
                            'KetQua': f"{pt}% (Tỷ trọng: {w:.1f}%)",
                            'DiemTru': round(diem_tru, 1)
                        })
                    
                    e_adj_df = adj_df[adj_df['TenNhanVien'] == emp_to_export] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
                    penalties = e_adj_df.to_dict('records')
                
                    def _get_pb(name):
                        # Try to find from current company's departments
                        depts = get_departments_for_company(selected_company, config)
                        if depts:
                            for d in depts:
                                p_list = get_personnel_for_company_dept(selected_company, d, config)
                                if name in p_list: return d
                        # Fallback to global config
                        for d, p_list in config.get("personnel_by_department", {}).items():
                            if name in p_list: return d
                        return "Khác"

                    emp_pb = _get_pb(emp_to_export)
                    word_data = kpi_reports.generate_individual_docx(emp_to_export, selected_month, selected_year, kpi_score, emp_tasks, penalties, "Nhân viên", emp_pb)
                    st.download_button("📥 Tải Phiếu Cá Nhân (Word)", data=word_data, file_name=f"Phieu_KPI_{emp_to_export}_Thang_{selected_month}_{selected_year}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                
            st.divider()
            st.info("Để xem Biểu đồ Phân tích, vui lòng qua tab 'Tổng kết KPI Cả Năm' và bấm 'Chạy / Cập nhật' trước.")

                    
    with kpi_tab3:
        st.divider()
        st.markdown("##### Lịch sử Thưởng / Phạt")
        hist_df = read_kpi_adjustments()
        if not hist_df.empty:
            # Filter out personnel not belonging to the current company
            hist_df = hist_df[hist_df["TenNhanVien"].isin(all_p_list)]
            
            if hist_df.empty:
                st.info("Chưa có lịch sử điều chỉnh cho đơn vị này.")
            else:
                def _get_pb(name):
                    # Try to find from current company's departments
                    if selected_company != "Tất cả đơn vị":
                        depts = get_departments_for_company(selected_company, config)
                        for d in depts:
                            p_list = get_personnel_for_company_dept(selected_company, d, config)
                            if name in p_list: return d
                    # Fallback to global config
                    for d, p_list in config.get("personnel_by_department", {}).items():
                        if name in p_list: return d
                    return "Khác"
                    
                hist_df["Phòng ban"] = hist_df["TenNhanVien"].apply(_get_pb)
                
                # Reorder columns to put Phòng ban next to TenNhanVien
                cols = list(hist_df.columns)
                if "Phòng ban" in cols:
                    cols.insert(cols.index("TenNhanVien") + 1, cols.pop(cols.index("Phòng ban")))
                    hist_df = hist_df[cols]
                
                # Lọc (Filter)
                if is_manager:
                    f_pb = "Tất cả"
                    f_thang = st.selectbox("Lọc Tháng", ["Tất cả"] + sorted(list(set(hist_df["Thang"])), reverse=True), key="flt_adj_thang")
                else:
                    col_flt1, col_flt2 = st.columns(2)
                    with col_flt1:
                        f_pb = st.selectbox("Lọc Phòng Ban", ["Tất cả"] + sorted(list(set(hist_df["Phòng ban"]))), key="flt_adj_pb")
                    with col_flt2:
                        f_thang = st.selectbox("Lọc Tháng", ["Tất cả"] + sorted(list(set(hist_df["Thang"])), reverse=True), key="flt_adj_thang")
                
                hist_display_df = hist_df.copy()
                if f_pb != "Tất cả":
                    hist_display_df = hist_display_df[hist_display_df["Phòng ban"] == f_pb]
                if f_thang != "Tất cả":
                    hist_display_df = hist_display_df[hist_display_df["Thang"] == f_thang]
                
                hist_display_df = hist_display_df.sort_values(by=["Phòng ban", "Thang", "ID"], ascending=[True, False, False])
                
                cols_to_drop = ["ID", "NguoiCapNhat", "ThoiGianCapNhat"]
                display_cols = [c for c in hist_display_df.columns if c not in cols_to_drop]
                
                st.dataframe(hist_display_df[display_cols], use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("##### 🗑️ Xóa Điều Chỉnh KPI")
                if is_hr:
                    st.info("Nhập số ID tương ứng trong bảng trên để xóa dữ liệu.")
                    col_del1, col_del2 = st.columns([1, 3])
                    with col_del1:
                        del_id = st.number_input("Nhập ID cần xóa", min_value=1, value=1)
                    with col_del2:
                        st.write("") # Spacer
                        st.write("")
                        if st.button("❌ Xóa dòng này", type="primary"):
                            success, msg = delete_kpi_adjustment(del_id)
                            if success:
                                st.success(f"Đã xóa thành công điều chỉnh có ID: {del_id}")
                                st.rerun()
                            else:
                                st.error(msg)
                else:
                    st.info("⚠️ Vui lòng liên hệ bộ phận HR nếu bạn nhập sai và cần xóa hoặc sửa điểm.")

        else:
            st.info("Chưa có lịch sử điều chỉnh.")

# ----------------- 6. QUẢN LÝ CẤU HÌNH -----------------# ----------------- 6. QUẢN LÝ CẤU HÌNH -----------------
