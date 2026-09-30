import pandas as pd
import glob

f = glob.glob(r"c:\Users\Admin\Desktop\AG\Theodoitiendo\Ban HCNS*.xlsx")[0]
xls = pd.ExcelFile(f)
print("Sheets:", xls.sheet_names)
for sheet in xls.sheet_names:
    print(f"\n--- {sheet} ---")
    df = pd.read_excel(f, sheet_name=sheet)
    print(df.head(5))
