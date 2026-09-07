import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add menu item
old_menu = '''        "🏆 Đánh giá KPI & Xếp loại",
        "⚙️ Quản Lý Cấu HÌnh"
    ],'''
new_menu = '''        "🏆 Đánh giá KPI & Xếp loại",
        "✅ Duyệt việc Khách quan",
        "⚙️ Quản Lý Cấu HÌnh"
    ],'''
content = content.replace(old_menu, new_menu)

# 2. Add the block for new menu
# Find the exact insertion point (before "⚙️ Quản Lý Cấu HÌnh")
insertion_marker = '''elif menu == "⚙️ Quản Lý Cấu HÌnh":'''

new_block = '''elif menu == "✅ Duyệt việc Khách quan":
    st.header("✅ Bàn làm việc Quản lý (Duyệt nhanh Khách quan)")
    
    if not st.session_state.is_admin_authenticated:
        st.warning("⚠️ Vui lòng nhập **Mật khẩu Quản lý** ở thanh bên trái (cột menu) để truy cập tính năng này.")
    else:
        df = read_db()
        if df.empty:
            st.info("Chưa có dữ liệu công việc.")
        else:
            col_thang, col_nam, col_phong = st.columns(3)
            with col_thang:
                thang_opts = list(range(1, 13))
                sel_thang = st.selectbox("Chọn Tháng", thang_opts, index=today.month - 1)
            with col_nam:
                nam_opts = [today.year - 1, today.year, today.year + 1]
                sel_nam = st.selectbox("Chọn Năm", nam_opts, index=1)
            with col_phong:
                phong_opts = ["Tất cả"] + OFFICIAL_DEPARTMENTS
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
                    
            df['is_in_month'] = df['Deadline'].apply(is_in_selected_month)
            
            # Condition: Deadline in month, objective reason
            mask = df['is_in_month'] & df['PhanLoaiTreHan'].astype(str).str.lower().str.contains("khách quan")
            if sel_phong != "Tất cả":
                mask = mask & (df['PhongBan'] == sel_phong)
                
            filtered_df = df[mask].copy()
            
            if filtered_df.empty:
                st.success(f"🎉 Không có công việc nào báo cáo Khách quan trong tháng {sel_thang}/{sel_nam}!")
            else:
                st.info(f"Đang hiển thị **{len(filtered_df)}** công việc báo cáo lý do Khách quan.")
                
                # Setup Editor
                edit_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "TrangThai", "GiaiTrinhDeXuat", "MucDoGhiNhan"]
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
                    "MucDoGhiNhan": st.column_config.SelectboxColumn(
                        "Mức độ Ghi nhận KPI",
                        help="Chọn mức điểm châm chước (Chỉ dành cho Quản lý)",
                        options=["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"],
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
                    # Update main df
                    changed = False
                    for idx, row in edited_df.iterrows():
                        task_id = row['ID']
                        new_val = row['MucDoGhiNhan']
                        old_val = df.loc[df['ID'] == task_id, 'MucDoGhiNhan'].values[0]
                        if new_val != old_val:
                            df.loc[df['ID'] == task_id, 'MucDoGhiNhan'] = new_val
                            changed = True
                            
                    if changed:
                        df = df.drop(columns=['is_in_month'], errors='ignore')
                        if save_db(df):
                            st.success("✅ Đã lưu toàn bộ phê duyệt thành công!")
                    else:
                        st.info("Chưa có thay đổi nào cần lưu.")

'''

content = content.replace(insertion_marker, new_block + insertion_marker)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
