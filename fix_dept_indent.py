with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'if selected_dept_m != "Tất cả phòng ban":' in line:
        # Determine the indentation of the if statement
        indent = len(line) - len(line.lstrip())
        lines[i+1] = (' ' * (indent + 4)) + 'kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_m, selected_dept_m)]\n'
    if 'if selected_dept_y != "Tất cả phòng ban":' in line:
        indent = len(line) - len(line.lstrip())
        lines[i+1] = (' ' * (indent + 4)) + 'yearly_df = yearly_df[yearly_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]\n'

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
