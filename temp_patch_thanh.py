import glob
import os

files = glob.glob('views/*.py')
old = '"Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bốn"]'
new = '"Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bốn", "Nguyễn Văn Bồn"]'

# Some files might have "Nguyễn Thị Mỹ Phương" or "Đặng Hiền" instead due to typos, let's also patch the other variants just in case.
old2 = '"Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân", "Nguyễn Văn Bốn"]'
new2 = '"Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân", "Nguyễn Văn Bốn", "Nguyễn Văn Bồn"]'

c = 0
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        replaced = False
        if old in content:
            content = content.replace(old, new)
            replaced = True
        if old2 in content:
            content = content.replace(old2, new2)
            replaced = True
            
        if replaced:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Replaced in {f}")
            c += 1
    except Exception as e:
        print(f"Error in {f}: {e}")

print(f"Total replaced: {c}")
