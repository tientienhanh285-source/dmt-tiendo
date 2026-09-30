import pandas as pd
import json
import os
import glob

filename = glob.glob('*HCNS*.xlsx')[0]

df = pd.read_excel(filename, sheet_name="A7.9.KPI Ban HCNS năm 2026")
print("Columns:", list(df.columns))

with open('temp_excel_out2.json', 'w', encoding='utf-8') as f:
    json.dump(df.fillna('').head(30).to_dict(orient='records'), f, ensure_ascii=False, indent=2)
