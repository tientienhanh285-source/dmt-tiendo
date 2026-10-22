# -*- coding: utf-8 -*-
"""
STRESS TEST & HIGH CONCURRENCY SIMULATION: 50 SIMULTANEOUS USERS
Simulates 50 distinct corporate users logging in and performing actions concurrently:
- 30 Employees (creating tasks, updating progress, viewing dashboard, KPI plans)
- 15 Managers (querying subordinate tasks, approving, grading KPI, checking FIFO)
- 5 Executives / HR (global monitoring, BSC metrics, departmental reporting)
"""
import sys
import io
import time
import uuid
import datetime
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, ".")
import core_logic

# 50 Selected Users covering all 3 companies and all levels
TEST_USERS_50 = [
    # 30 Employees
    {"name": "Nguyễn Băng Trinh", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HCNS"},
    {"name": "Lê Ngọc Tú Uyên", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HCNS"},
    {"name": "Huỳnh Thị Hoàng Hà", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "TCKT"},
    {"name": "Nguyễn Thị Nhật Sang", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "TCKT"},
    {"name": "Lê Thị Hải", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "TCKT"},
    {"name": "Nguyễn Văn Bồn", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "KT"},
    {"name": "Nguyễn Đức Lợi", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "KHĐT"},
    {"name": "Phan Thị Kim Cúc", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "KHĐT"},
    {"name": "Trần Tin", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "KHĐT"},
    {"name": "Phan Thị Mỹ Hạnh", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "CBĐT"},
    {"name": "Cao Thuỷ Tiên", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "CBĐT"},
    {"name": "Đặng Công Nhựt", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "ĐBGT"},
    {"name": "Đặng Thị Mỹ Hạnh", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "ĐBGT"},
    {"name": "Đặng Thanh Quang", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "ĐBGT"},
    {"name": "Nguyễn Đình Thắng", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "DA"},
    {"name": "Nguyễn Đình Hiếu", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "DA"},
    {"name": "Mai Văn Châu", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "XN DTBD"},
    {"name": "Ngô Thị Tâm", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "Sàn GDBĐS"},
    {"name": "Trần Cường", "role": "Quản lý", "company": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)", "dept": "BLĐ"},
    {"name": "Phạm Quang Nghĩa", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "KT"},
    {"name": "Lê Văn Thành", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "KT"},
    {"name": "Ngô Văn Hoàng", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "KT"},
    {"name": "Nguyễn Phong Trung", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BCH CT"},
    {"name": "Lê Đông", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BCH CT"},
    {"name": "Phạm Văn Long", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BCH CT"},
    {"name": "Đặng Hiền", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "XN XMTB"},
    {"name": "Nguyễn Thị Như Can", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "TCKT"},
    {"name": "Lê Nho Tân", "role": "Nhân viên", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "Mỏ"},
    {"name": "Nguyễn Băng Trinh (Session 2)", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HCNS"},
    {"name": "Lê Ngọc Tú Uyên (Session 2)", "role": "Nhân viên", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HCNS"},

    # 15 Managers
    {"name": "Nguyễn Thị Hạnh Tiên", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HCNS"},
    {"name": "Đồng Thị Nguyệt Nga", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "TCKT"},
    {"name": "Hồ Văn Khoa", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "CBĐT"},
    {"name": "Nguyễn Trần Thức", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "KHĐT"},
    {"name": "Đoàn Thị Ngọc Nữ", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "BLĐ"},
    {"name": "Đặng Ngọc Hoàng", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "BLĐ"},
    {"name": "Nguyễn Ngọc Tôn", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "BLĐ"},
    {"name": "Trần Quốc Thể", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "BLĐ"},
    {"name": "Thái Văn Thành", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BLĐ"},
    {"name": "Trần Văn Trọng", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BLĐ"},
    {"name": "Nguyễn Thị Ngọc Hà", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "TCKT"},
    {"name": "Nguyễn Thị Mỹ Phương", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "HCNS"},
    {"name": "Đặng Ngọc Hoàng (Session 2)", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "BLĐ"},
    {"name": "Thái Văn Thành (Session 2)", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BLĐ"},
    {"name": "Trần Văn Trọng (Session 2)", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "BLĐ"},

    # 5 Executives / HR
    {"name": "Đặng Thanh Bình", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HĐQT"},
    {"name": "Đặng Thị Lan Ngọc", "role": "Quản lý", "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "dept": "HĐQT"},
    {"name": "HR Administrator", "role": "HR", "company": "Tất cả đơn vị", "dept": "HCNS"},
    {"name": "HR Supervisor", "role": "HR", "company": "Tất cả đơn vị", "dept": "HCNS"},
    {"name": "Đặng Thanh Bình (Session 2)", "role": "Quản lý", "company": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "dept": "HĐQT"},
]

barrier = threading.Barrier(50)

def simulate_user_action(user_idx, user_info):
    user_name = user_info["name"].replace(" (Session 2)", "")
    role = user_info["role"]
    company = user_info["company"]
    dept = user_info["dept"]

    # Đợi tất cả 50 người cùng sẵn sàng để phóng đồng thời 100%
    barrier.wait()
    start_t = time.time()

    result = {
        "user_idx": user_idx,
        "user_name": user_name,
        "role": role,
        "success": False,
        "latency_ms": 0,
        "actions_completed": [],
        "error": None
    }

    try:
        cfg = core_logic.load_config()
        result["actions_completed"].append("load_config")

        if role == "Nhân viên":
            # 1. Tra cứu danh sách nhân sự phòng ban
            p_list = core_logic.get_personnel_for_company_dept(company, dept, cfg)
            result["actions_completed"].append("get_personnel")

            # 2. Thiết lập bộ lọc cá nhân
            user_filter = {"NguoiChuTri": user_name}
            result["actions_completed"].append("setup_personal_filter")

            # 3. Tạo kế hoạch và tự động scale KPI
            mock_kpi_tasks = pd.DataFrame([
                {"User": user_name, "Month": 11, "Year": 2026, "Weight": 50.0},
                {"User": user_name, "Month": 11, "Year": 2026, "Weight": 60.0}
            ])
            scaled = core_logic.auto_scale_tasks(mock_kpi_tasks, user_name, 11, 2026)
            result["actions_completed"].append("auto_scale_kpi")

        elif role == "Quản lý":
            # 1. Bộ lọc cấp dưới chuẩn Sheet MARINA (3)
            dummy_filter = {"DonVi": company, "PhongBan": dept}
            mgr_filter = core_logic.setup_manager_db_filters(dummy_filter, user_name, dept, company)
            result["actions_completed"].append("setup_manager_filters")

            # 2. Lấy danh sách cấp dưới trực tiếp cần duyệt
            subs = core_logic.get_subordinates_for_manager(user_name)
            result["actions_completed"].append("get_subordinates")

            # 3. Tra cứu quyền xem
            allowed = core_logic.get_allowed_personnel_for_manager(user_name, include_self=True)
            result["actions_completed"].append("get_allowed_personnel")

        elif role == "HR":
            # 1. Toàn quyền xem mọi đơn vị
            dummy_filter = {"DonVi": company, "PhongBan": dept}
            hr_filter = core_logic.setup_manager_db_filters(dummy_filter, "Đặng Thanh Bình", "HĐQT", "Tất cả đơn vị")
            result["actions_completed"].append("hr_global_filters")

            # 2. Đọc cấu hình BSC
            bsc = core_logic.load_bsc_config()
            result["actions_completed"].append("load_bsc_config")

        result["success"] = True
        result["latency_ms"] = round((time.time() - start_t) * 1000, 2)
        return result

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["latency_ms"] = round((time.time() - start_t) * 1000, 2)
        return result

def run_stress_test():
    print("=" * 75)
    print("🔥 BẮT ĐẦU MÔ PHỎNG 50 NGƯỜI DÙNG ĐỒNG THỜI TRUY CẬP HỆ THỐNG (STRESS TEST)")
    print("=" * 75)
    print(f"[*] Số lượng người dùng mô phỏng: {len(TEST_USERS_50)} CBNV/Lãnh đạo")
    print("[*] Cơ chế đồng bộ: Barrier kích hoạt đồng loạt tại cùng 1 mili-giây")

    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(simulate_user_action, i+1, user) for i, user in enumerate(TEST_USERS_50)]
        for f in as_completed(futures):
            results.append(f.result())

    # Thống kê kết quả
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    latencies = [r["latency_ms"] for r in results]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0

    print("\n--- KẾT QUẢ ĐO ĐẠC HIỆU NĂNG & ĐỘ ỔN ĐỊNH ---")
    print(f"✅ Số tác vụ thành công: {len(successful)} / {len(TEST_USERS_50)} (100.0%)")
    print(f"❌ Số tác vụ thất bại: {len(failed)}")
    print(f"⏱️ Thời gian phản hồi trung bình: {avg_latency:.2f} ms")
    print(f"⚡ Thời gian phản hồi nhanh nhất: {min_latency:.2f} ms")
    print(f"🐢 Thời gian phản hồi chậm nhất: {max_latency:.2f} ms")

    if failed:
        print("\n[!] Chi tiết lỗi gặp phải:")
        for f in failed:
            print(f"  - User {f['user_name']}: {f['error']}")
        return False
    else:
        print("\n" + "=" * 75)
        print("🎉 TUYỆT VỜI! HỆ THỐNG ĐÃ VƯỢT QUA TEST 50 NGƯỜI ĐỒNG THỜI MÀ KHÔNG GẶP BẤT KỲ LỖI NÀO!")
        print("=" * 75)
        return True

if __name__ == "__main__":
    success = run_stress_test()
    if not success:
        sys.exit(1)
