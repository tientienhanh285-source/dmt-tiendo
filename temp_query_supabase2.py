from supabase import create_client
import pandas as pd

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
response = supabase.table('tasks').select('*').execute()
tasks = response.data
df = pd.DataFrame(tasks)

# write unique NguoiChuTri
unique_users = pd.DataFrame(df['NguoiChuTri'].unique(), columns=['NguoiChuTri'])
unique_users.to_csv('debug_unique_users.csv', index=False)

subs = ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]
subs_tasks = df[df['NguoiChuTri'].isin(subs)]
subs_tasks[['ID', 'NguoiChuTri', 'DonVi', 'TrangThai', 'TenCongViec']].to_csv('debug_subs_tasks.csv', index=False)
