import os
import re

count = 0
for root, dirs, files in os.walk('views'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            old_str_1 = '"Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"]'
            new_str_1 = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"]'
            
            old_str_2 = '"Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"]'
            new_str_2 = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"]'
            
            old_str_3 = '"Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"]'
            new_str_3 = '"Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên"]'
            
            modified = False
            if old_str_1 in content:
                content = content.replace(old_str_1, new_str_1)
                modified = True
            if old_str_2 in content:
                content = content.replace(old_str_2, new_str_2)
                modified = True
            if old_str_3 in content:
                content = content.replace(old_str_3, new_str_3)
                modified = True
                
            if modified:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1

print(f'Updated {count} files for bld_hierarchy.')

for file in ['views/4_Nghiem_Thu.py', 'views/4_Nghiem_Thu_KQ.py']:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace:
    #             if manager_user != "Thái Văn Thành":
    #                 nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'] != manager_user]
    
    patch = '''            if 'manager_user' in locals() and manager_user:
                if manager_user not in ["Thái Văn Thành", "Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"]:
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'] != manager_user]'''
    
    content = re.sub(r"            if 'manager_user' in locals\(\) and manager_user:\n\s+if manager_user != \"Thái Văn Thành\":\n\s+nghiemthu_df = nghiemthu_df\[nghiemthu_df\['NguoiChuTri'\] != manager_user\]", patch, content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Patched self-approval in {file}')
