import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import threading
import time
import uuid
from datetime import datetime, date, timedelta
import pandas as pd
from core_logic import (
    get_gsheets_conn,
    insert_task,
    update_task,
    read_db,
    setup_manager_db_filters,
    get_subordinates_for_manager
)

def run_30_user_concurrency_test():
    print("=" * 80)
    print("🚀 BẮT ĐẦU TEST ĐỒNG THỜI 30 NGƯỜI DÙNG CÙNG LÚC (30 CONCURRENT USERS TEST)")
    print("=" * 80)

    test_run_tag = f"CONCUR_TEST_{uuid.uuid4().hex[:6].upper()}"
    results = {
        "creates_success": [],
        "creates_errors": [],
        "dedup_success": [],
        "dedup_errors": [],
        "updates_success": [],
        "updates_errors": [],
        "approves_success": [],
        "approves_errors": [],
        "reads_success": [],
        "reads_errors": []
    }
    created_task_ids = []
    lock = threading.Lock()

    # Pre-create 5 tasks for managers to approve and 5 tasks for employees to update
    print("\n[BƯỚC 1] Khởi tạo dữ liệu mẫu phục vụ kiểm thử cập nhật và nghiệm thu...")
    conn = get_gsheets_conn()
    pre_created_update_ids = []
    pre_created_approve_ids = []

    for i in range(5):
        tid = insert_task({
            "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
            "PhongBan": "HCNS",
            "NguoiChuTri": "Nguyễn Băng Trinh",
            "TenDuAn": "Dự án Test Đồng Thời",
            "TenCongViec": f"[{test_run_tag}] Công việc cần cập nhật {i}",
            "NgayBatDau": "2026-10-01",
            "Deadline": "2026-10-31",
            "TrangThai": "Đang thực hiện",
            "PhanTramHoanThanh": 20,
            "TyTrongKPI": 10
        })
        if tid:
            pre_created_update_ids.append(tid)
            created_task_ids.append(tid)

    for i in range(5):
        tid = insert_task({
            "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
            "PhongBan": "HCNS",
            "NguoiChuTri": "Lê Ngọc Tú Uyên",
            "TenDuAn": "Dự án Test Đồng Thời",
            "TenCongViec": f"[{test_run_tag}] Công việc chờ nghiệm thu {i}",
            "NgayBatDau": "2026-10-01",
            "Deadline": "2026-10-31",
            "TrangThai": "Chờ nghiệm thu",
            "PhanTramHoanThanh": 100,
            "LinkKetQua": "https://dmtgroup.vn/report.pdf",
            "TyTrongKPI": 10
        })
        if tid:
            pre_created_approve_ids.append(tid)
            created_task_ids.append(tid)

    print(f"   -> Đã chuẩn bị {len(pre_created_update_ids)} task cập nhật và {len(pre_created_approve_ids)} task nghiệm thu.")

    # Barrier to ensure all 30 threads fire at the EXACT SAME MICROSECOND
    barrier = threading.Barrier(30)

    # 1. 10 Workers tạo công việc mới (Employees creating genuine tasks)
    def worker_create_task(user_idx):
        user_name = f"User_{user_idx}_{test_run_tag}"
        task_data = {
            "DonVi": "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
            "PhongBan": "KT",
            "NguoiChuTri": user_name,
            "TenDuAn": "KDC Bàu Mạc",
            "TenCongViec": f"[{test_run_tag}] Việc mới user {user_idx}",
            "NgayBatDau": "2026-10-01",
            "Deadline": "2026-10-30",
            "TrangThai": "Đang thực hiện",
            "PhanTramHoanThanh": 0,
            "TyTrongKPI": 10
        }
        try:
            barrier.wait() # Đồng loạt kích hoạt
            new_id = insert_task(task_data)
            if new_id:
                with lock:
                    results["creates_success"].append((user_idx, new_id))
                    created_task_ids.append(new_id)
            else:
                with lock:
                    results["creates_errors"].append((user_idx, "insert_task returned False"))
        except Exception as e:
            with lock:
                results["creates_errors"].append((user_idx, str(e)))

    # 2. 5 Workers test bấm lưu lặp lại / click đúp đồng thời (Double click simulation)
    def worker_dedup_task(user_idx):
        user_name = f"DedupUser_{user_idx}_{test_run_tag}"
        task_data = {
            "DonVi": "CTY CP DMT - MARINA (Du thuyền Happy Yacht)",
            "PhongBan": "HCNS",
            "NguoiChuTri": user_name,
            "TenDuAn": "Du thuyền Happy Yacht",
            "TenCongViec": f"[{test_run_tag}] Thao tác click đúp nhanh",
            "NgayBatDau": "2026-10-01",
            "Deadline": "2026-10-28",
            "TrangThai": "Đang thực hiện",
            "PhanTramHoanThanh": 0,
            "TyTrongKPI": 10
        }
        try:
            barrier.wait()
            # Bấm lưu liên tiếp 3 lần
            id1 = insert_task(task_data.copy())
            id2 = insert_task(task_data.copy())
            id3 = insert_task(task_data.copy())
            
            with lock:
                if id1 and id1 == id2 and id2 == id3:
                    results["dedup_success"].append((user_idx, id1))
                    created_task_ids.append(id1)
                else:
                    results["dedup_errors"].append((user_idx, f"Duplicated! IDs: {id1}, {id2}, {id3}"))
        except Exception as e:
            with lock:
                results["dedup_errors"].append((user_idx, str(e)))

    # 3. 5 Workers cập nhật tiến độ công việc đồng thời
    def worker_update_task(user_idx, task_id):
        try:
            barrier.wait()
            update_data = {
                "PhanTramHoanThanh": 80,
                "TrangThai": "Chờ nghiệm thu",
                "LinkKetQua": f"https://dmtgroup.vn/update_{user_idx}.pdf",
                "NgayCapNhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ok = update_task(task_id, update_data)
            with lock:
                if ok:
                    results["updates_success"].append((user_idx, task_id))
                else:
                    results["updates_errors"].append((user_idx, "update_task returned False"))
        except Exception as e:
            with lock:
                results["updates_errors"].append((user_idx, str(e)))

    # 4. 5 Managers duyệt nghiệm thu công việc đồng thời
    def worker_approve_task(user_idx, task_id):
        try:
            barrier.wait()
            # Nguyễn Thị Hạnh Tiên duyệt công việc cho Tú Uyên
            update_data = {
                "TrangThai": "Hoàn thành",
                "PhanTramHoanThanh": 100,
                "MucDoGhiNhan": "100%",
                "NgayCapNhat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            ok = update_task(task_id, update_data)
            with lock:
                if ok:
                    results["approves_success"].append((user_idx, task_id))
                else:
                    results["approves_errors"].append((user_idx, "approve returned False"))
        except Exception as e:
            with lock:
                results["approves_errors"].append((user_idx, str(e)))

    # 5. 5 Users đọc dữ liệu đồng thời với các bộ lọc phân quyền khác nhau
    def worker_read_data(user_idx):
        try:
            barrier.wait()
            if user_idx % 2 == 0:
                # Quản lý đọc
                db_filters = setup_manager_db_filters({}, "Nguyễn Thị Hạnh Tiên", "HCNS", "CTY CP DMT - MARINA (Du thuyền Happy Yacht)")
                df = read_db(filters=db_filters)
            else:
                # Nhân viên đọc
                df = read_db(filters={"NguoiChuTri": "Lê Thị Hải"})
                
            with lock:
                if isinstance(df, pd.DataFrame):
                    results["reads_success"].append((user_idx, len(df)))
                else:
                    results["reads_errors"].append((user_idx, "read_db returned non-DataFrame"))
        except Exception as e:
            with lock:
                results["reads_errors"].append((user_idx, str(e)))

    # Assemble all 30 threads
    threads = []
    # 10 create
    for i in range(10):
        threads.append(threading.Thread(target=worker_create_task, args=(i,)))
    # 5 dedup
    for i in range(5):
        threads.append(threading.Thread(target=worker_dedup_task, args=(i+10,)))
    # 5 update
    for i in range(5):
        threads.append(threading.Thread(target=worker_update_task, args=(i+15, pre_created_update_ids[i])))
    # 5 approve
    for i in range(5):
        threads.append(threading.Thread(target=worker_approve_task, args=(i+20, pre_created_approve_ids[i])))
    # 5 read
    for i in range(5):
        threads.append(threading.Thread(target=worker_read_data, args=(i+25,)))

    print(f"\n[BƯỚC 2] Kích hoạt đồng thời {len(threads)} luồng người dùng cùng 1 thời điểm...")
    t_start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    t_elapsed = time.time() - t_start

    print(f"\n[BƯỚC 3] Hoàn tất 30 tác vụ đồng thời trong: {t_elapsed:.2f} giây!")
    print("-" * 80)
    print(f"   1. Tạo việc mới (10/10): Thành công {len(results['creates_success'])}, Lỗi {len(results['creates_errors'])}")
    print(f"   2. Chống click đúp (5/5): Thành công {len(results['dedup_success'])}, Lỗi {len(results['dedup_errors'])}")
    print(f"   3. Cập nhật tiến độ (5/5): Thành công {len(results['updates_success'])}, Lỗi {len(results['updates_errors'])}")
    print(f"   4. Nghiệm thu duyệt (5/5): Thành công {len(results['approves_success'])}, Lỗi {len(results['approves_errors'])}")
    print(f"   5. Đọc bảng tiến độ (5/5): Thành công {len(results['reads_success'])}, Lỗi {len(results['reads_errors'])}")
    print("-" * 80)

    total_errors = (
        len(results['creates_errors']) +
        len(results['dedup_errors']) +
        len(results['updates_errors']) +
        len(results['approves_errors']) +
        len(results['reads_errors'])
    )

    # Dọn dẹp dữ liệu test
    print("\n[BƯỚC 4] Dọn dẹp các bản ghi phát sinh trong quá trình test đồng thời...")
    unique_ids_to_clean = list(set(created_task_ids))
    try:
        conn.table("tasks").delete().in_("ID", unique_ids_to_clean).execute()
        print(f"   -> Đã xóa sạch {len(unique_ids_to_clean)} bản ghi thử nghiệm khỏi Supabase!")
    except Exception as e:
        print(f"   -> Lỗi dọn dẹp: {e}")

    if total_errors == 0:
        print("\n" + "=" * 80)
        print("🎉 THÀNH CÔNG TUYỆT ĐỐI: 30 NGƯỜI DÙNG CÙNG LÚC 100% PASS - KHÔNG CÓ BẤT KỲ LỖI NÀO!")
        print("=" * 80)
        return True
    else:
        print(f"\n❌ CÓ {total_errors} LỖI XẢY RA TRONG KIỂM THỬ ĐỒNG THỜI!")
        return False

if __name__ == "__main__":
    success = run_30_user_concurrency_test()
    if not success:
        exit(1)
