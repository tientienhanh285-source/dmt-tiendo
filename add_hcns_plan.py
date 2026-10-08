import json
import os

plans = [
    ("Tổ chức & Quản lý nhân sự", "Tuyển dụng, sắp xếp và bổ sung nhân sự khi có nhu cầu", "Trong Quý IV"),
    ("Tổ chức & Quản lý nhân sự", "Rà soát, sửa đổi và bổ sung Nội quy lao động", "Trong Quý IV"),
    ("Tổ chức & Quản lý nhân sự", "Theo dõi, hướng dẫn việc áp dụng Điều lệ mới tại các Đơn vị thành viên và quy chế hoạt động của các Tổ chuyên môn", "Trong Quý IV"),
    ("Tổ chức & Quản lý nhân sự", "Vận hành thử nghiệm Hệ thống KPI Quý IV", "Trong Quý IV"),
    ("Tổ chức & Quản lý nhân sự", "Lập kế hoạch rà soát, đánh giá xếp loại nhân sự cuối năm và báo cáo dự toán quỹ Lương tháng 13 / Thưởng Tết, các chi phí phát sinh cuối năm", "Cuối Quý IV"),

    ("Hành chính – Văn thư & Văn phòng", "Quản lý văn bản, con dấu và phần mềm DMT E-Office chính xác, kịp thời và an toàn bảo mật", "Thường xuyên"),
    ("Hành chính – Văn thư & Văn phòng", "Cung cấp văn phòng phẩm, trang thiết bị và theo dõi chi phí vận hành tại Văn phòng và các dự án/công trường dịp cuối năm", "Trong Quý IV"),
    ("Hành chính – Văn thư & Văn phòng", "Điều phối xe và theo dõi việc bảo dưỡng xe", "Thường xuyên"),
    ("Hành chính – Văn thư & Văn phòng", "Phối hợp Ban TCKT thực hiện công tác kiểm kê tài sản định kỳ", "Trong Quý IV"),
    ("Hành chính – Văn thư & Văn phòng", "Phối hợp với các đơn vị truyền thông, quảng cáo triển khai nội dung quảng bá hình ảnh Công ty trên các ấn phẩm, nền tảng Báo Xuân 2027", "Cuối Quý IV"),

    ("Lương, Chấm công & BHXH", "Tiền lương & Chấm công: Chấm công, tính lương, thưởng và phụ cấp đúng kỳ hạn hàng tháng; chuẩn bị dữ liệu quyết toán lương/thưởng năm 2026", "Hàng tháng; hoàn tất cuối Q4"),
    ("Lương, Chấm công & BHXH", "BHXH & Chế độ: Trích nộp BHXH/BHYT/BHTN đầy đủ, đúng hạn; thực hiện báo tăng/giảm, chốt sổ và giải quyết kịp thời chế độ BHXH cho NLĐ", "Thường xuyên"),
    ("Lương, Chấm công & BHXH", "Hồ sơ nhân sự: Rà soát các HĐLĐ hết hạn trong Quý 4/2026 để tiến hành tái ký hoặc thanh lý đúng thủ tục; hoàn thiện lưu trữ hồ sơ nhân sự năm 2026", "Trong Quý IV"),

    ("Chế độ & Chăm lo người lao động", "Tổ chức khám sức khỏe định kỳ năm 2026", "Trong Quý IV"),
    ("Chế độ & Chăm lo người lao động", "Thực hiện thăm hỏi ốm đau, hiếu hỉ, sinh nhật cho CBCNV và gia đình", "Thường xuyên"),
    ("Chế độ & Chăm lo người lao động", "Lập kế hoạch, dự toán Hội nghị Tổng kết năm 2026 và Chuẩn bị quà Tết Nguyên đán cho người lao động", "Cuối Quý IV"),

    ("Quản lý cho thuê Văn phòng", "Khai thác & Đăng tin: Phối hợp với Sàn DMT Land tìm kiếm khách thuê, đăng tin và phối hợp dẫn khách xem văn phòng", "Thường xuyên"),
    ("Quản lý cho thuê Văn phòng", "Quản lý vận hành: Theo dõi việc thực hiện nội quy, PCCC, an ninh và thu tiền thuê, phí dịch vụ", "Thường xuyên")
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
        "department": "HCNS",
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

print(f"Added {len(plans)} targets for HCNS.")
