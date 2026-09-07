with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lệnh sửa thụt lề từ dòng 3740 đến 3818 (cộng 4 spaces)
for i in range(3740, 3819):
    if i < len(lines):
        if lines[i].strip() != '':
            lines[i] = "    " + lines[i]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
