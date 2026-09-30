with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "views/8_Quan_Tri_BSC.py" in line or "views/9_Lap_Duyet_KPI.py" in line:
        continue
    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
