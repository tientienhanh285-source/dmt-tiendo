import codecs
import json
import re
import os

# 1. Update app.py
app_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py'
with codecs.open(app_file, 'r', 'utf-8') as f:
    app_content = f.read()

# Update DEPT_ABBR
new_dept_abbr = """DEPT_ABBR = {
    "Hội đồng quản trị": "HĐQT",
    "Ban Lãnh đạo": "BLĐ",
    "Ban Hành chính Nhân sự": "HCNS",
    "Ban Tài chính Kế toán": "TCKT",
    "Ban Kế hoạch Đầu tư": "KHĐT",
    "Ban Chuẩn bị Đầu tư": "CBĐT",
    "Ban Kỹ thuật": "KT",
    "Ban Đền bù Giải tỏa": "ĐBGT",
    "Ban Dự án": "DA",
    "Xí nghiệp DTBD": "XN DTBD",
    "Sàn GDBĐS": "Sàn GDBĐS",
    "Tổ KPI": "Tổ KPI"
}"""
app_content = re.sub(r'DEPT_ABBR = \{[\s\S]*?\}', new_dept_abbr, app_content)

# Update DEPT_LEADS
new_dept_leads = """DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "HĐQT": ["Đặng Thanh Bình", "Đặng Ngọc Hoàng"],
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"],
        "KHĐT": ["Nguyễn Trần Thức"],
        "CBĐT": ["Hồ Văn Khoa"],
        "KT": ["Trần Quốc Thể"],
        "ĐBGT": ["Nguyễn Ngọc Tôn"],
        "DA": ["Nguyễn Đình Thắng"],
        "XN DTBD": ["Mai Văn Châu"],
        "Sàn GDBĐS": ["Ngô Thị Tâm"],
        "Tổ KPI": []
    }
}"""
# Only replace the first match of DEPT_LEADS
app_content = re.sub(r'DEPT_LEADS = \{[\s\S]*?\n\}', new_dept_leads, app_content, count=1)

with codecs.open(app_file, 'w', 'utf-8') as f:
    f.write(app_content)

# 2. Update core_logic.py
core_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py'
with codecs.open(core_file, 'r', 'utf-8') as f:
    core_content = f.read()

new_default_personnel = """DEFAULT_PERSONNEL = {
    "Hội đồng quản trị": ["Đặng Thanh Bình", "Đặng Ngọc Hoàng"],
    "Ban Lãnh đạo": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"],
    "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"],
    "Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Đoàn Thị Ngọc Nữ"],
    "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Phan Thị Mỹ Hạnh", "Nguyễn Đức Lợi", "Trần Tin"],
    "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],
    "Ban Kỹ thuật": ["Nguyễn Văn Bồn"],
    "Ban Đền bù Giải tỏa": ["Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Ban chỉ huy Công trường": ["Nguyễn Phong Trung", "Phạm Văn Long", "Lê Đông"],
    "Xí nghiệp xe máy thiết bị": ["Đặng Hiền"],
    "Ban Dự án": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
    "Xí nghiệp DTBD": ["Mai Văn Châu"],
    "Sàn GDBĐS": ["Ngô Thị Tâm"],
    "Tổ KPI": []
}"""
core_content = re.sub(r'DEFAULT_PERSONNEL = \{[\s\S]*?\]\n\}', new_default_personnel, core_content)
core_content = re.sub(r'DEPT_LEADS = \{[\s\S]*?\n\}', new_dept_leads, core_content, count=1)

with codecs.open(core_file, 'w', 'utf-8') as f:
    f.write(core_content)

# 3. Update CONFIG_PROJECTS.json
config_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/OUTPUT/CONFIG_PROJECTS.json'
with codecs.open(config_file, 'r', 'utf-8') as f:
    config_data = json.load(f)

# Add "Hội đồng quản trị" if not present
if "Hội đồng quản trị" not in config_data["departments"]:
    config_data["departments"].insert(0, "Hội đồng quản trị")

# Update personnel mapping
p = config_data.get("personnel_by_department", {})

if "Hội đồng quản trị" not in p:
    p["Hội đồng quản trị"] = []
for user in ["Đặng Thanh Bình", "Đặng Ngọc Hoàng"]:
    if user not in p["Hội đồng quản trị"]:
        p["Hội đồng quản trị"].append(user)

if "Ban Lãnh đạo" not in p:
    p["Ban Lãnh đạo"] = []
for user in ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ"]:
    if user not in p["Ban Lãnh đạo"]:
        p["Ban Lãnh đạo"].append(user)

if "Ban Hành chính Nhân sự" not in p:
    p["Ban Hành chính Nhân sự"] = []
for user in ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"]:
    if user not in p["Ban Hành chính Nhân sự"]:
        p["Ban Hành chính Nhân sự"].append(user)

if "Ban Tài chính Kế toán" not in p:
    p["Ban Tài chính Kế toán"] = []
for user in ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"]:
    if user not in p["Ban Tài chính Kế toán"]:
        p["Ban Tài chính Kế toán"].append(user)

config_data["personnel_by_department"] = p

with codecs.open(config_file, 'w', 'utf-8') as f:
    json.dump(config_data, f, ensure_ascii=False, indent=4)
print("Updated permissions!")
