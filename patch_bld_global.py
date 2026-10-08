import glob

for filepath in glob.glob('views/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to replace:
    #                 if st.session_state.manager_dept == "HĐQT":
    #                     # HĐQT sees all companies, do not filter by DonVi or NguoiChuTri
    #                     if 'DonVi' in db_filters:
    #                         del db_filters['DonVi']
    #                 else:
    #                     db_filters['NguoiChuTri'] = list(set(all_truong_ban))

    old_logic = '''                if st.session_state.manager_dept == "HĐQT":
                    # HĐQT sees all companies, do not filter by DonVi or NguoiChuTri
                    if 'DonVi' in db_filters:
                        del db_filters['DonVi']
                else:
                    db_filters['NguoiChuTri'] = list(set(all_truong_ban))'''
    
    new_logic = '''                if st.session_state.manager_dept in ["HĐQT", "BLĐ"]:
                    # HĐQT and BLĐ see all companies, do not filter by DonVi
                    if 'DonVi' in db_filters:
                        del db_filters['DonVi']
                if st.session_state.manager_dept != "HĐQT":
                    db_filters['NguoiChuTri'] = list(set(all_truong_ban))'''

    if old_logic in content:
        content = content.replace(old_logic, new_logic)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"Could not find exact block in {filepath}")
