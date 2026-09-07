import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_block = False
for i, line in enumerate(lines):
    if '# 9. Kết quả / File đính kèm' in line:
        new_lines.append(line)
        new_lines.append('            if task_has_issue:\n')
        new_lines.append('                task_file = None\n')
        new_lines.append('                task_link_text = ""\n')
        new_lines.append('                result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"\n')
        new_lines.append('            else:\n')
        in_block = True
        continue
    if in_block:
        if '# 10. Ghi chú vướng mắc' in line:
            in_block = False
            new_lines.append(line)
        else:
            new_lines.append('    ' + line)
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done')
