import os
import glob

replacement = """db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass"""

target_str = """if 'display_df' not in locals():
    try:
        display_df = read_db()
    except:
        pass


# Apply Role-based Filtering globally for the view
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        display_df = display_df[display_df['NguoiChuTri'] == st.session_state.personal_user]
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        display_df = display_df[display_df['PhongBan'] == st.session_state.manager_dept]"""

for fpath in glob.glob('views/*.py'):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace(target_str, replacement)
    
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {fpath}')
