import glob
import os

approval_views = ['views/4_Nghiem_Thu.py', 'views/4_Nghiem_Thu_KQ.py', 'views/9_Lap_Duyet_KPI.py']
progress_views = [f for f in glob.glob('views/*.py') if f not in approval_views]

# We need to change the arrays in ALL files to their respective logic.
# Wait, let's just do a string replacement.
# But I must be careful because the arrays might have different indentations.
# A better way is to use regex or string replace.

old_the_full = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]'
new_the_short = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]'

old_nu_full = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"]'
new_nu_short = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"]'

def patch_file(f, the_full, the_new, nu_full, nu_new):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    if the_full in content:
        content = content.replace(the_full, the_new)
        modified = True
    if nu_full in content:
        content = content.replace(nu_full, nu_new)
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Replaced in {f}")

for f in approval_views:
    if os.path.exists(f):
        patch_file(f, old_the_full, new_the_short, old_nu_full, new_nu_short)
        
for f in progress_views:
    # Ensure they have the full arrays
    if os.path.exists(f):
        patch_file(f, new_the_short, old_the_full, new_nu_short, old_nu_full)
        
print("Done patching.")
