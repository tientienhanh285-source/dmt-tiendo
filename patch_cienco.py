import glob

# The replacement logic for bld_hierarchy
# We want to replace the old bld_hierarchy block with the new one

old_block = '''        bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
        if manager_user in bld_members:
            if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"],
                    "Thái Văn Thành": ["Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đồng", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"],
                    "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đồng", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]
                }'''

new_block = '''        bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
        if manager_user in bld_members:
            if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"],
                    "Thái Văn Thành": ["Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"],
                    "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]
                }'''

files_changed = 0
for filepath in glob.glob('views/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        files_changed += 1
        print(f"Updated {filepath}")
    else:
        # Maybe it uses double quotes or slight formatting diff? Let's check a loose replace
        print(f"Skipped {filepath}, could not find exact match")

print(f"Total files updated: {files_changed}")
