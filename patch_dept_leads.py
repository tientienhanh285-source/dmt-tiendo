import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

dept_leads_str = '''DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "BLĐ": "Trần Quốc Thể",
        "HCNS": "Nguyễn Thị Hạnh Tiên",
        "TCKT": "Đồng Thị Nguyệt Nga",
        "KHĐT": "Nguyễn Trần Thức",
        "CBĐT": "Hồ Văn Khoa",
        "KT": "Nguyễn Văn Bồn",
        "ĐBGT": "Nguyễn Ngọc Tôn",
        "DA": "Nguyễn Đình Thắng",
        "XN DTBD": "Mai Văn Châu",
        "Sàn GDBĐS": "Ngô Thị Tâm",
        "Tổ KPI": ""
    }
}'''
text = re.sub(r'DEPT_LEADS = \{.*?\n\s+\}\n\}', dept_leads_str, text, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated DEPT_LEADS")
