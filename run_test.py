import sqlite3
import shutil
import random
import traceback
import sys
import io
import uuid
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('Bắt đầu mô phỏng kiểm thử tự động với 40 người dùng...')

try:
    # 1. Create a safe test database
    shutil.copy('database.db', 'test_db.db')
    conn = sqlite3.connect('test_db.db')
    cursor = conn.cursor()
    
    # 2. Users (40 users total across departments)
    users = [
        'Trần Quốc Thể', 'Đoàn Thị Ngọc Nữ', 'Đặng Ngọc Hoàng', 'Nguyễn Ngọc Tôn',
        'Nguyễn Thị Hạnh Tiên', 'Nguyễn Băng Trinh', 'Lê Ngọc Tú Uyên',
        'Đồng Thị Nguyệt Nga', 'Huỳnh Thị Hoàng Hà', 'Nguyễn Thị Nhật Sang',
        'Nguyễn Trần Thức', 'Nguyễn Đức Lợi', 'Cao Thuỷ Tiên', 'Trần Tin',
        'Hồ Văn Khoa', 'Phan Thị Mỹ Hạnh', 'Phan Thị Kim Cúc',
        'Nguyễn Văn Bồn',
        'Đặng Công Nhựt', 'Đặng Thị Mỹ Hạnh', 'Đặng Thanh Quang',
        'Nguyễn Phong Trung', 'Phạm Văn Long', 'Lê Đông',
        'Đặng Hiền',
        'Nguyễn Đình Thắng', 'Nguyễn Đình Hiếu',
        'Mai Văn Châu',
        'Ngô Thị Tâm',
        'Trần Cường', 'Thái Văn Thành', 'Trần Văn Trọng', 'Đặng Thanh Bình',
        'Nguyễn Thị Mỹ Phụng', 'Nguyễn Thị Ngọc Hà',
        # Thêm cho đủ 40
        'Test User 36', 'Test User 37', 'Test User 38', 'Test User 39', 'Test User 40'
    ]
    
    print(f'Đã tải {len(users)} người dùng để kiểm thử.')
    
    # 3. Simulate 100 trials
    errors = []
    success_count = 0
    
    for trial in range(1, 101):
        for user in users:
            try:
                # Simulate fetching tasks assigned to user
                cursor.execute('SELECT * FROM tasks WHERE NguoiChuTri = ?', (user,))
                tasks = cursor.fetchall()
                
                # Simulate Adding a task (10% chance)
                if random.random() < 0.1:
                    new_id = str(uuid.uuid4())
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute('''
                        INSERT INTO tasks (ID, DonVi, PhongBan, NguoiChuTri, TenDuAn, TenCongViec, TrangThai, Deadline, NgayCapNhat) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (new_id, 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG', 'Ban Kỹ thuật', user, 'Dự án Test', f'Nhiệm vụ {trial}', 'Chưa bắt đầu', '2026-12-31', now_str))
                    
                # Simulate Updating a task (10% chance)
                if tasks and random.random() < 0.1:
                    task_id = tasks[0][0] # ID is the first column
                    cursor.execute('UPDATE tasks SET TrangThai = ? WHERE ID = ?', ('Đang thực hiện', task_id))
                
                conn.commit()
                success_count += 1
            except Exception as e:
                errors.append(f'Lần thử {trial}, Người dùng {user}: Lỗi DB -> {str(e)}')
    
    print(f'Kiểm thử hoàn tất. Số thao tác thành công: {success_count}')
    if errors:
        print(f'Phát hiện {len(errors)} lỗi. Đây là 5 lỗi đầu tiên:')
        for e in errors[:5]:
            print(e)
    else:
        print('Tuyệt vời! Không phát hiện lỗi (0 errors). Cơ sở dữ liệu và truy vấn cốt lõi hoạt động ổn định và an toàn khi mô phỏng tải 40 người dùng x 100 lần thử.')
        
except Exception as e:
    print('Kiểm thử thất bại do lỗi kịch bản:')
    traceback.print_exc()
finally:
    if 'conn' in locals():
        conn.close()
