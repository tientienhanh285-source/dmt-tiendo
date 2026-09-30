import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('.')
from app import get_gsheets_conn
import json

conn = get_gsheets_conn()

res = conn.table("tasks").select('*').eq("NguoiChuTri", "Phạm Quang Nghĩa").execute()

count = 0
for row in res.data:
    if row.get("PhongBan") == "BLĐ":
        print(f"Fixing task {row.get('ID')} from BLĐ to KT")
        # primary key in Sheet1 is likely 'ID'
        pk = "ID" if "ID" in row else "id"
        conn.table("tasks").update({"PhongBan": "KT"}).eq(pk, row[pk]).execute()
        count += 1

print(f"Fixed {count} tasks.")
