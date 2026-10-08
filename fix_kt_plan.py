import json
import uuid

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Remove the old ones added by me
# The old ones had these exact project names and departments
bad_projects = ["Khu TĐC Hoà Vang", "Trục I Tây Bắc", "Tuyến đường Lê Trọng Tấn", "Tuyến đường Trần Hưng Đạo (BT)", "TĐC Phước Lý 2 & Hoà Liên 5"]
bad_depts = ["KT", "BCH CT"]
filtered_data = []
for t in data:
    if t.get("department") in bad_depts and t.get("project_name") in bad_projects:
        continue # drop
    filtered_data.append(t)

# 2. Add them EXACTLY as the PDF
plan_data = [
    ("Khu Tái định cư Hoà Vang", [
        ("Hồ sơ thanh toán khối lượng hoàn thành", "31/10/2026"),
        ("Hồ sơ nghiệm thu quản lý chất lượng", "31/10/2026"),
        ("Thi công các hạng mục Giao thông, thoát nước, Cấp nước, Cây xanh", "31/10/2026"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty, Chủ đầu tư", "31/10/2026")
    ]),
    ("Tuyến đường Trục 1 Tây Bắc (Đoạn từ đường sắt đến QL1A)", [
        ("Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Thi công hạng mục giao thông, thoát nước, cấp nước", "30/12/2026"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty, Chủ đầu tư", "30/12/2026")
    ]),
    ("Tuyến đường Trục 1 Tây Bắc (Đoạn từ Hồ Tùng Mậu đến đường sắt)", [
        ("Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Thi công hạng mục cấp nước", "30/12/2026"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty, Chủ đầu tư", "30/12/2026")
    ]),
    ("Tuyến đường Lê Trọng Tấn (đoạn từ Phước Lý 6 đến Hoàng Văn Thái)", [
        ("Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Thi công hạng mục giao thông, thoát nước, cấp nước, điện chiếu sáng, di dời điện trên phạm vi có mặt bằng", "30/12/2026"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty, Chủ đầu tư", "30/12/2026")
    ]),
    ("Tuyến đường Trần Hưng Đạo nối dài", [
        ("Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu của Lãnh đạo"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty", "Theo yêu cầu của Lãnh đạo")
    ]),
    ("HTKT TĐC Phước Lý 2", [
        ("Bàn giao công trình", "Theo yêu cầu của Lãnh đạo"),
        ("Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu của Lãnh đạo"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty", "Theo yêu cầu của Lãnh đạo")
    ]),
    ("HTKT TĐC Hoà Liên 5", [
        ("Bàn giao công trình", "Theo yêu cầu của Lãnh đạo"),
        ("Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu của Lãnh đạo"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty", "Theo yêu cầu của Lãnh đạo")
    ])
]

departments_to_add = [
    ("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "KT"),
    ("CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "KT"),
    ("CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "BCH CT")
]

for company, dept in departments_to_add:
    for proj_name, tasks in plan_data:
        for task_name, deadline in tasks:
            t_id = "T" + str(uuid.uuid4())[:8].upper()
            filtered_data.append({
                "target_id": t_id,
                "project_name": proj_name,
                "department": dept,
                "company": company,
                "target_name": task_name,
                "deadline": deadline,
                "status": "Chưa bắt đầu",
                "approved": False,
                "progress": 0,
                "budget_2026": 0,
                "disbursed_value": 0
            })

with open('project_targets.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

print("Fixed KT and BCH CT targets")
