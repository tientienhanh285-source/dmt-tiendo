import glob
import re

for filepath in glob.glob('views/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to inject Tiên's logic right before:
    # "if st.session_state['role_mode'] == "Nhân viên":"
    
    inject_code = '''        
        # Hotfix for cross-company/custom approvals
        _mgr = st.session_state.get('manager_user', '')
        if _mgr == "Nguyễn Thị Hạnh Tiên":
            db_filters['NguoiChuTri'] = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Trần Cường":
            db_filters['NguoiChuTri'] = ["Trần Cường", "Ngô Thị Tâm"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Đồng Thị Nguyệt Nga":
            # For Nga, we only want to override if it's an approval view
            if '4_Nghiem_Thu' in __file__ or '9_Lap_Duyet_KPI' in __file__:
                db_filters['NguoiChuTri'] = ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']
        elif _mgr == "Nguyễn Thị Ngọc Hà":
            if '4_Nghiem_Thu' in __file__ or '9_Lap_Duyet_KPI' in __file__:
                db_filters['NguoiChuTri'] = ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"]
            if 'DonVi' in db_filters: del db_filters['DonVi']

    elif st.session_state['role_mode'] == "Nhân viên":'''

    if 'elif st.session_state[\'role_mode\'] == "Nhân viên":' in content:
        if '# Hotfix for cross-company/custom approvals' not in content:
            content = content.replace('    elif st.session_state[\'role_mode\'] == "Nhân viên":', inject_code)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {filepath}")
    else:
        print(f"Could not find anchor in {filepath}")
