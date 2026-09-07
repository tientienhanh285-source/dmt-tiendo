import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "current_link = task_data['LinkKetQua']" in line:
        # Keep this line, we might still need current_link later (e.g. for condition checks)
        new_lines.append(line)
        skip = True
        continue
    
    if skip:
        if "if u_is_completed:" in line:
            skip = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done")
