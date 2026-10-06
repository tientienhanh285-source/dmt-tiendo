import re

with open('views/5_Danh_Gia_KPI.py', 'r', encoding='utf-8') as f:
    text = f.read()

good_block = '''            bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
            if manager_user in bld_members:
                if selected_dept_m == "BLĐ":
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

pattern1 = r'bld_members = \["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"\]\s+if manager_user in bld_members:\s+if selected_dept_m == "BLĐ":\s+bld_hierarchy = \{\s+"Trần Quốc Thể": \["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"\],\s+"Đoàn Thị Ngọc Nữ": \["Đồng Thị Nguyệt Nga"\],\s+"Đặng Ngọc Hoàng": \["Đặng Ngọc Hoàng", "Nguyễn Thị Hành Tiên"\]\s+\}'
text = re.sub(pattern1, good_block, text)

good_block2 = '''                    bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
                    if manager_user in bld_members:
                        if selected_dept_y == "BLĐ":
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

pattern2 = r'bld_members = \["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"\]\s+if manager_user in bld_members:\s+if selected_dept_y == "BLĐ":\s+bld_hierarchy = \{\s+"Trần Quốc Thể": \["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"\],\s+"Đoàn Thị Ngọc Nữ": \["Đồng Thị Nguyệt Nga"\],\s+"Đặng Ngọc Hoàng": \["Đặng Ngọc Hoàng", "Nguyễn Thị Hành Tiên"\]\s+\}'
text = re.sub(pattern2, good_block2, text)

with open('views/5_Danh_Gia_KPI.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced successfully')
