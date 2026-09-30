with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the static pages dict
old_pages = """# --- MULTIPAGE NAVIGATION ---
pages = {
    'CÔNG VIỆC & TIẾN ĐỘ': [
        st.Page('views/1_Tong_Quan.py', title='Bảng Tổng Quan', icon='👀'),
        st.Page('views/2_Tien_Do.py', title='Theo dõi Tiến độ', icon='🚀'),
        st.Page('views/3_Cap_Nhat.py', title='Thêm/Cập nhật', icon='➕'),
        st.Page('views/4_Nghiem_Thu.py', title='Nghiệm thu việc', icon='✅'),
    ],
    'ĐÁNH GIÁ & KPI': [
        st.Page('views/5_Danh_Gia_KPI.py', title='Đánh giá KPI', icon='🏆'),
    ],
    'QUẢN TRỊ & HỆ THỐNG': [
        st.Page('views/6_Quan_Ly_JD.py', title='Đối chiếu JD', icon='🔍'),
        st.Page('views/7_Cau_Hinh.py', title='Cấu hình', icon='⚙️'),
        st.Page('views/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖'),
    ]
}"""

new_pages = """# --- MULTIPAGE NAVIGATION ---
p_tong_quan = st.Page('views/1_Tong_Quan.py', title='Bảng Tổng Quan', icon='👀')
p_tien_do = st.Page('views/2_Tien_Do.py', title='Bảng theo dõi tiến độ công việc', icon='🚀')
p_cap_nhat = st.Page('views/3_Cap_Nhat.py', title='Thêm / Cập Nhật Công Việc', icon='➕')
p_nghiem_thu = st.Page('views/4_Nghiem_Thu.py', title='Duyệt & Nghiệm thu công việc', icon='✅')
p_danh_gia = st.Page('views/5_Danh_Gia_KPI.py', title='Đánh giá KPI & Xếp loại', icon='🏆')
p_quan_ly_jd = st.Page('views/6_Quan_Ly_JD.py', title='Quản lý & Đối chiếu JD', icon='🔍')
p_cau_hinh = st.Page('views/7_Cau_Hinh.py', title='Quản Lý Cấu Hình', icon='⚙️')
p_so_tay = st.Page('views/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖')

if st.session_state.is_admin_authenticated:
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_so_tay]
    }
elif st.session_state.get('is_manager_authenticated', False):
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]
    }
else:
    # Nhân viên chưa đăng nhập hoặc đã đăng nhập
    pages = {
        'PHÂN HỆ CHỨC NĂNG': [p_tien_do, p_cap_nhat, p_so_tay]
    }
"""

content = content.replace(old_pages, new_pages)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated navigation logic")
