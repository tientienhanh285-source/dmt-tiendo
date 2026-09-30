import os
import glob

new_block = """        manager_user = st.session_state.get('manager_user', '')
        bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
        if manager_user in bld_members:
            if st.session_state.manager_dept == "BLĐ":
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
                db_filters['NguoiChuTri'] = list(set(all_truong_ban))
            else:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.manager_dept, [])
                truong_ban_list = [p for p in dept_leads if p not in bld_members]
                if truong_ban_list:
                    db_filters['NguoiChuTri'] = truong_ban_list
                else:
                    db_filters['PhongBan'] = st.session_state.manager_dept
        else:
            db_filters['PhongBan'] = st.session_state.manager_dept"""

old_block = """        if st.session_state.manager_dept == "BLĐ":
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
            db_filters['NguoiChuTri'] = list(set(all_truong_ban))
        else:
            db_filters['PhongBan'] = st.session_state.manager_dept"""

for file_path in glob.glob("views/*.py"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"Skipped {file_path}")
