import codecs

app_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py'
with codecs.open(app_file, 'r', 'utf-8') as f:
    app_content = f.read()

target = '''            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list:
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên của bạn", ["-- Chọn --"] + personnel_list, key="login_user")'''

replacement = '''            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                nhan_vien_list = [p for p in personnel_list if p not in dept_leads]
                
                sel_login_user = st.sidebar.selectbox("2. Chọn Tên của bạn", ["-- Chọn --"] + nhan_vien_list, key="login_user")'''

if target in app_content:
    app_content = app_content.replace(target, replacement)
    with codecs.open(app_file, 'w', 'utf-8') as f:
        f.write(app_content)
    print("Success")
else:
    print("Target not found")
