import json
from supabase import create_client

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
conn = create_client(SUPABASE_URL, SUPABASE_KEY)

def remove_person(d, dept, person):
    if dept in d:
        if isinstance(d[dept], list):
            if person in d[dept]:
                d[dept].remove(person)
        elif isinstance(d[dept], str):
            if d[dept] == person:
                d[dept] = []
        elif isinstance(d[dept], dict):
            pass # ignore

def clean_dict(data):
    remove_person(data, "DA", "Nguyễn Đình Thắng")
    remove_person(data, "Ban Dự án", "Nguyễn Đình Thắng")
    remove_person(data, "KHĐT", "Trần Quốc Thể")
    remove_person(data, "Ban Kế hoạch Đầu tư", "Trần Quốc Thể")
    remove_person(data, "CBĐT", "Trần Quốc Thể")
    remove_person(data, "Ban Chuẩn bị Đầu tư", "Trần Quốc Thể")
    remove_person(data, "KT", "Trần Quốc Thể")
    remove_person(data, "Ban Kỹ thuật", "Trần Quốc Thể")
    remove_person(data, "TCKT", "Đoàn Thị Ngọc Nữ")
    remove_person(data, "Ban Tài chính Kế toán", "Đoàn Thị Ngọc Nữ")

# 1. Fetch CONFIG row
res = conn.table("kpi_config").select("*").eq("NhanSu", "APP_GLOBAL_CONFIG").execute()
if res.data:
    row = res.data[0]
    config_json = row.get("config_json")
    if config_json:
        data = json.loads(config_json)
        
        # 2. Modify data
        if "personnel_by_department" in data:
            clean_dict(data["personnel_by_department"])
        if "DEPT_LEADS" in data:
            clean_dict(data["DEPT_LEADS"])
        if "companies" in data:
            for comp, comp_data in data["companies"].items():
                if "personnel_by_department" in comp_data:
                    clean_dict(comp_data["personnel_by_department"])
                if "DEPT_LEADS" in comp_data:
                    clean_dict(comp_data["DEPT_LEADS"])
                    
        # 3. Update Supabase
        new_json = json.dumps(data, ensure_ascii=False)
        update_res = conn.table("kpi_config").update({"config_json": new_json}).eq("id", row["id"]).execute()
        print("Successfully updated Supabase kpi_config!")
else:
    print("No APP_GLOBAL_CONFIG found in Supabase.")
