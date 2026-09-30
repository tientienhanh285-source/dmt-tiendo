

if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {'DonVi': selected_company}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        manager_user = st.session_state.get('manager_user', '')
        bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
        if manager_user in bld_members:
            if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"],
                    "Thái Văn Thành": ["Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"],
                    "Trần Văn Trọng": ["Lê Nho Tân", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]
                }
                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                db_filters['NguoiChuTri'] = list(set(all_truong_ban))
            else:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.manager_dept, [])
                truong_ban_list = [p for p in dept_leads if p not in bld_members]
                if truong_ban_list:
                    db_filters['NguoiChuTri'] = truong_ban_list
                else:
                    db_filters['PhongBan'] = st.session_state.manager_dept
        else:
            db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"


# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {'DonVi': selected_company}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        manager_user = st.session_state.get('manager_user', '')
        bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
        if manager_user in bld_members:
            if st.session_state.manager_dept in ["BLĐ", "HĐQT"]:
                bld_hierarchy = {
                    "Trần Quốc Thể": ["Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu"],
                    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Như Can"],
                    "Đặng Ngọc Hoàng": ["Nguyễn Thị Hạnh Tiên"],
                    "Thái Văn Thành": ["Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân"],
                    "Trần Văn Trọng": ["Lê Nho Tân", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"]
                }
                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                db_filters['NguoiChuTri'] = list(set(all_truong_ban))
            else:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.manager_dept, [])
                truong_ban_list = [p for p in dept_leads if p not in bld_members]
                if truong_ban_list:
                    db_filters['NguoiChuTri'] = truong_ban_list
                else:
                    db_filters['PhongBan'] = st.session_state.manager_dept
        else:
            db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()


if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()

