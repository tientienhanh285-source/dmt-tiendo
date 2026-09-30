import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
f = r"c:\Users\Admin\Desktop\AG\Theodoitiendo\OUTPUT\DATA_TIEN_DO_KPI.xlsx"
df = pd.read_excel(f)
print("Length:", len(df))
print("PhongBan unique:", df['PhongBan'].unique())
print(df.head(2).to_string())
