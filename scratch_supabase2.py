import os
import json
from supabase import create_client

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table("tasks").select("ID,NguoiChuTri,NguonGiaoViec").execute()
tasks = response.data

with open("scratch_output2.json", "w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print("Done")
