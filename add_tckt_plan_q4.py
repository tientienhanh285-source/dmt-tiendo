import json
import os

plans = [
    # Kế hoạch tài chính & Quản lý dòng tiền
    ("Kế hoạch tài chính & Quản lý dòng tiền", "Lập kế hoạch tài chính, cân đối nguồn tiền phục vụ hoạt động Công ty.", "Trong Quý IV"),
    ("Kế hoạch tài chính & Quản lý dòng tiền", "Theo dõi, báo cáo quỹ tiền mặt và các khoản thu – chi.", "Hàng ngày"),
    ("Kế hoạch tài chính & Quản lý dòng tiền", "Tham mưu, cân đối nguồn vốn và kế hoạch chi theo nhu cầu thực tế.", "Thường xuyên"),
    
    # Công nợ & Thanh toán
    ("Công nợ & Thanh toán", "Theo dõi, đối chiếu công nợ khách hàng và nhà cung cấp.", "Thường xuyên"),
    ("Công nợ & Thanh toán", "Theo dõi hồ sơ thanh toán, đảm bảo thanh toán đúng hạn.", "Thường xuyên"),
    ("Công nợ & Thanh toán", "Phối hợp đáp ứng nhu cầu vật tư phục vụ thi công theo tiến độ.", "Theo phát sinh"),
    
    # Ngân hàng & Tín dụng
    ("Ngân hàng & Tín dụng", "Làm việc với các tổ chức tín dụng, lập kế hoạch vay vốn và giải ngân.", "Trong Quý IV"),
    ("Ngân hàng & Tín dụng", "Theo dõi lãi suất, các khoản nợ đến hạn và nhu cầu vốn phát sinh.", "Thường xuyên"),
    ("Ngân hàng & Tín dụng", "Theo dõi tài sản thế chấp và hồ sơ tín dụng; thực hiện thủ tục khi phát sinh.", "Theo phát sinh"),
    
    # Kế toán & Thuế
    ("Kế toán & Thuế", "Thực hiện các nghiệp vụ kế toán, hạch toán chứng từ đầy đủ, chính xác, kịp thời.", "Thường xuyên"),
    ("Kế toán & Thuế", "Theo dõi chi phí vật tư, máy thi công, nhân công và các chi phí của công trình.", "Thường xuyên"),
    ("Kế toán & Thuế", "Phối hợp thực hiện hồ sơ nghiệm thu thanh toán với Chủ đầu tư.", "Theo phát sinh"),
    ("Kế toán & Thuế", "Thực hiện báo cáo, kê khai thuế theo định kỳ.", "Theo định kỳ"),
    ("Kế toán & Thuế", "Thực hiện nghiệp vụ TSCĐ & CCDC.", "Thường xuyên"),
    ("Kế toán & Thuế", "Thực hiện nghiệp vụ tiền lương và BHXH.", "Hàng tháng"),
    
    # Quyết toán vốn đầu tư
    ("Quyết toán vốn đầu tư", "Phối hợp các Ban thực hiện quyết toán vốn đầu tư các dự án BT.", "Trong Quý IV"),
    ("Quyết toán vốn đầu tư", "Tiếp tục thực hiện quyết toán các dự án Hòa Liên 5 và Trần Hưng Đạo.", "Trong Quý IV"),
    
    # Phối hợp thực hiện công việc & Báo cáo
    ("Phối hợp thực hiện công việc & Báo cáo", "Phối hợp với các Ban xử lý hồ sơ, công việc phát sinh hàng ngày.", "Thường xuyên"),
    ("Phối hợp thực hiện công việc & Báo cáo", "Thực hiện các báo cáo theo yêu cầu và công việc theo chỉ đạo của Lãnh đạo Công ty.", "Theo yêu cầu")
]

companies = [
    "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
    "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
]

target_file = "project_targets.json"

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

import uuid

existing_ids = set([t["target_id"] for t in data if "target_id" in t])

added_count = 0
for comp in companies:
    for proj, target, dl in plans:
        # Generate short unique ID
        new_id = f"T{str(uuid.uuid4())[:8].upper()}"
        while new_id in existing_ids:
            new_id = f"T{str(uuid.uuid4())[:8].upper()}"
        existing_ids.add(new_id)

        data.append({
            "target_id": new_id,
            "project_name": proj,
            "department": "TCKT",
            "target_name": target,
            "deadline": dl,
            "status": "Chưa bắt đầu",
            "approved": False,
            "progress": 0,
            "budget_2026": 0,
            "disbursed_value": 0,
            "company": comp
        })
        added_count += 1

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added_count} targets.")
