import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'df = read_gantt_db()' in line:
        continue
    if 'df_for_excel = read_gantt_db()' in line:
        line = line.replace('read_gantt_db()', 'df')
    if 'color="GiaiDoan"' in line:
        line = line.replace('color="GiaiDoan"', 'color="TrangThai"')
    if 'hover_data=["PhanTramHoanThanh", "Milestone"]' in line:
        line = line.replace('hover_data=["PhanTramHoanThanh", "Milestone"]', 'hover_data=["PhanTramHoanThanh", "MocTienDo"]')
    if 'legend_title_text="Giai đoạn"' in line:
        line = line.replace('legend_title_text="Giai đoạn"', 'legend_title_text="Trạng thái"')
    
    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
