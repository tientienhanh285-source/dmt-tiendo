import codecs
import re

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

page_decl = "\np_nhat_ky = st.Page('views/11_Nhat_Ky_He_Thong.py', title='Nhật ký Hệ thống', icon='🕵️‍♂️')\n"
if "p_nhat_ky =" not in content:
    content = content.replace("if st.session_state.is_admin_authenticated:",
                              page_decl + "\nif st.session_state.is_admin_authenticated:")

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Fixed missing declaration")
