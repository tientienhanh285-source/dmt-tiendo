import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import random
from datetime import date, datetime, timedelta
from core_logic import (
    read_db,
    insert_task,
    update_task,
    delete_task,
    get_personnel_for_company_dept,
    get_departments_for_company,
    get_subordinates_for_manager,
    get_allowed_personnel_for_manager,
    setup_manager_db_filters,
    load_config,
    COMPANIES
)

print("=" * 80)
print("🔥 BẮT ĐẦU CHẠY 50 LẦN STRESS TEST KIỂM THỬ CHUYÊN SÂU HỆ THỐNG TIẾN ĐỘ & KPI DMT GROUP")
print("=" * 80)

config = load_config()
today = date.today()
created_stress_ids = []

def cleanup_stress():
    print(f"\n🧹 Đang dọn dẹp {len(created_stress_ids)} task sinh ra trong quá trình 50 vòng test...")
    for tid in set(created_stress_ids):
        try:
            delete_task(tid)
        except Exception:
            pass
    print("   -> Đã dọn dẹp sạch sẽ cơ sở dữ liệu Supabase!")

try:
    for i in range(1, 51):
        print(f"\n[VÒNG {i:02d}/50] ----------------------------------------------------")
        
        # --- 1. KIỂM TRA CHẶN CLICK ĐÚP (DOUBLE-CLICK / MULTI-SAVE DEDUPLICATION) ---
        test_task_name = f"[STRESS-TEST-{i:02d}] Kiểm tra chặn trùng lặp click đúp"
        task_data = {
            "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
            "PhongBan": "HCTH",
            "NguoiChuTri": "Nguyễn Băng Trinh",
            "TenDuAn": "Du thuyền Happy Yacht",
            "MocTienDo": "Tự do",
            "SanPhamBanGiao": "Báo cáo test",
            "TenCongViec": test_task_name,
            "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
            "NgayBatDau": today.strftime('%Y-%m-%d'),
            "Deadline": (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            "DoUuTien": "Trung bình",
            "PhanTramHoanThanh": 100,
            "TrangThai": "Chờ nghiệm thu",
            "LinkKetQua": "https://dmt.vn/test.pdf",
            "GiaiTrinhDeXuat": "Stress test click đúp",
            "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "ChuKyTheoDoi": "Theo dự án / Tự do",
            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ",
            "TyTrongKPI": 20,
            "NguonGiaoViec": "Công việc được giao / định kì",
            "MucDoGhiNhan": "0% (Không ghi nhận)"
        }
        
        # Bấm Lưu lần 1
        id_1 = insert_task(task_data.copy())
        assert id_1, f"Vòng {i}: Lần lưu 1 thất bại!"
        created_stress_ids.append(id_1)
        
        # Giả lập người dùng bấm Lưu lần 2 ngay lập tức (cách 0.2 giây)
        time.sleep(0.2)
        id_2 = insert_task(task_data.copy())
        
        # Giả lập người dùng bấm Lưu lần 3
        time.sleep(0.1)
        id_3 = insert_task(task_data.copy())
        
        # Cả 3 lần bấm Lưu đều phải trả về đúng DUY NHẤT 1 ID công việc (Chặn trùng 100%)
        assert id_1 == id_2 == id_3, f"Vòng {i}: LỖI TRÙNG LẶP TASK! Bấm lưu 3 lần nhưng sinh ra các ID khác nhau: {id_1}, {id_2}, {id_3}"
        print(f"   ✓ 1. Chống click đúp: Bấm lưu 3 lần liên tiếp -> Chỉ tạo DUY NHẤT 1 task ID: {id_1}")

        # --- 2. KIỂM TRA HIỂN THỊ ĐẦY ĐỦ NHÂN SỰ CỦA CẢ 3 CÔNG TY ---
        # Marina
        marina_p = get_personnel_for_company_dept("CTY CP DMT - MARINA (Du thuyền Happy Yacht)", "HCTH", config)
        assert "Nguyễn Băng Trinh" in marina_p and "Lê Ngọc Tú Uyên" in marina_p and "Nguyễn Thị Hạnh Tiên" in marina_p, f"Vòng {i}: Thiếu nhân sự HCTH Marina! Got: {marina_p}"
        
        marina_tckt = get_personnel_for_company_dept("CTY CP DMT - MARINA (Du thuyền Happy Yacht)", "TCKT", config)
        assert "Lê Thị Hải" in marina_tckt, f"Vòng {i}: Thiếu Lê Thị Hải trong TCKT Marina!"

        # Cienco
        cienco_kt = get_personnel_for_company_dept("CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "KT", config)
        assert "Lê Nho Tân" in cienco_kt and "Lê Văn Thành" in cienco_kt and "Ngô Văn Hoàng" in cienco_kt, f"Vòng {i}: Thiếu nhân sự Kỹ thuật Cienco! Got: {cienco_kt}"
        
        cienco_bch = get_personnel_for_company_dept("CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "BCH CT", config)
        assert "Nguyễn Phong Trung" in cienco_bch and "Phạm Văn Long" in cienco_bch and "Lê Đông" in cienco_bch, f"Vòng {i}: Thiếu nhân sự BCH CT Cienco! Got: {cienco_bch}"

        # Đầu Tư
        dautu_khdt = get_personnel_for_company_dept("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "KHĐT", config)
        assert "Nguyễn Trần Thức" in dautu_khdt and "Cao Thuỷ Tiên" in dautu_khdt and "Trần Tin" in dautu_khdt, f"Vòng {i}: Thiếu nhân sự KHĐT Đầu Tư!"

        dautu_cbdt = get_personnel_for_company_dept("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "CBĐT", config)
        assert "Hồ Văn Khoa" in dautu_cbdt and "Phan Thị Mỹ Hạnh" in dautu_cbdt and "Phan Thị Kim Cúc" in dautu_cbdt, f"Vòng {i}: Thiếu nhân sự CBĐT Đầu Tư!"

        print("   ✓ 2. Dropdown nhân sự: 100% nhân sự của cả 3 công ty hiển thị chuẩn xác!")

        # --- 3. KIỂM TRA ĐA QUẢN LÝ LIÊN CÔNG TY & HÀNG CHỜ FIFO ---
        # Hạnh Tiên vào duyệt task của Băng Trinh
        db_f_tien = setup_manager_db_filters({'DonVi': 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)'}, "Nguyễn Thị Hạnh Tiên", "HCTH", 'CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
        df_tien = read_db(filters=db_f_tien)
        subs_tien = get_subordinates_for_manager("Nguyễn Thị Hạnh Tiên")
        assert id_1 in df_tien[(df_tien['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_tien['NguoiChuTri'].isin(subs_tien))]['ID'].values, f"Vòng {i}: Hạnh Tiên không thấy task {id_1} chờ duyệt!"

        # Hạnh Tiên bấm Duyệt -> Hoàn thành
        update_task(id_1, {"TrangThai": "Hoàn thành", "PhanTramHoanThanh": 100})
        df_tien_after = read_db(filters=db_f_tien)
        assert id_1 not in df_tien_after[(df_tien_after['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])) & (df_tien_after['NguoiChuTri'].isin(subs_tien))]['ID'].values, f"Vòng {i}: Task {id_1} chưa biến mất sau khi duyệt!"
        print(f"   ✓ 3. Quản lý nhận việc & duyệt FIFO: Hạnh Tiên thấy việc {id_1}, duyệt xong biến mất chuẩn xác!")

        # --- 4. KIỂM TRA CHỐNG LẪN LỘN CÔNG VIỆC GIỮA CÁC NHÂN VIÊN ---
        sample_emp = random.choice(["Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên", "Lê Thị Hải", "Nguyễn Văn Bồn", "Nguyễn Phong Trung", "Cao Thuỷ Tiên"])
        emp_filter = {'NguoiChuTri': sample_emp}
        df_emp = read_db(filters=emp_filter)
        for _, row in df_emp.iterrows():
            assert row['NguoiChuTri'] == sample_emp, f"Vòng {i}: LỖI LẪN LỘN DỮ LIỆU! Xem tài khoản '{sample_emp}' nhưng lọt việc của '{row['NguoiChuTri']}'!"
        print(f"   ✓ 4. Cách ly dữ liệu: Kiểm tra tài khoản '{sample_emp}' -> 100% dữ liệu đúng chủ, không bị lẫn lộn!")

    print("\n" + "=" * 80)
    print("🎉 THÀNH CÔNG RỰC RỠ: TẤT CẢ 50 VÒNG STRESS TEST ĐÃ HOÀN TẤT VỚI KẾT QUẢ 100% PASS!")
    print("=" * 80)

finally:
    cleanup_stress()
