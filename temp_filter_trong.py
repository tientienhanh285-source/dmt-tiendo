import os
import re

# Patch 1_Tong_Quan.py
with open('views/1_Tong_Quan.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch_1 = '''            dept_opts = ["Tất cả phòng ban"] + get_departments_for_company(selected_company, config)
            if st.session_state.manager_user == "Trần Văn Trọng":
                dept_opts = [d for d in dept_opts if d not in ["TCKT", "Ban Tài chính Kế toán", "HCNS", "Ban Hành chính Nhân sự"]]
            sel_d = st.selectbox("Lọc Phòng ban (Master View)", dept_opts, key="master_dept_tongquan")'''
content = re.sub(r'dept_opts = \["Tất cả phòng ban"\] \+ get_departments_for_company\(selected_company, config\)\s+sel_d = st.selectbox\("Lọc Phòng ban \(Master View\)", dept_opts, key="master_dept_tongquan"\)', patch_1, content)

with open('views/1_Tong_Quan.py', 'w', encoding='utf-8') as f:
    f.write(content)


# Patch 2_Tien_Do.py
with open('views/2_Tien_Do.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch_2 = '''            dept_opts = ["Tất cả phòng ban"] + get_departments_for_company(selected_company, config)
            if st.session_state.get('manager_user') == "Trần Văn Trọng":
                dept_opts = [d for d in dept_opts if d not in ["TCKT", "Ban Tài chính Kế toán", "HCNS", "Ban Hành chính Nhân sự"]]
            sel_d = st.selectbox("Lọc Phòng ban (Master View)", dept_opts, key="master_dept")'''
content = re.sub(r'dept_opts = \["Tất cả phòng ban"\] \+ get_departments_for_company\(selected_company, config\)\s+sel_d = st.selectbox\("Lọc Phòng ban \(Master View\)", dept_opts, key="master_dept"\)', patch_2, content)

patch_3 = '''    if active_dept:
        project_targets = [t for t in project_targets if t.get("department") == active_dept]
    elif role_mode == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_user') == "Trần Văn Trọng":
        project_targets = [t for t in project_targets if t.get("department") not in ["TCKT", "Ban Tài chính Kế toán", "HCNS", "Ban Hành chính Nhân sự"]]'''
content = re.sub(r'    if active_dept:\n        project_targets = \[t for t in project_targets if t.get\("department"\) == active_dept\]', patch_3, content)

with open('views/2_Tien_Do.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
