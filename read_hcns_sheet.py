import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
import glob

f = glob.glob(r"c:\Users\Admin\Desktop\AG\Theodoitiendo\Ban HCNS*.xlsx")[0]
df = pd.read_excel(f, sheet_name='A7.9.KPI Ban HCNS Quy 2.26')
print(df.columns)
print(df.head(10).to_string())
