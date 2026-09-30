import codecs
import re

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Replace DEPT_LEADS
new_dept_leads = """DEPT_LEADS = {
    "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
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
    "CÔNG TY CP DMT - MARINA (Du thuyền Happy Yacht)": {
        "BLĐ": ["Trần Quốc Thể"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đồng Thị Nguyệt Nga"]
    },
    "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "BLĐ": ["Trần Quốc Thể"],
        "HCNS": ["Nguyễn Thị Mỹ Phương"],
        "TCKT": ["Đồng Thị Nguyệt Nga"]
    }
}"""

# Replace old DEPT_LEADS block
# Note: old block uses CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG, need to match exactly
old_dept_leads_regex = r"DEPT_LEADS = \{[\s\S]*?\"Tổ KPI\": \"\"\n\s*\}\n\s*\}"
if re.search(old_dept_leads_regex, content):
    content = re.sub(old_dept_leads_regex, new_dept_leads, content)

# 2. Update logic in manager login
old_logic = """                dept_lead = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, "")
                
                # Make sure the department lead is at the top or selected by default if exists
                default_idx = 0
                if dept_lead in personnel_list:
                    default_idx = personnel_list.index(dept_lead)
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + personnel_list, index=default_idx + 1 if dept_lead else 0, key="mgr_login_user")"""

new_logic = """                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                
                # Only show managers defined in DEPT_LEADS if available
                valid_leads = [lead for lead in dept_leads if lead in personnel_list]
                
                if valid_leads:
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + valid_leads, key="mgr_login_user")
                else:
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + personnel_list, key="mgr_login_user")"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Patched app.py")
