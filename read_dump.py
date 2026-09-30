import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
f = r"c:\Users\Admin\Desktop\AG\Theodoitiendo\data_dump.xlsx"
df = pd.read_excel(f)
print("Length:", len(df))
print(df.columns)
print(df.head(2).to_string())
