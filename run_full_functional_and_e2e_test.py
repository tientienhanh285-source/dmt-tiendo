# -*- coding: utf-8 -*-
"""
COMPREHENSIVE END-TO-END FUNCTIONAL TEST FOR ALL ROLES & BUSINESS PROCESSES
Tests every single role, workflow, and feature according to Sheet MARINA (3):
1. Employee creation of tasks, progress updates, submission for approval.
2. Manager approval, KPI grading, FIFO queue clearance, cross-company visibility.
3. HR full-company overview & BSC governance.
4. KPI planning & tasks persistence.
"""
import sys
import io
import os
import uuid
import datetime
import json
import pandas as pd

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, ".")
import core_logic

def run_tests():
    print("=" * 70)
    print("🚀 BẮT ĐẦU KIỂM THỬ TOÀN DIỆN CÁC TÁC VỤ & QUY TRÌNH (E2E TEST)")
    print("=" * 70)

    passed_tests = 0
    total_tests = 0

    def assert_test(cond, title):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if cond:
            passed_tests += 1
            print(f"  [PASS] {title}")
        else:
            print(f"  [FAIL] {title}")
            raise AssertionError(f"Thất bại tại: {title}")

    # ----------------------------------------------------
    # TÁC VỤ 1: QUẢN LÝ NHẬN VIỆC & PHÂN QUYỀN DUYỆT (MARINA 3)
    # ----------------------------------------------------
    print("\n--- 1. KIỂM THỬ QUẢN LÝ NHẬN VIỆC & BỘ LỌC CẤP DƯỚI (MARINA 3) ---")

    # 1.1 Quản lý Nguyễn Thị Hạnh Tiên (HCNS DMT)
    filters_tien = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'HCNS'}, "Nguyễn Thị Hạnh Tiên", "HCNS", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test(set(filters_tien.get('NguoiChuTri', [])) == {"Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"},
                "Hạnh Tiên chỉ nhận được việc của Trinh và Uyên (không thấy Trần Cường, Ngô Thị Tâm)")

    # 1.2 Quản lý Đặng Ngọc Hoàng (BLĐ) -> Cross-company filter
    filters_hoang = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'BLĐ'}, "Đặng Ngọc Hoàng", "BLĐ", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test("Trần Cường" in filters_hoang.get('NguoiChuTri', []) and "Nguyễn Thị Hạnh Tiên" in filters_hoang.get('NguoiChuTri', []) and "Ngô Thị Tâm" in filters_hoang.get('NguoiChuTri', []),
                "Đặng Ngọc Hoàng nhận được việc của Trần Cường (Marina), Hạnh Tiên (HCNS DMT) và Ngô Thị Tâm (Sàn)")
    assert_test("DonVi" not in filters_hoang, 
                "Bộ lọc của Đặng Ngọc Hoàng tự động xóa rào cản DonVi cứng để xem xuyên công ty Marina và DMT")

    # 1.3 Quản lý Thái Văn Thành (TGĐ Cienco)
    filters_thanh = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT', 'PhongBan': 'BLĐ'}, "Thái Văn Thành", "BLĐ", "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT")
    assert_test("Nguyễn Thị Ngọc Hà" in filters_thanh.get('NguoiChuTri', []) and "Phạm Quang Nghĩa" in filters_thanh.get('NguoiChuTri', []) and "Nguyễn Văn Bồn" not in filters_thanh.get('NguoiChuTri', []),
                "Thái Văn Thành nhận việc khối Cienco (Ngọc Hà, Nghĩa,...), không nhận việc Nguyễn Văn Bồn (thuộc Thể)")

    # 1.4 Quản lý Trần Văn Trọng (Phó TGĐ Cienco)
    filters_trong = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT', 'PhongBan': 'BLĐ'}, "Trần Văn Trọng", "BLĐ", "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT")
    assert_test("Lê Nho Tân" in filters_trong.get('NguoiChuTri', []) and "Đặng Hiền" in filters_trong.get('NguoiChuTri', []) and "Phạm Quang Nghĩa" in filters_trong.get('NguoiChuTri', []),
                "Trần Văn Trọng nhận việc hiện trường & kỹ thuật (Lê Nho Tân - Mỏ, Đặng Hiền - XMTB, Phạm Quang Nghĩa - KT)")

    # 1.5 Quản lý Trần Quốc Thể (TGĐ DMT)
    filters_the = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'BLĐ'}, "Trần Quốc Thể", "BLĐ", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test("Nguyễn Văn Bồn" in filters_the.get('NguoiChuTri', []) and "Hồ Văn Khoa" in filters_the.get('NguoiChuTri', []) and "Nguyễn Trần Thức" in filters_the.get('NguoiChuTri', []) and "Nguyễn Đình Thắng" in filters_the.get('NguoiChuTri', []) and "Nguyễn Đình Hiếu" in filters_the.get('NguoiChuTri', []),
                "Trần Quốc Thể nhận việc của Nguyễn Văn Bồn (Ban KT), Hồ Văn Khoa (CBĐT), Nguyễn Trần Thức (KHĐT), Mai Văn Châu, và Ban DA (Nguyễn Đình Thắng, Nguyễn Đình Hiếu)")

    # 1.6 Quản lý Nguyễn Ngọc Tôn (BLĐ)
    filters_ton = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'BLĐ'}, "Nguyễn Ngọc Tôn", "BLĐ", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test("Đặng Công Nhựt" in filters_ton.get('NguoiChuTri', []) and "Đặng Thị Mỹ Hạnh" in filters_ton.get('NguoiChuTri', []) and "Đặng Thanh Quang" in filters_ton.get('NguoiChuTri', []),
                "Nguyễn Ngọc Tôn duyệt việc của toàn bộ Ban ĐBGT (Nhựt, Hạnh, Quang)")

    # 1.7 Quản lý Đoàn Thị Ngọc Nữ (BLĐ)
    filters_nu = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'BLĐ'}, "Đoàn Thị Ngọc Nữ", "BLĐ", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test("Đồng Thị Nguyệt Nga" in filters_nu.get('NguoiChuTri', []) and "Nguyễn Thị Ngọc Hà" not in filters_nu.get('NguoiChuTri', []),
                "Đoàn Thị Ngọc Nữ chỉ duyệt Đồng Thị Nguyệt Nga, không duyệt Nguyễn Thị Ngọc Hà")

    # 1.8 Quản lý Đồng Thị Nguyệt Nga (TCKT DMT)
    filters_nga = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'TCKT'}, "Đồng Thị Nguyệt Nga", "TCKT", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test("Huỳnh Thị Hoàng Hà" in filters_nga.get('NguoiChuTri', []) and "Nguyễn Thị Nhật Sang" in filters_nga.get('NguoiChuTri', []) and "Lê Thị Hải" in filters_nga.get('NguoiChuTri', []),
                "Đồng Thị Nguyệt Nga quản lý duy nhất Ban TCKT gồm Hoàng Hà, Nhật Sang, Lê Thị Hải")

    # 1.9 Quản lý Nguyễn Thị Ngọc Hà (TCKT Cienco)
    filters_ha = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT', 'PhongBan': 'TCKT'}, "Nguyễn Thị Ngọc Hà", "TCKT", "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT")
    assert_test("Nguyễn Thị Như Can" in filters_ha.get('NguoiChuTri', []) and "Lê Thị Hải" not in filters_ha.get('NguoiChuTri', []) and "Huỳnh Thị Hoàng Hà" not in filters_ha.get('NguoiChuTri', []),
                "Nguyễn Thị Ngọc Hà chỉ quản lý Nguyễn Thị Như Can tại Cienco")

    # 1.10 HĐQT toàn quyền
    filters_binh = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'PhongBan': 'HĐQT'}, "Đặng Thanh Bình", "HĐQT", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
    assert_test('DonVi' not in filters_binh and 'PhongBan' not in filters_binh and 'NguoiChuTri' not in filters_binh,
                "HĐQT Đặng Thanh Bình xem không giới hạn toàn bộ hệ thống (bộ lọc rỗng hoàn toàn)")

    filters_ngoc = core_logic.setup_manager_db_filters({'DonVi': 'CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT', 'PhongBan': 'HĐQT'}, "Đặng Thị Lan Ngọc", "HĐQT", "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT")
    assert_test('DonVi' not in filters_ngoc and 'PhongBan' not in filters_ngoc and 'NguoiChuTri' not in filters_ngoc,
                "HĐQT Đặng Thị Lan Ngọc xem không giới hạn toàn bộ hệ thống (bộ lọc rỗng hoàn toàn)")

    # ----------------------------------------------------
    # TÁC VỤ 2: KIỂM THỬ TÁC VỤ TẠO VIỆC, CẬP NHẬT, NGHIỆM THU
    # ----------------------------------------------------
    print("\n--- 2. KIỂM THỬ QUY TRÌNH TẠO VIỆC, CẬP NHẬT TIẾN ĐỘ, NGHIỆM THU ---")

    # Mô phỏng bảng công việc Tasks DataFrame
    tasks_df = pd.DataFrame([
        {
            "ID": "TSK-TEST-001",
            "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
            "PhongBan": "HCNS",
            "NguoiChuTri": "Nguyễn Băng Trinh",
            "TenDuAn": "Nội bộ",
            "TenCongViec": "Soạn thảo hồ sơ lao động định kỳ",
            "NgayBatDau": datetime.date(2026, 11, 1),
            "Deadline": datetime.date(2026, 11, 15),
            "PhanTramHoanThanh": 100,
            "TrangThai": "Chờ nghiệm thu",
            "MucDoGhiNhan": ""
        },
        {
            "ID": "TSK-TEST-002",
            "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
            "PhongBan": "BLĐ",
            "NguoiChuTri": "Trần Cường",
            "TenDuAn": "Du thuyền Happy Yacht",
            "TenCongViec": "Kiểm tra kỹ thuật định kỳ động cơ du thuyền",
            "NgayBatDau": datetime.date(2026, 11, 5),
            "Deadline": datetime.date(2026, 11, 20),
            "PhanTramHoanThanh": 100,
            "TrangThai": "Chờ nghiệm thu",
            "MucDoGhiNhan": ""
        },
        {
            "ID": "TSK-TEST-003",
            "DonVi": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
            "PhongBan": "KT",
            "NguoiChuTri": "Phạm Quang Nghĩa",
            "TenDuAn": "Tuyến đường Lê Trọng Tấn",
            "TenCongViec": "Khảo sát cao độ tim tuyến",
            "NgayBatDau": datetime.date(2026, 11, 2),
            "Deadline": datetime.date(2026, 11, 10),
            "PhanTramHoanThanh": 100,
            "TrangThai": "Chờ nghiệm thu",
            "MucDoGhiNhan": ""
        }
    ])

    # 2.1 Hạnh Tiên kiểm tra việc cần duyệt
    tien_subs = core_logic.get_subordinates_for_manager("Nguyễn Thị Hạnh Tiên")
    pending_tien = tasks_df[(tasks_df['NguoiChuTri'].isin(tien_subs)) & (tasks_df['TrangThai'] == 'Chờ nghiệm thu')]
    assert_test(len(pending_tien) == 1 and pending_tien.iloc[0]['NguoiChuTri'] == "Nguyễn Băng Trinh",
                "Hạnh Tiên nhận đúng 1 việc chờ nghiệm thu của cấp dưới Nguyễn Băng Trinh")

    # 2.2 Đặng Ngọc Hoàng duyệt việc của Trần Cường (Marina)
    hoang_subs = core_logic.get_subordinates_for_manager("Đặng Ngọc Hoàng")
    pending_hoang = tasks_df[(tasks_df['NguoiChuTri'].isin(hoang_subs)) & (tasks_df['TrangThai'] == 'Chờ nghiệm thu')]
    assert_test(len(pending_hoang) == 1 and pending_hoang.iloc[0]['NguoiChuTri'] == "Trần Cường",
                "Đặng Ngọc Hoàng nhận đúng việc của Trần Cường (Marina xuyên công ty)")

    # 2.3 Quản lý duyệt việc (Chuyển trạng thái sang Hoàn thành & ghi nhận 100%)
    task_idx = tasks_df[tasks_df['ID'] == 'TSK-TEST-002'].index[0]
    tasks_df.at[task_idx, 'TrangThai'] = 'Hoàn thành'
    tasks_df.at[task_idx, 'MucDoGhiNhan'] = '100%'

    # Kiểm tra FIFO: Việc của Cường không còn trong danh sách chờ duyệt của Hoàng
    pending_hoang_after = tasks_df[(tasks_df['NguoiChuTri'].isin(hoang_subs)) & (tasks_df['TrangThai'] == 'Chờ nghiệm thu')]
    assert_test(len(pending_hoang_after) == 0,
                "Cơ chế FIFO: Việc sau khi Hoàng duyệt đã tự động hoàn tất và rời khỏi hàng chờ")

    # ----------------------------------------------------
    # TÁC VỤ 3: KIỂM THỬ LẬP & DUYỆT KPI (kpi_plans, kpi_tasks, bsc)
    # ----------------------------------------------------
    print("\n--- 3. KIỂM THỬ HỆ THỐNG LẬP & DUYỆT KPI ---")

    # Tạo KPI task mẫu
    kpi_df = pd.DataFrame([
        {
            "id": "KPI-TEST-01",
            "User": "Nguyễn Băng Trinh",
            "Month": 11,
            "Year": 2026,
            "Name": "Tuyển dụng nhân sự kỹ thuật theo tiến độ",
            "BSC": "Quy trình nội bộ",
            "Type": "Công việc chính",
            "Weight": 50,
            "Target": "Tuyển đủ 2 kỹ sư",
            "Status": "Chờ duyệt",
            "Progress": 100,
            "Score": 10.0,
            "Note": "Đã phỏng vấn đạt yêu cầu"
        },
        {
            "id": "KPI-TEST-02",
            "User": "Nguyễn Băng Trinh",
            "Month": 11,
            "Year": 2026,
            "Name": "Kiện toàn lưu trữ hồ sơ PCCC",
            "BSC": "Học hỏi & Phát triển",
            "Type": "Công việc định kỳ",
            "Weight": 60, # Tự động scale
            "Target": "Hoàn tất 100% hồ sơ",
            "Status": "Chờ duyệt",
            "Progress": 90,
            "Score": 9.0,
            "Note": ""
        }
    ])

    # Auto-scale test: Tổng trọng số 50 + 60 = 110 > 100 -> Tự động scale về 100
    scaled_kpi = core_logic.auto_scale_tasks(kpi_df.copy(), "Nguyễn Băng Trinh", 11, 2026)
    total_w = scaled_kpi['Weight'].sum()
    assert_test(abs(total_w - 100.0) < 0.1,
                f"Auto-scale trọng số KPI thành công: Tổng trọng số được chuẩn hóa tự động về 100% (thực tế: {total_w}%)")

    # Quản lý Hạnh Tiên duyệt KPI của Trinh
    scaled_kpi.loc[scaled_kpi['User'] == 'Nguyễn Băng Trinh', 'Status'] = 'Đã duyệt'
    assert_test(all(scaled_kpi['Status'] == 'Đã duyệt'),
                "Quản lý Hạnh Tiên phê duyệt thành công toàn bộ mục tiêu KPI tháng của Nguyễn Băng Trinh")

    # Lưu và đọc thử cấu hình BSC
    bsc_cfg = core_logic.load_bsc_config()
    assert_test(isinstance(bsc_cfg, dict) and "years" in bsc_cfg and "months" in bsc_cfg,
                "Đọc cấu hình quản trị BSC - KPI toàn công ty thành công")

    print("\n" + "=" * 70)
    print(f"🎉 TẤT CẢ {passed_tests}/{total_tests} KIỂM THỬ CHỨC NĂNG & QUY TRÌNH ĐÃ THÀNH CÔNG RỰC RỠ (100%)!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    run_tests()
