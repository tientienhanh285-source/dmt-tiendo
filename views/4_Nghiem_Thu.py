import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

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
                        "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"],
                        "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"],
                        "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                        "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tâm"],
                        "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bồn"],
                        "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển"],
                        "Trần Cường": ["Trần Cường", "Ngô Thị Tâm"],
                        "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
                        "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
                    }
                if manager_user in bld_hierarchy:
                    all_truong_ban = bld_hierarchy[manager_user]
                else:
                    all_truong_ban = []
                    for leads in DEPT_LEADS.get(selected_company, {}).values():
                        all_truong_ban.extend(leads)
                
                if st.session_state.manager_dept in ["HĐQT", "BLĐ"]:
                    # HĐQT and BLĐ see all companies, do not filter by DonVi
                    if 'DonVi' in db_filters:
                        del db_filters['DonVi']
                if st.session_state.manager_dept != "HĐQT":
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
            if 'PhongBan' in db_filters: del db_filters['PhongBan']

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
            if 'PhongBan' in db_filters: del db_filters['PhongBan']

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



st.header("✅ Duyệt & Nghiệm thu công việc")

if not (st.session_state.is_admin_authenticated or st.session_state.get("is_manager_authenticated", False)):
    st.warning("⚠️ Vui lòng nhập **Mật khẩu Quản lý** ở thanh bên trái (cột menu) để truy cập tính năng này.")
