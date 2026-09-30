import codecs
import re

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

bad_indent = "                                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])"
good_indent = "                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])"

content = content.replace(bad_indent, good_indent)

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
