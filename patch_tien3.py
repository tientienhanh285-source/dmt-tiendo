import glob

for filepath in glob.glob('views/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_inject = '''
        # --- GLOBAL OVERRIDES ---
        _mgr = st.session_state.get('manager_user', '')
        if _mgr == "Nguyễn Thị Hạnh Tiên":
            db_filters['NguoiChuTri'] = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Trần Cường":
            db_filters['NguoiChuTri'] = ["Trần Cường", "Ngô Thị Tâm"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Đồng Thị Nguyệt Nga":
            db_filters['NguoiChuTri'] = ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"]
            if '4_Nghiem_Thu' in __file__ or '9_Lap_Duyet_KPI' in __file__:
                db_filters['NguoiChuTri'] = ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Nguyễn Thị Ngọc Hà":
            db_filters['NguoiChuTri'] = ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']'''
    
    new_inject = '''
        # --- GLOBAL OVERRIDES ---
        _mgr = st.session_state.get('manager_user', '')
        if _mgr == "Nguyễn Thị Hạnh Tiên":
            db_filters['NguoiChuTri'] = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
            if 'PhongBan' in db_filters: del db_filters['PhongBan']
        elif _mgr == "Trần Cường":
            db_filters['NguoiChuTri'] = ["Trần Cường", "Ngô Thị Tâm"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
            if 'PhongBan' in db_filters: del db_filters['PhongBan']
        elif _mgr == "Đồng Thị Nguyệt Nga":
            db_filters['NguoiChuTri'] = ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"]
            if '4_Nghiem_Thu' in __file__ or '9_Lap_Duyet_KPI' in __file__ or '4_Nghiem_Thu_KQ' in __file__:
                db_filters['NguoiChuTri'] = ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
            if 'PhongBan' in db_filters: del db_filters['PhongBan']
        elif _mgr == "Nguyễn Thị Ngọc Hà":
            db_filters['NguoiChuTri'] = ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
            if 'PhongBan' in db_filters: del db_filters['PhongBan']'''

    if old_inject in content:
        content = content.replace(old_inject, new_inject)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"Could not find exact block in {filepath}")
