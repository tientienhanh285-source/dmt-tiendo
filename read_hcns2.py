import pandas as pd
import glob
import os

files = glob.glob(r"c:\Users\Admin\Desktop\AG\Theodoitiendo\Ban HCNS*.xlsx")
if not files:
    print("No files found!")
else:
    for f in files:
        print("Found file:", repr(f))
        try:
            df = pd.read_excel(f)
            print("Successfully read")
            print(df.columns)
            print(df.head(2))
        except Exception as e:
            print("Error reading:", e)
