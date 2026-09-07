import pandas as pd
import glob
import os

try:
    df = pd.read_excel('c:/Users/Admin/Desktop/AG/Theodoitiendo/INPUT/DMT Group/tieu chi 06.2026.xlsx', sheet_name=None)
    with open('c:/Users/Admin/Desktop/AG/Theodoitiendo/template_excel_info.txt', 'w', encoding='utf-8') as f:
        for sheet, data in df.items():
            f.write(f"Sheet: {sheet}\n")
            f.write(f"Columns: {list(data.columns)}\n")
            f.write(f"Sample data:\n{data.head(5).to_string()}\n")
            f.write("-" * 50 + "\n")
    print("Excel info saved to template_excel_info.txt")
except Exception as e:
    print("Error reading excel:", e)
