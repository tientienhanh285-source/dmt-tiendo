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

db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
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



st.markdown("### ✏️ Phân hệ Thêm / Cập Nhật Công Việc")

tab_new, tab_update = st.tabs(["➕ Khởi tạo công việc mới", "✏️ Cập nhật tiến độ công việc"])

# Form: Add New
with tab_new:
    # --- TÍNH NĂNG NHÂN BẢN KẾ HOẠCH TỪ THÁNG TRƯỚC ---
    if role_mode in ["Quản lý", "Nhân viên"] and is_local:
        with st.expander("🪄 Nhập khẩu Kế hoạch (Sao chép từ tháng trước)", expanded=False):
            st.info("💡 Tính năng này giúp sao chép danh sách công việc & Tỷ trọng KPI của chính bạn từ tháng trước sang tháng này. Các việc 'Hoàn thành' sẽ tự động reset về 'Chưa bắt đầu'.")
            if st.button("🚀 Bê nguyên xi việc tháng trước sang tháng này"):
                with acquire_db_lock():
                    fresh_df = read_db()
                    if not fresh_df.empty:
                        from datetime import date
                        import re
                        
                        # Xác định tháng trước
                        prev_month = today.month - 1
                        prev_year = today.year
                        if prev_month == 0:
                            prev_month = 12
                            prev_year -= 1
                        
                        def is_prev_month(d):
                            import pandas as pd
                            from datetime import datetime, date
                            if pd.isna(d): return False
                            if isinstance(d, str):
                                try: d = datetime.strptime(d, "%Y-%m-%d").date()
                                except: return False
                            if isinstance(d, datetime): d = d.date()
                            if isinstance(d, date): return d.month == prev_month and d.year == prev_year
                            return False
                            
                        # Lọc các việc của tháng trước do người này phụ trách
                        user_name = st.session_state.personal_user if role_mode == "Nhân viên" else st.session_state.username
                        if role_mode == "Quản lý" and st.session_state.get('manager_dept'):
                            # Quản lý copy cho cả phòng ban
                            mask = (fresh_df['PhongBan'] == st.session_state.manager_dept) & fresh_df['Deadline'].apply(is_prev_month)
                        else:
                            mask = (fresh_df['NguoiChuTri'] == user_name) & fresh_df['Deadline'].apply(is_prev_month)
                            
                        tasks_to_copy = fresh_df[mask].copy()
                        
                        if tasks_to_copy.empty:
                            st.warning(f"Không tìm thấy công việc nào trong tháng {prev_month}/{prev_year} để sao chép!")
                        else:
                            # Tạo ID mới
                            next_id = 1
                            ids = fresh_df['ID'].tolist()
                            nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                            if nums: next_id = max(nums) + 1
                            
                            new_rows = []
                            import calendar
                            # Ngày cuối của tháng hiện tại
                            last_day = calendar.monthrange(today.year, today.month)[1]
                            new_start = date(today.year, today.month, 1)
                            new_deadline = date(today.year, today.month, last_day)
                            
                            for _, row in tasks_to_copy.iterrows():
                                new_row = row.copy()
                                new_row['ID'] = f"TSK-{next_id:03d}"
                                next_id += 1
                                
                                # Reset trạng thái
                                new_row['NgayBatDau'] = new_start
                                new_row['Deadline'] = new_deadline
                                new_row['TrangThai'] = "Chưa bắt đầu"
                                new_row['PhanTramHoanThanh'] = 0
                                new_row['LinkKetQua'] = ""
                                new_row['MucDoGhiNhan'] = "Mức 3 (100%)" # Reset đánh giá
                                new_row['PhanLoaiTreHan'] = "🟢 Không trễ hạn / Đúng tiến độ"
                                
                                new_rows.append(new_row)
                                
                            for r in new_rows:
                                r_dict = r.to_dict()
                                insert_task(r_dict)
                            st.success(f"🎉 Đã nhân bản thành công {len(new_rows)} công việc sang tháng {today.month}/{today.year}!")
                            st.rerun()

    st.markdown("#### Thêm mới công việc tự do")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Company selection
        company_list = list(COMPANIES.keys())
        default_company_idx = 0
        if selected_company in company_list:
            default_company_idx = company_list.index(selected_company)
        entry_company = st.selectbox(
            "Đơn vị / Công ty thành viên", 
            company_list, 
            index=default_company_idx,
            format_func=lambda x: str(x).replace("CTY CP", "CÔNG TY CP")
        )
        
        # 4. Department
        allowed_depts = get_departments_for_company(entry_company, config)
        is_personal = (role_mode == "Nhân viên" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
        if is_personal:
            # Deduce their department from their existing tasks or default to first
            user_dept_mode = display_df['PhongBan'].mode()
            user_dept = user_dept_mode[0] if not user_dept_mode.empty else allowed_depts[0]
            task_dept = st.selectbox("Phòng ban chịu trách nhiệm", [user_dept], index=0, disabled=True)
        else:
            task_dept = st.selectbox("Phòng ban chịu trách nhiệm", allowed_depts)
        
        # 5. Owner (based on configuration with custom type option)
        dept_personnel = get_personnel_for_company_dept(entry_company, task_dept, config)
        owner_options = list(dept_personnel) + ["✍️ Nhập tên người khác..."]
        
        # Find default lead index if present in department personnel
        dept_lead = DEPT_LEADS.get(entry_company, {}).get(task_dept, "")
        default_lead_idx = 0
        if dept_lead in dept_personnel:
            default_lead_idx = dept_personnel.index(dept_lead)
        
        is_personal = (role_mode == "Nhân viên" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
        if is_personal:
            sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", [st.session_state.personal_user], index=0, disabled=True)
            task_owner = st.session_state.personal_user
        else:
            sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", owner_options, index=default_lead_idx)
            if sel_owner_opt == "✍️ Nhập tên người khác...":
                task_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value="")
            else:
                task_owner = sel_owner_opt
        
        # 2. Project selection (Categorized dropdown or custom)
        project_targets = load_project_targets()
        khdt_projects = []
        for t in project_targets:
            if t.get("department") == task_dept and t.get("project_name") not in khdt_projects:
                khdt_projects.append(t.get("project_name"))
                
        db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
        merged_projs = get_filtered_projects(entry_company, config, db_projs, department=global_active_dept)
        
        for p in khdt_projects:
            if p not in merged_projs:
                merged_projs.append(p)
                
        proj_options_with_custom = merged_projs + ["✍️ Tự nhập Dự án / Hạng mục khác..."]
            
        default_proj_opt = st.selectbox("Dự án / Hạng mục", proj_options_with_custom)
        
        if default_proj_opt in ["✍️ Tự nhập Dự án / Hạng mục khác...", "➕ Tạo / Nhập Dự án mới..."]:
            project_name = st.text_input("Nhập tên Dự án / Hạng mục mới", value="")
        else:
            project_name = clean_proj_name(default_proj_opt)
            
        # 2.1 Target (Chỉ tiêu) selection
        clean_p = project_name.replace("[Dự án] ", "").replace("[Hạng mục] ", "").strip()
        associated_targets = [t["target_name"] for t in project_targets if t.get("project_name") == clean_p and t.get("department") == task_dept]
        
        selected_target = ""
        selected_budget = 0
        if associated_targets:
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #d97706; margin-bottom: 5px; margin-top: 15px;'>🎯 Thuộc Chỉ tiêu (Kế hoạch năm)</p>", unsafe_allow_html=True)
            target_options = associated_targets + ["Tự do / Không thuộc Chỉ tiêu nào"]
            selected_target = st.selectbox("Chọn Chỉ tiêu", target_options, label_visibility="collapsed")
            
            # Check if selected target has budget
            for t in project_targets:
                if t.get("target_name") == selected_target and t.get("budget_2026", 0) > 0:
                    selected_budget = t.get("budget_2026")
                    break
                    
            if selected_budget > 0:
                st.info(f"💡 Chỉ tiêu này có Kế hoạch giải ngân 2026 là **{selected_budget} Tỷ VNĐ**.")
                task_giai_ngan = st.number_input("💰 Giá trị giải ngân đợt này (Tỷ VNĐ)", min_value=0.0, step=0.1, value=0.0)
            else:
                task_giai_ngan = 0.0
        else:
            selected_target = "Tự do / Không thuộc Chỉ tiêu nào"
            task_giai_ngan = 0.0
        
        # 3. Task details
        task_name = st.text_input("Tên công việc (tự nhập tự do)", value="")
        
        task_weight = 0
            
        task_nguon = st.selectbox("Nguồn giao việc", ["Công việc được giao / định kì", 'CV giao ban / VB đến'])
        st.caption("💡 **Định kỳ:** Đăng ký đầu tháng / quản lý giao. **Giao ban:** Phát sinh sau khi họp giao ban.")
        
        task_moc_tien_do = "Tự do / Không gắn mục tiêu"
        if is_local:
            # --- 🚀 TÍNH NĂNG MỚI: TAGGING MỤC TIÊU QUÝ ---
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #1e3a8a; margin-bottom: 5px; margin-top: 15px;'>📌 Gắn với Mục tiêu Quý</p>", unsafe_allow_html=True)
            
            # Lấy danh sách Mục tiêu Quý
            current_year = str(today.year)
            year_key = f"{task_dept}_{current_year}"
            
            bsc_goals = []
            if "bsc_data" in st.session_state and "years" in st.session_state.bsc_data:
                if year_key in st.session_state.bsc_data["years"]:
                    bsc_goals = [f"[{g['quarter']}] {g['name']}" for g in st.session_state.bsc_data["years"][year_key]]
            
            if not bsc_goals:
                bsc_goals = ["Không có Mục tiêu Quý nào được thiết lập (Liên hệ Quản lý)"]
                
            task_moc_tien_do = st.selectbox("Chọn Mục tiêu Quý", ["Tự do / Không gắn mục tiêu"] + bsc_goals, label_visibility="collapsed")
        
    with col2:
        # 6. Dates
        task_start = st.date_input("Ngày bắt đầu thực hiện", today, format="DD/MM/YYYY")
        task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today, format="DD/MM/YYYY")
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔽 Tùy chọn nâng cao: Ghi nhận trạng thái / Nộp kết quả ngay", expanded=False):
            with st.container():
                st.markdown("<div style='padding: 15px; border-radius: 8px; border: 1px dashed #ccc; background-color: #f9f9f9; margin-bottom: 20px;'>", unsafe_allow_html=True)
                # 7 & 8. Status radio
                st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                is_late_for_status = (task_deadline < today)
                if is_late_for_status:
                    status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                else:
                    status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc"]
                task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                task_is_completed = (task_status_choice == "✅ Xác nhận ĐÃ HOÀN THÀNH công việc")
                task_has_issue = (task_status_choice == "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC")
                
                if task_status_choice is not None:
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    # 10. Ghi chú vướng mắc
                    is_late = (task_deadline < today) and not task_is_completed
                    task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if is_late:
                        st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                        task_late_cause = st.radio(
                            "Phân loại nguyên nhân trễ hạn",
                            ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                            index=0,
                            label_visibility="collapsed",
                            key="new_task_late_cause"
                        )
                    if is_late or task_has_issue:
                        task_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
                        if is_late and task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            st.caption("💡 **Lưu ý:** Giải trình này sẽ được hệ thống gửi đến Quản lý để xem xét mức độ ghi nhận KPI.")
                    else:
                        task_explain = ""
                    
                    # 9. Kết quả / File đính kèm
                    if task_has_issue:
                        task_file = None
                        task_link_text = ""
                        result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                    else:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if task_is_completed:
                            st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                        else:
                            st.markdown("**Kết quả / File đính kèm**")
                        result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key="new_result_mode")
                        if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            if task_is_completed:
                                st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                            else:
                                st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                            task_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link", height=100, label_visibility="collapsed", placeholder="Ví dụ: Báo cáo số 01/BC-DMT, đã trình sếp, hoặc dán link Google Drive...", key="new_result_text")
                            task_file = None
                        else:
                            task_file = st.file_uploader("Tải file đính kèm (PDF, Word, Excel, Ảnh...)", key="new_result_file")
                            task_link_text = ""
                else:
                    task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    task_explain = ""
                    result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                    task_link_text = ""
                    task_file = None
                    
                st.markdown("</div>", unsafe_allow_html=True)
            

        # 11. Chu kỳ theo dõi
        task_cycle = "Theo dự án / Tự do"

        
    submit_new = st.button("💾 Lưu", type="primary", key="btn_save_new_task")
    
    if submit_new:
        if not task_name.strip():
            st.error("⚠️ Vui lòng nhập Tên công việc!")
        elif not task_owner.strip():
            st.error("⚠️ Vui lòng nhập Người thực hiện!")
        else:
            # Calculate status and progress automatically
            if task_is_completed:
                calc_status = "Hoàn thành"
            elif task_has_issue:
                calc_status = "Có vướng mắc"
            elif task_deadline < today:
                calc_status = "Quá hạn"
            elif today >= task_start:
                calc_status = "Đang thực hiện"
            else:
                calc_status = "Chưa bắt đầu"
                
            task_progress = calculate_time_progress(task_start, task_deadline, task_is_completed)
            
            is_late = (task_deadline < today and not task_is_completed)
                
            # Constraints validation
            has_error = False
            if calc_status == "Hoàn thành":
                if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)" and not task_link_text.strip():
                    st.error("⚠️ Bắt buộc điền 'Kết quả / File đính kèm'!")
                    has_error = True
                elif result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and task_file is None:
                    st.error("⚠️ Bắt buộc tải file đính kèm!")
                    has_error = True
                    
            if is_late:
                if task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                    if not task_explain.strip() or len(task_explain.strip()) < 5:
                        st.error("⚠️ Bắt buộc nhập 'Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý' (tối thiểu 5 ký tự)!")
                        has_error = True
            elif calc_status == "Có vướng mắc":
                if not task_explain.strip() or len(task_explain.strip()) < 5:
                    st.error("⚠️ Bắt buộc nhập 'Chi tiết vướng mắc & Đề xuất hỗ trợ'!")
                    has_error = True
                    
            if not has_error:
                with acquire_db_lock():
                    
                    fresh_df = read_db()
                    
                    # Kiểm tra trùng lặp để cảnh báo người dùng (tránh click đúp)
                    is_duplicate = False
                    if not fresh_df.empty:
                        dup_df = fresh_df[
                            (fresh_df['TenCongViec'].astype(str).str.strip() == task_name.strip()) & 
                            (fresh_df['NguoiChuTri'].astype(str).str.strip() == task_owner.strip()) & 
                            (fresh_df['TenDuAn'].astype(str).str.strip() == project_name) &
                            (fresh_df['Deadline'].astype(str) == str(task_deadline)) &
                            (fresh_df['NgayBatDau'].astype(str) == str(task_start))
                        ]
                        if not dup_df.empty:
                            is_duplicate = True
                            
                    if is_duplicate:
                        st.error("⚠️ Công việc này đã tồn tại (trùng Tên công việc, Người thực hiện, Dự án và Thời gian)! Để tránh trùng lặp do bấm nhầm, hệ thống đã chặn lại. Nếu bạn thực sự muốn tạo 1 công việc giống hệt, vui lòng sửa lại Tên công việc (ví dụ: thêm số 2 vào cuối).")
                    else:
                        # Auto ID generator
                        next_id = 1
                        if not fresh_df.empty:
                            ids = fresh_df['ID'].tolist()
                            nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                            if nums:
                                next_id = max(nums) + 1
                        task_id = f"TSK-{next_id:03d}"
                        
                        saved_result = ""
                        
                        if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            saved_result = task_link_text.strip()
                        elif result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and task_file is not None:
                                upload_dir = os.path.join("OUTPUT", "UPLOADED_FILES")
                                if not os.path.exists(upload_dir):
                                    os.makedirs(upload_dir, exist_ok=True)
                                safe_name = re.sub(r'[^\w\-_.]', '_', task_file.name)
                                file_name = f"{task_id}_{safe_name}"
                                file_path = os.path.join(upload_dir, file_name)
                                with open(file_path, "wb") as f:
                                    f.write(task_file.getbuffer())
                                saved_result = file_path
                                
                        new_row = {
                            "ID": task_id,
                            "DonVi": entry_company,
                            "PhongBan": task_dept,
                            "NguoiChuTri": task_owner.strip(),
                            "TenDuAn": project_name,
                            "SanPhamBanGiao": selected_target,
                            "MocTienDo": task_moc_tien_do,
                            "TenCongViec": task_name.strip(),
                            "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
                            "NgayBatDau": task_start,
                            "Deadline": task_deadline,
                            "DoUuTien": "Trung bình",
                            "PhanTramHoanThanh": task_progress,
                            "TrangThai": calc_status,
                            "LinkKetQua": saved_result,
                            "GiaiTrinhDeXuat": (task_explain.strip() + f"\n[GIẢI NGÂN: {task_giai_ngan} TỶ]").strip() if task_giai_ngan > 0 else task_explain.strip(),
                            "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                            "ChuKyTheoDoi": task_cycle,
                            "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ",
                            "TyTrongKPI": task_weight,
                            "NguonGiaoViec": task_nguon,
                            "MucDoGhiNhan": "0% (Không ghi nhận)"
                        }
                        
                        new_id = insert_task(new_row)
                        if new_id:
                            st.session_state["success_msg"] = f"🎉 Đã khởi tạo thành công công việc mã: {new_id}!"
                            st.rerun()


