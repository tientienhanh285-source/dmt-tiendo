import codecs
import re

app_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py'
with codecs.open(app_file, 'r', 'utf-8') as f:
    app_content = f.read()

def replacer(match):
    return """            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                nhan_vien_list = [p for p in personnel_list if p not in dept_leads]
                
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên của bạn", ["-- Chọn --"] + nhan_vien_list, key="login_user")
"""

app_content = re.sub(
    r'\s*personnel_list\s*=\s*get_personnel_for_company_dept\(selected_company,\s*sel_login_dept,\s*config\)\s*\n\s*if\s*personnel_list:\s*\n\s*sel_login_user\s*=\s*st\.sidebar\.selectbox\(\"2\.\s*Chọn\s*Tên\s*của\s*bạn\",\s*\[\"--\s*Chọn\s*--\"\]\s*\+\s*personnel_list,\s*key=\"login_user\"\)\n',
    replacer,
    app_content
)

with codecs.open(app_file, 'w', 'utf-8') as f:
    f.write(app_content)