else:
    # df is already loaded and mapped with DEPT_ABBR globally
    
    tab_nghiemthu, tab_khachquan = st.tabs(["📑 1. Nghiệm thu công việc (Checker)", "⚖️ 2. Duyệt lý do Khách quan"])
    
    with tab_nghiemthu:
        st.markdown("### Nghiệm thu công việc")
        st.info("Danh sách các công việc nhân viên đã báo cáo hoàn thành. Vui lòng kiểm tra Minh chứng và chọn Trạng thái duyệt.")
        if display_df.empty:
            st.info("Chưa có dữ liệu công việc.")
        else:
            nghiemthu_df = display_df[display_df['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])].copy()
            if role_mode == "Quản lý":
                manager_dept = st.session_state.get("manager_dept", "Tất cả")
                manager_user = st.session_state.get('manager_user', '')
                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
                if manager_user in bld_members:
                    if manager_dept in ["BLĐ", "HĐQT"]:
                        bld_hierarchy = {
                        "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"],
                        "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"],
                        "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                        "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tâm"],
                        "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bồn"],
                        "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển"],
                        "Trần Cường": ["Trần Cường", "Ngô Thị Tâm"],
                        "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
                        "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
                    }
                        if manager_user in bld_hierarchy:
                            all_truong_ban = bld_hierarchy[manager_user]
                        else:
                            all_truong_ban = []
                            for leads in DEPT_LEADS.get(selected_company, {}).values():
                                all_truong_ban.extend(leads)
                        nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(all_truong_ban)]
                    else:
                        dept_leads = DEPT_LEADS.get(selected_company, {}).get(manager_dept, [])
                        truong_ban_list = [p for p in dept_leads if p not in bld_members]
                        if truong_ban_list:
                            nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'].isin(truong_ban_list)]
                elif manager_dept != "Tất cả":
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['PhongBan'] == manager_dept]
                    
            # Prevent managers from approving their own tasks
            if 'manager_user' in locals() and manager_user:
                nghiemthu_df = nghiemthu_df[nghiemthu_df['NguoiChuTri'] != manager_user]
                    
            if nghiemthu_df.empty:
                st.success("🎉 Hiện tại không có công việc nào chờ nghiệm thu!")
            else:
                st.warning(f"Có **{len(nghiemthu_df)}** công việc đang chờ nghiệm thu.")
                nt_cols = ["ID", "NguoiChuTri", "TenCongViec", "Deadline", "LinkKetQua", "TrangThaiNghiemThu"]
                if "TrangThaiNghiemThu" not in nghiemthu_df.columns:
                    nghiemthu_df["TrangThaiNghiemThu"] = "Chờ duyệt"
                disp_nt = nghiemthu_df[nt_cols].copy()
                
                nt_col_config = {
                    "ID": st.column_config.TextColumn("Mã CV", disabled=True),
                    "NguoiChuTri": st.column_config.TextColumn("Người Phụ Trách", disabled=True),
                    "TenCongViec": st.column_config.TextColumn("Tên Công Việc", disabled=True),
                    "Deadline": st.column_config.DateColumn("Hạn Chót", disabled=True, format="DD/MM/YYYY"),
                    "LinkKetQua": st.column_config.LinkColumn("Minh Chứng", disabled=True),
                    "TrangThaiNghiemThu": st.column_config.SelectboxColumn(
                        "Trạng thái Duyệt",
                        options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)"],
                        required=True
                    )
                }
                edited_nt = st.data_editor(
                    disp_nt,
                    column_config=nt_col_config,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed",
                    key="editor_nghiemthu"
                )
                
                # Trình tải file đính kèm
                file_tasks = disp_nt[disp_nt['LinkKetQua'].astype(str).str.contains("OUTPUT", na=False)]
                if not file_tasks.empty:
                    st.markdown("### 📥 Xem / Tải File đính kèm")
                    sel_task_id = st.selectbox("Chọn Mã CV để tải file:", ["-- Chọn --"] + file_tasks['ID'].tolist())
                    if sel_task_id != "-- Chọn --":
                        file_path = file_tasks[file_tasks['ID'] == sel_task_id]['LinkKetQua'].values[0]
                        import os
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                st.download_button(f"Tải xuống ({os.path.basename(file_path)})", f, file_name=os.path.basename(file_path))
                        else:
                            st.error("File đính kèm không tồn tại trên máy chủ (có thể đã bị xóa)!")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Lưu kết quả Nghiệm thu", type="primary"):
                    with acquire_db_lock():
                        fresh_df = read_db()
                        changed = False
                        for idx, row in edited_nt.iterrows():
                            task_id = row['ID']
                            new_val = row['TrangThaiNghiemThu']
                            if new_val == "✅ Duyệt (Hoàn thành)":
                                update_task(task_id, {'TrangThai': 'Hoàn thành'})
                                changed = True
                        
                        if changed:
                            st.success("✅ Đã lưu kết quả nghiệm thu thành công!")
                            st.rerun()
                                
    with tab_khachquan:
        if display_df.empty:
            st.info("Chưa có dữ liệu công việc.")
        else:
            if role_mode == "Quản lý":
                col_thang, col_nam = st.columns(2)
                with col_thang:
                    thang_opts = list(range(1, 13))
                    sel_thang = st.selectbox("Chọn Tháng", thang_opts, index=today.month - 1)
                with col_nam:
                    nam_opts = [today.year - 1, today.year, today.year + 1]
                    sel_nam = st.selectbox("Chọn Năm", nam_opts, index=1)
                sel_phong = "Tất cả"
            else:
                col_thang, col_nam, col_phong = st.columns(3)
                with col_thang:
                    thang_opts = list(range(1, 13))
                    sel_thang = st.selectbox("Chọn Tháng", thang_opts, index=today.month - 1)
                with col_nam:
                    nam_opts = [today.year - 1, today.year, today.year + 1]
                    sel_nam = st.selectbox("Chọn Năm", nam_opts, index=1)
                with col_phong:
                    valid_depts = sorted([d for d in display_df['PhongBan'].dropna().unique() if str(d).strip() != ""])
                    phong_opts = ["Tất cả"] + valid_depts
                    sel_phong = st.selectbox("Lọc theo Phòng/Ban", phong_opts)
                
            st.markdown("---")
            
            # Filter logic
            def is_in_selected_month(d_str):
                if not d_str: return False
                try:
                    d = pd.to_datetime(d_str)
                    return d.month == sel_thang and d.year == sel_nam
                except:
                    return False
            
            local_df = display_df.copy()        
            local_df['is_in_month'] = local_df['Deadline'].apply(is_in_selected_month)
            
            # Condition: Deadline in month, objective reason
            mask = local_df['is_in_month'] & local_df['PhanLoaiTreHan'].astype(str).str.lower().str.contains("khách quan")
            if sel_phong != "Tất cả":
                mask = mask & (local_df['PhongBan'] == sel_phong)
            if role_mode == "Quản lý":
                manager_user = st.session_state.get('manager_user', '')
                bld_members = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Ngọc Tôn", "Đặng Thanh Bình"]
                if manager_user in bld_members:
                    if st.session_state.get("manager_dept") in ["BLĐ", "HĐQT"]:
                        bld_hierarchy = {
                        "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"],
                        "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga"],
                        "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                        "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tâm"],
                        "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phụng", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển", "Lê Nho Tân", "Nguyễn Văn Bồn"],
                        "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiển"],
                        "Trần Cường": ["Trần Cường", "Ngô Thị Tâm"],
                        "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
                        "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
                    }
                        if manager_user in bld_hierarchy:
                            all_truong_ban = bld_hierarchy[manager_user]
                        else:
                            all_truong_ban = []
                            for leads in DEPT_LEADS.get(selected_company, {}).values():
                                all_truong_ban.extend(leads)
                        mask = mask & local_df['NguoiChuTri'].isin(all_truong_ban)
                    else:
                        dept_leads = DEPT_LEADS.get(selected_company, {}).get(st.session_state.get("manager_dept"), [])
                        truong_ban_list = [p for p in dept_leads if p not in bld_members]
                        if truong_ban_list:
                            mask = mask & local_df['NguoiChuTri'].isin(truong_ban_list)
                
            # Prevent managers from approving their own tasks
            if 'manager_user' in locals() and manager_user:
                mask = mask & (local_df['NguoiChuTri'] != manager_user)
                
            filtered_df = local_df[mask].copy()
            
            if filtered_df.empty:
                st.success(f"🎉 Không có công việc nào báo cáo Khách quan trong tháng {sel_thang}/{sel_nam}!")
            else:
                st.info(f"Đang hiển thị **{len(filtered_df)}** công việc báo cáo lý do Khách quan.")
                
                # Setup Editor
                # Compute dynamic state for UI
                filtered_df["TrangThaiDuyetKQ"] = filtered_df["MucDoGhiNhan"].apply(lambda x: "🔴 Chưa duyệt" if pd.isna(x) or str(x).strip() in ["", "nan", "None", "Chưa đánh giá"] else "🟢 Đã duyệt")

                edit_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "TrangThai", "GiaiTrinhDeXuat", "TrangThaiDuyetKQ", "MucDoGhiNhan"]
                disp_df = filtered_df[edit_cols].copy()
                
                # We need to make all columns disabled EXCEPT MucDoGhiNhan
                col_config = {
                    "ID": st.column_config.TextColumn("Mã CV", disabled=True),
                    "PhongBan": st.column_config.TextColumn("Phòng/Ban", disabled=True),
                    "NguoiChuTri": st.column_config.TextColumn("Người Phụ Trách", disabled=True),
                    "TenCongViec": st.column_config.TextColumn("Tên Công Việc", disabled=True),
                    "Deadline": st.column_config.DateColumn("Hạn Chót", disabled=True, format="DD/MM/YYYY"),
                    "TrangThai": st.column_config.TextColumn("Trạng Thái", disabled=True),
                    "GiaiTrinhDeXuat": st.column_config.TextColumn("Giải Trình Khách Quan", disabled=True),
                    "TrangThaiDuyetKQ": st.column_config.TextColumn("Trạng thái", disabled=True),
                    "MucDoGhiNhan": st.column_config.SelectboxColumn(
                        "Mức độ Ghi nhận KPI",
                        help="Chọn mức điểm đánh giá theo lý do khách quan (Chỉ dành cho Quản lý)",
                        options=["0% (Không ghi nhận)", "50%", "80%", "90%"],
                        required=True
                    )
                }
                
                edited_df = st.data_editor(
                    disp_df,
                    column_config=col_config,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed",
                    key=f"editor_approve_{sel_thang}_{sel_nam}"
                )
                
                # Trình tải file đính kèm
                file_tasks_kq = filtered_df[filtered_df['LinkKetQua'].astype(str).str.contains("OUTPUT", na=False)]
                if not file_tasks_kq.empty:
                    st.markdown("### 📥 Xem / Tải File đính kèm (Giải trình Khách quan)")
                    sel_task_id_kq = st.selectbox("Chọn Mã CV để tải file:", ["-- Chọn --"] + file_tasks_kq['ID'].tolist(), key="dl_kq")
                    if sel_task_id_kq != "-- Chọn --":
                        file_path_kq = file_tasks_kq[file_tasks_kq['ID'] == sel_task_id_kq]['LinkKetQua'].values[0]
                        import os
                        if os.path.exists(file_path_kq):
                            with open(file_path_kq, "rb") as f:
                                st.download_button(f"Tải xuống ({os.path.basename(file_path_kq)})", f, file_name=os.path.basename(file_path_kq))
                        else:
                            st.error("File đính kèm không tồn tại trên máy chủ (có thể đã bị xóa)!")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Lưu tất cả thay đổi", type="primary"):
                    with acquire_db_lock():
                        
                        fresh_df = read_db()
                        changed = False
                        for idx, row in edited_df.iterrows():
                            task_id = row['ID']
                            new_val = row['MucDoGhiNhan']
                            if task_id in fresh_df['ID'].values:
                                old_val = fresh_df.loc[fresh_df['ID'] == task_id, 'MucDoGhiNhan'].values[0]
                                if new_val != old_val:
                                    update_task(task_id, {'MucDoGhiNhan': new_val})
                                    changed = True
                                
                        if changed:
                            st.success("✅ Đã lưu toàn bộ phê duyệt thành công!")
                            st.rerun()
                        else:
                            st.info("Chưa có thay đổi nào cần lưu.")


