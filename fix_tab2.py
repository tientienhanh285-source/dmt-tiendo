# -*- coding: utf-8 -*-
lines = []
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if line.startswith('    with kpi_tab2:'):
        start_idx = i
        break

end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if 'st.session_state.is_admin_authenticated:' in lines[i] and 'kpi_tab3:' in lines[i+1]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx]
    new_lines.append("    if 'kpi_tab2' in locals():\n")
    new_lines.append("        with kpi_tab2:\n")

    for line in lines[start_idx+1:end_idx]:
        if line.strip():
            new_lines.append('    ' + line)
        else:
            new_lines.append(line)

    new_lines.extend(lines[end_idx:])

    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Done!")
else:
    print(f"Failed! start_idx={start_idx}, end_idx={end_idx}")