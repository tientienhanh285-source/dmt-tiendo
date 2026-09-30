import sys
sys.path.append('.')
from app import get_gsheets_conn, safe_gsheets_read
import json

conn = get_gsheets_conn()
df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=0)
for idx, row in df.iterrows():
    if "config_json" in row and row["config_json"]:
        try:
            data = json.loads(row["config_json"])
            if "personnel_by_department" in data:
                for dept, p_list in data["personnel_by_department"].items():
                    if "Phạm Quang Nghĩa" in p_list:
                        print(f"Global: {dept} -> Phạm Quang Nghĩa")
            if "companies" in data:
                for comp, c_data in data["companies"].items():
                    if "personnel_by_department" in c_data:
                        for dept, p_list in c_data["personnel_by_department"].items():
                            if "Phạm Quang Nghĩa" in p_list:
                                print(f"Company {comp}: {dept} -> Phạm Quang Nghĩa")
        except Exception as e:
            print("Error parsing JSON")
