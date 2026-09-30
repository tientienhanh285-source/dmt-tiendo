import codecs
import re

with codecs.open('app.py', 'r', 'utf-8') as f:
    content = f.read()
    
# Use regex to find the exact line
content = re.sub(
    r'sel_login_user\s*=\s*st\.sidebar\.selectbox\("2\.\s*Chọn\s*Tên\s*của\s*bạn",\s*\["--\s*Chọn\s*--"\]\s*\+\s*personnel_list,\s*key="login_user"\)',
    r'''dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                nhan_vien_list = [p for p in personnel_list if p not in dept_leads]
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên của bạn", ["-- Chọn --"] + nhan_vien_list, key="login_user")''',
    content
)

with codecs.open('app.py', 'w', 'utf-8') as f:
    f.write(content)
print('Done')
