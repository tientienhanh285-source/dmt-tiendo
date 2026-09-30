import os
import re

def update_bld_hierarchy(content):
    # Regex to find bld_hierarchy dict and replace it
    # We want to ensure Tôn is in there.
    
    # We will just replace the specific line for Nữ and add Tôn right after it.
    old_nu = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"],'
    new_nu_ton = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"],\n                    "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],'
    
    if old_nu in content:
        return content.replace(old_nu, new_nu_ton)
    
    # Try another variation with different spacing
    old_nu2 = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"]'
    if old_nu2 in content and '"Nguyễn Ngọc Tôn"' not in content:
        return content.replace(old_nu2, new_nu_ton)

    return content

for root, dirs, files in os.walk('views'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = update_bld_hierarchy(content)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Updated bld_hierarchy in {path}')
