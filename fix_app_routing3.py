import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

target = """        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_lap_duyet, p_quan_ly_jd, p_cau_hinh, p_so_tay]
    }
elif st.session_state.get('is_manager_authenticated', False):
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_lap_duyet, p_so_tay]
    }"""

replacement = """        'ĐÁNH GIÁ & KPI': [p_lap_duyet, p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_quan_ly_jd, p_cau_hinh, p_so_tay]
    }
elif st.session_state.get('is_manager_authenticated', False):
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]
    }"""

# Using robust replace
import re
content = re.sub(r"'QUẢN TRỊ & HỆ THỐNG': \[p_quan_tri_bsc, p_lap_duyet, p_quan_ly_jd, p_cau_hinh, p_so_tay\]", r"'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_quan_ly_jd, p_cau_hinh, p_so_tay]", content)
content = re.sub(r"'QUẢN TRỊ & HỆ THỐNG': \[p_quan_tri_bsc, p_lap_duyet, p_so_tay\]", r"'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]", content)
content = re.sub(r"'ĐÁNH GIÁ & KPI': \[p_danh_gia\],\s*'QUẢN TRỊ & HỆ THỐNG': \[p_quan_tri_bsc", r"'ĐÁNH GIÁ & KPI': [p_lap_duyet, p_danh_gia],\n        'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc", content)

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
    f.write(content)
print("Done!")
