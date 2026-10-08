import json
import uuid

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define tasks per project
plan_data = [
    ("Khu TĐC Hoà Vang", [
        ("Hồ sơ thanh toán khối lượng hoàn thành", "31/10/2026"),
        ("Hồ sơ nghiệm thu quản lý chất lượng", "31/10/2026"),
        ("Thi công các hạng mục Giao thông, thoát nước, Cấp nước, Cây xanh", "31/10/2026"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty, Chủ đầu tư", "31/10/2026")
    ]),
    ("Trục I Tây Bắc", [
        ("Đoạn từ đường sắt đến QL1A - Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Đoạn từ đường sắt đến QL1A - Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Đoạn từ đường sắt đến QL1A - Thi công hạng mục giao thông, thoát nước, cấp nước", "30/12/2026"),
        ("Đoạn từ đường sắt đến QL1A - Các nội dung khác theo yêu cầu", "30/12/2026"),
        ("Đoạn từ Hồ Tùng Mậu đến đường sắt - Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Đoạn từ Hồ Tùng Mậu đến đường sắt - Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Đoạn từ Hồ Tùng Mậu đến đường sắt - Thi công hạng mục cấp nước", "30/12/2026"),
        ("Đoạn từ Hồ Tùng Mậu đến đường sắt - Các nội dung khác theo yêu cầu", "30/12/2026")
    ]),
    ("Tuyến đường Lê Trọng Tấn", [
        ("Đoạn từ Phước Lý 6 đến Hoàng Văn Thái - Hồ sơ thanh toán khối lượng hoàn thành", "30/12/2026"),
        ("Đoạn từ Phước Lý 6 đến Hoàng Văn Thái - Hồ sơ nghiệm thu quản lý chất lượng", "30/12/2026"),
        ("Đoạn từ Phước Lý 6 đến Hoàng Văn Thái - Thi công giao thông, thoát nước, cấp nước, điện chiếu sáng", "30/12/2026"),
        ("Đoạn từ Phước Lý 6 đến Hoàng Văn Thái - Các nội dung khác theo yêu cầu", "30/12/2026")
    ]),
    ("Tuyến đường Trần Hưng Đạo (BT)", [
        ("Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu"),
        ("Các nội dung khác theo yêu cầu của Lãnh đạo Công ty", "Theo yêu cầu")
    ]),
    ("TĐC Phước Lý 2 & Hoà Liên 5", [
        ("HTKT TĐC Phước Lý 2 - Bàn giao công trình", "Theo yêu cầu"),
        ("HTKT TĐC Phước Lý 2 - Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu"),
        ("HTKT TĐC Phước Lý 2 - Các nội dung khác theo yêu cầu", "Theo yêu cầu"),
        ("HTKT TĐC Hoà Liên 5 - Bàn giao công trình", "Theo yêu cầu"),
        ("HTKT TĐC Hoà Liên 5 - Điều chỉnh giá hợp đồng, Quyết toán công trình", "Theo yêu cầu"),
        ("HTKT TĐC Hoà Liên 5 - Các nội dung khác theo yêu cầu", "Theo yêu cầu")
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
            data.append({
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
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Added KT and BCH CT targets")
