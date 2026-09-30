import traceback
from core_logic import get_gsheets_conn

conn = get_gsheets_conn()
new_row = {
    'ID': 'a1b2c3d4', 
    'TenNhanVien': 'Test', 
    'Thang': 9, 
    'Nam': 2026, 
    'LoaiHanhVi': 'Thuong', 
    'DiemDieuChinh': 5, 
    'LyDo': 'Test'
}

try:
    conn.table('kpi_adjustments').insert(new_row).execute()
    print('Success')
except Exception as e:
    print('Error:', e)
    traceback.print_exc()
