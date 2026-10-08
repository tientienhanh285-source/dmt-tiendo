import json
from core_logic import get_gsheets_conn, safe_gsheets_read

conn = get_gsheets_conn()
df = safe_gsheets_read(conn, 'CONFIG')

with open('all_depts.txt', 'w', encoding='utf-8') as f:
    for idx, row in df.iterrows():
        if row.get('NhanSu') == 'APP_GLOBAL_CONFIG':
            try:
                config_json = json.loads(row['config_json'])
                depts = config_json.get("companies", {}).get("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", {}).get("departments")
                f.write(f"Row {idx}: {json.dumps(depts, ensure_ascii=False)}\n")
            except Exception as e:
                f.write(f"Row {idx}: ERROR {e}\n")
