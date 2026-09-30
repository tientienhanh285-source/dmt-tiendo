import os
import re

for root, dirs, files in os.walk('views'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find the block where db_filters is initialized and modified
            # We want to add:
            # if st.session_state.get('manager_dept') == 'HĐQT':
            #     if 'DonVi' in db_filters:
            #         del db_filters['DonVi']
            
            # It's better to insert this right after `db_filters['NguoiChuTri'] = list(set(all_truong_ban))`
            # or `if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:`
            
            # First, check if file has the bld_hierarchy logic
            if 'bld_hierarchy = {' in content and 'db_filters = ' in content:
                # We can do a string replacement
                old_str = '''                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                db_filters['NguoiChuTri'] = list(set(all_truong_ban))'''
                
                new_str = '''                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                
                if st.session_state.manager_dept == "HĐQT":
                    # HĐQT sees all companies, do not filter by DonVi or NguoiChuTri
                    if 'DonVi' in db_filters:
                        del db_filters['DonVi']
                else:
                    db_filters['NguoiChuTri'] = list(set(all_truong_ban))'''
                
                if old_str in content:
                    new_content = content.replace(old_str, new_str)
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as file:
                            file.write(new_content)
                        print(f'Updated {path}')
