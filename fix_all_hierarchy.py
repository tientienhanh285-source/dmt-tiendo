import glob
import re
import codecs

good_hierarchy = '''bld_hierarchy = {
                        "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bốn"],
                        "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"],
                        "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                        "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tám"],
                        "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bốn"],
                        "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển"],
                        "Trần Cường": ["Trần Cường", "Ngô Thị Tám"],
                        "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
                        "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
                    }'''

for file in glob.glob('views/*.py'):
    with codecs.open(file, 'r', 'utf-8') as f:
        text = f.read()
    
    # We find all occurrences of "bld_hierarchy = {" and replace them.
    # We will use regex: bld_hierarchy\s*=\s*\{.*?\}
    # But wait, there might be other dicts. We can use a regex that looks for bld_hierarchy and matches until the FIRST matching '}' 
    # Or just replace the entire block using re.sub with DOTALL.
    # The regex: r"bld_hierarchy\s*=\s*\{[^\}]*\}"
    # Wait, the dict contains lists which have ']' but no '}'. 
    # So r"bld_hierarchy\s*=\s*\{[^\}]*\}" will perfectly match the dictionary!
    
    new_text = re.sub(r"bld_hierarchy\s*=\s*\{[^\}]*\}", good_hierarchy, text)
    
    if new_text != text:
        with codecs.open(file, 'w', 'utf-8') as f:
            f.write(new_text)
        print(f"Updated {file}")
