#
# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'emp_to_export = st.selectbox' in line and 'emp_export' in line:
        spaces = line[:len(line) - len(line.lstrip())]
        lines.insert(i, spaces + 'st.info(f"Đang xuất dữ liệu của: **Tháng {selected_month}/{selected_year}** (Để xuất tháng khác, vui lòng đổi Tháng/Năm ở trên cùng).")\n')
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
