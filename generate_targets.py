import json

targets = []
target_counter = 1

def add_target(dept, proj, name, deadline="", budget=0):
    global target_counter
    targets.append({
        "target_id": f"T{target_counter:03d}",
        "project_name": proj,
        "department": dept,
        "target_name": name,
        "deadline": deadline,
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": budget,
        "disbursed_value": 0
    })
    target_counter += 1

# 1. Ban Đền Bù Giải Tỏa (ĐBGT / GPMB) -> Department: "ĐBGT" (Wait, what are valid depts? "BLĐ", "KT", "KHĐT", "CBĐT", "HCNS", "KTTC", "KD", "ĐBGT"?)
# Let's map to existing valid departments in app.py: "BLĐ", "KT", "KHĐT", "CBĐT", "HCNS", "KTTC", "KD". 
# The PDF mentions "Ban ĐBGT" (Đền bù giải tỏa). Let's use "CBĐT" (Chuẩn bị đầu tư) or "KHĐT" (Kế hoạch đầu tư) or add "ĐBGT".
# Wait, "CBĐT" is usually Chuẩn bị đầu tư. "KHĐT" is Kế hoạch đầu tư. 
# Let's just use "KHĐT" for Đền bù, or "CBĐT" ? The JSON earlier had:
# valid_depts = get_departments_for_company(selected_company, config)
# Actually, the user can add new departments in the UI/JSON later, but let's use the ones I know: "KHĐT", "KT", "KD", "KTTC", "HCNS", "BLĐ", "ĐBGT", "BĐS", "XNDT"

