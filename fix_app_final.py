with open('app_backup_full_16_09.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_app_code = lines[:1737]

# Add st.navigation logic
new_app_code.append("\n# --- MULTIPAGE NAVIGATION ---\n")
new_app_code.append("pages = {\n")
new_app_code.append("    'CÔNG VIỆC & TIẾN ĐỘ': [\n")
new_app_code.append("        st.Page('pages/1_Tong_Quan.py', title='Bảng Tổng Quan', icon='👀'),\n")
new_app_code.append("        st.Page('pages/2_Tien_Do.py', title='Theo dõi Tiến độ', icon='🚀'),\n")
new_app_code.append("        st.Page('pages/3_Cap_Nhat.py', title='Thêm/Cập nhật', icon='➕'),\n")
new_app_code.append("        st.Page('pages/4_Nghiem_Thu.py', title='Nghiệm thu việc', icon='✅'),\n")
new_app_code.append("    ],\n")
new_app_code.append("    'ĐÁNH GIÁ & KPI': [\n")
new_app_code.append("        st.Page('pages/5_Danh_Gia_KPI.py', title='Đánh giá KPI', icon='🏆'),\n")
new_app_code.append("        st.Page('pages/8_Quan_Tri_BSC.py', title='Quản trị BSC', icon='📊'),\n")
new_app_code.append("        st.Page('pages/9_Lap_Duyet_KPI.py', title='Lập & Duyệt KPI', icon='📝'),\n")
new_app_code.append("    ],\n")
new_app_code.append("    'QUẢN TRỊ & HỆ THỐNG': [\n")
new_app_code.append("        st.Page('pages/6_Quan_Ly_JD.py', title='Đối chiếu JD', icon='🔍'),\n")
new_app_code.append("        st.Page('pages/7_Cau_Hinh.py', title='Cấu hình', icon='⚙️'),\n")
new_app_code.append("        st.Page('pages/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖'),\n")
new_app_code.append("    ]\n")
new_app_code.append("}\n")
new_app_code.append("pg = st.navigation(pages)\n")
new_app_code.append("pg.run()\n")

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_app_code)

print("Đã fix app.py với st.navigation")
