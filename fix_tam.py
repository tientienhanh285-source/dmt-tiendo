import glob
import os

files = glob.glob('views/*.py')
files.append('core_logic.py')
files.append('app.py')

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    if 'Ngô Thị Tám' in content:
        content = content.replace('Ngô Thị Tám', 'Ngô Thị Tâm')
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
