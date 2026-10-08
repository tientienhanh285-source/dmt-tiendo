import json

plans = [
    ("KĐT Phước Lý", "Xử lý dứt điểm việc bàn giao đất hộ bà Thủy", "Tháng 10/2026"),
    ("KĐT Phước Lý", "Phối hợp ban KTXD tiến hành trồng cây xanh", "Tháng 11/2026"),
    ("Khu TĐC Phước Lý 2", "Phối hợp TTPTQĐ, UBND Phường An Khê xác nhận hạ tầng theo hiện trạng làm cơ sở để nghiệm thu và bàn giao", "Tháng 10/2026"),
    ("Dự án KDC Bàu Mạc", "Rà soát phần diện tích còn lại của KDC Bàu Mạc (trên 1200 m2) căn cứ trên tổng diện tích đất cần thu hồi để lập hồ sơ, hoàn tất việc ban hành quyết định giao đất của dự án", "Tháng 11/2026"),
    ("Dự án KDC Bàu Mạc", "Liên hệ TTPTQĐ để bàn giao 8,3 m2 đất cho TTPTQĐ quản lý", "Tháng 11/2026"),
    ("Dự án KDC Bàu Mạc", "Phối hợp, TTPTQĐ, gia đình bà Xoa, phòng công chứng Ngọc Yến làm hồ sơ hoàn tất thủ tục chuyển nhượng quyền SDĐ để bố trí TĐC cho hộ bà Hồng Xoa (HS62)", "Tháng 11/2026"),
    ("Dự án KDC Bàu Mạc", "Phối hợp ban KHĐT thực hiện các thủ tục có liên quan đến lô đất hộ ông Tâm, lưu ý số tiền chuyển mục đích 28m2 từ đất mương sau nhà thành đất ở do ông Tâm chi trả", "Tháng 11/2026"),
    ("Dự án KDC Bàu Mạc", "Liên quan đến HS 106 - Nguyễn Quỳnh Chi (phục vụ ĐCQH): tìm hồ sơ pháp lý, biên bản họp hộ bà Chi + bà Mỹ Phước về ý kiến giữ lại chỉnh trang, biên bản nhận tiền", "Tháng 11/2026"),
    ("Dự án KDC Bàu Mạc", "Phối hợp với ban KHĐT lập hồ sơ điều chỉnh quy hoạch theo quy định", "Tháng 12/2026"),
    ("Dự án KDC Bàu Mạc", "Liên hệ Trung tâm đo đạc tổ chức đo đạc thực tế tại hiện trường làm cơ sở hoàn thiện hồ sơ hoàn thiện việc giao đất đợt còn lại", "Tháng 12/2026"),
    ("KĐT Phong Nam", "Xác định rõ quy mô, diện tích ĐBGT, làm rõ diện tích thuộc phạm vi đã ĐBGT và phần diện tích còn lại, phần diện tích còn lại chủ yếu đất do Nhà nước quản lý, do đó yêu cầu anh Tôn rà soát lại tính pháp lý, đơn giá đền bù để tính toán lại phương án ĐBGT", "Tháng 10/2026"),
    ("KĐT Phong Nam", "Làm việc với TTPTQĐ, UBND Phường Hòa Xuân triển khai theo thông báo kết luận của Thành phố", "Tháng 12/2026"),
    ("KBT Sinh Thái Hòa Ninh", "Đối với GCNQSDĐ 13.330 m2: theo dõi kết quả trả lời của phòng kinh tế xã Bà Nà về kết luận Thanh tra", "Tháng 11/2026"),
    ("KBT Sinh Thái Hòa Ninh", "Đối với GCNQSDĐ 4.388 m2: theo dõi kết quả trả lời của phòng kinh tế xã Bà Nà về hạn mức chuyển đổi từ đất thổ cư sang đất ở", "Tháng 11/2026"),
    ("KBT Sinh Thái Hòa Ninh", "Đối với 5 lô mặt tiền DT 602: phối hợp làm việc với cơ quan Thuế, kế toán để hoàn tất việc nộp thuế", "Tháng 10/2026"),
    ("KBT Sinh Thái Hòa Ninh", "Thực hiện các công việc chăm sóc cây trồng vật nuôi tại dự án.", "Hằng tháng"),
    ("KBT Sinh Thái Hòa Ninh", "Cắm mốc, đề xuất phương án tường bảo vệ ranh giới dự án.", "Tháng 10/2026"),
    ("Tuyến đường Lê Trọng Tấn – Hoàng Văn Thái", "Tiếp tục phối hợp TTPTQĐ CN KV5 vận động các hộ BGMB và phối hợp đơn vị thi công triển khai thi công", "Tháng 12/2026"),
    ("Tuyến đường Lê Trọng Tấn – Hoàng Văn Thái", "Phối hợp TTPTQĐ xử lý việc số tiền đã chi trả đền bù để di dời mộ gia đình ông Mai Thanh và Nguyễn Đình Hùng", "Tháng 12/2026"),
    ("Khu đất 5ha (gần trạm bê tông nhựa)", "Phối hợp quản lý hiện trạng", "Hằng tháng"),
    ("Khu đất 5ha (gần trạm bê tông nhựa)", "Đưa ra phương án trồng keo", "Tháng 11/2026"),
    ("CÁC DỰ ÁN BT", "Phối hợp xử lý theo các văn bản chỉ đạo của UBND TP", "Tháng 12/2026"),
    ("Công tác Công đoàn", "Phối hợp theo dõi, thực hiện các công tác chăm lo đời sống cho NLĐ", "Hằng tháng"),
    ("Công tác Công đoàn", "Hoàn thiện các thủ tục, hồ sơ khen thưởng", "Hằng tháng"),
    ("Công tác Công đoàn", "Quản lý, báo cáo công tác tài chính công đoàn", "Hằng tháng, BC cuối năm"),
    ("Công tác Đảng", "Thực hiện các nội dung sinh hoạt chi bộ hằng tháng", "Hằng tháng"),
    ("Công tác Đảng", "Tham gia các buổi họp, đào tạo các công tác Đảng", "Hằng tháng")
]

data = []
for i, (proj, target, dl) in enumerate(plans):
    data.append({
        "target_id": f"T{i+1:03d}",
        "project_name": proj,
        "department": "ĐBGT",
        "target_name": target,
        "deadline": dl,
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    })

with open("project_targets.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done")
