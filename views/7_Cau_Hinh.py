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



st.markdown("### ⚙️ Quản Lý Cấu Hình Hệ Thống")

tab_proj, tab_dept, tab_gsheets = st.tabs(["📁 Quản lý Dự án", "🏢 Quản lý Phòng ban", "📊 Đồng bộ Google Sheets"])

with tab_proj:
    if selected_company == "Tất cả đơn vị":
        st.warning("⚠️ Vui lòng chọn cụ thể một **Công ty / Đơn vị** ở menu bên trái để tiến hành cấu hình (Không áp dụng cho 'Tất cả đơn vị').")
    else:
        st.info(f"Đang cấu hình dữ liệu cho: **{selected_company}**")
        # Load current company's config
        comp_config = config.get("companies", {}).get(selected_company, {})
        comp_projects_by_cat = comp_config.get("projects_by_category", {})
        
        st.markdown(f"#### Quản lý Danh mục Dự án - {selected_company}")
        
        cats = list(comp_projects_by_cat.keys())
        if not cats:
            st.info("Chưa có lĩnh vực dự án nào. Vui lòng cập nhật cấu trúc JSON hoặc thêm mới.")
        else:
            sel_cat = st.selectbox("Chọn Lĩnh vực dự án", cats)
            projs_in_cat = comp_projects_by_cat.get(sel_cat, [])
            
            st.markdown(f"**Danh sách dự án hiện tại trong [{sel_cat}]:**")
            st.write(", ".join(projs_in_cat) if projs_in_cat else "Chưa có dự án nào")
            
            st.markdown("---")
            
            col_add, col_edit, col_del = st.columns(3)
            
            with col_add:
                st.markdown("**➕ Thêm dự án mới**")
                new_proj_name = st.text_input("Tên dự án mới", key="admin_add_proj")
                if st.button("Thêm dự án", type="primary"):
                    if new_proj_name.strip():
                        if new_proj_name.strip() not in projs_in_cat:
                            config["companies"][selected_company]["projects_by_category"][sel_cat].append(new_proj_name.strip())
                            if save_config(config):
                                st.success(f"Đã thêm dự án: {new_proj_name}")
                                
                                st.rerun()
                        else:
                            st.error("Dự án đã tồn tại!")
                    else:
                        st.error("Tên dự án không được để trống!")
                        
            with col_edit:
                st.markdown("**✏️ Đổi tên dự án**")
                if projs_in_cat:
                    proj_to_edit = st.selectbox("Chọn dự án cần sửa", projs_in_cat, key="admin_edit_proj_sel")
                    edited_proj_name = st.text_input("Tên dự án mới", value=proj_to_edit, key="admin_edit_proj_val")
                    if st.button("Lưu đổi tên"):
                        if edited_proj_name.strip():
                            idx = config["companies"][selected_company]["projects_by_category"][sel_cat].index(proj_to_edit)
                            config["companies"][selected_company]["projects_by_category"][sel_cat][idx] = edited_proj_name.strip()
                            if save_config(config):
                                st.success(f"Đã đổi tên thành: {edited_proj_name}")
                                
                                st.rerun()
                        else:
                            st.error("Tên mới không được để trống!")
                else:
                    st.write("Không có dự án để sửa.")
                    
            with col_del:
                st.markdown("**🗑️ Xóa dự án**")
                if projs_in_cat:
                    proj_to_del = st.selectbox("Chọn dự án cần xóa", projs_in_cat, key="admin_del_proj_sel")
                    if st.button("Xác nhận xóa dự án", type="secondary"):
                        config["companies"][selected_company]["projects_by_category"][sel_cat].remove(proj_to_del)
                        if save_config(config):
                            st.success(f"Đã xóa dự án: {proj_to_del}")
                            
                            st.rerun()
                else:
                    st.write("Không có dự án để xóa.")

