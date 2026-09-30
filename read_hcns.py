import pandas as pd
import os

filepath = os.path.join(r"c:\Users\Admin\Desktop\AG\Theodoitiendo", "Ban HCNS - KPI QUY II.xlsx")
print("File exists:", os.path.exists(filepath))
try:
    df = pd.read_excel(filepath)
    print(df.columns)
    print(df.head(2))
except Exception as e:
    print("Error:", e)
