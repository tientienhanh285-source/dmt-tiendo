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

try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

require_authentication()

db_filters = {'DonVi': selected_company}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters = {'NguoiChuTri': st.session_state.personal_user}
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated'):
        manager_user = st.session_state.get('manager_user', '')
        manager_dept = st.session_state.get('manager_dept', '')
        db_filters = setup_manager_db_filters(db_filters, manager_user, manager_dept, selected_company)

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except Exception as e:
        import traceback
        st.error(f"Lỗi khi gọi read_db(): {e}")
        st.code(traceback.format_exc())
        display_df = pd.DataFrame()
if 'df' not in locals():
    df = display_df.copy()

st.header("✅ Duyệt & Nghiệm thu công việc")

if not (st.session_state.is_admin_authenticated or st.session_state.get("is_manager_authenticated", False)):
    st.warning("⚠️ Vui lòng nhập **Mật khẩu Quản lý** ở thanh bên trái (cột menu) để truy cập tính năng này.")
else:
    manager_user = st.session_state.get('manager_user', '') if role_mode == "Quản lý" else ''
    subs = get_subordinates_for_manager(manager_user) if role_mode == "Quản lý" else None
    has_split_queue = (role_mode == "Quản lý" and is_hr_equivalent_leader(manager_user) and subs is not None and len(subs) > 0)

    tab_nghiemthu, tab_khachquan = st.tabs(["📑 1. Nghiệm thu công việc (Checker)", "⚖️ 2. Duyệt lý do Khách quan"])
    
    with tab_nghiemthu:
        if display_df.empty:
            st.info("Chưa có dữ liệu công việc.")
        else:
            all_pending_nt = display_df[display_df['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])].copy()
            
            # 1. Xác định danh sách "Các CV bạn cần duyệt"
            if role_mode == "Quản lý":
                if subs is None:
                    my_approve_nt = all_pending_nt.copy()
                elif subs:
                    my_approve_nt = all_pending_nt[all_pending_nt['NguoiChuTri'].isin(subs)].copy()
                else:
                    my_approve_nt = all_pending_nt.iloc[0:0].copy()
                if manager_user and manager_user not in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
                    my_approve_nt = my_approve_nt[my_approve_nt['NguoiChuTri'] != manager_user]
            else:
                my_approve_nt = all_pending_nt.copy()

            if has_split_queue:
                st.markdown(f"### 📌 Mục 1: Các công việc BẠN CẦN DUYỆT ({', '.join(subs)})")
                st.caption(f"Danh sách công việc chờ nghiệm thu của nhân sự thuộc quyền duyệt trực tiếp của **{manager_user}**.")
            else:
                st.markdown("### 📌 Công việc bạn cần nghiệm thu")
                st.info("Danh sách các công việc nhân viên đã báo cáo hoàn thành. Vui lòng kiểm tra Minh chứng và chọn Trạng thái duyệt.")

            if my_approve_nt.empty:
                st.success("🎉 Hiện tại không có công việc nào thuộc phạm vi bạn cần duyệt trực tiếp!")
            else:
                st.warning(f"Có **{len(my_approve_nt)}** công việc đang chờ bạn nghiệm thu.")
                nt_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "LinkKetQua", "TrangThaiNghiemThu"]
                if "TrangThaiNghiemThu" not in my_approve_nt.columns:
                    my_approve_nt["TrangThaiNghiemThu"] = "Chờ duyệt"
                disp_nt = my_approve_nt[[c for c in nt_cols if c in my_approve_nt.columns]].copy()
                
                nt_col_config = {
                    "ID": st.column_config.TextColumn("Mã CV", disabled=True),
                    "PhongBan": st.column_config.TextColumn("Phòng/Ban", disabled=True),
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
                
                file_tasks = disp_nt[disp_nt['LinkKetQua'].astype(str).str.contains("OUTPUT", na=False)]
                if not file_tasks.empty:
                    st.markdown("#### 📥 Xem / Tải File đính kèm")
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

            # 2. Mục 2 dành cho Lãnh đạo xem toàn hệ thống (như anh Đặng Ngọc Hoàng): Các CV đang chờ duyệt của các Ban khác
            if has_split_queue:
                st.markdown("---")
                st.markdown("### 🌐 Mục 2: Các công việc đang chờ duyệt trên toàn hệ thống (Các Ban khác)")
                st.caption("Danh sách toàn bộ công việc đang ở trạng thái Chờ nghiệm thu của tất cả các Phòng/Ban để theo dõi chung.")
                
                valid_depts_nt = sorted([d for d in all_pending_nt['PhongBan'].dropna().unique() if str(d).strip() != ""])
                sel_dept_nt_all = st.selectbox("Lọc theo Phòng/Ban (Toàn hệ thống)", ["Tất cả các Ban"] + valid_depts_nt, key="nt_all_dept_filter")
                
                view_all_nt = all_pending_nt.copy()
                if sel_dept_nt_all != "Tất cả các Ban":
                    view_all_nt = view_all_nt[view_all_nt['PhongBan'] == sel_dept_nt_all]
                    
                if view_all_nt.empty:
                    st.info("Hiện không có công việc nào đang chờ duyệt ở mục này.")
                else:
                    st.info(f"Đang có **{len(view_all_nt)}** công việc chờ nghiệm thu trên toàn hệ thống.")
                    view_cols = ["ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "TenCongViec", "Deadline", "TrangThai", "LinkKetQua"]
                    disp_all_nt = view_all_nt[[c for c in view_cols if c in view_all_nt.columns]].copy()
                    st.dataframe(
                        disp_all_nt,
                        column_config={
                            "ID": "Mã CV",
                            "DonVi": "Đơn vị",
                            "PhongBan": "Phòng/Ban",
                            "NguoiChuTri": "Người Phụ Trách",
                            "TenDuAn": "Dự án",
                            "TenCongViec": st.column_config.TextColumn("Tên Công Việc", width="large"),
                            "Deadline": st.column_config.DateColumn("Hạn Chót", format="DD/MM/YYYY"),
                            "TrangThai": "Trạng Thái",
                            "LinkKetQua": st.column_config.LinkColumn("Minh Chứng")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                                
    with tab_khachquan:
        if display_df.empty:
            st.info("Chưa có dữ liệu công việc.")
        else:
            if role_mode == "Quản lý" and not is_hr_equivalent_leader(manager_user):
                col_thang, col_nam = st.columns(2)
                with col_thang:
                    thang_opts = ["Tất cả"] + list(range(1, 13))
                    sel_thang = st.selectbox("Chọn Tháng", thang_opts, index=today.month)
                with col_nam:
                    nam_opts = [today.year - 1, today.year, today.year + 1]
                    sel_nam = st.selectbox("Chọn Năm", nam_opts, index=1)
                sel_phong = "Tất cả"
            else:
                col_thang, col_nam, col_phong = st.columns(3)
                with col_thang:
                    thang_opts = ["Tất cả"] + list(range(1, 13))
                    sel_thang = st.selectbox("Chọn Tháng", thang_opts, index=today.month)
                with col_nam:
                    nam_opts = [today.year - 1, today.year, today.year + 1]
                    sel_nam = st.selectbox("Chọn Năm", nam_opts, index=1)
                with col_phong:
                    valid_depts = sorted([d for d in display_df['PhongBan'].dropna().unique() if str(d).strip() != ""])
                    phong_opts = ["Tất cả"] + valid_depts
                    sel_phong = st.selectbox("Lọc theo Phòng/Ban", phong_opts)
                
            st.markdown("---")
            
            def is_in_selected_month(d_str):
                if not d_str: return False
                if sel_thang == "Tất cả": return True
                try:
                    d = pd.to_datetime(d_str)
                    return d.month == sel_thang and d.year == sel_nam
                except:
                    return False
            
            local_df = display_df.copy()        
            local_df['is_in_month'] = local_df['Deadline'].apply(is_in_selected_month)
            
            is_obj = local_df['PhanLoaiTreHan'].astype(str).str.lower().str.contains("khách quan")
            is_issue = local_df['TrangThai'] == 'Có vướng mắc'
            has_explain = (local_df['GiaiTrinhDeXuat'].astype(str).str.strip() != "") & (local_df['TrangThai'].isin(['Quá hạn', 'Đang thực hiện', 'Có vướng mắc']))

            base_mask = local_df['is_in_month'] & (is_obj | is_issue | has_explain)
            if sel_phong != "Tất cả":
                base_mask = base_mask & (local_df['PhongBan'] == sel_phong)
                
            all_kq_df = local_df[base_mask].copy()
            
            if role_mode == "Quản lý":
                if subs is None:
                    my_kq_df = all_kq_df.copy()
                elif subs:
                    my_kq_df = all_kq_df[all_kq_df['NguoiChuTri'].isin(subs)].copy()
                else:
                    my_kq_df = all_kq_df.iloc[0:0].copy()
                if manager_user and manager_user not in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
                    my_kq_df = my_kq_df[my_kq_df['NguoiChuTri'] != manager_user]
            else:
                my_kq_df = all_kq_df.copy()

            if has_split_queue:
                st.markdown(f"### 📌 Mục 1: Các CV BẠN CẦN DUYỆT Khách quan ({', '.join(subs)})")
            else:
                st.markdown("### 📌 Các CV cần duyệt lý do Khách quan")
                
            if my_kq_df.empty:
                st.success("🎉 Không có công việc nào thuộc phạm vi bạn cần duyệt lý do Khách quan / Vướng mắc!")
            else:
                st.info(f"Đang hiển thị **{len(my_kq_df)}** công việc báo cáo lý do Khách quan / Vướng mắc cần bạn duyệt.")

                my_kq_df["TrangThaiDuyetKQ"] = my_kq_df["MucDoGhiNhan"].apply(lambda x: "🔴 Chưa duyệt" if pd.isna(x) or str(x).strip() in ["", "nan", "None", "Chưa đánh giá"] else "🟢 Đã duyệt")

                edit_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "TrangThai", "GiaiTrinhDeXuat", "TrangThaiDuyetKQ", "MucDoGhiNhan"]
                disp_df = my_kq_df[edit_cols].copy()
                
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
                
                file_tasks_kq = my_kq_df[my_kq_df['LinkKetQua'].astype(str).str.contains("OUTPUT", na=False)]
                if not file_tasks_kq.empty:
                    st.markdown("#### 📥 Xem / Tải File đính kèm (Giải trình Khách quan)")
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

            if has_split_queue:
                st.markdown("---")
                st.markdown("### 🌐 Mục 2: Các CV báo cáo Khách quan / Vướng mắc toàn hệ thống (Theo dõi chung)")
                if all_kq_df.empty:
                    st.info("Không có công việc nào báo cáo Khách quan / Vướng mắc trong kỳ đã chọn.")
                else:
                    all_kq_view = all_kq_df.copy()
                    all_kq_view["TrangThaiDuyetKQ"] = all_kq_view["MucDoGhiNhan"].apply(lambda x: "🔴 Chưa duyệt" if pd.isna(x) or str(x).strip() in ["", "nan", "None", "Chưa đánh giá"] else "🟢 Đã duyệt")
                    view_kq_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "TrangThai", "GiaiTrinhDeXuat", "TrangThaiDuyetKQ", "MucDoGhiNhan"]
                    st.dataframe(
                        all_kq_view[[c for c in view_kq_cols if c in all_kq_view.columns]],
                        column_config={
                            "ID": "Mã CV",
                            "PhongBan": "Phòng/Ban",
                            "NguoiChuTri": "Người Phụ Trách",
                            "TenCongViec": st.column_config.TextColumn("Tên Công Việc", width="large"),
                            "Deadline": st.column_config.DateColumn("Hạn Chót", format="DD/MM/YYYY"),
                            "TrangThai": "Trạng Thái",
                            "GiaiTrinhDeXuat": st.column_config.TextColumn("Giải Trình Khách Quan", width="medium"),
                            "TrangThaiDuyetKQ": "Trạng thái duyệt",
                            "MucDoGhiNhan": "Mức độ Ghi nhận KPI"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
