import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Remove task_weight selectbox
    if 'task_weight = st.number_input("Tỷ trọng KPI' in line or 'task_weight = st.number_input("T tr?ng KPI' in line:
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + "task_weight = 0\n")
        continue

    # Remove u_weight section
    if 'current_weight = int(float(str(task_data.get(\'TyTrongKPI\', 0)).strip() or 0))' in line:
        skip = True
        
    if 'st.caption("💡 **Lưu ý:**' in line or 'st.caption("dY' in line:
        if skip:
            skip = False
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + "u_weight = current_weight\n")
            continue

    if not skip:
        # Also let's catch the try/except block before it if skip missed it
        if line.strip() == 'try:' and 'current_weight =' in lines[i+1]:
            skip = True
        elif not skip:
            new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done")
