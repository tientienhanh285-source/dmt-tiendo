import codecs
import re

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

# Add the page declaration
page_decl = "p_nhat_ky = st.Page('views/11_Nhat_Ky_He_Thong.py', title='Nhật ký Hệ thống', icon='🕵️‍♂️')\n"
if "p_nhat_ky =" not in content:
    content = content.replace("p_so_tay = st.Page('views/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖')\n",
                              "p_so_tay = st.Page('views/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖')\n" + page_decl)

# Add to Admin role
# Currently it is: 'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_so_tay]
content = re.sub(
    r"'QUẢN TRỊ & HỆ THỐNG': \[p_quan_ly_jd, p_cau_hinh, p_so_tay\]",
    r"'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_nhat_ky, p_so_tay]",
    content
)

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Injected Audit Log into app.py")
