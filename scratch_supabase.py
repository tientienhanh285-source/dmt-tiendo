import os
from supabase import create_client

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch tasks
response = supabase.table("tasks").select("*").execute()
tasks = response.data
print("Total tasks:", len(tasks))

if len(tasks) > 0:
    print("Columns:", list(tasks[0].keys()))
    # filter for users:
    target_users = ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên", "Lê Thị Tú Uyên"]
    # Let's count by NguonGiaoViec or NguoiChuTri
    
    count_nguoi_chu_tri = {u: 0 for u in target_users}
    count_nguon_giao_viec = {u: 0 for u in target_users}
    
    for t in tasks:
        nct = t.get("NguoiChuTri", "")
        ngv = t.get("NguonGiaoViec", "")
        for u in target_users:
            if u in str(nct):
                count_nguoi_chu_tri[u] += 1
            if u in str(ngv):
                count_nguon_giao_viec[u] += 1
                
    print("Tasks by NguoiChuTri:", count_nguoi_chu_tri)
    print("Tasks by NguonGiaoViec:", count_nguon_giao_viec)
