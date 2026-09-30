import codecs
import re

app_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py'
with codecs.open(app_file, 'r', 'utf-8') as f:
    app_content = f.read()

new_dept_leads = """DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đồng Thị Nguyệt Nga"],
        "KHĐT": ["Nguyễn Trần Thức"],
        "CBĐT": ["Hồ Văn Khoa"],
        "KT": ["Trần Quốc Thể"],
        "ĐBGT": ["Nguyễn Ngọc Tôn"],
        "DA": ["Nguyễn Đình Thắng"],
        "XN DTBD": ["Mai Văn Châu"],
        "Sàn GDBĐS": ["Ngô Thị Tâm"],
        "Tổ KPI": []
    },
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "HĐQT": ["Đặng Thanh Bình", "Đặng Ngọc Hoàng"],
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Nguyễn Ngọc Tôn"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"],
        "KT": ["Trần Văn Trọng", "Phạm Quang Nghĩa"],
        "BCH CT": ["Nguyễn Phong Trung"],
        "XN XMTB": ["Đặng Hiền"]
    }
}"""

app_content = re.sub(r'DEPT_LEADS = \{[\s\S]*?\}\n\}', new_dept_leads, app_content, count=1)
with codecs.open(app_file, 'w', 'utf-8') as f:
    f.write(app_content)
