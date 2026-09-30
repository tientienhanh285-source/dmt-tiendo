import codecs
import re

core_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py'
with codecs.open(core_file, 'r', 'utf-8') as f:
    content = f.read()

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
        "Sàn GDBĐS": ["Ngô Thị Tâm"]
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

content = re.sub(r'DEPT_LEADS = \{[\s\S]*?\}\n\}', new_dept_leads, content, count=1)

new_func = '''def get_personnel_for_company_dept(company, dept, config):
    companies = config.get("companies", {})
    personnel_list = []
    if company in companies:
        personnel_list = companies[company].get("personnel_by_department", {}).get(dept, [])
    else:
        # Fallback to global config if any, or empty list
        personnel_list = config.get("personnel_by_department", {}).get(dept, [])
        
    # Exclude managers from the personnel list
    dept_leads = DEPT_LEADS.get(company, {}).get(dept, [])
    if isinstance(dept_leads, str):
        dept_leads = [dept_leads] if dept_leads else []
        
    return [p for p in personnel_list if p not in dept_leads]'''

content = re.sub(r'def get_personnel_for_company_dept\(company, dept, config\):[\s\S]*?return config\.get\("personnel_by_department", \{\}\)\.get\(dept, \[\]\)', new_func, content, count=1)

with codecs.open(core_file, 'w', 'utf-8') as f:
    f.write(content)
print('Done')
