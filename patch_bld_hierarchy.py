import os
import glob

bld_mapping_code = """        if st.session_state.manager_dept == "BLĐ":
            manager_user = st.session_state.get('manager_user', '')
            bld_hierarchy = {
                "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]
            }
            if manager_user in bld_hierarchy:
                all_truong_ban = bld_hierarchy[manager_user]
            else:
                all_truong_ban = []
                for leads in DEPT_LEADS.get(selected_company, {}).values():
                    all_truong_ban.extend(leads)
            db_filters['NguoiChuTri'] = list(set(all_truong_ban))"""

old_block = """        if st.session_state.manager_dept == "BLĐ":
            all_truong_ban = []
            for leads in DEPT_LEADS.get(selected_company, {}).values():
                all_truong_ban.extend(leads)
            db_filters['NguoiChuTri'] = list(set(all_truong_ban))"""

bld_mapping_local_1 = """                if manager_dept == "BLĐ":
                    manager_user = st.session_state.get('manager_user', '')
                    bld_hierarchy = {
                        "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                        "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                        "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]
                    }
                    if manager_user in bld_hierarchy:
                        all_truong_ban = bld_hierarchy[manager_user]
                    else:
                        all_truong_ban = []
                        for leads in DEPT_LEADS.get(selected_company, {}).values():
                            all_truong_ban.extend(leads)
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(all_truong_ban)]"""

old_local_1 = """                if manager_dept == "BLĐ":
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(all_truong_ban)]"""

bld_mapping_local_2 = """            if role_mode == "Quản lý" and st.session_state.get("manager_dept") == "BLĐ":
                manager_user = st.session_state.get('manager_user', '')
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]
                }
                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                mask = mask & local_df['NguoiChuTri'].isin(all_truong_ban)"""

old_local_2 = """            if role_mode == "Quản lý" and st.session_state.get("manager_dept") == "BLĐ":
                all_truong_ban = []
                for leads in DEPT_LEADS.get(selected_company, {}).values():
                    all_truong_ban.extend(leads)
                mask = mask & local_df['NguoiChuTri'].isin(all_truong_ban)"""

bld_mapping_local_3 = """            if selected_dept_m == "BLĐ":
                manager_user = st.session_state.get('manager_user', '')
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]
                }
                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                kpi_month_df = kpi_month_df[kpi_month_df["Người thực hiện"].isin(all_truong_ban)]"""

old_local_3 = """            if selected_dept_m == "BLĐ":
                all_truong_ban = []
                for leads in DEPT_LEADS.get(selected_company, {}).values():
                    all_truong_ban.extend(leads)
                kpi_month_df = kpi_month_df[kpi_month_df["Người thực hiện"].isin(all_truong_ban)]"""

bld_mapping_local_4 = """                    if selected_dept_y == "BLĐ":
                        manager_user = st.session_state.get('manager_user', '')
                        bld_hierarchy = {
                            "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                            "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                            "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]
                        }
                        if manager_user in bld_hierarchy:
                            all_truong_ban = bld_hierarchy[manager_user]
                        else:
                            all_truong_ban = []
                            for leads in DEPT_LEADS.get(selected_company, {}).values():
                                all_truong_ban.extend(leads)
                        yearly_df = yearly_df[yearly_df["Người thực hiện"].isin(all_truong_ban)]"""

old_local_4 = """                    if selected_dept_y == "BLĐ":
                        all_truong_ban = []
                        for leads in DEPT_LEADS.get(selected_company, {}).values():
                            all_truong_ban.extend(leads)
                        yearly_df = yearly_df[yearly_df["Người thực hiện"].isin(all_truong_ban)]"""


for file_path in glob.glob("views/*.py"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = False
    
    if old_block in content:
        content = content.replace(old_block, bld_mapping_code)
        modified = True
        
    if "4_Nghiem_Thu.py" in file_path:
        if old_local_1 in content:
            content = content.replace(old_local_1, bld_mapping_local_1)
            modified = True
        if old_local_2 in content:
            content = content.replace(old_local_2, bld_mapping_local_2)
            modified = True
            
    if "5_Danh_Gia_KPI.py" in file_path:
        if old_local_3 in content:
            content = content.replace(old_local_3, bld_mapping_local_3)
            modified = True
        if old_local_4 in content:
            content = content.replace(old_local_4, bld_mapping_local_4)
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"Skipped {file_path} (pattern not found)")
