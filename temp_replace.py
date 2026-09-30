import sys

content = open('app.py', encoding='utf-8').read()

# Replace all other instances
content = content.replace('role_mode == "Cá nhân (Thử nghiệm)"', 'role_mode == "Nhân viên"')

open('app.py', 'w', encoding='utf-8').write(content)
print('Replacement complete.')
