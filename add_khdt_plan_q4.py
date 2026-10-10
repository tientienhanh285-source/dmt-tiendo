import json
import os
import uuid

plans = [
    # 01. Khu TĐC Phước Lý 2
    ("Khu TĐC Phước Lý 2", "Điều chỉnh dự án đầu tư: bổ sung các hạng mục, bổ sung tổng mức đầu tư", "Quý IV/2026"),
    ("Khu TĐC Phước Lý 2", "Điều chỉnh Giấy CNĐKĐT", "Quý IV/2026"),
    ("Khu TĐC Phước Lý 2", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "Phụ thuộc vào chủ trương của UBND TP"),
    ("Khu TĐC Phước Lý 2", "Kế hoạch vốn 2026 để t/toán BT", "Năm 2026"),

    # 02. Khu TĐC Phước Lý 6
    ("Khu TĐC Phước Lý 6", "Kế hoạch vốn 2026 để t/toán BT", "Quý IV/2026"),
    ("Khu TĐC Phước Lý 6", "Điều chỉnh dự án đầu tư: bổ sung tổng mức đầu tư (nếu có)", "Quý IV/2026"),
    ("Khu TĐC Phước Lý 6", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "Phụ thuộc vào chủ trương của UBND TP"),

    # 03. Khu đô thị Phước Lý
    ("Khu đô thị Phước Lý", "Thủ tục cấp Giấy CNQSDĐ đợt 19: 06 lô", "Phụ thuộc vào việc xác định nghĩa vụ tài chính của dự án"),

    # 04. Tuyến đường Lê Trọng Tấn nối dài
    ("Tuyến đường Lê Trọng Tấn nối dài", "Kế hoạch vốn 2026 để t/toán BT", "Quý IV/2026"),
    ("Tuyến đường Lê Trọng Tấn nối dài", "Điều chỉnh dự án đầu tư: bổ sung tổng mức đầu tư (nếu có)", "Quý IV/2026"),
    ("Tuyến đường Lê Trọng Tấn nối dài", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "Phụ thuộc vào chủ trương của UBND TP"),

    # 05. KDC Bàu Mạc
    ("KDC Bàu Mạc", "Điều chỉnh Quy hoạch giữ lại chỉnh trang đối với phần diện tích khoảng 117 m2", "Quý IV/2026"),
    ("KDC Bàu Mạc", "Thủ tục Quyết định giao đất đợt cuối", "Quý IV/2026"),
    ("KDC Bàu Mạc", "QĐ điều chỉnh chủ trương đầu tư bổ sung dự án 52 căn nhà đường Nguyễn An Ninh", "Quý IV/2026"),
    ("KDC Bàu Mạc", "Hồ sơ Báo cáo nghiên cứu khả thi", "Quý IV/2026"),

    # 06. KDC Nam Bàu Mạc
    ("KDC Nam Bàu Mạc", "Chấp thuận cho phép chuyển quyền sử dụng đất cho người dân tự xây dựng nhà ở", "Quý IV/2026"),
    ("KDC Nam Bàu Mạc", "Hoàn thành thủ tục giao đất (đo đạc, cấp GCNQSDĐ)", "Quý IV/2026"),
    ("KDC Nam Bàu Mạc", "QĐ điều chỉnh chủ trương đầu tư bổ sung dự án xây dựng nhà", "Phụ thuộc vào chủ trương UBND TP"),

    # 07. Khu đô thị Phong Nam
    ("Khu đô thị Phong Nam", "Bổ sung dự án vào danh mục dự án áp dụng Nghị quyết số 29/2026/QH16", "Quý IV/2026"),
    ("Khu đô thị Phong Nam", "UBND thành phố phê duyệt kế hoạch thực hiện dự án theo Nghị quyết số 29/2026/QH16", "Quý IV/2026"),
    ("Khu đô thị Phong Nam", "Lập hồ sơ trình UBND thành phố Ban hành Quyết định tiếp tục cho giao đất (nếu có) và thủ tục đầu tư", "Quý IV/2026"),

    # 08. Khu TĐC Hòa Liên 5
    ("Khu TĐC Hòa Liên 5", "Điều chỉnh dự án ĐTXD bổ sung các hạng mục, bổ sung tổng mức đầu tư", "Quý IV/2026"),
    ("Khu TĐC Hòa Liên 5", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "Tuỳ thuộc vào chủ trương"),
    ("Khu TĐC Hòa Liên 5", "Kế hoạch vốn 2026 để t/toán BT", "Năm 2026"),
    ("Khu TĐC Hòa Liên 5", "Thủ tục kết thúc dự án", "Năm 2026"),

    # 09. Đường Trần Hưng Đạo
    ("Đường Trần Hưng Đạo", "Kế hoạch vốn 2026 để t/toán BT", "Năm 2026"),
    ("Đường Trần Hưng Đạo", "Điều chỉnh dự án đầu tư: bổ sung tổng mức đầu tư (nếu có)", "Quý IV/2026"),
    ("Đường Trần Hưng Đạo", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "Quý IV/2026"),

    # 10. Khu BT sinh thái Hòa Ninh
    ("Khu BT sinh thái Hòa Ninh", "Bổ sung vào QHC Thành phố đối với phần diện tích đã được phê duyệt quy hoạch Phân khu", "Quý IV/2026"),
    ("Khu BT sinh thái Hòa Ninh", "Bổ sung vào Nghị quyết HĐND dự án thí điểm", "Quý IV/2026"),
    ("Khu BT sinh thái Hòa Ninh", "UBND TP có văn bản cho phép nhận chuyển nhượng dự án thí điểm", "Quý IV/2026"),

    # 11. CCN Thanh Vinh mở rộng
    ("CCN Thanh Vinh mở rộng", "Thu phí sử dụng hạ tầng năm 2026 và công nợ của các doanh nghiệp", "Năm 2026"),
    ("CCN Thanh Vinh mở rộng", "Khởi kiện Doanh nghiệp nợ phí sử dụng hạ tầng", "Theo chỉ đạo của Lãnh đạo Công ty"),
    ("CCN Thanh Vinh mở rộng", "Bổ sung vào nghị quyết HĐND dự án thí điểm", "Quý IV/2026"),
    ("CCN Thanh Vinh mở rộng", "UBND TP có văn bản cho phép nhận chuyển nhượng dự án thí điểm", "Quý IV/2026"),

    # 12. Khách sạn DMT GROUP
    ("Khách sạn DMT GROUP", "Cấp đổi Giấy CNQSDĐ", "Quý IV/2026"),
    ("Khách sạn DMT GROUP", "Phối hợp với các Ban lựa chọn ĐVTC để thi công các HM", "Theo tiến độ triển khai thi công"),
    ("Khách sạn DMT GROUP", "Hợp đồng/PLHĐ thi công các HM", "Theo tiến độ triển khai thi công"),
    ("Khách sạn DMT GROUP", "Phê duyệt Hs TK-DT điều chỉnh, bổ sung (nếu có)", "Theo hồ sơ của Ban QLDA"),
    ("Khách sạn DMT GROUP", "Thủ tục kiểm tra hiện trường của các cơ quan chức năng (nếu có)", "Theo tiến độ triển khai thi công"),
    ("Khách sạn DMT GROUP", "Chủ trương cho phép nghiệm thu của cơ quan chức năng (nếu có)", "Theo tiến độ triển khai thi công"),
    ("Khách sạn DMT GROUP", "Thực hiện các thủ tục để được phép bán căn hộ trong tương lai", "Năm 2026")
]

company = "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"
target_file = "project_targets.json"

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

existing_ids = set([t["target_id"] for t in data if "target_id" in t])

added_count = 0
for proj, target, dl in plans:
    new_id = f"T{str(uuid.uuid4())[:8].upper()}"
    while new_id in existing_ids:
        new_id = f"T{str(uuid.uuid4())[:8].upper()}"
    existing_ids.add(new_id)

    data.append({
        "target_id": new_id,
        "project_name": proj,
        "department": "KHĐT",
        "target_name": target,
        "deadline": dl,
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0,
        "company": company
    })
    added_count += 1

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {added_count} targets for KHĐT.")
