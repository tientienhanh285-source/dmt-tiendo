import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

mapping_code = '''DEPT_ABBR = {
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
}
'''
if 'DEPT_ABBR = {' not in text:
    text = text.replace('DEPT_LEADS = {', mapping_code + '\nDEPT_LEADS = {')

# 1. Update Monthly KPI table
# Find: "Phòng ban": pb,
# Replace: "Phòng ban": DEPT_ABBR.get(pb, pb),
text = re.sub(
    r'"Phòng ban": pb,',
    r'"Phòng ban": DEPT_ABBR.get(pb, pb),',
    text
)

# 2. Update filtering for Monthly KPI table
# Find: if selected_dept_m != "Tất cả phòng ban":
#            kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == selected_dept_m]
text = re.sub(
    r'if selected_dept_m != "Tất cả phòng ban":\n\s+kpi_month_df = kpi_month_df\[kpi_month_df\["Phòng ban"\] == selected_dept_m\]',
    r'if selected_dept_m != "Tất cả phòng ban":\n            kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_m, selected_dept_m)]',
    text
)

# 3. Update Yearly KPI table
# Find: "Phòng ban": person_df['PhongBan'].mode()[0] if not person_df.empty else ""
# Replace: "Phòng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else ""
text = re.sub(
    r'"Phòng ban": person_df\[\'PhongBan\'\]\.mode\(\)\[0\] if not person_df\.empty else ""',
    r'"Phòng ban": DEPT_ABBR.get(person_df[\'PhongBan\'].mode()[0], person_df[\'PhongBan\'].mode()[0]) if not person_df.empty else ""',
    text
)

# 4. Update filtering for Yearly KPI table
# Find: if selected_dept_y != "Tất cả phòng ban":
#            yearly_df = yearly_df[yearly_df["Phòng ban"] == selected_dept_y]
text = re.sub(
    r'if selected_dept_y != "Tất cả phòng ban":\n\s+yearly_df = yearly_df\[yearly_df\["Phòng ban"\] == selected_dept_y\]',
    r'if selected_dept_y != "Tất cả phòng ban":\n                yearly_df = yearly_df[yearly_df["Phòng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]',
    text
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated successfully.")
