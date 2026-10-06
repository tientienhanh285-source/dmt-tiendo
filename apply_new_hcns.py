import json

filepath = 'project_targets.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# The new tasks from the PDF
hcns_tasks = [
    # Nhóm 1
    {"project_name": "Tổ chức & Quản lý nhân sự", "target_name": "Tuyển dụng, sắp xếp và bổ sung nhân sự khi có nhu cầu", "deadline": "Trong Quý IV"},
    {"project_name": "Tổ chức & Quản lý nhân sự", "target_name": "Rà soát, sửa đổi và bổ sung Nội quy lao động", "deadline": "Trong Quý IV"},
    {"project_name": "Tổ chức & Quản lý nhân sự", "target_name": "Theo dõi, hướng dẫn việc áp dụng Điều lệ mới tại các Đơn vị thành viên và quy chế hoạt động của các Tổ chuyên môn", "deadline": "Trong Quý IV"},
    {"project_name": "Tổ chức & Quản lý nhân sự", "target_name": "Vận hành thử nghiệm Hệ thống KPI Quý IV", "deadline": "Trong Quý IV"},
    {"project_name": "Tổ chức & Quản lý nhân sự", "target_name": "Lập kế hoạch rà soát, đánh giá xếp loại nhân sự cuối năm và báo cáo dự toán quỹ Lương tháng 13 / Thưởng Tết, các chi phí phát sinh cuối năm", "deadline": "Cuối Quý IV"},
    
    # Nhóm 2
    {"project_name": "Hành chính – Văn thư & Văn phòng", "target_name": "Quản lý văn bản, con dấu và phần mềm DMT E-Office chính xác, kịp thời và an toàn bảo mật", "deadline": "Thường xuyên"},
    {"project_name": "Hành chính – Văn thư & Văn phòng", "target_name": "Cung cấp văn phòng phẩm, trang thiết bị và theo dõi chi phí vận hành tại Văn phòng và các dự án/công trường dịp cuối năm", "deadline": "Trong Quý IV"},
    {"project_name": "Hành chính – Văn thư & Văn phòng", "target_name": "Điều phối xe và theo dõi việc bảo dưỡng xe", "deadline": "Thường xuyên"},
    {"project_name": "Hành chính – Văn thư & Văn phòng", "target_name": "Phối hợp Ban TCKT thực hiện công tác kiểm kê tài sản định kỳ.", "deadline": "Trong Quý IV"},
    {"project_name": "Hành chính – Văn thư & Văn phòng", "target_name": "Phối hợp với các đơn vị truyền thông, quảng cáo triển khai nội dung quảng bá hình ảnh Công ty trên các ấn phẩm, nền tảng Báo Xuân 2027", "deadline": "Cuối Quý IV"},
    
    # Nhóm 3
    {"project_name": "Lương, Chấm công & BHXH", "target_name": "Tiền lương & Chấm công: Chấm công, tính lương, thưởng và phụ cấp đúng kỳ hạn hàng tháng; chuẩn bị dữ liệu quyết toán lương/thưởng năm 2026.", "deadline": "Hàng tháng; hoàn tất cuối Q4"},
    {"project_name": "Lương, Chấm công & BHXH", "target_name": "BHXH & Chế độ: Trích nộp BHXH/BHYT/BHTN đầy đủ, đúng hạn; thực hiện báo tăng/giảm, chốt sổ và giải quyết kịp thời chế độ BHXH cho NLĐ.", "deadline": "Thường xuyên"},
    {"project_name": "Lương, Chấm công & BHXH", "target_name": "Hồ sơ nhân sự: Rà soát các HĐLĐ hết hạn trong Quý 4/2026 để tiến hành tái ký hoặc thanh lý đúng thủ tục; hoàn thiện lưu trữ hồ sơ nhân sự năm 2026.", "deadline": "Trong Quý IV"},
    
    # Nhóm 4
    {"project_name": "Chế độ & Chăm lo người lao động", "target_name": "Tổ chức khám sức khỏe định kỳ năm 2026", "deadline": "Trong Quý IV"},
    {"project_name": "Chế độ & Chăm lo người lao động", "target_name": "Thực hiện thăm hỏi ốm đau, hiếu hỉ, sinh nhật cho CBCNV và gia đình", "deadline": "Thường xuyên"},
    {"project_name": "Chế độ & Chăm lo người lao động", "target_name": "Lập kế hoạch, dự toán Hội nghị Tổng kết năm 2026 và Chuẩn bị quà Tết Nguyên đán cho người lao động", "deadline": "Cuối Quý IV"},
    
    # Nhóm 5
    {"project_name": "Quản lý cho thuê Văn phòng", "target_name": "Khai thác & Đăng tin: Phối hợp với Sàn DMT Land tìm kiếm khách thuê, đăng tin và phối hợp dẫn khách xem văn phòng", "deadline": "Thường xuyên"},
    {"project_name": "Quản lý cho thuê Văn phòng", "target_name": "Quản lý vận hành: Theo dõi việc thực hiện nội quy, PCCC, an ninh và thu tiền thuê, phí dịch vụ", "deadline": "Thường xuyên"}
]

# Tạo target cho 3 ban HCNS
depts_to_apply = ["HCNS", "HCNS Cienco", "HCNS Marina"] # Giả sử DMT là HCNS, Cienco và Marina có suffix
new_targets = []

for dept in depts_to_apply:
    for t in hcns_tasks:
        new_targets.append({
            "project_name": t["project_name"],
            "department": dept,
            "target_name": t["target_name"],
            "deadline": t["deadline"],
            "status": "Chưa bắt đầu",
            "approved": False,
            "progress": 0,
            "budget_2026": 0,
            "disbursed_value": 0
        })

# Xóa KH cũ của HCNS
filtered_data = [x for x in data if not (x.get('department') in ["HCNS", "HCNS Cienco", "HCNS Marina"])]

# Append new
final_list = filtered_data + new_targets

# Đánh lại target_id
for i, task in enumerate(final_list):
    task['target_id'] = f"T{i+1:03d}"

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print("Đã cập nhật Kế hoạch mới cho Ban HCNS (DMT, Cienco, Marina) thành công!")
