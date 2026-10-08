import sys
sys.path.append('.')
from core_logic import get_gsheets_conn
conn = get_gsheets_conn()
response = conn.table('kpi_config').select('DonVi, PhongBan, NguoiChuTri').execute()
for row in response.data:
    if row['DonVi'] == 'CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG' and row['PhongBan'] in ['KHĐT', 'CBĐT', 'KT', 'XN DTBD', 'XN ĐTBD']:
        print(f"{row['PhongBan']}: {row['NguoiChuTri']}")
