import sys, json, uuid
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, date
from core_logic import get_gsheets_conn, insert_task

TASKS_TO_SEED = [
    # --- DMT GROUP ---
    # HCNS
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "HCNS",
        "NguoiChuTri": "Nguyễn Thị Hạnh Tiên",
        "TenDuAn": "Hệ thống KPI - DMT GROUP",
        "SanPhamBanGiao": "Rà soát lại nhân sự, tham mưu định hướng công tác nhân sự",
        "TenCongViec": "Xây dựng định biên nhân sự và rà soát phương án điều chỉnh quy chế đánh giá KPI",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 60
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "HCNS",
        "NguoiChuTri": "Nguyễn Băng Trinh",
        "TenDuAn": "Lương, Chấm công & BHXH",
        "SanPhamBanGiao": "Tiền lương & Chấm công: Chấm công, tính lương, thưởng và phụ cấp đúng kỳ hạn hàng tháng",
        "TenCongViec": "Chấm công, tính lương và trích nộp BHXH tháng 10/2026 cho toàn thể CBCNV",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-30",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 70
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "HCNS",
        "NguoiChuTri": "Lê Ngọc Tú Uyên",
        "TenDuAn": "Hành chính – Văn thư & Văn phòng",
        "SanPhamBanGiao": "Quản lý văn bản, con dấu và phần mềm DMT E-Office chính xác, kịp thời",
        "TenCongViec": "Tiếp nhận, số hóa văn bản đi - đến và kiểm soát con dấu trên hệ thống E-Office",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 65
    },
    # TCKT DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "TCKT",
        "NguoiChuTri": "Đồng Thị Nguyệt Nga",
        "TenDuAn": "Công tác Kế toán",
        "SanPhamBanGiao": "Khóa sổ & Báo cáo tài chính",
        "TenCongViec": "Kiểm soát và duyệt báo cáo cân đối tài chính, dòng tiền hoạt động Quý IV",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 55
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "TCKT",
        "NguoiChuTri": "Huỳnh Thị Hoàng Hà",
        "TenDuAn": "Công tác Kế toán",
        "SanPhamBanGiao": "Khai thuế & Báo cáo thuế định kỳ",
        "TenCongViec": "Lập báo cáo kê khai thuế GTGT, TNCN và đối chiếu sổ phụ ngân hàng tháng 10/2026",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-25",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 20,
        "PhanTramHoanThanh": 80
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "TCKT",
        "NguoiChuTri": "Lê Thị Hải",
        "TenDuAn": "Công nợ & Thanh toán",
        "SanPhamBanGiao": "Đối chiếu và thu hồi công nợ",
        "TenCongViec": "Rà soát công nợ phải thu, phải trả và đối chiếu hồ sơ thanh toán nhà thầu",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-30",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 20,
        "PhanTramHoanThanh": 50
    },
    # KHĐT DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "KHĐT",
        "NguoiChuTri": "Nguyễn Trần Thức",
        "TenDuAn": "KĐT Phong Nam",
        "SanPhamBanGiao": "Kế hoạch đầu tư và giám sát giải ngân",
        "TenCongViec": "Tổng hợp báo cáo tiến độ và kế hoạch giải ngân vốn các dự án đầu tư Quý IV",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 60
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "KHĐT",
        "NguoiChuTri": "Trần Tin",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Hồ sơ quy hoạch và phê duyệt điều chỉnh",
        "TenCongViec": "Hoàn thiện hồ sơ thẩm định điều chỉnh quy hoạch chi tiết 1/500 dự án KDC Bàu Mạc",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 20,
        "PhanTramHoanThanh": 50
    },
    # CBĐT DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "CBĐT",
        "NguoiChuTri": "Hồ Văn Khoa",
        "TenDuAn": "KĐT Phong Nam",
        "SanPhamBanGiao": "Phối hợp Ban KHĐT rà soát, hoàn thiện quy hoạch KĐT Phong Nam",
        "TenCongViec": "Chỉ đạo hoàn thiện thủ tục thẩm định Báo cáo nghiên cứu khả thi dự án KĐT Phong Nam",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 55
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "CBĐT",
        "NguoiChuTri": "Phan Thị Mỹ Hạnh",
        "TenDuAn": "KBT Sinh Thái Hòa Ninh",
        "SanPhamBanGiao": "Theo dõi các thông báo, kết luận của UBND TP",
        "TenCongViec": "Theo dõi văn bản thông báo kết luận của UBND TP liên quan đến dự án KBT Sinh Thái Hòa Ninh",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 20,
        "PhanTramHoanThanh": 45
    },
    # KT DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "KT",
        "NguoiChuTri": "Nguyễn Văn Bồn",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Thẩm tra thiết kế và bản vẽ thi công",
        "TenCongViec": "Thẩm tra hồ sơ thiết kế bản vẽ thi công và biện pháp thi công hạ tầng KDC Bàu Mạc",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 65
    },
    # ĐBGT DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "ĐBGT",
        "NguoiChuTri": "Đặng Công Nhựt",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Kiểm đếm và áp giá bồi thường GPMB",
        "TenCongViec": "Phối hợp Hội đồng GPMB kiểm đếm hiện trạng và áp giá đền bù dự án KDC Bàu Mạc",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 50
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "ĐBGT",
        "NguoiChuTri": "Đặng Thanh Quang",
        "TenDuAn": "KĐT Phong Nam",
        "SanPhamBanGiao": "Xác định rõ quy mô, diện tích đền bù Phong Nam",
        "TenCongViec": "Vận động các hộ dân nhận tiền bồi thường, bàn giao mặt bằng dự án KĐT Phong Nam",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 40
    },
    # Ban Dự án (DA) DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "DA",
        "NguoiChuTri": "Nguyễn Đình Thắng",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Kiểm tra chất lượng và tiến độ thi công hạ tầng",
        "TenCongViec": "Giám sát kỹ thuật và kiểm tra chất lượng thi công đường giao thông KDC Bàu Mạc",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 60
    },
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "DA",
        "NguoiChuTri": "Nguyễn Đình Hiếu",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Nghiệm thu khối lượng hoàn thành bàn giao",
        "TenCongViec": "Nghiệm thu cốt nền và hệ thống cấp thoát nước giai đoạn 1 dự án KDC Bàu Mạc",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 55
    },
    # XN DTBD DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "XN DTBD",
        "NguoiChuTri": "Mai Văn Châu",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Duy tu, bảo dưỡng hệ thống kỹ thuật",
        "TenCongViec": "Kiểm tra, bảo dưỡng định kỳ hệ thống chiếu sáng và nạo vét mương thoát nước KDC Bàu Mạc",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 70
    },
    # Sàn GDBĐS DMT
    {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "Sàn GDBĐS",
        "NguoiChuTri": "Ngô Thị Tâm",
        "TenDuAn": "KDC Bàu Mạc",
        "SanPhamBanGiao": "Kế hoạch kinh doanh và mở bán sản phẩm",
        "TenCongViec": "Lập kế hoạch truyền thông và tiếp thị phân khu đất nền dự án KDC Bàu Mạc",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 50
    },
    # --- DMT MARINA ---
    {
        "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
        "PhongBan": "BLĐ",
        "NguoiChuTri": "Trần Cường",
        "TenDuAn": "Du thuyền Happy Yacht",
        "SanPhamBanGiao": "Bảo dưỡng kỹ thuật và vận hành an toàn Du thuyền Happy Yacht",
        "TenCongViec": "Kiểm tra kỹ thuật máy móc, trang thiết bị an toàn và bảo dưỡng Du thuyền Happy Yacht định kỳ",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 65
    },
    # --- CIENCO ---
    # Cienco KT
    {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "KT",
        "NguoiChuTri": "Phạm Quang Nghĩa",
        "TenDuAn": "Tuyến đường Lê Trọng Tấn",
        "SanPhamBanGiao": "Hồ sơ nghiệm thu chất lượng công trình",
        "TenCongViec": "Lập hồ sơ quản lý chất lượng và nhật ký thi công dự án Tuyến đường Lê Trọng Tấn",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 60
    },
    {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "KT",
        "NguoiChuTri": "Ngô Văn Hoàng",
        "TenDuAn": "HTKT TĐC Hoà Liên 5",
        "SanPhamBanGiao": "Nghiệm thu kỹ thuật hiện trường",
        "TenCongViec": "Kiểm tra cao độ nền đường và nghiệm thu lớp cấp phối đá dăm công trình Hòa Liên 5",
        "NgayBatDau": "2026-10-05",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 55
    },
    # Cienco BCH CT
    {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "BCH CT",
        "NguoiChuTri": "Lê Đông",
        "TenDuAn": "Tuyến đường Lê Trọng Tấn",
        "SanPhamBanGiao": "Thi công thảm bê tông nhựa mặt đường",
        "TenCongViec": "Điều phối nhân lực và máy móc thi công thảm bê tông nhựa mặt đường Lê Trọng Tấn",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 65
    },
    # Cienco TCKT
    {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "TCKT",
        "NguoiChuTri": "Nguyễn Thị Ngọc Hà",
        "TenDuAn": "Tuyến đường Lê Trọng Tấn",
        "SanPhamBanGiao": "Quản lý dòng tiền và thanh toán công trường",
        "TenCongViec": "Cân đối dòng tiền phục vụ mua vật tư và thanh toán tiền máy thi công công trường",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 25,
        "PhanTramHoanThanh": 60
    },
    # Cienco Mỏ
    {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "Mỏ",
        "NguoiChuTri": "Lê Nho Tân",
        "TenDuAn": "Các nhiệm vụ khác",
        "SanPhamBanGiao": "Khai thác mỏ đá và cung ứng đá dăm thành phẩm",
        "TenCongViec": "Điều hành khai thác mỏ đá và cấp phối đá các loại phục vụ công trình giao thông",
        "NgayBatDau": "2026-10-01",
        "Deadline": "2026-10-31",
        "TrangThai": "Đang thực hiện",
        "TyTrongKPI": 30,
        "PhanTramHoanThanh": 70
    }
]