# 7. CÔNG TÁC HÀNH CHÍNH NHÂN SỰ (HCNS) - Pages 39-43
hcns_tasks = [
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Giấy Chứng nhận đăng ký Kinh doanh", "Quý I/2026"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Giấy chứng nhận đăng ký Đầu tư", "Quý I/2026"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Giấy phép Xây dựng", "Quý I/2026"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Giấy phép pháp lý về phòng cháy chữa cháy", "Quý I/2026"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Kiện toàn hồ sơ quản lý về hoạt động Phòng cháy chữa cháy", "Quý I/2026"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Hợp đồng mua bán điện với các mã Khách hàng", "Định kỳ"),
    ("Hồ sơ pháp lý - Công ty CP Đầu tư Đà Nẵng Miền Trung", "Hợp đồng mua bán nước với các mã Khách hàng", "Định kỳ"),
    ("Hồ sơ pháp lý của Đơn vị thành viên", "Sắp xếp rà soát đánh số lên danh mục theo dõi lại chi tiết", "Định kỳ"),
    ("Lưu trữ Công văn hồ sơ Sở ban ngành - đoàn thể", "Rà soát lại để có phương án lưu trữ tối ưu", "Định kỳ"),
    ("Báo cáo thành tích SBN", "Theo dõi định kỳ hằng năm lập báo cáo thành tích nộp SBN liên quan", "Định kỳ"),
    ("XÂY DỰNG HỆ THỐNG CẤP BẬC", "Xây dựng ban hành sơ đồ tổ chức Tổng Công ty DMT GROUP", "Quý I - Quý II/2026"),
    ("KHUNG NĂNG LỰC CBNV", "Xây dựng hệ thống cấp bậc chức danh CBNV Công ty DMT Group", "2026"),
    ("KHUNG NĂNG LỰC CBNV", "Xây dựng bản mô tả công việc của từng vị trí chức năng", "2026"),
    ("KHUNG NĂNG LỰC CBNV", "Phê duyệt và chuẩn hóa khung năng lực, đào tạo quản lý đánh giá", "2026"),
    ("Hệ thống KPI - DMT GROUP", "Thành lập đội KPIs, xây dựng mục tiêu KPI theo ban/cá nhân", "Quý III - Quý IV/2026"),
    ("NGÂN SÁCH NGUỒN NHÂN LỰC / XÂY DỰNG CHÍNH SÁCH", "Xây lại Ngân sách lương tổng toàn hệ thống 2026", "Kết thúc tháng 1/2026"),
    ("NGÂN SÁCH NGUỒN NHÂN LỰC / XÂY DỰNG CHÍNH SÁCH", "Rà soát lại nhân sự, tham mưu định hướng công tác nhân sự", "Kết thúc tháng 1/2026"),
    ("THƯỞNG", "Xây dựng lại Quy chế lương thưởng / Đánh giá cập nhật", "2026"),
    ("HỆ THỐNG VĂN BẢN NỘI BỘ DOANH NGHIỆP", "Xây dựng lại 10 Quy chế hoạt động, Quy trình quy định", "Quý I - Quý III/2026"),
    ("Biểu mẫu vận hành tối ưu", "Hệ thống hoá lại các Biểu mẫu tối ưu vận hành", "2026"),
    ("CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)", "Thay đổi lại toàn bộ mẫu HĐ DMT GROUP với các điều khoản phù hợp LLĐ 2019", "Quý I - Quý II/2026"),
    ("CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)", "Kiện toàn mới áp dụng lưu trữ Thang lương bảng lương BHXH", "01/2026"),
    ("CÔNG TÁC C&B (LƯƠNG VÀ CHẾ ĐỘ PHÚC LỢI)", "Kết hợp Công đoàn xây dựng hoạt động chung (Sinh nhật, Kỷ niệm)", "Định kỳ"),
    ("Bảo hiểm xã hội", "Giám sát việc đóng BHYT, BHXH, BHTN, bảo hộ lao động", "Chuẩn tại kỳ lương"),
    ("Thuế TNCN", "Rà soát hồ sơ Người phụ thuộc, Đảm bảo khấu trừ thuế TNCN", "02/2026"),
    ("Tính LƯƠNG và tính CÔNG", "Kiện toàn biểu mẫu tính lương, bảng tăng giảm nhân sự", "2026"),
    ("Máy chấm công", "Đề xuất mua mới lại Máy chấm công, Hệ thống MCC liên kết", "Tháng 2/2026"),
    ("Khám sức khoẻ", "Tổ chức khám sức khoẻ định kỳ cho toàn thể CBNV", "2026"),
    ("ĐÀO TẠO VÀ XÂY DỰNG PHÁT TRIỂN NGUỒN NHÂN LỰC", "Xây dựng quy trình tuyển dụng và Onboarding - Văn hóa doanh nghiệp", "2026"),
    ("ĐÀO TẠO VÀ XÂY DỰNG PHÁT TRIỂN NGUỒN NHÂN LỰC", "Xây dựng bộ chương trình phát triển năng lực Quản lý cấp trung", "2026"),
    ("ĐÀO TẠO VÀ XÂY DỰNG PHÁT TRIỂN NGUỒN NHÂN LỰC", "Tổ chức đào tạo nâng tầm quản lý từ các chuyên gia", "2026"),
    ("BỘ tiêu chuẩn SOP Vận hành Khách sạn", "Lên kế hoạch phối hợp Xây dựng BỘ TIÊU CHUẨN SOP VẬN HÀNH KHÁCH SẠN", "2026"),
    ("CÔNG TÁC HÀNH CHÍNH", "Tiếp tục thực hiện tốt các công việc thường xuyên của Ban", "Định kỳ"),
    ("QUẢN LÝ VÀ CHO THUÊ VĂN PHÒNG", "Phối hợp Sàn DMT Land soạn thảo hợp đồng, làm việc môi giới", "Quý I/2026"),
    ("CÔNG TÁC LIÊN PHÒNG BAN VÀ PHỐI HỢP PHÁP LÝ", "Chủ động công việc liên phòng ban, tham vấn yêu cầu pháp lý", "Định kỳ")
]

for proj, name, dl in hcns_tasks:
    add_target("HCNS", proj, name, dl)

# 1. ĐỐI VỚI CÔNG TÁC GIẢI PHÓNG MẶT BẰNG (Ban ĐBGT -> "CBĐT" or "KHĐT" let's use "KHĐT")
# Let's map "Ban Đền Bù Giải Tỏa" to KHĐT for now.
gpmb_tasks = [
    ("Khu TĐC Phước Lý 2", "Tiếp tục theo dõi các hồ sơ còn lại, lập kế hoạch khi có vốn", "2026", 11499.8),
    ("Khu Đô Thị Phước Lý", "Theo dõi, rà soát hồ sơ các hộ chưa nhận tiền", "2026", 0),
    ("Khu Dân Cư Bàu Mạc", "Giải phóng mặt bằng phần còn lại (1 hồ sơ)", "Quý I/2026", 181.0),
    ("Khu Dân Cư Nam Bàu Mạc", "Hoàn thành GPMB, xử lý công tác thi công", "2026", 685.0),
    ("Khu TĐC Hòa Liên 5", "Chuẩn bị hồ sơ nghiệm thu và bàn giao (Dự án tạm dừng thi công)", "2026", 5357.8),
    ("KDC Phong Nam", "Tiếp tục triển khai công tác ĐBGT sau khi hoàn thiện tính pháp lý", "2026", 75589.0),
    ("Khu biệt thự sinh thái Hòa Ninh", "Phối hợp VPĐK ĐĐ, theo dõi thanh tra TNMT, giải quyết hồ sơ Thanh Nhung, Bình Linh, Tiếu Thu", "Quý I+II/2026", 105000.0),
    ("Khu biệt thự sinh thái Hòa Ninh", "Tiếp tục phối hợp xử lý hồ sơ ông Ngọ, thương lượng ông Hưng", "Quý III+IV/2026", 0),
    ("Trục 1 Tây Bắc (Giai đoạn 2)", "Hoàn thành công tác GPMB, phối hợp đơn vị thi công", "2026", 8190.8),
    ("Tuyến đường Lê Trọng Tấn nối dài", "Giải phóng mặt bằng 80 hồ sơ còn lại", "Quý I-III/2026", 74987.8),
    ("Trạm nghiền Hòa Nhơn", "Quản lý, theo dõi phần diện tích đã GPMB", "2026", 0)
]