with tab_dept:
    if selected_company == "Tất cả đơn vị":
        st.warning("⚠️ Vui lòng chọn cụ thể một **Công ty / Đơn vị** ở menu bên trái để tiến hành cấu hình (Không áp dụng cho 'Tất cả đơn vị').")
    else:
        comp_config = config.get("companies", {}).get(selected_company, {})
        comp_depts = comp_config.get("departments", [])
        comp_personnel = comp_config.get("personnel_by_department", {})
        
        st.markdown(f"#### Quản lý Danh sách Phòng ban - {selected_company}")
        st.markdown(f"**Danh sách phòng ban hiện tại ({len(comp_depts)} phòng ban):**")
        st.write(", ".join(comp_depts) if comp_depts else "Chưa có phòng ban nào")
        
        st.markdown("---")
        
        col_d_add, col_d_edit, col_d_del = st.columns(3)
        
        with col_d_add:
            st.markdown("**➕ Thêm phòng ban mới**")
            new_dept_name = st.text_input("Tên phòng ban mới", key="admin_add_dept")
            if st.button("Thêm phòng ban", type="primary"):
                if new_dept_name.strip():
                    if new_dept_name.strip() not in comp_depts:
                        config["companies"][selected_company]["departments"].append(new_dept_name.strip())
                        if save_config(config):
                            st.success(f"Đã thêm phòng ban: {new_dept_name}")
                            
                            st.rerun()
                    else:
                        st.error("Phòng ban đã tồn tại!")
                else:
                    st.error("Tên không được để trống!")
                    
        with col_d_edit:
            st.markdown("**✏️ Đổi tên phòng ban**")
            if comp_depts:
                dept_to_edit = st.selectbox("Chọn phòng ban cần sửa", comp_depts, key="admin_edit_dept_sel")
                edited_dept_name = st.text_input("Tên phòng ban mới", value=dept_to_edit, key="admin_edit_dept_val")
                if st.button("Lưu đổi tên phòng"):
                    if edited_dept_name.strip():
                        idx = config["companies"][selected_company]["departments"].index(dept_to_edit)
                        config["companies"][selected_company]["departments"][idx] = edited_dept_name.strip()
                        # Update personnel keys as well
                        if dept_to_edit in config["companies"][selected_company]["personnel_by_department"]:
                            config["companies"][selected_company]["personnel_by_department"][edited_dept_name.strip()] = config["companies"][selected_company]["personnel_by_department"].pop(dept_to_edit, [])
                        if save_config(config):
                            st.success(f"Đã đổi tên thành: {edited_dept_name}")
                            
                            st.rerun()
                    else:
                        st.error("Tên mới không được để trống!")
            else:
                st.write("Không có phòng ban để sửa.")
                
        with col_d_del:
            st.markdown("**🗑️ Xóa phòng ban**")
            if comp_depts:
                dept_to_del = st.selectbox("Chọn phòng ban cần xóa", comp_depts, key="admin_del_dept_sel")
                if st.button("Xác nhận xóa phòng", type="secondary"):
                    config["companies"][selected_company]["departments"].remove(dept_to_del)
                    # Remove personnel mapping too
                    config["companies"][selected_company]["personnel_by_department"].pop(dept_to_del, None)
                    if save_config(config):
                        st.success(f"Đã xóa phòng ban: {dept_to_del}")
                        
                        st.rerun()
            else:
                st.write("Không có phòng ban để xóa.")

        st.markdown("---")
        st.markdown(f"#### 👥 Quản lý Nhân sự theo Phòng ban - {selected_company}")
        
        if comp_depts:
            sel_dept_p = st.selectbox("Chọn phòng ban để quản lý nhân sự", comp_depts, key="admin_sel_dept_p")
                
            # Load personnel list
            current_p_list = comp_personnel.get(sel_dept_p, [])
            
            st.markdown(f"**Danh sách nhân sự thuộc [{sel_dept_p}] ({len(current_p_list)} người):**")
            st.write(", ".join(current_p_list) if current_p_list else "Chưa có nhân sự nào")
            
            st.markdown("---")
            
            col_p_add, col_p_edit, col_p_del = st.columns(3)
            
            with col_p_add:
                st.markdown("**➕ Thêm nhân sự mới**")
                new_p_name = st.text_input("Tên nhân sự mới", key="admin_add_p_name")
                if st.button("Thêm nhân sự", type="primary", key="btn_admin_add_p"):
                    if new_p_name.strip():
                        if new_p_name.strip() not in current_p_list:
                            if sel_dept_p not in config["companies"][selected_company]["personnel_by_department"]:
                                config["companies"][selected_company]["personnel_by_department"][sel_dept_p] = []
                            config["companies"][selected_company]["personnel_by_department"][sel_dept_p].append(new_p_name.strip())
                            if save_config(config):
                                st.success(f"Đã thêm nhân sự: {new_p_name.strip()}")
                                
                                st.rerun()
                        else:
                            st.error("Nhân sự đã tồn tại trong phòng ban này!")
                    else:
                        st.error("Tên nhân sự không được để trống!")
                        
            with col_p_edit:
                st.markdown("**✏️ Sửa tên nhân sự**")
                if current_p_list:
                    p_to_edit = st.selectbox("Chọn nhân sự cần sửa", current_p_list, key="admin_edit_p_sel")
                    edited_p_name = st.text_input("Tên nhân sự mới", value=p_to_edit, key="admin_edit_p_val")
                    if st.button("Lưu thay đổi", key="btn_admin_edit_p"):
                        if edited_p_name.strip():
                            if edited_p_name.strip() not in current_p_list or edited_p_name.strip() == p_to_edit:
                                idx = current_p_list.index(p_to_edit)
                                config["companies"][selected_company]["personnel_by_department"][sel_dept_p][idx] = edited_p_name.strip()
                                if save_config(config):
                                    st.success(f"Đã cập nhật tên nhân sự thành: {edited_p_name.strip()}")
                                    
                                    st.rerun()
                            else:
                                st.error("Tên mới đã tồn tại trong phòng ban này!")
                        else:
                            st.error("Tên mới không được để trống!")
                else:
                    st.write("Không có nhân sự để sửa.")
                    
            with col_p_del:
                st.markdown("**🗑️ Xóa nhân sự**")
                if current_p_list:
                    p_to_del = st.selectbox("Chọn nhân sự cần xóa", current_p_list, key="admin_del_p_sel")
                    if st.button("Xác nhận xóa", type="secondary", key="btn_admin_del_p"):
                        config["companies"][selected_company]["personnel_by_department"][sel_dept_p].remove(p_to_del)
                        if save_config(config):
                            st.success(f"Đã xóa nhân sự: {p_to_del}")
                            
                            st.rerun()
                else:
                    st.write("Không có nhân sự để xóa.")
        else:
            st.warning("Vui lòng tạo ít nhất một phòng ban trước khi cấu hình nhân sự.")

