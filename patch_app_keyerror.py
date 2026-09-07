import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

t = "if p['Nhân viên'] == emp_to_export:"
r = "if p['Người thực hiện'] == emp_to_export:"

if t in content:
    content = content.replace(t, r)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched app.py successfully!")
else:
    print("Target not found.")
