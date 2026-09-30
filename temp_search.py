import sys
with open('views/5_Danh_Gia_KPI.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('temp_out.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if 'selected_dept' in line:
            f.write(f"{i+1}: {line}")