def seed_tasks():
    conn = get_gsheets_conn()
    if not conn:
        print("ERROR: Cannot connect to Supabase!")
        return

    # Check existing tasks in Supabase
    res = conn.table("tasks").select("NguoiChuTri, TenCongViec").execute()
    existing_pairs = set((r.get("NguoiChuTri", "").strip(), r.get("TenCongViec", "").strip()) for r in res.data)
    print(f"Current existing task count in Supabase: {len(res.data)}")

    added = 0
    for t in TASKS_TO_SEED:
        pair = (t["NguoiChuTri"].strip(), t["TenCongViec"].strip())
        if pair in existing_pairs:
            print(f"  Skipping existing task for {t['NguoiChuTri']}")
            continue

        task_id = f"TSK-{uuid.uuid4().hex[:8].upper()}"
        row = {
            "ID": task_id,
            "DonVi": t["DonVi"],
            "PhongBan": t["PhongBan"],
            "NguoiChuTri": t["NguoiChuTri"],
            "TenDuAn": t["TenDuAn"],
            "MocTienDo": "Tự do / Không gắn mục tiêu",
            "SanPhamBanGiao": t["SanPhamBanGiao"],
            "TenCongViec": t["TenCongViec"],
            "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
            "NgayBatDau": t["NgayBatDau"],
            "Deadline": t["Deadline"],
            "DoUuTien": "Trung bình",
            "PhanTramHoanThanh": t["PhanTramHoanThanh"],
            "TrangThai": t["TrangThai"],
            "LinkKetQua": "",
            "GiaiTrinhDeXuat": "",
            "NgayCapNhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ChuKyTheoDoi": "Theo dự án / Tự do",
            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
            "TyTrongKPI": t["TyTrongKPI"],
            "NguonGiaoViec": "Công việc được giao / định kì",
            "MucDoGhiNhan": "100% (Hoàn thành tốt)"
        }
        res_insert = conn.table("tasks").insert(row).execute()
        if res_insert.data:
            print(f"  + Added task for {t['NguoiChuTri']} ({t['PhongBan']}) - {t['TenCongViec'][:30]}...")
            added += 1

    print(f"\nSuccessfully seeded {added} baseline tasks into Supabase!")

if __name__ == "__main__":
    seed_tasks()
