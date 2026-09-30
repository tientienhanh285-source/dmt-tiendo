import pandas as pd
import json
import os
import glob

files = glob.glob('*HCNS*.xlsx')
if not files:
    print("No file found")
    exit()

filename = files[0]
print(f"Reading {filename}...")

df = pd.read_excel(filename, sheet_name=0)

with open('temp_excel_out.json', 'w', encoding='utf-8') as f:
    # Just save the first 20 rows to understand the structure
    json.dump(df.head(20).to_dict(orient='records'), f, ensure_ascii=False, indent=2)
