import pandas as pd
from core_logic import get_gsheets_conn

df = pd.read_excel(r"c:\Users\Admin\Desktop\AG\Theodoitiendo\data_dump.xlsx")
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

hcns_df = df[df['PhongBan'].str.contains('Hành chính Nhân sự', na=False, case=False)].copy()
print(f"Found {len(hcns_df)} tasks for Ban HCNS in data_dump.xlsx")

allowed_cols = ["ID", "NguoiCapNhat", "ThoiGianCapNhat", "TenDuAn", "DonVi", "PhongBan", "NguoiChuTri", "MocTienDo", "SanPhamBanGiao", "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", "TrangThai", "PhanTramHoanThanh", "PhanLoaiTreHan", "LinkKetQua", "GiaiTrinhDeXuat", "TyTrongKPI", "ChuKyTheoDoi", "NguonGiaoViec", "MucDoGhiNhan"]

conn = get_gsheets_conn()
if conn:
    data = hcns_df.to_dict('records')
    filtered_data = []
    for row in data:
        new_row = {}
        for k, v in row.items():
            if k in allowed_cols:
                if pd.isna(v):
                    new_row[k] = ""
                else:
                    new_row[k] = str(v)
        filtered_data.append(new_row)
        
    try:
        res = conn.table("tasks").upsert(filtered_data).execute()
        print("Success! Restored", len(res.data), "records.")
    except Exception as e:
        print("Error upserting to Supabase:", e)
else:
    print("Could not connect to Supabase.")
