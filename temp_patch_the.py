import glob
import os

files = glob.glob('views/*.py')
old = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bốn"]'
new = '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]'

c = 0
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if old in content:
            content = content.replace(old, new)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Replaced in {f}")
            c += 1
    except Exception as e:
        print(f"Error in {f}: {e}")

print(f"Total replaced: {c}")
