import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
import glob

f = glob.glob(r"c:\Users\Admin\Desktop\AG\Theodoitiendo\Ban HCNS*.xlsx")[0]
xls = pd.ExcelFile(f)
print(f"Sheets: {xls.sheet_names}".encode('utf-8').decode('utf-8'))
