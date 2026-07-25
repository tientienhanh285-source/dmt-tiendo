import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Refactor read_gantt_db
pattern = r'(def read_gantt_db\(\):)\n(\s+conn = get_gsheets_conn\(\))'
replacement = r'\1\n    required_cols = ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]\n\2'
content = re.sub(pattern, replacement, content)
content = content.replace('pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])', 'pd.DataFrame(columns=required_cols)')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Refactored read_gantt_db.')
