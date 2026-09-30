import os
import glob

old_1 = """                if manager_dept == "BLĐ":
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

new_1 = """                manager_user = st.session_state.get('manager_user', '')
                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
                if manager_user in bld_members:
                    if manager_dept == "BLĐ":
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
                        nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(all_truong_ban)]
                    else:
                        dept_leads = DEPT_LEADS.get(selected_company, {}).get(manager_dept, [])
                        truong_ban_list = [p for p in dept_leads if p not in bld_members]
                        if truong_ban_list:
                            nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(truong_ban_list)]"""

old_2 = """            if role_mode == "Quản lý" and st.session_state.get("manager_dept") == "BLĐ":
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

new_2 = """            if role_mode == "Quản lý":
                manager_user = st.session_state.get('manager_user', '')
                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
                if manager_user in bld_members:
                    if st.session_state.get("manager_dept") == "BLĐ":
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
                        mask = mask & local_df['NguoiChuTri'].isin(all_truong_ban)
                    else:
                        dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.get("manager_dept"), [])
                        truong_ban_list = [p for p in dept_leads if p not in bld_members]
                        if truong_ban_list:
                            mask = mask & local_df['NguoiChuTri'].isin(truong_ban_list)"""

old_3 = """            if selected_dept_m == "BLĐ":
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

new_3 = """            manager_user = st.session_state.get('manager_user', '')
            bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
            if manager_user in bld_members:
                if selected_dept_m == "BLĐ":
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
                    kpi_month_df = kpi_month_df[kpi_month_df["Người thực hiện"].isin(all_truong_ban)]
                elif selected_dept_m != "Tất cả phòng ban":
                    dept_leads = DEPT_LEADS.get(selected_company, {}).get(selected_dept_m, [])
                    truong_ban_list = [p for p in dept_leads if p not in bld_members]
                    if truong_ban_list:
                        kpi_month_df = kpi_month_df[kpi_month_df["Người thực hiện"].isin(truong_ban_list)]
                    else:
                        kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_m, selected_dept_m)]
            elif selected_dept_m == "BLĐ":
                kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == "BLĐ"]"""

old_4 = """                    if selected_dept_y == "BLĐ":
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

new_4 = """                    manager_user = st.session_state.get('manager_user', '')
                    bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]
                    if manager_user in bld_members:
                        if selected_dept_y == "BLĐ":
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
                            yearly_df = yearly_df[yearly_df["Người thực hiện"].isin(all_truong_ban)]
                        elif selected_dept_y != "Tất cả phòng ban":
                            dept_leads = DEPT_LEADS.get(selected_company, {}).get(selected_dept_y, [])
                            truong_ban_list = [p for p in dept_leads if p not in bld_members]
                            if truong_ban_list:
                                yearly_df = yearly_df[yearly_df["Người thực hiện"].isin(truong_ban_list)]
                            else:
                                yearly_df = yearly_df[yearly_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]
                    elif selected_dept_y == "BLĐ":
                        yearly_df = yearly_df[yearly_df["Phòng ban"] == "BLĐ"]"""


with open("views/4_Nghiem_Thu.py", "r", encoding="utf-8") as f:
    c = f.read()
if old_1 in c:
    c = c.replace(old_1, new_1)
if old_2 in c:
    c = c.replace(old_2, new_2)
with open("views/4_Nghiem_Thu.py", "w", encoding="utf-8") as f:
    f.write(c)

with open("views/5_Danh_Gia_KPI.py", "r", encoding="utf-8") as f:
    c = f.read()
if old_3 in c:
    c = c.replace(old_3, new_3)
if old_4 in c:
    c = c.replace(old_4, new_4)
with open("views/5_Danh_Gia_KPI.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Done updating local filters in 4 and 5")