# Form: Update Progress
with tab_update:
    st.markdown("#### Cập nhật tiến độ công việc đang chạy")
    
    # Display only items matching selected company
    avail_update_df = display_df.copy()
    if 'NgayCapNhat' in avail_update_df.columns:
        avail_update_df = avail_update_df.sort_values(by=['NgayCapNhat', 'ID'], ascending=[False, False]).reset_index(drop=True)
    
    is_personal_update = role_mode == "Nhân viên" and st.session_state.get("is_personal_authenticated", False)
    if is_personal_update:
        col_f3, col_f4 = st.columns(2)
        filter_dept = "Tất cả"
        filter_owner = "Tất cả"
    else:
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            departments = ["Tất cả"] + sorted(list(avail_update_df['PhongBan'].dropna().astype(str).unique()))
            filter_dept = st.selectbox("Lọc theo Phòng ban", departments, key="filter_dept_update")
        with col_f2:
            owners = ["Tất cả"] + sorted(list(avail_update_df['NguoiChuTri'].dropna().astype(str).unique()))
            filter_owner = st.selectbox("Lọc theo Người phụ trách", owners, key="filter_owner_update")
            
    with col_f3:
        projects = ["Tất cả"] + sorted(list(avail_update_df['TenDuAn'].dropna().astype(str).unique()))
        filter_proj = st.selectbox("Lọc theo Dự án", projects, key="filter_proj_update")
    with col_f4:
        months = set()
        if not avail_update_df.empty:
            for _, row in avail_update_df.iterrows():
                if pd.notna(row.get('NgayBatDau')) and hasattr(row['NgayBatDau'], 'strftime'):
                    months.add(row['NgayBatDau'].strftime('%m/%Y'))
                if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                    months.add(row['Deadline'].strftime('%m/%Y'))
        month_options = ["Tất cả"] + sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        filter_month = st.selectbox("Lọc theo Tháng", month_options, key="filter_month_update")
        
    if filter_dept != "Tất cả":
        avail_update_df = avail_update_df[avail_update_df['PhongBan'] == filter_dept]
    if filter_owner != "Tất cả":
        avail_update_df = avail_update_df[avail_update_df['NguoiChuTri'] == filter_owner]
    if filter_proj != "Tất cả":
        avail_update_df = avail_update_df[avail_update_df['TenDuAn'] == filter_proj]
    if filter_month != "Tất cả":
        mask = (
            avail_update_df['NgayBatDau'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == filter_month
        ) | (
            avail_update_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == filter_month
        )
        avail_update_df = avail_update_df[mask]

    if avail_update_df.empty:
        st.info("Chưa có công việc nào khả dụng.")
    else:
        def format_task_option(task_id):
            row = df[df['ID'] == task_id].iloc[0]
            pic = row.get('NguoiChuTri', 'Chưa rõ')
            prefix = "🌟 [QUẢN LÝ GIAO] " if ("[Mục tiêu" in str(row.get('GiaiTrinhDeXuat', ''))) else ""
            return f"{prefix}{row['TenCongViec']} - Phụ trách: {pic}"
        
        selected_id = st.selectbox("Chọn công việc cần cập nhật", avail_update_df['ID'].tolist(), format_func=format_task_option)
        task_data = df[df['ID'] == selected_id].iloc[0]
        
        with st.container():
            col_u1, col_u2 = st.columns(2)
            
            with col_u1:
                st.markdown(f"**Mã Hạng mục:** `{task_data['ID']}`")
                st.markdown(f"**Đơn vị:** {task_data['DonVi']}")
                st.markdown(f"**Phòng ban phụ trách:** {task_data['PhongBan']}")
                
                u_proj = st.text_input("Dự án / Hạng mục", value=task_data['TenDuAn'], key=f"u_proj_{task_data['ID']}")
                u_name = st.text_input("Tên công việc", value=task_data['TenCongViec'], key=f"u_name_{task_data['ID']}")
                u_nguon_opts = ["Công việc được giao / định kì", 'CV giao ban / VB đến']
                current_nguon = task_data.get('NguonGiaoViec', 'Công việc được giao / định kì')
                u_nguon_idx = u_nguon_opts.index(current_nguon) if current_nguon in u_nguon_opts else 0
                u_nguon = st.selectbox("Nguồn giao việc", u_nguon_opts, index=u_nguon_idx, key=f"u_nguon_{task_data['ID']}")
                st.caption("💡 **Định kỳ:** Đăng ký đầu tháng. **Giao ban:** Phát sinh sau khi họp giao ban.")
                
                # Owner selection based on configuration
                u_dept = task_data['PhongBan']
                u_dept_personnel = get_personnel_for_company_dept(task_data['DonVi'], u_dept, config)
                u_owner_options = list(u_dept_personnel) + ["✍️ Nhập tên người khác..."]
                
                current_owner = task_data['NguoiChuTri']
                is_personal = (role_mode == "Nhân viên" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
                if is_personal:
                    st.selectbox("Người thực hiện / Phụ trách", [st.session_state.personal_user], index=0, disabled=True, key=f"u_owner_sel_{task_data['ID']}")
                    u_owner = st.session_state.personal_user
                else:
                    if current_owner in u_dept_personnel:
                        u_default_index = u_dept_personnel.index(current_owner)
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                        if u_sel_owner_opt == "✍️ Nhập tên người khác...":
                            u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value="", key=f"u_owner_custom_{task_data['ID']}")
                        else:
                            u_owner = u_sel_owner_opt
                    else:
                        u_default_index = len(u_owner_options) - 1
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                        u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value=current_owner, key=f"u_owner_custom_{task_data['ID']}")
                
            with col_u2:
                is_emp_locked = (role_mode == "Nhân viên")
                u_start = st.date_input("Ngày bắt đầu thực hiện", value=pd.to_datetime(task_data['NgayBatDau']).date() if pd.notna(task_data['NgayBatDau']) and str(task_data['NgayBatDau']).strip() else today, format="DD/MM/YYYY", disabled=is_emp_locked, key=f"u_start_{task_data['ID']}")
                u_deadline = st.date_input("Hạn hoàn thành (Deadline)", value=pd.to_datetime(task_data['Deadline']).date() if pd.notna(task_data['Deadline']) and str(task_data['Deadline']).strip() else today, format="DD/MM/YYYY", disabled=is_emp_locked, key=f"u_deadline_{task_data['ID']}")
                
                st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                u_current_status = task_data.get('TrangThai', 'Đang thực hiện')
                u_is_late_for_status = (u_deadline is not None and u_deadline < today)
                if u_is_late_for_status or u_current_status == 'Có vướng mắc':
                    u_status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                else:
                    u_status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc"]
                
                if u_current_status == 'Hoàn thành':
                    u_status_idx = 0
                elif u_current_status == 'Có vướng mắc':
                    u_status_idx = 1
                else:
                    u_status_idx = None
                    
                u_status_choice = st.radio("Trạng thái công việc", u_status_opts, index=u_status_idx, label_visibility="collapsed", key=f"u_status_choice_{task_data['ID']}")
                u_is_completed = (u_status_choice == "✅ Xác nhận ĐÃ HOÀN THÀNH công việc")
                u_has_issue = (u_status_choice == "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC")
                
                # 11. Chu kỳ theo dõi
                current_cycle = task_data.get('ChuKyTheoDoi', 'Theo dự án / Tự do')
                cycle_list = ["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]
                default_cycle_idx = cycle_list.index(current_cycle) if current_cycle in cycle_list else 3
                u_cycle = current_cycle
                
                is_emp_locked = (role_mode == "Nhân viên")
                u_weight = task_data.get('TyTrongKPI', '')
                
            
            u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
            current_link = task_data.get('LinkKetQua', '')
            if u_status_choice is not None:
                st.markdown("<div style='padding: 15px; border-radius: 8px; border: 1px dashed #ccc; background-color: #f9f9f9; margin-top: 15px;'>", unsafe_allow_html=True)
                u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                if u_is_late:
                    st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                    u_options = ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                    u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                    u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                    u_late_cause = st.radio(
                        "Phân loại nguyên nhân trễ hạn",
                        u_options,
                        index=u_default_idx,
                        label_visibility="collapsed",
                        key=f"u_late_cause_sel_{task_data['ID']}"
                    )
                if u_is_late or u_has_issue:
                    u_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key=f"u_explain_txt_{task_data['ID']}")
                    if u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                        if st.session_state.is_admin_authenticated or st.session_state.get('is_manager_authenticated', False):
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            chamchuoc_opts = ["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"]
                            idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                            u_chamchuoc = st.selectbox("Mức độ ghi nhận (Dành cho Quản lý)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                        else:
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            u_chamchuoc = current_chamchuoc
                            if current_chamchuoc != '0% (Không ghi nhận)':
                                st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                            else:
                                st.caption("💡 **Lưu ý:** Giải trình này sẽ được hệ thống gửi đến Quản lý để xem xét mức độ ghi nhận KPI.")
                    else:
                        u_chamchuoc = '0% (Không ghi nhận)'
                else:
                    u_explain = ""
                    u_chamchuoc = '0% (Không ghi nhận)'
                

                
                u_link_text = ""
                u_file = None
                u_result_mode = None
                if not u_has_issue:
                    if u_is_completed:
                        st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown("**Cập nhật Kết quả / File đính kèm**")
                        
                    u_result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                    
                    if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                        if u_is_completed:
                            st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                        else:
                            st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                        u_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", height=100, label_visibility="collapsed", placeholder="Ví dụ: Đã hoàn thành 50%, trình ký sếp...", key=f"u_result_text_{task_data['ID']}")
                    elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                        u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                u_explain = ""
                u_chamchuoc = '0% (Không ghi nhận)'
                u_link_text = ""
                u_file = None
                u_result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"

                

            btn_save, btn_del = st.columns([3, 2])
            
            with btn_save:
                save_click = st.button("💾 LƯU CẬP NHẬT TIẾN ĐỘ", type="primary", key=f"btn_save_update_{task_data['ID']}")
            with btn_del:
                del_click = False
                if st.session_state.is_admin_authenticated:
                    confirm_del = st.checkbox("Xác nhận xóa dữ liệu này", key=f"confirm_del_{task_data['ID']}")
                    if confirm_del:
                        del_click = st.button("🗑️ XÓA CÔNG VIỆC CHỌN", type="secondary", key=f"btn_del_update_{task_data['ID']}")


            if save_click:
                has_error = False
                
                # Validate evidence if completed
                if u_is_completed and not u_link_text.strip() and not u_file:
                    st.error("❌ Lỗi: Bạn phải nhập Link kết quả hoặc Tải file đính kèm để báo cáo Hoàn thành!")
                    has_error = True
                else:
                    # Calculate status and progress automatically
                    if u_is_completed:
                        u_status = "Chờ nghiệm thu"
                    elif u_has_issue:
                        u_status = "Có vướng mắc"
                    elif u_deadline < today:
                        u_status = "Quá hạn"
                    elif today >= u_start:
                        u_status = "Đang thực hiện"
                    else:
                        u_status = "Chưa bắt đầu"
                        
                    u_progress = calculate_time_progress(u_start, u_deadline, u_is_completed)
                        
                    # Constraints validation
                    if u_status == "Chờ nghiệm thu":
                        if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)" and not u_link_text.strip() and not current_link:
                            st.error("⚠️ Bắt buộc điền 'Kết quả / File đính kèm' để hoàn thành công việc!")
                            has_error = True
                        elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and u_file is None and not current_link:
                            st.error("⚠️ Bắt buộc tải file đính kèm để hoàn thành công việc!")
                            has_error = True
                        
                    if u_is_late:
                        if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            if not u_explain.strip() or len(u_explain.strip()) < 5:
                                st.error("⚠️ Bắt buộc nhập 'Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý' (tối thiểu 5 ký tự)!")
                                has_error = True
                    elif u_status == "Có vướng mắc":
                        if not u_explain.strip() or len(u_explain.strip()) < 5:
                            st.error("⚠️ Bắt buộc nhập 'Chi tiết vướng mắc & Đề xuất hỗ trợ'!")
                            has_error = True
                            
                    if not has_error:
                        # Determine final link value
                        final_link = current_link
                        
                        if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            if u_link_text.strip():
                                final_link = u_link_text.strip()
                        elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and u_file is not None:
                            upload_dir = os.path.join("OUTPUT", "UPLOADED_FILES")
                            if not os.path.exists(upload_dir):
                                os.makedirs(upload_dir, exist_ok=True)
                            safe_name = re.sub(r'[^\w\-_.]', '_', u_file.name)
                            file_name = f"{selected_id}_{safe_name}"
                            file_path = os.path.join(upload_dir, file_name)
                            with open(file_path, "wb") as f:
                                f.write(u_file.getbuffer())
                            final_link = file_path
                            
                        with acquire_db_lock():
                            
                            fresh_df = read_db()
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'TenDuAn'] = u_proj.strip()
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'TenCongViec'] = u_name.strip()
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'NguoiChuTri'] = u_owner.strip()
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'NgayBatDau'] = u_start
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'Deadline'] = u_deadline
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'PhanTramHoanThanh'] = u_progress
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'TrangThai'] = u_status
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'LinkKetQua'] = final_link
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'GiaiTrinhDeXuat'] = u_explain.strip()
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'NgayCapNhat'] = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'ChuKyTheoDoi'] = u_cycle
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'PhanLoaiTreHan'] = u_late_cause if u_is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'TyTrongKPI'] = str(u_weight)
                            fresh_df.loc[fresh_df['ID'] == selected_id, 'NguonGiaoViec'] = u_nguon
                            if u_is_late:
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'MucDoGhiNhan'] = u_chamchuoc
                            else:
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'MucDoGhiNhan'] = '0% (Không ghi nhận)'

                            update_dict = {
                                'TenDuAn': u_proj.strip(),
                                'TenCongViec': u_name.strip(),
                                'NguoiChuTri': u_owner.strip(),
                                'NgayBatDau': u_start,
                                'Deadline': u_deadline,
                                'PhanTramHoanThanh': u_progress,
                                'TrangThai': u_status,
                                'LinkKetQua': final_link,
                                'GiaiTrinhDeXuat': u_explain.strip(),
                                'NgayCapNhat': (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                                'ChuKyTheoDoi': u_cycle,
                                'PhanLoaiTreHan': u_late_cause if u_is_late else "🟢 Không trễ hạn / Đúng tiến độ",
                                'TyTrongKPI': str(u_weight),
                                'NguonGiaoViec': u_nguon,
                                'MucDoGhiNhan': u_chamchuoc if u_is_late else '0% (Không ghi nhận)'
                            }
                            if update_task(selected_id, update_dict):
                                st.session_state["success_msg"] = f"🎉 Đã lưu cập nhật công việc mã: {selected_id}!"
                                st.rerun()
                            
                if has_error:
                    st.session_state.is_updating_task = False
                        
            if del_click:
                with acquire_db_lock():
                    
                    if delete_task(selected_id):
                        st.session_state["success_msg"] = f"🗑️ Đã xóa thành công công việc mã: {selected_id}!"
                        st.rerun()

            st.markdown("---")
            with st.expander("🔄 Tái tạo công việc định kỳ (Nhân bản cho kỳ sau)"):
                st.info("Tính năng này giúp nhân bản công việc hiện tại thành một công việc mới cho kỳ tiếp theo (dành cho các báo cáo tuần, giao ban tháng...).")
                
                rep_name = st.text_input("Tên công việc mới", value=f"{task_data['TenCongViec']} (Kỳ tiếp theo)", key=f"rep_name_{task_data['ID']}")
                
                try:
                    from dateutil.relativedelta import relativedelta
                    import pandas as pd
                    
                    # Fix for cases where NgayBatDau or Deadline might be NaT or None
                    if pd.notna(task_data.get('NgayBatDau')):
                        default_start = task_data['NgayBatDau'] + relativedelta(months=1)
                    else:
                        default_start = today
                        
                    if pd.notna(task_data.get('Deadline')):
                        default_deadline = task_data['Deadline'] + relativedelta(months=1)
                    else:
                        default_deadline = default_start + timedelta(days=6)
                except Exception as e:
                    default_start = task_data['Deadline'] + timedelta(days=1) if pd.notna(task_data.get('Deadline')) else today
                    default_deadline = default_start + timedelta(days=6)
                
                col_rep1, col_rep2 = st.columns(2)
                with col_rep1:
                    rep_start = st.date_input("Ngày bắt đầu mới", value=default_start, format="DD/MM/YYYY", key=f"rep_start_{task_data['ID']}")
                with col_rep2:
                    rep_deadline = st.date_input("Hạn chót mới", value=default_deadline, format="DD/MM/YYYY", key=f"rep_deadline_{task_data['ID']}")
                    
                if st.button("🔄 TẠO CÔNG VIỆC CHO KỲ SAU", type="primary", key=f"btn_rep_{task_data['ID']}"):
                    with acquire_db_lock():
                        
                        fresh_df = read_db()
                        
                        next_id = 1
                        if not fresh_df.empty:
                            ids = fresh_df['ID'].tolist()
                            import re
                            nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                            if nums:
                                next_id = max(nums) + 1
                        new_id = f"TSK-{next_id:03d}"
                        
                        new_row = {
                            "ID": new_id,
                            "DonVi": task_data['DonVi'],
                            "PhongBan": task_data['PhongBan'],
                            "NguoiChuTri": task_data['NguoiChuTri'],
                            "TenDuAn": task_data['TenDuAn'],
                            "MocTienDo": "Tự do",
                            "SanPhamBanGiao": "Xem chi tiết",
                            "TenCongViec": rep_name.strip(),
                            "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
                            "NgayBatDau": rep_start,
                            "Deadline": rep_deadline,
                            "DoUuTien": "Trung bình",
                            "PhanTramHoanThanh": 0,
                            "TrangThai": "Chưa bắt đầu" if today < rep_start else "Đang thực hiện",
                            "LinkKetQua": "",
                            "GiaiTrinhDeXuat": "",
                            "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                            "ChuKyTheoDoi": task_data['ChuKyTheoDoi'],
                            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ"
                        }
                        
                        df_rep = pd.concat([fresh_df, pd.DataFrame([new_row])], ignore_index=True)
                        if save_db(df_rep):
                            st.session_state["success_msg"] = f"🎉 Đã nhân bản thành công công việc mới mã: {new_id}!"
                            st.rerun()

# ----------------- 5. ĐÁNH GIÁ KPI & XẾP LOẠI -----------------