with tab_gsheets:
    st.markdown("#### 📊 Cấu hình kết nối Google Sheets")
    if is_gsheets_configured():
        st.success("🎉 Hệ thống đã kết nối thành công với Google Sheets! Mọi thay đổi dữ liệu sẽ được tự động đồng bộ thời gian thực.")
        try:
            st.info(f"**Spreadsheet URL:** `{st.secrets['connections']['gsheets']['spreadsheet']}`")
        except Exception:
            pass
    else:
        st.warning("⚠️ Hiện tại hệ thống đang hoạt động ở chế độ ngoại tuyến (Offline) bằng file Excel cục bộ.")
        
    st.markdown("""
    ### 📝 Hướng dẫn kết nối Google Sheets trên Streamlit Cloud
    Để đồng bộ dữ liệu trực tuyến, vui lòng thực hiện các bước sau:
    
    1. **Tạo Google Sheet**: Tạo một bảng tính Google Sheets mới. Đảm bảo sheet đầu tiên có tên là `Sheet1`.
    2. **Định cấu hình cột mẫu**: Bạn có thể tải file Excel hiện tại từ sidebar xuống và copy cấu trúc cột sang Google Sheets. Các cột gồm:
       `ID`, `DonVi`, `PhongBan`, `NguoiChuTri`, `TenDuAn`, `MocTienDo`, `SanPhamBanGiao`, `TenCongViec`, `PhanLoaiChiSo`, `NgayBatDau`, `Deadline`, `DoUuTien`, `PhanTramHoanThanh`, `TrangThai`, `LinkKetQua`, `GiaiTrinhDeXuat`, `NgayCapNhat`
    3. **Chia sẻ quyền chỉnh sửa**: Chia sẻ Google Sheet đó với tài khoản **Google Service Account** của bạn (cấp quyền **Editor**).
    4. **Cấu hình Secrets trên Streamlit Cloud**:
       - Truy cập Dashboard của Streamlit Cloud -> Vào ứng dụng -> Chọn **Settings** -> **Secrets**.
       - Nhập thông tin cấu hình Service Account theo định dạng sau:
       ```toml
       [connections.gsheets]
       spreadsheet = "https://docs.google.com/spreadsheets/d/your-spreadsheet-id"
       type = "service_account"
       project_id = "your-project-id"
       private_key_id = "your-private-key-id"
       private_key = "-----BEGIN PRIVATE KEY-----\\nyour-private-key-details\\n-----END PRIVATE KEY-----\\n"
       client_email = "your-service-account-email@your-project.iam.gserviceaccount.com"
       client_id = "your-client-id"
       auth_uri = "https://accounts.google.com/o/oauth2/auth"
       token_uri = "https://oauth2.googleapis.com/token"
       auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
       client_x509_cert_url = "https://www.googleapis.com/workspace/3pid/cert"
       ```
    5. **Khởi động lại (Reboot) app**: Lưu lại Secrets, Streamlit sẽ tự động đồng bộ và nạp dữ liệu từ Google Sheets.
    """)

# ----------------- 6. SỔ TAY HƯỚNG DẪN -----------------

