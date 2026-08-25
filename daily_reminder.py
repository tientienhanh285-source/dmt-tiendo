import os
import sys
import pandas as pd
from datetime import datetime, date
from supabase import create_client
from mailer import send_reminder_email

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'

CONTACT_BOOK = {
    "Nguyễn Băng Trinh": "bangtrinhtrinh210@gmail.com",
    "Lê Ngọc Tú Uyên": "lengoctuuyen2002@gmail.com",
    "Nguyễn Thị Hạnh Tiên": "hanhtien2805@gmail.com"
}

def main():
    print("Bắt đầu tiến trình tự động nhắc nhở...")
    
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        print("Lỗi: Thiếu thông tin Email gửi (SENDER_EMAIL, SENDER_PASSWORD) trong GitHub Secrets.")
        sys.exit(1)
        
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("tasks").select("*").execute()
        
        if not response.data:
            print("Không có dữ liệu công việc.")
            sys.exit(0)
            
        full_df = pd.DataFrame(response.data)
        today = date.today()
        full_df['Deadline'] = pd.to_datetime(full_df['Deadline'], errors='coerce')
        
        # Lặp qua từng người trong danh bạ
        for name, email in CONTACT_BOOK.items():
            print(f"\n--- Đang xử lý cho: {name} ({email}) ---")
            df = full_df[full_df['NguoiChuTri'] == name].copy()
            
            if df.empty:
                print(f"Không có công việc nào của {name}.")
                continue
                
            # Xác định công việc trễ hạn hoặc có vướng mắc
            late_tasks = []
            for _, row in df.iterrows():
                status = str(row.get('TrangThai', ''))
                deadline = row['Deadline']
                
                is_late_by_date = False
                if pd.notna(deadline) and isinstance(deadline, datetime):
                    if deadline.date() < today and "Đã xong" not in status and "Hoàn thành" not in status:
                        is_late_by_date = True
                        
                if is_late_by_date or "Quá hạn" in status or "Trễ hạn" in status or "Có vướng mắc" in status:
                    late_tasks.append(row)
                    
            if not late_tasks:
                print(f"Tuyệt vời! {name} không có công việc nào bị trễ hạn hoặc vướng mắc.")
                continue
                
            late_df = pd.DataFrame(late_tasks)
            late_df['Deadline'] = late_df['Deadline'].dt.strftime('%d/%m/%Y')
            
            # Gửi email
            print(f"Phát hiện {len(late_df)} công việc trễ/vướng mắc. Đang gửi email...")
            success, msg = send_reminder_email(sender_email, sender_password, email, late_df)
            
            if success:
                print(f"✅ Gửi mail thành công cho {name}: {msg}")
            else:
                print(f"❌ Lỗi gửi mail cho {name}: {msg}")
                
        print("\nTiến trình hoàn tất.")
            
    except Exception as e:
        print(f"Lỗi hệ thống: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
