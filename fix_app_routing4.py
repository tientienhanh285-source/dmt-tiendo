import codecs
import re

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

# For Admin role
content = re.sub(
    r"'ĐÁNH GIÁ & KPI': \[p_lap_duyet, p_danh_gia\],",
    r"'ĐÁNH GIÁ & KPI': [p_danh_gia],",
    content
)

content = re.sub(
    r"'QUẢN TRỊ & HỆ THỐNG': \[p_quan_tri_bsc, p_quan_ly_jd, p_cau_hinh, p_so_tay\]",
    r"'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_so_tay]",
    content
)

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Removed from HR/Admin role!")
