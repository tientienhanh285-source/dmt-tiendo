import sys
import re

file_path = "app.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

clone_pattern = re.compile(r'(st\.markdown\("#### Thêm mới công việc tự do"\))', re.DOTALL)

clone_code = """\\1
        
        # --- TÍNH NĂNG NHÂN BẢN KẾ HOẠCH TỪ THÁNG TRƯỚC ---
        if role_mode in ["Quản lý", "Nhân viên"]:
            with st.expander("🪄 Nhập khẩu Kế hoạch (Sao chép từ tháng trước)", expanded=False):
                st.info("💡 Tính năng này giúp sao chép danh sách công việc & Tỷ trọng KPI của chính bạn từ tháng trước sang tháng này. Các việc 'Hoàn thành' sẽ tự động reset về 'Chưa bắt đầu'.")
                if st.button("🚀 Bê nguyên xi việc tháng trước sang tháng này"):
                    with acquire_db_lock():
                        fresh_df = read_db()
                        if not fresh_df.empty:
                            from datetime import date
                            
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
                                    
                                df_updated = pd.concat([fresh_df, pd.DataFrame(new_rows)], ignore_index=True)
                                if save_db(df_updated):
                                    st.success(f"🎉 Đã nhân bản thành công {len(new_rows)} công việc sang tháng {today.month}/{today.year}!")
                                    st.rerun()
"""

content = clone_pattern.sub(clone_code, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully!")
