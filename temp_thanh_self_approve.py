import os

old_str = '"Thái Văn Thành": ["Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"]'
new_str = '"Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"]'

count = 0
for root, dirs, files in os.walk('views'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if old_str in content:
                content = content.replace(old_str, new_str)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1

print(f'Updated {count} files for bld_hierarchy.')

# Now patch 4_Nghiem_Thu.py and 4_Nghiem_Thu_KQ.py to allow him to approve his own tasks
import re

for file in ['views/4_Nghiem_Thu.py', 'views/4_Nghiem_Thu_KQ.py']:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace:
    # if 'manager_user' in locals() and manager_user:
    #     nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'] != manager_user]
    
    patch = '''            if 'manager_user' in locals() and manager_user:
                if manager_user != "Thái Văn Thành":
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'] != manager_user]'''
    
    content = re.sub(r"            if 'manager_user' in locals\(\) and manager_user:\n\s+nghiemthu_df = nghiemthu_df\[nghiemthu_df\['NguoiChuTri'\] != manager_user\]", patch, content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Patched self-approval in {file}')
