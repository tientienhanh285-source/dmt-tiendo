import glob

for filepath in glob.glob('views/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The current structure is:
    #         if manager_user in bld_members:
    #             if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:
    #                 bld_hierarchy = { ... }
    #                 if manager_user in bld_hierarchy: ...
    #                 else: ...
    #                 if st.session_state.manager_dept in ["HĐQT", "BLĐ"]: ...
    #                 if st.session_state.manager_dept != "HĐQT": ...
    #             else:
    #                 dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.manager_dept, [])
    #                 ...
    #         else:
    #             dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.manager_dept, [])
    #             ...

    # Let's just do a simple string replace for Tiên and others in the `else` blocks where they usually fall.
    # Actually, the user ONLY mentioned:
    # Tiên HCNS duyệt c Tâm.
    # Nga TCKT duyệt Hà.
    # Hà TCKT duyệt Hà.
    # Cường BLĐ Marina duyệt Tâm.
    
    # Since Cường is BLĐ, he already passes `st.session_state.manager_dept in ["BLĐ", "HĐQT"]`.
    # His `bld_hierarchy` is ALREADY defined as: `"Trần Cường": ["Trần Cường", "Ngô Thị Tâm"]`.
    # Since he is BLĐ, he ALSO gets `del db_filters['DonVi']`. 
    # So Cường is ALREADY WORKING PERFECTLY!

    pass
