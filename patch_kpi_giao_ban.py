import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update required_cols
old_cols = '''        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI"'''
new_cols = '''        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI", "NguonGiaoViec"'''
content = content.replace(old_cols, new_cols)

# 2. Add init for NguonGiaoViec
old_init = '''    if "PhanLoaiTreHan" not in df.columns:
        df["PhanLoaiTreHan"] = "🟢 Không trễ hạn / Đúng tiến độ"'''
new_init = '''    if "PhanLoaiTreHan" not in df.columns:
        df["PhanLoaiTreHan"] = "🟢 Không trễ hạn / Đúng tiến độ"
    if "NguonGiaoViec" not in df.columns:
        df["NguonGiaoViec"] = "Công việc được giao / định kì"'''
content = content.replace(old_init, new_init)

# 3. Add to save_db
old_save_init = '''        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')'''
new_save_init = '''        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
        if 'NguonGiaoViec' not in df_save.columns: df_save['NguonGiaoViec'] = 'Công việc được giao / định kì'
        df_save['NguonGiaoViec'] = df_save['NguonGiaoViec'].fillna('Công việc được giao / định kì')'''
content = content.replace(old_save_init, new_save_init)

# 4. Add to UI (Add Task)
old_add_ui = '''            task_name = st.text_input("Tên công việc (tự nhập tự do)", value="")'''
new_add_ui = '''            task_name = st.text_input("Tên công việc (tự nhập tự do)", value="")
            task_nguon = st.selectbox("Nguồn giao việc", ["Công việc được giao / định kì", 'Công việc trong "Giao ban"'])'''
content = content.replace(old_add_ui, new_add_ui)

old_add_dict = '''                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ",
                        "TyTrongKPI": task_weight'''
new_add_dict = '''                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ",
                        "TyTrongKPI": task_weight,
                        "NguonGiaoViec": task_nguon'''
content = content.replace(old_add_dict, new_add_dict)

# 5. Add to UI (Update Task)
old_update_ui = '''                    u_name = st.text_input("Tên công việc", value=task_data['TenCongViec'], key=f"u_name_{task_data['ID']}")'''
new_update_ui = '''                    u_name = st.text_input("Tên công việc", value=task_data['TenCongViec'], key=f"u_name_{task_data['ID']}")
                    u_nguon_opts = ["Công việc được giao / định kì", 'Công việc trong "Giao ban"']
                    current_nguon = task_data.get('NguonGiaoViec', 'Công việc được giao / định kì')
                    u_nguon_idx = u_nguon_opts.index(current_nguon) if current_nguon in u_nguon_opts else 0
                    u_nguon = st.selectbox("Nguồn giao việc", u_nguon_opts, index=u_nguon_idx, key=f"u_nguon_{task_data['ID']}")'''
content = content.replace(old_update_ui, new_update_ui)

old_update_save = '''                        df.loc[df['ID'] == selected_id, 'TyTrongKPI'] = u_weight'''
new_update_save = '''                        df.loc[df['ID'] == selected_id, 'TyTrongKPI'] = u_weight
                        df.loc[df['ID'] == selected_id, 'NguonGiaoViec'] = u_nguon'''
content = content.replace(old_update_save, new_update_save)

# 6. KPI Monthly Logic
old_kpi_monthly = '''                task_score = 0
                for idx, row in group_copy.iterrows():
                    weight = row['TyTrongKPI']
                    if weight <= 0:
                        weight = auto_weight
                    
                    pt_hoan_thanh = row.get('PhanTramHoanThanh', 0)
                    if pd.isna(pt_hoan_thanh): pt_hoan_thanh = 0
                    
                    task_score += (pt_hoan_thanh / 100.0) * weight'''

new_kpi_monthly = '''                # Calculate score dynamically based on NguonGiaoViec (70/30 rule)
                ke_hoach_tasks = group_copy[group_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']
                
                def calc_score_for_group(grp):
                    if grp.empty: return 0
                    t_score = 0
                    for idx, row in grp.iterrows():
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        p = row.get('PhanTramHoanThanh', 0)
                        if pd.isna(p): p = 0
                        t_score += (p / 100.0) * w
                    # Normalize back to 100 max if auto_weight was not used or weights don't sum to 100
                    total_w = grp['TyTrongKPI'].apply(lambda x: x if x > 0 else auto_weight).sum()
                    if total_w > 0:
                        return (t_score / total_w) * 100
                    return 0

                if len(giao_ban_tasks) > 0:
                    kh_score = calc_score_for_group(ke_hoach_tasks)
                    gb_score = calc_score_for_group(giao_ban_tasks)
                    task_score = kh_score * 0.7 + gb_score * 0.3
                else:
                    task_score = calc_score_for_group(ke_hoach_tasks)
'''
content = content.replace(old_kpi_monthly, new_kpi_monthly)

# 7. KPI Yearly Logic
old_kpi_yearly = '''                        t_score = 0
                        for idx, row in m_df_copy.iterrows():
                            w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                            p = row.get('PhanTramHoanThanh', 0)
                            t_score += (p / 100.0) * w'''

new_kpi_yearly = '''                        ke_hoach_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                        giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']
                        
                        def calc_score_for_group_y(grp, auto_w):
                            if grp.empty: return 0
                            score = 0
                            for idx, row in grp.iterrows():
                                w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                                p = row.get('PhanTramHoanThanh', 0)
                                if pd.isna(p): p = 0
                                score += (p / 100.0) * w
                            total_w = grp['TyTrongKPI'].apply(lambda x: x if x > 0 else auto_w).sum()
                            if total_w > 0:
                                return (score / total_w) * 100
                            return 0
                            
                        if len(giao_ban_tasks_y) > 0:
                            kh_score_y = calc_score_for_group_y(ke_hoach_tasks_y, auto_w)
                            gb_score_y = calc_score_for_group_y(giao_ban_tasks_y, auto_w)
                            t_score = kh_score_y * 0.7 + gb_score_y * 0.3
                        else:
                            t_score = calc_score_for_group_y(ke_hoach_tasks_y, auto_w)'''
content = content.replace(old_kpi_yearly, new_kpi_yearly)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
