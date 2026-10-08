import sqlite3
import pandas as pd

conn = sqlite3.connect('database.db')
query = '''
SELECT DISTINCT NguoiChuTri, TrangThai, DonVi, PhongBan 
FROM tasks 
WHERE NguoiChuTri IN ("Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn")
'''
df = pd.read_sql_query(query, conn)
print(df)
conn.close()
