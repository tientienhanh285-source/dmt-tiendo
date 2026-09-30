import json
import os

filepath = 'project_targets.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_targets = [
    {
        "project_name": "XÂY DỰNG HỆ THỐNG CẤP BẬC NHÂN VIÊN - KHUNG NĂNG LỰC CBNV",
        "department": "HCNS",
        "target_name": "Sơ đồ Cơ cấu tổ chức chi tiết: Xây dựng ban hành sơ đồ tổ chức Tổng Công ty DMT GROUP làm căn cứ hệ thống hoá Quy chế HCNS",
        "deadline": "Tháng 07/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "XÂY DỰNG HỆ THỐNG CẤP BẬC NHÂN VIÊN - KHUNG NĂNG LỰC CBNV",
        "department": "HCNS",
        "target_name": "Hệ thống cấp bậc chức danh: Xây dựng hệ thống cấp bậc chức danh CBNV Công ty DMT Group (Nhóm chức danh, bộ phận, chi tiết các bộ phận)",
        "deadline": "Tháng 07/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "XÂY DỰNG HỆ THỐNG CẤP BẬC NHÂN VIÊN - KHUNG NĂNG LỰC CBNV",
        "department": "HCNS",
        "target_name": "Mô tả công việc: 1. Xây dựng bản mô tả công việc của từng vị trí chức năng. 2. Phối hợp với GĐ ban chuyên môn để chuẩn hoá - Làm cơ sở xây dựng khung năng lực",
        "deadline": "Tháng 07/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "XÂY DỰNG HỆ THỐNG CẤP BẬC NHÂN VIÊN - KHUNG NĂNG LỰC CBNV",
        "department": "HCNS",
        "target_name": "Khung năng lực CBNV DMT GROUP: 1. Phê duyệt khung năng lực tổng thể. 2. Chuẩn hóa năng lực. 3. Đào tạo quản lý cách đánh giá. 4. Áp dụng thí điểm 1-2 Ban. 5. Áp dụng toàn Công ty",
        "deadline": "Tháng 07/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "Hệ thống KPI - DMT GROUP",
        "department": "HCNS",
        "target_name": "Nghiên cứu và lên phương án thực hiện: Thành lập đội KPIs, kế hoạch xây dựng bảng phân giao KPIs, xây dựng mục tiêu KPI theo từng ban/cá nhân, đánh giá hàng tháng",
        "deadline": "Quý III - Quý IV /2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "NGÂN SÁCH NGUỒN NHÂN LỰC / XÂY DỰNG CHÍNH SÁCH THƯỞNG",
        "department": "HCNS",
        "target_name": "Ngân sách nhân sự trong năm: 1. Xây lại Ngân sách lương tổng 2026. 2. Rà soát nhân sự, tham mưu Chủ tịch định hướng nhân sự (tinh giảm, điều động, tuyển dụng bổ sung)",
        "deadline": "Kết thúc tháng 7/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "NGÂN SÁCH NGUỒN NHÂN LỰC / XÂY DỰNG CHÍNH SÁCH THƯỞNG",
        "department": "HCNS",
        "target_name": "Chính sách thưởng phúc lợi / khen thưởng: Căn cứ Khung năng lực CBNV DMT GROUP để xây dựng lại Quy chế lương thưởng / Đánh giá cập nhật",
        "deadline": "Quý III/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "HÊ THỐNG VĂN BẢN NỘI BỘ DOANH NGHỆP",
        "department": "HCNS",
        "target_name": "Quy trình quy định: Xây dựng lại 10 Quy chế hoạt động. Đào tạo – triển khai – rà soát định kỳ các quy định và áp chỉ tiêu cho GĐ Ban kiểm soát",
        "deadline": "Quý III/2026 - Quý IV/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "HÊ THỐNG VĂN BẢN NỘI BỘ DOANH NGHỆP",
        "department": "HCNS",
        "target_name": "Biểu mẫu vận hành tối ưu: Hệ thống hoá lại các Biểu mẫu tối ưu vận hành",
        "deadline": "Theo thực trạng",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Hợp đồng lao động: Thay đổi lại toàn bộ mẫu HĐ DMT GROUP với các điều khoản phù hợp LLĐ 2019 (HĐ thử việc, HĐLĐ, Phụ lục, HĐ trách nhiệm)",
        "deadline": "Tháng 7/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Hồ sơ đăng ký thang bảng lương: Kiện toàn mới áp dụng 01/2026 lưu trữ tại Công ty (Thang lương bảng lương BHXH, Quy định tiêu chuẩn chức danh)",
        "deadline": "08/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Công đoàn: Kết hợp với Ban chấp hành Công đoàn Công ty tổ chức các Hoạt động Sinh nhật, vinh danh CBNV và Kỷ niệm kết nối",
        "deadline": "Định kỳ",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Bảo hiểm xã hội: Giám sát việc thực hiện các chế độ chính sách đóng BHYT, BHXH, BHTN, chế độ bảo hộ lao động",
        "deadline": "Quý III/2026 ; Quý IV/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Tính LƯƠNG và tính CÔNG: 1. Kiện toàn biểu mẫu tính lương. 2. Xây dựng mẫu đánh giá công việc",
        "deadline": "Thực hiện định kỳ và khi có phát sinh",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)",
        "department": "HCNS",
        "target_name": "Khám sức khoẻ cho CBNV: Đề xuất HĐQT cho tổ chức khám sức khoẻ định kỳ cho toàn thể CBNV",
        "deadline": "Quý III/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "ĐÀO TẠO VÀ XÂY DỰNG PHÁT TRIỂN NGUỒN NHÂN LỰC",
        "department": "HCNS",
        "target_name": "Đào tạo nguồn nhân lực: 1. Xây dựng quy trình tuyển dụng và Onboarding. 2. Xây dựng bộ chương trình phát triển năng lực quản lý cấp trung. 3. Tổ chức đào tạo nâng tầm quản lý từ các chuyên gia",
        "deadline": "Trong năm 2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "ĐÀO TẠO VÀ XÂY DỰNG PHÁT TRIỂN NGUỒN NHÂN LỰC",
        "department": "HCNS",
        "target_name": "BỘ tiêu chuẩn SOP Vận hành Khách sạn: Nghiên cứu và lên kế hoạch phối hợp Xây dựng 'BỘ TIÊU CHUẨN SOP VẬN HÀNH KHÁCH SẠN'",
        "deadline": "Trong năm 2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC HÀNH CHÍNH",
        "department": "HCNS",
        "target_name": "Công tác hành chính: Tiếp tục thực hiện tốt các công việc thường xuyên của Ban và các công tác phát sinh",
        "deadline": "Định kỳ",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "QUẢN LÝ VÀ CHO THUÊ VĂN PHÒNG",
        "department": "HCNS",
        "target_name": "Cho thuê văn phòng: 1. Phối hợp với Sàn DMT Land soạn thảo hợp đồng cho thuê VP. 2. Làm việc với Đơn vị môi giới, quảng bá hoạt động cho thuê tối ưu doanh thu",
        "deadline": "Quý III/2026",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    },
    {
        "project_name": "CÔNG TÁC LIÊN PHÒNG BAN VÀ PHỐI HỢP PHÁP LÝ KHÁC",
        "department": "HCNS",
        "target_name": "Công tác liên phòng ban: 1. Chủ động trong công việc liên phòng ban. 2. Tuân thủ và tham vấn kịp thời các yêu cầu pháp lý, hồ sơ, thủ tục liên quan",
        "deadline": "Định kỳ",
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    }
]

filtered_data = [x for x in data if not (x['target_id'].startswith('T') and 11 <= int(x['target_id'][1:]) <= 35)]
insert_idx = next((i for i, x in enumerate(filtered_data) if x['target_id'] == 'T010'), -1)
if insert_idx != -1:
    insert_idx += 1
else:
    insert_idx = len(filtered_data)

final_list = filtered_data[:insert_idx] + new_targets + filtered_data[insert_idx:]

for i, task in enumerate(final_list):
    task['target_id'] = f"T{i+1:03d}"

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print("Successfully updated project_targets.json with detailed HCNS data!")
