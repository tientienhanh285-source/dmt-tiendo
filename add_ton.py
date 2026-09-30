import os

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except:
                continue
            
            # 1. Add Tôn back to bld_members
            new_content = content.replace('"Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"', '"Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"')
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Added Ton to bld_members in {path}')
