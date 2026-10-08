from supabase import create_client

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
response = supabase.table('tasks').select('*').execute()
tasks = response.data

import pandas as pd
df = pd.DataFrame(tasks)

print("Unique NguoiChuTri in Supabase:")
print(df['NguoiChuTri'].unique())
print("\nTasks for Thể's subordinates:")
subs = ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]
subs_tasks = df[df['NguoiChuTri'].isin(subs)]
print(subs_tasks[['ID', 'NguoiChuTri', 'DonVi', 'TrangThai', 'TenCongViec']])

print("\nTasks with 'Kế hoạch Đầu tư':")
print(df[df['NguoiChuTri'].str.contains('Kế hoạch Đầu tư', na=False)][['ID', 'NguoiChuTri', 'TenCongViec']])
