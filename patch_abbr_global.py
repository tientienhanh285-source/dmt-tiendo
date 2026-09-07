import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

config_map_code = '''config = load_config()

DEPT_ABBR = {
    "Ban Lãnh đạo": "BLĐ",
    "Lãnh đạo": "BLĐ",
    "Ban Hành chính Nhân sự": "HCNS",
    "Ban Tài chính Kế toán": "TCKT",
    "Ban Kế hoạch Đầu tư": "KHĐT",
    "Ban Chuẩn bị Đầu tư": "CBĐT",
    "Ban Kỹ thuật": "KT",
    "Ban Đền bù Giải tỏa": "ĐBGT",
    "Ban Dự án": "DA",
    "Xí nghiệp DTBD": "XN DTBD",
    "Sàn GDBĐS": "Sàn GDBĐS",
    "Tổ KPI": "Tổ KPI",
    "Ban chỉ huy Công trường": "BCH CT",
    "Xí nghiệp xe máy thiết bị": "XN XMTB",
    "Xí nghiệp xe thiết bị": "XN XMTB"
}

for comp_name, comp_data in config.get("companies", {}).items():
    if "departments" in comp_data:
        comp_data["departments"] = [DEPT_ABBR.get(d, d) for d in comp_data["departments"]]
    if "personnel_by_department" in comp_data:
        new_personnel = {}
        for d, p in comp_data["personnel_by_department"].items():
            new_personnel[DEPT_ABBR.get(d, d)] = p
        comp_data["personnel_by_department"] = new_personnel
'''

# Find config = load_config() and replace it
text = re.sub(r'^config = load_config\(\)$', config_map_code, text, flags=re.MULTILINE)

# Now find df = read_db()
df_map_code = '''df = read_db()
if not df.empty and "PhongBan" in df.columns:
    df["PhongBan"] = df["PhongBan"].map(lambda x: DEPT_ABBR.get(x, x))
'''
text = re.sub(r'^df = read_db\(\)$', df_map_code, text, flags=re.MULTILINE)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated")
