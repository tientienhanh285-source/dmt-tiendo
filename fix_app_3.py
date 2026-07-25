import re
import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add column mapping and NA handling in read_db
mapping_code = """
            df.columns = [str(c).strip() for c in df.columns]
            
            # 1. Tự động chuẩn hóa và ánh xạ tên cột
            col_mapping = {
                'Mã CV': 'ID', 'MaCV': 'ID',
                'Tên công việc': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nội dung': 'TenCongViec', 'Công việc': 'TenCongViec',
                'Tiến độ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiến độ': 'PhanTramHoanThanh',
                'Trạng thái': 'TrangThai', 'Status': 'TrangThai',
                'Hạn chót': 'Deadline', 'Ngày hoàn thành': 'Deadline'
            }
            new_cols = []
            for c in df.columns:
                matched = c
                for k, v in col_mapping.items():
                    if c.lower() == k.lower():
                        matched = v
                        break
                new_cols.append(matched)
            df.columns = new_cols
            
            # 3. Xử lý dữ liệu rỗng / NaN an toàn
            if 'PhanTramHoanThanh' in df.columns:
                import pandas as pd
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('Đang thực hiện')
                df['TrangThai'] = df['TrangThai'].replace('', 'Đang thực hiện')
"""

if "# 1. Tự động chuẩn hóa và ánh xạ tên cột" not in content:
    content = content.replace("df.columns = [str(c).strip() for c in df.columns]", mapping_code)

# 2. Add st.cache_data.clear() before st.rerun()
content = re.sub(r'(\s+)st\.rerun\(\)', r'\1st.cache_data.clear()\1st.rerun()', content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied fixes to app.py")