for proj, name, dl, budget in gpmb_tasks:
    # budget is area in m2, let's just use it as arbitrary number or 0
    add_target("CBĐT", proj, "GPMB: " + name, dl, budget / 1000.0) # convert m2 to simple value or just use as plan

# 2. KẾ HOẠCH ĐẦU TƯ XÂY DỰNG CÔNG TRÌNH HẠ TẦNG KỸ THUẬT (Ban KT)
kt_tasks = [
    ("Khu dân cư Bàu Mạc", "Thi công SN, GT, TN, Cấp điện, Cấp nước, Cây xanh (Khớp nối Nguyễn An Ninh)", "2026", 4.75),
    ("Khu DC Nam Bàu Mạc", "Thi công SN, GT, TN, Cấp điện & DCS, Cấp nước, Cây xanh", "2026", 6.56),
    ("Khu TĐC Hòa Liên 5", "Bàn giao công trình", "2026", 0),
    ("Tuyến đường Trần Hưng Đạo", "Bàn giao công trình", "2026", 0),
    ("Trục 1 Tây Bắc (Đoạn 1)", "Hạng mục cấp nước (KL còn lại)", "2026", 0.38),
    ("Trục 1 Tây Bắc (Đoạn 2)", "Thi công hạ tầng (Đã điều chỉnh GTHĐ)", "2026", 39.07),
    ("Tuyến đường Lê Trọng Tấn", "Thi công ĐCS, di dời điện, Cấp nước, CX, GT, TN", "2026", 22.42),
    ("Khu TĐC Hoà Vang", "Thi công SN, GT, TN, Cấp nước, Thoát nước thải, cấp quyền KT", "2026", 25.53)
]

for proj, name, dl, budget in kt_tasks:
    add_target("KT", proj, name, dl, budget)

# 3. CÔNG TÁC KẾ HOẠCH ĐẦU TƯ TRONG NĂM 2026 (Ban KHĐT)
khdt_tasks = [
    ("Khu TĐC Phước Lý 2", "HĐ với đvị quan trắc định kỳ năm 2026", "Quý I/2026"),
    ("Khu TĐC Phước Lý 2", "Báo cáo quan trắc định kỳ", "Theo quy định"),
    ("Khu TĐC Phước Lý 2", "Chủ trương dừng thi công dự án, bổ sung HM: Đường dây 110kV vào DA ĐTXD", "Quý I/2026"),
    ("Khu TĐC Phước Lý 2", "Điều chỉnh dự án ĐTXD", "Quý II/2026"),
    ("Khu TĐC Phước Lý 2", "Điều chỉnh Giấy CNĐKĐT", "Quý III/2026"),
    ("Khu TĐC Phước Lý 2", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "2026"),
    ("Khu đô thị Phước Lý", "Thủ tục cấp Giấy CNQSDĐ đợt 19: 06 lô", "2026"),
    ("KDC Phước Lý MR", "Xác định nghĩa vụ tài chính và kết thúc dự án", "2026"),
    ("KDC Quang Thành 3B và Lô A1.1", "Thực hiện các thủ tục để cấp Giấy CNQSDĐ cho Cty Bạch Hải", "Tháng 01/2026"),
    ("Tuyến đường Lê Trọng Tấn nối dài", "Phụ lục hợp đồng BT, Thủ tục để t/toán BT", "2026"),
    ("Khu TĐC Hòa Hiệp 4", "Kế hoạch vốn 2026 để t/toán BT, Thủ tục kết thúc dự án", "2026"),
    ("KDC Bàu Mạc", "Hoàn thành thủ tục đ/c các QĐ giao đất (đo đạc, cấp GCNQSDĐ các lô còn lại)", "Quý II/2026"),
    ("KDC Bàu Mạc", "Hồ sơ Báo cáo nghiên cứu khả thi, Hồ sơ TKBVTC", "Quý II/2026"),
    ("KDC Bàu Mạc", "Hoàn thiện thủ tục GPXD", "Quý III/2026"),
    ("KDC Nam Bàu Mạc", "Chấp thuận cho phép chuyển quyền sử dụng đất cho người dân tự xây dựng", "Quý I/2026"),
    ("Khu đô thị Phong Nam", "Liên quan đến các thủ tục điều chỉnh chủ trương đầu tư và công nhận nhà đầu tư", "2026"),
    ("Đường Trần Hưng Đạo", "Hoàn thiện các thủ tục liên quan để quyết toán, thanh toán", "2026"),
    ("Khu BT sinh thái Hòa Ninh", "Đưa dự án Khu nhà ở Hoà Ninh GĐ 1 vào dự án thí điểm về nhà ở thương mại", "Quý I/2026"),
    ("CCN Thanh Vinh mở rộng", "Thu phí sử dụng hạ tầng năm 2026 và công nợ của các doanh nghiệp", "Năm 2026"),
    ("Khách sạn DMT-GROUP", "Giấy phép xây dựng, Hợp đồng thi công, Triển khai thi công", "2026")
]

