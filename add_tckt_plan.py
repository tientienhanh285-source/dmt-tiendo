import json
import os

plans = [
    ("Công tác tài chính Quản lý dòng tiền & Công nợ", "Theo dõi thu chi, lập báo cáo dòng tiền hằng ngày để cân đối nguồn vốn", "Hàng ngày"),
    ("Công tác tài chính Quản lý dòng tiền & Công nợ", "Theo dõi công nợ phải thu, phải trả; thu hồi nợ và lập kế hoạch thanh toán", "Thường xuyên"),
    ("Công tác tài chính Quản lý dòng tiền & Công nợ", "Theo dõi các khoản vay tại tổ chức tín dụng, cân đối nguồn vốn trả nợ đúng hạn", "Thường xuyên"),
    ("Công tác tài chính Quản lý dòng tiền & Công nợ", "Theo dõi nguồn chi đền bù các dự án; cập nhật chứng từ và đối chiếu số liệu", "Thường xuyên"),

    ("Công tác Kế toán", "Hạch toán đầy đủ, kịp thời các nghiệp vụ thanh toán, tạm ứng, tiền mặt, ngân hàng", "Thường xuyên"),
    ("Công tác Kế toán", "Theo dõi hồ sơ chuyển nhượng, hợp đồng cho thuê văn phòng, phí hạ tầng; xuất hóa đơn và ghi nhận doanh thu", "Thường xuyên"),
    ("Công tác Kế toán", "Theo dõi chi phí, giá vốn, doanh thu theo từng dự án; tính giá tính thuế GTGT khi phát sinh", "Theo phát sinh"),
    ("Công tác Kế toán", "Theo dõi tài sản cố định, công cụ dụng cụ; tính khấu hao và kiểm kê tài sản", "Thường xuyên"),
    ("Công tác Kế toán", "Theo dõi tài sản thế chấp tại các tổ chức tín dụng; đăng ký, xóa thế chấp khi phát sinh", "Theo phát sinh"),
    ("Công tác Kế toán", "Kiểm tra bảng thanh toán tiền lương, bảo hiểm và hạch toán", "Hàng tháng"),

    ("Ngân hàng & Vay vốn", "Làm việc với các tổ chức tín dụng, lập kế hoạch giải ngân phục vụ hoạt động và Khách sạn DMT Group", "Theo phát sinh"),
    ("Ngân hàng & Vay vốn", "Lập hồ sơ nhận nợ từng lần với ngân hàng khi phát sinh", "Thường xuyên"),

    ("Thuế", "Kê khai các loại thuế định kỳ: GTGT, thuế Phi nông nghiệp, TNCN, TNDN, thuế tài nguyên…", "Theo định kỳ"),
    ("Thuế", "Chuẩn bị hồ sơ, số liệu phục vụ công tác kiểm tra thuế", "Theo yêu cầu dự kiến trong tháng 10"),

    ("Khóa sổ & Báo cáo tài chính", "Thực hiện khóa sổ và lập Báo cáo tài chính năm 2026", "Cuối Quý IV"),

    ("Quyết toán dự án BT", "Thực hiện quyết toán vốn và hoàn vốn các dự án BT theo chỉ đạo của Ban Lãnh đạo", "Thường xuyên cho đến kết thúc dự án"),

    ("Các công việc khác", "Phối hợp với các Ban trong Công ty thực hiện các công việc liên quan", "Thường xuyên"),
    ("Các công việc khác", "Thực hiện các công việc phát sinh theo chỉ đạo của Ban Lãnh đạo", "Theo phát sinh")
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
        "department": "TCKT",
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

print(f"Added {len(plans)} targets for TCKT.")
