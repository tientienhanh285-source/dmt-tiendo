import json
from supabase import create_client

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table("tasks").select("ID,NguoiChuTri").execute()
tasks = response.data

# User specifies: Mỹ Phương, Đức Lợi, Sang, Hà
target_keywords = ["Mỹ Phương", "Đức Lợi", "Sang", "Hà"]

ids_to_delete = []
for t in tasks:
    nct = str(t.get("NguoiChuTri", ""))
    if any(k in nct for k in target_keywords):
        ids_to_delete.append(t["ID"])

if ids_to_delete:
    print(f"Deleting {len(ids_to_delete)} tasks...")
    for i in range(0, len(ids_to_delete), 50):
        batch = ids_to_delete[i:i+50]
        supabase.table("tasks").delete().in_("ID", batch).execute()
    print("Deleted successfully")
else:
    print("No tasks found to delete.")
