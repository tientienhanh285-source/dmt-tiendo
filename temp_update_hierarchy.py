import os

old_str = '"Trần Văn Trọng": ["Lê Nho Tân", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]'
new_str = '"Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]'

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
                print(f'Updated {path}')
                count += 1

print(f'Updated {count} files.')
