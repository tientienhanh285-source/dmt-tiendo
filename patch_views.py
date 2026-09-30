import os
import glob

old_block = """db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept"""

new_block = """db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        if st.session_state.manager_dept == "BLĐ":
            all_truong_ban = []
            for leads in DEPT_LEADS.get(selected_company, {}).values():
                all_truong_ban.extend(leads)
            db_filters['NguoiChuTri'] = list(set(all_truong_ban))
        else:
            db_filters['PhongBan'] = st.session_state.manager_dept"""

for file_path in glob.glob("views/*.py"):
    # Skip the ones we already modified manually
    if "4_Nghiem_Thu.py" in file_path or "5_Danh_Gia_KPI.py" in file_path:
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"Skipped {file_path} (pattern not found)")
