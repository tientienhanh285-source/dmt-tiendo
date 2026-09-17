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

if 'display_df' not in locals():
    try:
        display_df = read_db()
    except:
        pass


# Apply Role-based Filtering globally for the view
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        display_df = display_df[display_df['NguoiChuTri'] == st.session_state.personal_user]
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        display_df = display_df[display_df['PhongBan'] == st.session_state.manager_dept]

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
            nghiemthu_df = display_df[display_df['TrangThai'] == 'Chờ nghiệm thu'].copy()
            if role_mode == "Quản lý":
                manager_dept = st.session_state.get("manager_dept", "Tất cả")
                if manager_dept != "Tất cả":
                    nghiemthu_df = nghiemthu_df[nghiemthu_df['PhongBan'] == manager_dept]
                    
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
                        options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)", "❌ Từ chối (Làm lại)"],
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
                
                if st.button("💾 Lưu kết quả Nghiệm thu", type="primary"):
                    with acquire_db_lock():
                        fresh_df = read_db()
                        changed = False
                        for idx, row in edited_nt.iterrows():
                            task_id = row['ID']
                            new_val = row['TrangThaiNghiemThu']
                            if new_val == "✅ Duyệt (Hoàn thành)":
                                fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThai'] = 'Hoàn thành'
                                if 'TrangThaiNghiemThu' in fresh_df.columns:
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThaiNghiemThu'] = 'Đã duyệt'
                                changed = True
                            elif new_val == "❌ Từ chối (Làm lại)":
                                fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThai'] = 'Đang thực hiện'
                                fresh_df.loc[fresh_df['ID'] == task_id, 'PhanTramHoanThanh'] = 0
                                if 'TrangThaiNghiemThu' in fresh_df.columns:
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThaiNghiemThu'] = 'Từ chối'
                                changed = True
                        
                        if changed:
                            if save_db(fresh_df):
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
                
            filtered_df = local_df[mask].copy()
            
            if filtered_df.empty:
                st.success(f"🎉 Không có công việc nào báo cáo Khách quan trong tháng {sel_thang}/{sel_nam}!")
            else:
                st.info(f"Đang hiển thị **{len(filtered_df)}** công việc báo cáo lý do Khách quan.")
                
                # Setup Editor
                # Compute dynamic state for UI
                filtered_df["TrangThaiDuyetKQ"] = filtered_df["MucDoGhiNhan"].apply(lambda x: "🔴 Chưa duyệt" if str(x).strip() == "Chưa đánh giá" else "🟢 Đã duyệt")

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
                        options=["Chưa đánh giá", "0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"],
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
                
                if st.button("💾 Lưu tất cả thay đổi", type="primary"):
                    with acquire_db_lock():
                        
                        fresh_df = read_db()
                        changed = False
                        for idx, row in edited_df.iterrows():
                            task_id = row['ID']
                            new_val = row['MucDoGhiNhan']
                            # Some tasks might not exist if deleted concurrently, but for robustness:
                            if task_id in fresh_df['ID'].values:
                                old_val = fresh_df.loc[fresh_df['ID'] == task_id, 'MucDoGhiNhan'].values[0]
                                if new_val != old_val:
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'MucDoGhiNhan'] = new_val
                                    changed = True
                                
                        if changed:
                            fresh_df = fresh_df.drop(columns=['is_in_month', 'TrangThaiDuyetKQ_disp'], errors='ignore')
                            if save_db(fresh_df):
                                st.success("✅ Đã lưu toàn bộ phê duyệt thành công!")
                                st.rerun()
                        else:
                            st.info("Chưa có thay đổi nào cần lưu.")


