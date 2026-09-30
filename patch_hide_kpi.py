import sys

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"📊 Quản trị BSC - KPI",', '# "📊 Quản trị BSC - KPI",')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Hide menu successfully!')
