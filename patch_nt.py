import codecs

def patch_file(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
        text = f.read()

    bad1 = '''                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
                if manager_user in bld_members:
                    if st.session_state.manager_dept == "BLĐ":
                        bld_hierarchy = {
                            "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                            "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"],
                            "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hành Tiên"]
                        }'''
    good1 = '''                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
                if manager_user in bld_members:
                    if st.session_state.manager_dept == "BLĐ":
                        bld_hierarchy = {
                            "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bốn"],
                            "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"],
                            "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                            "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hành Tiên", "Trần Cường", "Ngô Thị Tám"],
                            "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bốn"],
                            "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển"],
                            "Trần Cường": ["Trần Cường", "Ngô Thị Tám"],
                            "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
                            "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
                        }'''
    if bad1 in text:
        text = text.replace(bad1, good1)
        print(f'Replaced block in {filename}')
    
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(text)

import glob
files = glob.glob('views/*.py')
for file in files:
    patch_file(file)