for proj, name, dl in khdt_tasks:
    add_target("KHĐT", proj, name, dl)

# 4. KẾ HOẠCH KINH DOANH NĂM 2026 CỦA SÀN BĐS (Ban KD)
kd_tasks = [
    ("KDC Nam Bàu Mạc", "Tiếp nhận và bàn giao đất cho khách hàng mua đất", "2026", 350.0),
    ("Căn hộ khách sạn DMT Group", "Thực hiện kế hoạch bán hàng theo dự kiến", "2026", 100.0),
    ("Tòa nhà văn phòng DMT", "Tiếp tục triển khai kế hoạch cho thuê tầng 4 và tầng 6", "2026", 0)
]

for proj, name, dl, budget in kd_tasks:
    add_target("KD", proj, name, dl, budget) # budget here acts as target revenue

# 5. CHỈ TIÊU KINH TẾ TÀI CHÍNH (Ban KTTC)
kttc_tasks = [
    ("Hoạt động Tài chính Kế toán", "Báo cáo tài chính, quyết toán thuế năm 2025 đúng tiến độ", "2026"),
    ("Hoạt động Tài chính Kế toán", "Quyết toán vốn đầu tư các dự án hoàn thành và dự án BT", "2026"),
    ("Hoạt động Tài chính Kế toán", "Kế hoạch vốn vay, giải ngân, bảo lãnh đáp ứng nhu cầu vốn", "2026"),
    ("Hoạt động Tài chính Kế toán", "Thu hồi công nợ kịp thời (SCD, phí hạ tầng, thuê văn phòng)", "2026"),
    ("Chỉ tiêu Tài chính DMT", "Tổng doanh thu kế hoạch: 413,8 Tỷ", "2026", 413.8),
    ("Chỉ tiêu Tài chính DMT-CIENCO", "Tổng doanh thu kế hoạch: 136,22 Tỷ", "2026", 136.22),
    ("Chỉ tiêu Tài chính MARINA", "Doanh thu dự kiến: 18,28 Tỷ", "2026", 18.28)
]

for proj, name, dl, *budget in kttc_tasks:
    b = budget[0] if budget else 0
    add_target("KTTC", proj, name, dl, b)

# 8. XÍ NGHIỆP DUY TU BẢO DƯỠNG (Ban Xí Nghiệp / Bảo dưỡng -> "XNDT" or "KT")
# Let's map to KT for now
xd_tasks = [
    ("Toà Nhà DMT", "Kiểm tra hệ thống thang máy, điện năng lượng mặt trời, điều hòa", "Thường xuyên"),
    ("Đội PCCC", "Lắp đặt hệ thống truyền tin về phòng CS PCCC Thành phố", "Tháng 2/2026"),
    ("Dự án do DMT làm chủ đầu tư", "Kiểm tra, báo cáo đề xuất sửa chữa các hư hỏng, cắt tỉa cây xanh", "Thường xuyên"),
    ("Đội Phòng chống bão lụt", "Cập nhật tình hình dự báo thời tiết lên phương án phòng chống bão lụt", "Thường xuyên")
]

for proj, name, dl in xd_tasks:
    add_target("KT", proj, name, dl)

with open("project_targets.json", "w", encoding="utf-8") as f:
    json.dump(targets, f, ensure_ascii=False, indent=2)

print("Saved project_targets_full.json successfully!")
