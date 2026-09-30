from core_logic import read_db
import pandas as pd

df = read_db()
print(f"Total tasks in DB: {len(df)}")
print("Data types:")
print(df.dtypes)
print("\nChecking for nulls in critical columns:")
critical = ['Deadline', 'TrangThai', 'PhanTramHoanThanh', 'PhongBan']
for col in critical:
    if col in df.columns:
        null_count = df[col].isna().sum()
        print(f"{col} nulls: {null_count}")

# Check if any tasks have missing status
invalid_status = df[~df['TrangThai'].isin(['Chưa bắt đầu', 'Đang thực hiện', 'Hoàn thành', 'Hoàn thành (Trễ hạn)', 'Quá hạn', 'Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)', 'Có vướng mắc'])]
if len(invalid_status) > 0:
    print(f"\nFound {len(invalid_status)} tasks with weird status:")
    print(invalid_status[['ID', 'TrangThai']].head())

print("\nData looks structurally sound if no major errors above.")
