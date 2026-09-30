import codecs

for file in ['c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py']:
    with codecs.open(file, 'r', 'utf-8') as f:
        content = f.read()
    
    # We don't want to replace with regex because the existing text might have ANSI corruption in app.py.
    # Wait, the ANSI corruption in app.py is just how powershell reads it. Inside python with utf-8, it's fine.
    # Let's replace the company name in DEPT_LEADS
    content = content.replace('"CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"', '"CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"')
    content = content.replace('"CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"', '"CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"')
    
    with codecs.open(file, 'w', 'utf-8') as f:
        f.write(content)
print('Fixed company names in DEPT_LEADS')
