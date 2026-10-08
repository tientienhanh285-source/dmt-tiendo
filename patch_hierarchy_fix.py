import glob
import os

files = glob.glob('views/*.py')
approval_views = ['4_Nghiem_Thu.py', '4_Nghiem_Thu_KQ.py', '9_Lap_Duyet_KPI.py']

old_the_full = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]'
new_the_short = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]'

old_nu_full = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"]'
new_nu_short = '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"]'

def patch_file(f, the_old, the_new, nu_old, nu_new):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    if the_old in content:
        content = content.replace(the_old, the_new)
        modified = True
    if nu_old in content:
        content = content.replace(nu_old, nu_new)
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Replaced in {f}")

for f in files:
    filename = os.path.basename(f)
    if filename in approval_views:
        patch_file(f, old_the_full, new_the_short, old_nu_full, new_nu_short)
    else:
        patch_file(f, new_the_short, old_the_full, new_nu_short, old_nu_full)

print("Done patching properly.")
