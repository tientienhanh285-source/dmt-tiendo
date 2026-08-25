import os
import sys
import pandas as pd
from datetime import datetime, date
from supabase import create_client
from mailer import send_reminder_email

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'

def main():
    print("Bắt đầu tiến trình tự động nhắc nhở...")
    
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not sender_email or not sender_password or not receiver_email:
        print("Lỗi: Thiếu thông tin Email trong Environment Variables (GitHub Secrets).")
        sys.exit(1)
        
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("tasks").select("*").execute()
        
        if not response.data:
            print("Không có dữ liệu công việc.")
            sys.exit(0)
            
        df = pd.DataFrame(response.data)
        
        # Lọc công việc của người thử nghiệm
        df = df[df['NguoiChuTri'] == 'Nguyễn Thị Hạnh Tiên'].copy()
        
        if df.empty:
            print("Không có công việc nào của Nguyễn Thị Hạnh Tiên.")
            sys.exit(0)
            
        # Xử lý ngày tháng và trạng thái
        today = date.today()
        df['Deadline'] = pd.to_datetime(df['Deadline'], errors='coerce')
        
        # Xác định công việc trễ hạn hoặc có vướng mắc
        late_tasks = []
        for _, row in df.iterrows():
            status = str(row.get('TrangThai', ''))
            deadline = row['Deadline']
            
            # Logic tính trễ hạn tương tự hệ thống chính
            is_late_by_date = False
            if pd.notna(deadline) and isinstance(deadline, datetime):
                if deadline.date() < today and "Đã xong" not in status:
                    is_late_by_date = True
                    
            if is_late_by_date or "Quá hạn" in status or "Trễ hạn" in status or "Có vướng mắc" in status:
                late_tasks.append(row)
                
        if not late_tasks:
            print("Thật tuyệt! Bạn không có công việc nào bị trễ hạn hoặc vướng mắc.")
            sys.exit(0)
            
        late_df = pd.DataFrame(late_tasks)
        late_df['Deadline'] = late_df['Deadline'].dt.strftime('%d/%m/%Y')
        
        # Gửi email
        print(f"Đang gửi email nhắc nhở cho {len(late_df)} công việc trễ hạn/vướng mắc...")
        success, msg = send_reminder_email(sender_email, sender_password, receiver_email, late_df)
        
        if success:
            print(f"Gửi mail thành công: {msg}")
        else:
            print(f"Lỗi gửi mail: {msg}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Lỗi hệ thống: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
