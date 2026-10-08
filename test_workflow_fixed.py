import json

DEPT_LEADS = {
    "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG": {
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên", "Đặng Ngọc Hoàng"],
        "TCKT": ["Đồng Thị Nguyệt Nga"],
        "KHĐT": ["Nguyễn Trần Thức"],
        "CBĐT": ["Hồ Văn Khoa"],
        "KT": [],
        "ĐBGT": ["Nguyễn Ngọc Tôn"],
        "DA": [],
        "XN DTBD": [],
        "Sàn GDBĐS": []
    },
    "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "HĐQT": ["Đặng Thanh Bình"],
        "BLĐ": ["Thái Văn Thành", "Trần Văn Trọng"],
        "HCNS": ["Nguyễn Thị Mỹ Phương"],
        "TCKT": ["Nguyễn Thị Ngọc Hà"],
        "KT": ["Thái Văn Thành", "Trần Văn Trọng"],
        "BCH CT": ["Thái Văn Thành", "Trần Văn Trọng"],
        "XN XMTB": ["Thái Văn Thành", "Trần Văn Trọng"]
    },
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {
        "BLĐ": ["Trần Cường"]
    }
}

bld_hierarchy = {
    "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"],
    "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"],
    "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tâm"],
    "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân", "Nguyễn Văn Bồn"],
    "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"],
    "Trần Cường": ["Trần Cường"],
    "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
    "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
}

bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]

def simulate_manager_view(manager_user, manager_dept, selected_company, task_employee):
    # Prevent self-approval (like line 160 in 4_Nghiem_Thu.py)
    if manager_user == task_employee:
        return []

    if manager_user in bld_members:
        if manager_dept in ["BLĐ", "HĐQT"]:
            if manager_user in bld_hierarchy:
                all_truong_ban = bld_hierarchy[manager_user]
            else:
                all_truong_ban = []
                for leads in DEPT_LEADS.get(selected_company, {}).values():
                    all_truong_ban.extend(leads)
        else:
            all_truong_ban = [manager_user]
    else:
        all_truong_ban = [manager_user]
        
    # If the manager is not in BLĐ and just approves their dept, they see all dept tasks
    if manager_dept != "Tất cả" and manager_user not in bld_members:
        # In reality, they see all users in their dept. 
        # For simulation, we assume if they are the manager of HCNS, they see HCNS tasks.
        pass
        
    return all_truong_ban

all_managers = []
for comp, depts in DEPT_LEADS.items():
    for dept, leads in depts.items():
        for lead in leads:
            all_managers.append((comp, dept, lead))

employees_to_test = [
    "Ngô Thị Tâm", 
    "Nguyễn Đình Thắng", 
    "Nguyễn Đình Hiếu",
    "Mai Văn Châu",
    "Nguyễn Văn Bồn",
    "Huỳnh Thị Hoàng Hà",
    "Nguyễn Thị Hạnh Tiên"
]

print("=== MÔ PHỎNG LUỒNG DUYỆT ===")
for employee in employees_to_test:
    print(f"\\n[Nhân viên]: {employee} tạo công việc và nộp báo cáo.")
    
    approvers = []
    for comp, dept, manager in all_managers:
        visible_employees = simulate_manager_view(manager, dept, comp, employee)
        if employee in visible_employees or (manager not in bld_members and employee in DEPT_LEADS.get(comp, {}).get(dept, [])):
            if manager != employee: # double check
                approvers.append(f"{manager} (phòng {dept} - {comp})")
            
    if not approvers:
        print(f"  ❌ LỖI: Không có bất kỳ Quản lý nào nhìn thấy công việc của {employee}!")
    else:
        print(f"  ✅ Đã gửi thành công đến danh sách chờ duyệt của:")
        for app in set(approvers):
            print(f"      - {app}")
