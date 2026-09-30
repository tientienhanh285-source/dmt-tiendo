import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Replace DEPT_LEADS
old_dept = """DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "BLĐ": "Trần Quốc Thể",
        "HCNS": "Nguyễn Thị Hạnh Tiên",
        "TCKT": "Đồng Thị Nguyệt Nga",
        "KHĐT": "Nguyễn Trần Thức",
        "CBĐT": "Hồ Văn Khoa",
        "KT": "Nguyễn Văn Bốn",
        "ĐBGT": "Nguyễn Ngọc Tôn",
        "DA": "Nguyễn Đình Thắng",
        "XN DTBD": "Mai Văn Châu",
        "Sàn GDBĐS": "Ngô Thị Tám",
        "Tổ KPI": ""
    }
}"""

new_dept = """DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đồng Thị Nguyệt Nga", "Đoàn Thị Ngọc Nữ"],
        "KHĐT": ["Nguyễn Trần Thức"],
        "CBĐT": ["Hồ Văn Khoa"],
        "KT": ["Nguyễn Văn Bốn"],
        "ĐBGT": ["Nguyễn Ngọc Tôn"],
        "DA": ["Nguyễn Đình Thắng"],
        "XN DTBD": ["Mai Văn Châu"],
        "Sàn GDBĐS": ["Ngô Thị Tám"]
    },
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {
        "BLĐ": ["Trần Quốc Thể"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đồng Thị Nguyệt Nga"]
    },
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "BLĐ": ["Trần Quốc Thể"],
        "HCNS": ["Nguyễn Thị Mỹ Phương"],
        "TCKT": ["Đồng Thị Nguyệt Nga"]
    }
}"""

if old_dept in content:
    content = content.replace(old_dept, new_dept)
else:
    print("Failed to replace DEPT_LEADS")

old_logic = """                dept_lead = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, "")
                
                # Make sure the department lead is at the top or selected by default if exists
                default_idx = 0
                if dept_lead in personnel_list:
                    default_idx = personnel_list.index(dept_lead)
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + personnel_list, index=default_idx + 1 if dept_lead else 0, key="mgr_login_user")"""

new_logic = """                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                
                # Filter personnel_list to only include dept_leads
                valid_leads = [lead for lead in dept_leads if lead in personnel_list]
                
                if valid_leads:
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + valid_leads, key="mgr_login_user")
                else:
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + personnel_list, key="mgr_login_user")"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
else:
    print("Failed to replace logic")

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Done!")
