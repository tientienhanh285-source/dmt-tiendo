import json
from core_logic import get_gsheets_conn, safe_gsheets_read

conn = get_gsheets_conn()
df = safe_gsheets_read(conn, 'CONFIG')

results = []
for idx, row in df.iterrows():
    try:
        config_json = json.loads(row['config_json'])
        if "companies" in config_json:
            depts = config_json["companies"].get("CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", {}).get("departments")
            results.append({
                "row_idx": idx,
                "nhansu": row.get('NhanSu', ''),
                "depts": depts
            })
    except:
        pass

with open('all_depts.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
