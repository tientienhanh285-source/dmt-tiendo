import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. required_cols and init
old_cols = '''        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI", "NguonGiaoViec"'''
new_cols = '''        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI", "NguonGiaoViec", "MucDoChamChuoc"'''
content = content.replace(old_cols, new_cols)

old_init = '''    if "NguonGiaoViec" not in df.columns:
        df["NguonGiaoViec"] = "Công việc được giao / định kì"'''
new_init = '''    if "NguonGiaoViec" not in df.columns:
        df["NguonGiaoViec"] = "Công việc được giao / định kì"
    if "MucDoChamChuoc" not in df.columns:
        df["MucDoChamChuoc"] = "0% (Không ghi nhận)"'''
content = content.replace(old_init, new_init)

old_save_init = '''        if 'NguonGiaoViec' not in df_save.columns: df_save['NguonGiaoViec'] = 'Công việc được giao / định kì'
        df_save['NguonGiaoViec'] = df_save['NguonGiaoViec'].fillna('Công việc được giao / định kì')'''
new_save_init = '''        if 'NguonGiaoViec' not in df_save.columns: df_save['NguonGiaoViec'] = 'Công việc được giao / định kì'
        df_save['NguonGiaoViec'] = df_save['NguonGiaoViec'].fillna('Công việc được giao / định kì')
        if 'MucDoChamChuoc' not in df_save.columns: df_save['MucDoChamChuoc'] = '0% (Không ghi nhận)'
        df_save['MucDoChamChuoc'] = df_save['MucDoChamChuoc'].fillna('0% (Không ghi nhận)')'''
content = content.replace(old_save_init, new_save_init)

old_add_dict = '''                        "TyTrongKPI": task_weight,
                        "NguonGiaoViec": task_nguon'''
new_add_dict = '''                        "TyTrongKPI": task_weight,
                        "NguonGiaoViec": task_nguon,
                        "MucDoChamChuoc": "0% (Không ghi nhận)"'''
content = content.replace(old_add_dict, new_add_dict)

# 2. Update UI
old_update_ui = '''                        u_late_cause = st.selectbox(
                            "Phân loại nguyên nhân trễ hạn",
                            ["👤 Do chủ quan", "🌍 Do khách quan"],
                            index=0 if u_current_val == "👤 Do chủ quan" else 1,
                            key=f"u_late_cause_{task_data['ID']}"
                        )'''
new_update_ui = '''                        u_late_cause = st.selectbox(
                            "Phân loại nguyên nhân trễ hạn",
                            ["👤 Do chủ quan", "🌍 Do khách quan"],
                            index=0 if u_current_val == "👤 Do chủ quan" else 1,
                            key=f"u_late_cause_{task_data['ID']}"
                        )
                        if u_late_cause == "🌍 Do khách quan":
                            if st.session_state.is_admin_authenticated:
                                current_chamchuoc = task_data.get('MucDoChamChuoc', '0% (Không ghi nhận)')
                                chamchuoc_opts = ["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"]
                                idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                                u_chamchuoc = st.selectbox("Mức độ ghi nhận (Dành cho Quản lý)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                            else:
                                current_chamchuoc = task_data.get('MucDoChamChuoc', '0% (Không ghi nhận)')
                                u_chamchuoc = current_chamchuoc
                                if current_chamchuoc != '0% (Không ghi nhận)':
                                    st.info(f"Đã được Quản lý ghi nhận mức độ: **{current_chamchuoc}**")
                        else:
                            u_chamchuoc = '0% (Không ghi nhận)'
'''
content = content.replace(old_update_ui, new_update_ui)

old_update_save = '''                        df.loc[df['ID'] == selected_id, 'NguonGiaoViec'] = u_nguon'''
new_update_save = '''                        df.loc[df['ID'] == selected_id, 'NguonGiaoViec'] = u_nguon
                        if u_is_late:
                            df.loc[df['ID'] == selected_id, 'MucDoChamChuoc'] = u_chamchuoc
                        else:
                            df.loc[df['ID'] == selected_id, 'MucDoChamChuoc'] = '0% (Không ghi nhận)'
'''
content = content.replace(old_update_save, new_update_save)

# 3. Monthly KPI Logic
old_kpi_monthly = '''                def calc_score_for_group(grp):
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
                    return 0'''

new_kpi_monthly = '''                def calc_score_for_group(grp):
                    if grp.empty: return 0
                    t_score = 0
                    total_w = 0
                    for idx, row in grp.iterrows():
                        is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        
                        if is_comp:
                            p = 100
                        else:
                            if row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                                cc = row.get('MucDoChamChuoc', '0% (Không ghi nhận)')
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
                        t_score += (p / 100.0) * w
                        total_w += w
                        
                    if total_w > 0:
                        return (t_score / total_w) * 100
                    return 0'''
content = content.replace(old_kpi_monthly, new_kpi_monthly)

# 4. Yearly KPI Logic
old_kpi_yearly = '''                        def calc_score_for_group_y(grp, auto_w):
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
                            return 0'''

new_kpi_yearly = '''                        def calc_score_for_group_y(grp, auto_w):
                            if grp.empty: return 0
                            score = 0
                            total_w = 0
                            for idx, row in grp.iterrows():
                                is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                                w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                                
                                if is_comp:
                                    p = 100
                                else:
                                    if row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                                        cc = row.get('MucDoChamChuoc', '0% (Không ghi nhận)')
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
                            return 0'''
content = content.replace(old_kpi_yearly, new_kpi_yearly)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
