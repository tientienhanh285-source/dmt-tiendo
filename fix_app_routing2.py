import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'r', 'utf-8') as f:
    content = f.read()

# Find the location of p_cau_hinh
if "p_cau_hinh = st.Page('views/7_Cau_Hinh.py'" in content and "p_quan_tri_bsc" not in content:
    # Insert declarations
    insertion = "p_lap_duyet = st.Page('views/9_Lap_Duyet_KPI.py', title='Lập & Duyệt KPI', icon='🎯')\np_quan_tri_bsc = st.Page('views/8_Quan_Tri_BSC.py', title='Quản trị BSC - KPI', icon='⚙️')\n"
    
    parts = content.split("p_cau_hinh = ")
    new_content = parts[0] + insertion + "p_cau_hinh = " + parts[1]
    
    # Now replace the pages array
    target_admin = "'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_so_tay]"
    target_mgr = "'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]"
    
    new_content = new_content.replace(target_admin, "'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_lap_duyet, p_quan_ly_jd, p_cau_hinh, p_so_tay]")
    new_content = new_content.replace(target_mgr, "'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_lap_duyet, p_so_tay]")
    
    # Fix the other occurrence for admin/mgr
    # Let's just do a manual replace for the exact dictionary values
    new_content = new_content.replace("[p_quan_ly_jd, p_cau_hinh, p_so_tay]", "[p_quan_tri_bsc, p_lap_duyet, p_quan_ly_jd, p_cau_hinh, p_so_tay]")
    # But for manager, it is [p_so_tay], which is risky to replace globally.
    mgr_block_target = "'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]"
    mgr_block_replace = "'QUẢN TRỊ & HỆ THỐNG': [p_quan_tri_bsc, p_lap_duyet, p_so_tay]"
    new_content = new_content.replace(mgr_block_target, mgr_block_replace)
    
    with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py', 'w', 'utf-8') as f:
        f.write(new_content)
    print("Fixed!")
else:
    print("Could not find the target or it's already fixed.")
