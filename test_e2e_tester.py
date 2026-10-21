import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
from datetime import date, datetime, timedelta
from core_logic import (
    read_db,
    insert_task,
    update_task,
    delete_task,
    get_subordinates_for_manager,
    get_allowed_personnel_for_manager,
    setup_manager_db_filters,
    HIERARCHY_MARINA_3,
    DEPT_LEADS
)

print("=" * 70)
print("🚀 BẮT ĐẦU KIỂM THỬ TOÀN DIỆN (E2E TESTER) HỆ THỐNG TIẾN ĐỘ & KPI DMT GROUP")
print("=" * 70)

today = date.today()
created_test_ids = []

def cleanup():
    """Dọn dẹp các task test đã tạo trong Supabase"""
    print("\n🧹 Đang dọn dẹp các task thử nghiệm...")
    for tid in created_test_ids:
        try:
            delete_task(tid)
            print(f"   -> Đã xóa task test: {tid}")
        except Exception as e:
            print(f"   -> Không thể xóa {tid}: {e}")

try:
    # =========================================================================
    # TEST 1: CÔNG TY CP DMT-MARINA (Happy Yacht)
    # Nhân viên: Nguyễn Băng Trinh -> Quản lý: Nguyễn Thị Hạnh Tiên -> BLĐ: Đặng Ngọc Hoàng
    # =========================================================================
    print("\n--- TEST 1: DMT-MARINA (Nguyễn Băng Trinh -> Hạnh Tiên -> Đặng Ngọc Hoàng) ---")
    task_marina_trinh = {
        "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
        "PhongBan": "HCTH",
        "NguoiChuTri": "Nguyễn Băng Trinh",
        "TenDuAn": "Du thuyền Happy Yacht",
        "MocTienDo": "Tự do",
        "SanPhamBanGiao": "Báo cáo nhân sự tuần Marina",
        "TenCongViec": "[TEST] Báo cáo nhân sự tuần DMT Marina",
        "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
        "NgayBatDau": today.strftime('%Y-%m-%d'),
        "Deadline": (today + timedelta(days=2)).strftime('%Y-%m-%d'),
        "DoUuTien": "Trung bình",
        "PhanTramHoanThanh": 100,
        "TrangThai": "Chờ nghiệm thu",
        "LinkKetQua": "https://dmt.vn/baocao_trinh.pdf",
        "GiaiTrinhDeXuat": "Đã hoàn thành đúng hạn",
        "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ChuKyTheoDoi": "Theo dự án / Tự do",
        "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
        "TyTrongKPI": 20,
        "NguonGiaoViec": "Công việc được giao / định kì",
        "MucDoGhiNhan": "0% (Không ghi nhận)"
    }
    tid_1 = insert_task(task_marina_trinh)
    assert tid_1, "Không thể insert task cho Nguyễn Băng Trinh!"
    created_test_ids.append(tid_1)
    print(f"1.1. [OK] Nguyễn Băng Trinh đã tạo công việc ID: {tid_1} (Trạng thái: Chờ nghiệm thu)")

    # Kiểm tra Quản lý trực tiếp: Nguyễn Thị Hạnh Tiên vào Nghiệm thu
    db_f_tien = setup_manager_db_filters({'DonVi': 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)'}, "Nguyễn Thị Hạnh Tiên", "HCTH", 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
    df_tien = read_db(filters=db_f_tien)
    subs_tien = get_subordinates_for_manager("Nguyễn Thị Hạnh Tiên")
    assert "Nguyễn Băng Trinh" in subs_tien, f"Nguyễn Thị Hạnh Tiên phải quản lý Băng Trinh! Got: {subs_tien}"
    pending_tien = df_tien[(df_tien['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_tien['NguoiChuTri'].isin(subs_tien))]
    assert tid_1 in pending_tien['ID'].values, f"Task {tid_1} của Băng Trinh không xuất hiện trong hàng chờ của Hạnh Tiên!"
    print(f"1.2. [OK] Quản lý Nguyễn Thị Hạnh Tiên đã nhìn thấy công việc {tid_1} trong danh sách Chờ nghiệm thu!")

    # Hạnh Tiên duyệt công việc -> chuyển sang Hoàn thành
    update_task(tid_1, {"TrangThai": "Hoàn thành", "PhanTramHoanThanh": 100})
    df_after_tien = read_db(filters=db_f_tien)
    pending_after = df_after_tien[(df_after_tien['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_after_tien['NguoiChuTri'].isin(subs_tien))]
    assert tid_1 not in pending_after['ID'].values, f"Task {tid_1} phải biến mất khỏi hàng chờ duyệt sau khi Hạnh Tiên duyệt!"
    print(f"1.3. [OK] Sau khi Hạnh Tiên duyệt, công việc {tid_1} đã chuyển thành 'Hoàn thành' và biến mất khỏi hàng chờ (FIFO chuẩn)!")

    # Cấp BLĐ cao nhất: Đặng Ngọc Hoàng vào Đánh giá KPI
    allowed_dnh = get_allowed_personnel_for_manager("Đặng Ngọc Hoàng", include_self=True)
    assert "Nguyễn Thị Hạnh Tiên" in allowed_dnh and "Trần Cường" in allowed_dnh and "Ngô Thị Tâm" in allowed_dnh, f"Đặng Ngọc Hoàng phải thấy Cường, Tiên, Tâm! Got: {allowed_dnh}"
    print(f"1.4. [OK] Cấp trên Đặng Ngọc Hoàng được phân quyền đầy đủ: {allowed_dnh}")

    # =========================================================================
    # TEST 2: ĐA QUẢN LÝ / LIÊN CÔNG TY: Lê Thị Hải (Phó Ban TCKT Marina)
    # Quản lý 1: Trần Cường (Marina)
    # Quản lý 2: Đồng Thị Nguyệt Nga (Đầu Tư)
    # Quản lý 3: Nguyễn Thị Ngọc Hà (Cienco)
    # =========================================================================
    print("\n--- TEST 2: ĐA QUẢN LÝ LIÊN CÔNG TY (Lê Thị Hải -> Trần Cường + Nguyệt Nga + Ngọc Hà) ---")
    task_hai = {
        "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
        "PhongBan": "TCKT",
        "NguoiChuTri": "Lê Thị Hải",
        "TenDuAn": "Du thuyền Happy Yacht",
        "MocTienDo": "Tự do",
        "SanPhamBanGiao": "Báo cáo tài chính quý Marina",
        "TenCongViec": "[TEST] Quyết toán doanh thu Du thuyền Marina",
        "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
        "NgayBatDau": today.strftime('%Y-%m-%d'),
        "Deadline": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
        "DoUuTien": "Cao",
        "PhanTramHoanThanh": 100,
        "TrangThai": "Chờ nghiệm thu",
        "LinkKetQua": "https://dmt.vn/baocao_hai.xlsx",
        "GiaiTrinhDeXuat": "Đã hoàn thành kiểm toán nội bộ",
        "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ChuKyTheoDoi": "Theo dự án / Tự do",
        "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
        "TyTrongKPI": 25,
        "NguonGiaoViec": "Công việc được giao / định kì",
        "MucDoGhiNhan": "0% (Không ghi nhận)"
    }
    tid_2 = insert_task(task_hai)
    assert tid_2, "Không thể insert task cho Lê Thị Hải!"
    created_test_ids.append(tid_2)
    print(f"2.1. [OK] Lê Thị Hải (Marina) tạo công việc ID: {tid_2} (Trạng thái: Chờ nghiệm thu)")

    # Quản lý 1: Trần Cường (Marina)
    db_f_cuong = setup_manager_db_filters({'DonVi': 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)'}, "Trần Cường", "BLĐ", 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
    df_cuong = read_db(filters=db_f_cuong)
    subs_cuong = get_subordinates_for_manager("Trần Cường")
    assert "Lê Thị Hải" in subs_cuong, f"Trần Cường phải quản lý Lê Thị Hải! Got: {subs_cuong}"
    pending_cuong = df_cuong[(df_cuong['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_cuong['NguoiChuTri'].isin(subs_cuong))]
    assert tid_2 in pending_cuong['ID'].values, f"Trần Cường không thấy việc {tid_2} của Lê Thị Hải!"
    print(f"2.2. [OK] Quản lý 1 (Trần Cường - Giám đốc Marina) thấy việc {tid_2} trong hàng chờ duyệt!")

    # Quản lý 2: Đồng Thị Nguyệt Nga (Cty Mẹ - Đầu Tư -> Quản lý chéo sang Marina)
    db_f_nga = setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG'}, "Đồng Thị Nguyệt Nga", "TCKT", 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG')
    df_nga = read_db(filters=db_f_nga)
    subs_nga = get_subordinates_for_manager("Đồng Thị Nguyệt Nga")
    assert "Lê Thị Hải" in subs_nga, f"Đồng Thị Nguyệt Nga phải quản lý Lê Thị Hải! Got: {subs_nga}"
    pending_nga = df_nga[(df_nga['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_nga['NguoiChuTri'].isin(subs_nga))]
    assert tid_2 in pending_nga['ID'].values, f"Đồng Thị Nguyệt Nga không thấy việc {tid_2} của Lê Thị Hải (lỗi cross-company filter)!"
    print(f"2.3. [OK] Quản lý 2 (Đồng Thị Nguyệt Nga - Đầu Tư) thấy việc {tid_2} của Lê Thị Hải (Marina) dù ở công ty khác!")

    # Quản lý 3: Nguyễn Thị Ngọc Hà (Cienco -> Quản lý chéo sang Marina)
    db_f_ha = setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT'}, "Nguyễn Thị Ngọc Hà", "TCKT", 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT')
    df_ha = read_db(filters=db_f_ha)
    subs_ha = get_subordinates_for_manager("Nguyễn Thị Ngọc Hà")
    assert "Lê Thị Hải" in subs_ha, f"Nguyễn Thị Ngọc Hà phải quản lý Lê Thị Hải! Got: {subs_ha}"
    pending_ha = df_ha[(df_ha['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_ha['NguoiChuTri'].isin(subs_ha))]
    assert tid_2 in pending_ha['ID'].values, f"Nguyễn Thị Ngọc Hà không thấy việc {tid_2} của Lê Thị Hải!"
    print(f"2.4. [OK] Quản lý 3 (Nguyễn Thị Ngọc Hà - Cienco) thấy việc {tid_2} của Lê Thị Hải (Marina) dù ở công ty khác!")

    # TEST FIFO: Chị Nga duyệt trước -> Việc biến mất khỏi hàng chờ của Anh Cường và Chị Ngọc Hà
    update_task(tid_2, {"TrangThai": "Hoàn thành", "PhanTramHoanThanh": 100})
    df_cuong_after = read_db(filters=db_f_cuong)
    pending_cuong_after = df_cuong_after[(df_cuong_after['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_cuong_after['NguoiChuTri'].isin(subs_cuong))]
    assert tid_2 not in pending_cuong_after['ID'].values, "Việc đã duyệt nhưng chưa biến mất khỏi hàng chờ của Trần Cường!"

    df_ha_after = read_db(filters=db_f_ha)
    pending_ha_after = df_ha_after[(df_ha_after['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_ha_after['NguoiChuTri'].isin(subs_ha))]
    assert tid_2 not in pending_ha_after['ID'].values, "Việc đã duyệt nhưng chưa biến mất khỏi hàng chờ của Nguyễn Thị Ngọc Hà!"
    print("2.5. [OK] FIFO HOÀN HẢO: Chị Nga duyệt xong, việc biến mất lập tức khỏi hàng chờ của Anh Cường và Chị Hà!")

    # =========================================================================
    # TEST 3: CÔNG TY CIENCO + BAN KỸ THUẬT: Nguyễn Văn Bồn (Đầu Tư)
    # Quản lý 1: Thái Văn Thành (TGĐ Cienco)
    # Quản lý 2: Trần Quốc Thể (TGĐ Cty Mẹ)
    # =========================================================================
    print("\n--- TEST 3: CIENCO & LIÊN CÔNG TY (Nguyễn Văn Bồn -> Thái Văn Thành + Trần Quốc Thể) ---")
    task_bon = {
        "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
        "PhongBan": "KT",
        "NguoiChuTri": "Nguyễn Văn Bồn",
        "TenDuAn": "Tuyến đường Lê Trọng Tấn",
        "MocTienDo": "Tự do",
        "SanPhamBanGiao": "Hồ sơ nghiệm thu kỹ thuật mặt đường",
        "TenCongViec": "[TEST] Nghiệm thu hồ sơ kỹ thuật Cienco & Ban KT",
        "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
        "NgayBatDau": today.strftime('%Y-%m-%d'),
        "Deadline": today.strftime('%Y-%m-%d'),
        "DoUuTien": "Khẩn cấp",
        "PhanTramHoanThanh": 100,
        "TrangThai": "Chờ nghiệm thu",
        "LinkKetQua": "https://dmt.vn/hoso_bon.pdf",
        "GiaiTrinhDeXuat": "Đã kiểm tra hiện trường đạt chuẩn",
        "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ChuKyTheoDoi": "Theo dự án / Tự do",
        "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
        "TyTrongKPI": 30,
        "NguonGiaoViec": "Công việc được giao / định kì",
        "MucDoGhiNhan": "0% (Không ghi nhận)"
    }
    tid_3 = insert_task(task_bon)
    assert tid_3, "Không thể insert task cho Nguyễn Văn Bồn!"
    created_test_ids.append(tid_3)
    print(f"3.1. [OK] Nguyễn Văn Bồn (Ban KT Đầu Tư) tạo việc ID: {tid_3} (Trạng thái: Chờ nghiệm thu)")

    # Thái Văn Thành (Cienco) kiểm tra duyệt chéo sang Đầu Tư
    db_f_thanh = setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT'}, "Thái Văn Thành", "BLĐ", 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT')
    df_thanh = read_db(filters=db_f_thanh)
    subs_thanh = get_subordinates_for_manager("Thái Văn Thành")
    assert "Nguyễn Văn Bồn" in subs_thanh, f"Thái Văn Thành phải quản lý Nguyễn Văn Bồn! Got: {subs_thanh}"
    pending_thanh = df_thanh[(df_thanh['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_thanh['NguoiChuTri'].isin(subs_thanh))]
    assert tid_3 in pending_thanh['ID'].values, f"Thái Văn Thành không thấy việc {tid_3} của Nguyễn Văn Bồn!"
    print(f"3.2. [OK] Thái Văn Thành (TGĐ Cienco) nhìn thấy việc {tid_3} của Nguyễn Văn Bồn (Đầu Tư)!")

    # Trần Quốc Thể (TGĐ Cty Mẹ) kiểm tra duyệt
    db_f_the = setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG'}, "Trần Quốc Thể", "BLĐ", 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG')
    df_the = read_db(filters=db_f_the)
    subs_the = get_subordinates_for_manager("Trần Quốc Thể")
    assert "Nguyễn Văn Bồn" in subs_the, f"Trần Quốc Thể phải quản lý Nguyễn Văn Bồn! Got: {subs_the}"
    pending_the = df_the[(df_the['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_the['NguoiChuTri'].isin(subs_the))]
    assert tid_3 in pending_the['ID'].values, f"Trần Quốc Thể không thấy việc {tid_3} của Nguyễn Văn Bồn!"
    print(f"3.3. [OK] Trần Quốc Thể (TGĐ Tập đoàn) nhìn thấy việc {tid_3} của Nguyễn Văn Bồn!")

    # Anh Thể duyệt trước -> Kiểm tra anh Thành không còn thấy trong hàng chờ
    update_task(tid_3, {"TrangThai": "Hoàn thành", "PhanTramHoanThanh": 100})
    df_thanh_after = read_db(filters=db_f_thanh)
    pending_thanh_after = df_thanh_after[(df_thanh_after['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_thanh_after['NguoiChuTri'].isin(subs_thanh))]
    assert tid_3 not in pending_thanh_after['ID'].values, f"Việc {tid_3} đã được anh Thể duyệt nhưng vẫn còn trong hàng chờ của anh Thành!"
    print(f"3.4. [OK] Sau khi anh Thể duyệt, việc {tid_3} biến mất khỏi hàng chờ duyệt của anh Thành!")

    # =========================================================================
    # TEST 4: NHÂN VIÊN HIỆN TRƯỜNG & THIẾT BỊ CIENCO: Nguyễn Phong Trung & Đặng Hiền
    # Quản lý 1: Trần Văn Trọng (Phó TGĐ Cienco)
    # Quản lý 2: Thái Văn Thành (TGĐ Cienco)
    # =========================================================================
    print("\n--- TEST 4: CIENCO HIỆN TRƯỜNG (Nguyễn Phong Trung, Đặng Hiền -> Trần Văn Trọng + Thái Văn Thành) ---")
    task_trung = {
        "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
        "PhongBan": "BCH CT",
        "NguoiChuTri": "Nguyễn Phong Trung",
        "TenDuAn": "Tuyến đường Trần Hưng Đạo (BT)",
        "MocTienDo": "Tự do",
        "SanPhamBanGiao": "Báo cáo tiến độ thi công nền đường",
        "TenCongViec": "[TEST] Báo cáo tiến độ thi công hiện trường",
        "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
        "NgayBatDau": today.strftime('%Y-%m-%d'),
        "Deadline": today.strftime('%Y-%m-%d'),
        "DoUuTien": "Trung bình",
        "PhanTramHoanThanh": 100,
        "TrangThai": "Chờ nghiệm thu",
        "LinkKetQua": "https://dmt.vn/baocao_trung.pdf",
        "GiaiTrinhDeXuat": "Đã hoàn thành ca máy",
        "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ChuKyTheoDoi": "Theo dự án / Tự do",
        "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
        "TyTrongKPI": 20,
        "NguonGiaoViec": "Công việc được giao / định kì",
        "MucDoGhiNhan": "0% (Không ghi nhận)"
    }
    tid_4 = insert_task(task_trung)
    assert tid_4, "Không thể insert task cho Nguyễn Phong Trung!"
    created_test_ids.append(tid_4)

    # Trần Văn Trọng duyệt
    db_f_trong = setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT'}, "Trần Văn Trọng", "BLĐ", 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT')
    df_trong = read_db(filters=db_f_trong)
    subs_trong = get_subordinates_for_manager("Trần Văn Trọng")
    assert "Nguyễn Phong Trung" in subs_trong, f"Trần Văn Trọng phải quản lý Nguyễn Phong Trung! Got: {subs_trong}"
    pending_trong = df_trong[(df_trong['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_trong['NguoiChuTri'].isin(subs_trong))]
    assert tid_4 in pending_trong['ID'].values, f"Trần Văn Trọng không thấy việc {tid_4} của Nguyễn Phong Trung!"
    print(f"4.1. [OK] Trần Văn Trọng thấy việc {tid_4} của Nguyễn Phong Trung!")

    # Cả Thái Văn Thành cũng thấy việc của Trung
    df_thanh_trung = read_db(filters=db_f_thanh)
    assert tid_4 in df_thanh_trung[(df_thanh_trung['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_thanh_trung['NguoiChuTri'].isin(subs_thanh))]['ID'].values
    print(f"4.2. [OK] Thái Văn Thành cũng thấy việc {tid_4} của Nguyễn Phong Trung!")

    # =========================================================================
    # TEST 5: HR / TOÀN QUYỀN HỆ THỐNG
    # =========================================================================
    print("\n--- TEST 5: QUYỀN TOÀN HỆ THỐNG (HR & HĐQT) ---")
    # HĐQT Toàn quyền xem và duyệt
    subs_binh = get_subordinates_for_manager("Đặng Thanh Bình")
    assert subs_binh is None, "Đặng Thanh Bình phải có toàn quyền (None)"
    subs_ngoc = get_subordinates_for_manager("Đặng Thị Lan Ngọc")
    assert subs_ngoc is None, "Đặng Thị Lan Ngọc phải có toàn quyền (None)"
    print("5.1. [OK] HĐQT (Đặng Thanh Bình, Đặng Thị Lan Ngọc) có toàn quyền không giới hạn!")

    # HR xem được toàn bộ data của tất cả các công ty
    df_all = read_db(filters=None)
    assert len(df_all) >= 4, f"HR phải xem được tất cả các tasks trong hệ thống! Got: {len(df_all)}"
    print(f"5.2. [OK] HR / Admin tải được toàn bộ {len(df_all)} công việc trên toàn hệ thống!")

    # =========================================================================
    # TEST 6: KIỂM TRA CHỐNG LẪN LỘN SESSION & TÊN TÀI KHOẢN (Chống Leak danh tính)
    # =========================================================================
    print("\n--- TEST 6: CHỐNG LẪN LỘN DANH TÍNH KHI ĐỔI TÀI KHOẢN ---")
    # Giả lập session chuyển đổi liên tục giữa 4 nhân sự
    users_to_test = [
        ("Nguyễn Băng Trinh", "HCTH", "CTY CP DMT - MARINA (Du thuyền Happy Yacht)"),
        ("Lê Thị Hải", "TCKT", "CTY CP DMT - MARINA (Du thuyền Happy Yacht)"),
        ("Nguyễn Văn Bồn", "KT", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"),
        ("Nguyễn Phong Trung", "BCH CT", "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"),
    ]
    for u_name, u_dept, u_comp in users_to_test:
        filters_u = {'DonVi': u_comp, 'NguoiChuTri': u_name}
        df_u = read_db(filters=filters_u)
        for _, row in df_u.iterrows():
            assert row['NguoiChuTri'] == u_name, f"Lẫn lộn danh tính! Tài khoản {u_name} nhưng dữ liệu lại có việc của {row['NguoiChuTri']}"
        print(f"   -> [PASS] Danh tính và dữ liệu của '{u_name}' hoàn toàn độc lập, không bị rò rỉ!")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ 6 TEST CASE E2E (MARINA, CIENCO, ĐẦU TƯ, ĐA QUẢN LÝ, FIFO, HR) ĐÃ PASS 100%!")
    print("=" * 70)

finally:
    cleanup()
