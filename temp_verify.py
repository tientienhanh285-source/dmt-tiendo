import glob

files = glob.glob('views/*.py')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên", "Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin", "Phan Thị Kim Cúc", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]' in content:
        print(f, 'FULL THE')
    elif '"Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn", "Nguyễn Văn Bốn"]' in content:
        print(f, 'SHORT THE')
        
    if '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"]' in content:
        print(f, 'FULL NU')
    elif '"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"]' in content:
        print(f, 'SHORT NU')
