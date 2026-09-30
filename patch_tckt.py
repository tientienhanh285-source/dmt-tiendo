import codecs

for file in ['c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py']:
    with codecs.open(file, 'r', 'utf-8') as f:
        content = f.read()
    content = content.replace('"TCKT": ["Đồng Thị Nguyệt Nga"]', '"TCKT": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"]')
    with codecs.open(file, 'w', 'utf-8') as f:
        f.write(content)
print('Updated TCKT')
