import pandas as pd
from datetime import datetime, date

def is_in_month(d, m, y):
    if pd.isna(d): return False
    if isinstance(d, str):
        try: d = datetime.strptime(d, "%Y-%m-%d").date()
        except: return False
    if isinstance(d, datetime): d = d.date()
    if isinstance(d, date): return d.month == m and d.year == y
    return False

def is_same_person_local(db_name, target_name):
    db_str = str(db_name).strip().lower()
    tgt_str = str(target_name).strip().lower()
    if db_str == tgt_str: return True
    tgt_parts = tgt_str.split()
    if len(tgt_parts) >= 2:
        return tgt_parts[0] in db_str and tgt_parts[-1] in db_str
    return False

try:
    display_df = pd.read_excel("data_dump.xlsx")
    print(f"Loaded display_df: {len(display_df)} rows")
except Exception as e:
    print(f"Error loading data_dump.xlsx: {e}")
    exit()

selected_month = 8
selected_year = 2026
p_name = "Nguyễn Thị Hạnh Tiên"

ai_tasks = display_df[
    (display_df['NguoiChuTri'].apply(lambda x: is_same_person_local(x, p_name))) & 
    (display_df['Deadline'].apply(lambda x: is_in_month(x, selected_month, selected_year)))
]

with open("out.txt", "w", encoding="utf-8") as f:
    f.write(f"DEBUG ai_tasks for {p_name}: size={len(ai_tasks)}\n")
    if not ai_tasks.empty:
        for _, r in ai_tasks.iterrows():
            f.write(f"- {r.get('TenCongViec')}\n")
