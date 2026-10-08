import json
import os

plans = [
    ("Xác định NVTC của các DA: KĐT Phước Lý, KDC Phước Lý MR, KDC Bàu Mạc, KDC Nam Bàu Mạc", "Tiếp tục làm việc với Phòng Kinh tế đất - Sở NN&MT rà soát, cung cấp thông tin, hồ sơ liên quan đến NVTC các dự án", "Quý IV/2026"),
    ("Xác định NVTC của các DA: KĐT Phước Lý, KDC Phước Lý MR, KDC Bàu Mạc, KDC Nam Bàu Mạc", "Làm việc với Lãnh đạo Sở, cán bộ chuyên môn của Sở NN&MT để hoàn thiện dự thảo BC xác định NVTC. Tham mưu nội dung, thời gian cho Lãnh đạo Cty và Sở NN&MT họp thảo luận, cho ý kiến dự thảo trước khi trình UBND TP xem xét, quyết định.", "Quý IV/2026"),
    ("Xác định NVTC của các DA: KĐT Phước Lý, KDC Phước Lý MR, KDC Bàu Mạc, KDC Nam Bàu Mạc", "Theo dõi, đôn đốc tiến độ xử lý hồ sơ, kịp thời tham mưu, đề xuất phương án tháo gỡ vướng mắc phát sinh trong quá trình thực hiện", "Quý IV/2026"),

    ("05 dự án BT: Khu TĐC Phước Lý 6, Đường Lê Trọng Tấn, Khu TĐC Phước Lý 2, Khu TĐC Hòa Liên 5, Đường Trần Hưng Đạo nối dài", "Làm việc UBNDTP, các Sở liên quan chủ trương điều chỉnh, bổ sung DAĐT và HĐ BT dự án Phước Lý 2 và Hoà Liên 5", "Tháng 10/2026"),
    ("05 dự án BT: Khu TĐC Phước Lý 6, Đường Lê Trọng Tấn, Khu TĐC Phước Lý 2, Khu TĐC Hòa Liên 5, Đường Trần Hưng Đạo nối dài", "Tổng hợp, hoàn thiện hồ sơ pháp lý của 05 dự án BT để cung cấp UBNDTP, HĐNDTP để bố trí kế hoạch vốn năm 2026", "Tháng 10/2026"),
    ("05 dự án BT: Khu TĐC Phước Lý 6, Đường Lê Trọng Tấn, Khu TĐC Phước Lý 2, Khu TĐC Hòa Liên 5, Đường Trần Hưng Đạo nối dài", "Tham mưu cho Lãnh đạo Cty làm việc với SXD thống nhất về mức lãi suất, lãi chậm trả, lợi nhuận. Phối hợp với các Ban Cty tính, hoàn thiện PA hoàn vốn bổ sung... Phối hợp với Ban KHĐT điều chỉnh, bổ sung DAĐT. Ký kết PLHĐ 05 dự án BT.", "Quý IV/2026"),
    ("05 dự án BT: Khu TĐC Phước Lý 6, Đường Lê Trọng Tấn, Khu TĐC Phước Lý 2, Khu TĐC Hòa Liên 5, Đường Trần Hưng Đạo nối dài", "Phối hợp với các cơ quan, đơn vị liên quan cung cấp hồ sơ phục vụ công tác kiểm toán của KTNN về 05 dự án BT.", "Tháng 10,11/2026"),
    ("05 dự án BT: Khu TĐC Phước Lý 6, Đường Lê Trọng Tấn, Khu TĐC Phước Lý 2, Khu TĐC Hòa Liên 5, Đường Trần Hưng Đạo nối dài", "Theo dõi, phối hợp với SXD, STC để thực hiện thủ tục giải ngân giá trị vốn đầu tư gốc của 05 dự án BT.", "Quý IV/2026"),

    ("Khu đô thị Phong Nam - Hòa Châu và Khu Thanh Vinh", "Phối hợp Ban KHĐT rà soát, hoàn thiện các hồ sơ, thủ tục pháp lý phục vụ công tác chuẩn bị triển khai thực hiện dự án.", "Tháng 10,11/2026"),
    ("Khu đô thị Phong Nam - Hòa Châu và Khu Thanh Vinh", "Theo dõi các thông báo, kết luận của Chủ tịch, Phó chủ tịch UBNDTP và bám sát tiến độ giải quyết các thủ tục của các Sở ban ngành để kịp thời tổng hợp, báo cáo và tham mưu Ban lãnh đạo.", "Quý IV/2026"),

    ("Dự án Khách sạn DMT-GROUP", "Phối hợp, thực hiện các công việc, hồ sơ liên quan để làm việc với các nhà thầu.", "Thường xuyên trong Quý IV/2026"),
    ("Dự án Khách sạn DMT-GROUP", "Tiếp tục thực hiện các công việc liên quan đến dự án và thường xuyên báo cáo, xin ý kiến Lãnh đạo công ty.", "Thường xuyên trong Quý IV/2026"),

    ("Các nhiệm vụ khác", "Tiếp tục thực hiện các nhiệm vụ, chức năng theo phân công và chỉ đạo của Ban Lãnh đạo Công ty.", "Thường xuyên trong Quý IV/2026"),
    ("Các nhiệm vụ khác", "Phối hợp với các phòng, ban, đơn vị trong quá trình thực hiện công việc.", "Thường xuyên trong Quý IV/2026")
]

target_file = "project_targets.json"

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

# Generate new IDs
existing_ids = [int(t["target_id"].replace("T", "")) for t in data if "target_id" in t and t["target_id"].startswith("T")]
next_id = max(existing_ids) + 1 if existing_ids else 1

for proj, target, dl in plans:
    data.append({
        "target_id": f"T{next_id:03d}",
        "project_name": proj,
        "department": "CBĐT",
        "target_name": target,
        "deadline": dl,
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    })
    next_id += 1

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Added {len(plans)} targets for CBĐT.")
