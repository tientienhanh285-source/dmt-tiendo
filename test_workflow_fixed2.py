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

DEFAULT_PERSONNEL = {
    "Ban Lãnh đạo": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
    "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên", "Đặng Ngọc Hoàng"],
    "Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"],
    "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Cao Thuỷ Tiên", "Trần Tin"],
    "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Phan Thị Kim Cúc"],
    "Ban Kỹ thuật": ["Nguyễn Văn Bồn"],
    "Ban Đền bù Giải tỏa": ["Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Ban chỉ huy Công trường": ["Nguyễn Phong Trung", "Phạm Văn Long", "Lê Đông"],
    "Xí nghiệp xe máy thiết bị": ["Đặng Hiền"],
    "Ban Dự án": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
    "Xí nghiệp DTBD": ["Mai Văn Châu"],
    "Sàn GDBĐS": ["Ngô Thị Tâm"],
}

# Map abbreviated departments to full ones for mapping employee to department
DEPT_MAP = {
    "BLĐ": "Ban Lãnh đạo",
    "HCNS": "Ban Hành chính Nhân sự",
    "TCKT": "Ban Tài chính Kế toán",
    "KHĐT": "Ban Kế hoạch Đầu tư",
    "CBĐT": "Ban Chuẩn bị Đầu tư",
    "KT": "Ban Kỹ thuật",
    "ĐBGT": "Ban Đền bù Giải tỏa",
    "DA": "Ban Dự án",
    "XN DTBD": "Xí nghiệp DTBD",
    "Sàn GDBĐS": "Sàn GDBĐS",
    "HĐQT": "Ban Lãnh đạo", # Usually HĐQT is BLĐ
    "BCH CT": "Ban chỉ huy Công trường",
    "XN XMTB": "Xí nghiệp xe máy thiết bị"
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

def get_employee_department(employee):
    for dept, people in DEFAULT_PERSONNEL.items():
        if employee in people:
            return dept
    return None

def simulate_manager_view(manager_user, manager_dept_abbr, selected_company, task_employee):
    # Anti-self approval
    if manager_user == task_employee:
        return False

    # Get employee's full department name
    task_employee_full_dept = get_employee_department(task_employee)

    if manager_user in bld_members:
        if manager_dept_abbr in ["BLĐ", "HĐQT"]:
            if manager_user in bld_hierarchy:
                all_truong_ban = bld_hierarchy[manager_user]
            else:
                all_truong_ban = []
                for leads in DEPT_LEADS.get(selected_company, {}).values():
                    all_truong_ban.extend(leads)
            
            return task_employee in all_truong_ban
        else:
            return False # Just seeing themselves
    else:
        # Regular manager
        # If manager logs in with a specific dept, they see ALL tasks of that department
        if manager_dept_abbr != "Tất cả":
            manager_full_dept = DEPT_MAP.get(manager_dept_abbr)
            if task_employee_full_dept == manager_full_dept:
                return True
        return False

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
        can_see = simulate_manager_view(manager, dept, comp, employee)
        if can_see:
            approvers.append(f"{manager} (phòng {dept} - {comp})")
            
    if not approvers:
        print(f"  ❌ LỖI: Không có bất kỳ Quản lý nào nhìn thấy công việc của {employee}!")
    else:
        print(f"  ✅ Đã gửi thành công đến danh sách chờ duyệt của:")
        for app in set(approvers):
            print(f"      - {app}")
