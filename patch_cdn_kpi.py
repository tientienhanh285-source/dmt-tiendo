import sys
import re

file_path = "app.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Bỏ Hệ số A-B-C, quay lại gõ Tỷ trọng
abc_pattern = re.compile(
    r"# --- 🚀 TÍNH NĂNG MỚI: TỪ ĐIỂN HỆ SỐ A-B-C ---.*?task_weight = 1", 
    re.DOTALL
)
replacement_weight = """task_weight = st.number_input("Tỷ trọng KPI cho công việc này (%)", value=0)
            st.caption("💡 Mẹo: Quản lý tự chia tỷ trọng cho các việc trong tháng (Tổng có thể là 100%).")"""
content = abc_pattern.sub(replacement_weight, content)

# 2. Sửa UI Đánh giá (kpi_tab1)
# Currently kpi_tab1 calculates score by: def calc_score_for_group(grp): ...
calc_score_pattern = re.compile(
    r"def calc_score_for_group\(grp\):.*?return 0",
    re.DOTALL
)

new_calc_score = """def calc_score_for_group(grp):
                    if grp.empty: return 0
                    t_score = 0
                    total_w = 0
                    for idx, row in grp.iterrows():
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        muc_dat = str(row.get('MucDoGhiNhan', 'Mức 3'))
                        
                        if 'Mức 4' in muc_dat: p = 125
                        elif 'Mức 3' in muc_dat: p = 100
                        elif 'Mức 2' in muc_dat: p = 75
                        elif 'Mức 1' in muc_dat: p = 50
                        elif 'Mức 0' in muc_dat: p = 0
                        elif 'Mức -1' in muc_dat: p = -50
                        elif 'Mức -2' in muc_dat: p = -75
                        elif 'Mức -3' in muc_dat: p = -100
                        else:
                            # Tương thích ngược: Nếu chưa chấm mức, tính theo Trạng thái
                            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                            p = 100 if is_comp else 0

                        t_score += (p / 100.0) * w
                        total_w += w
                        
                    if total_w > 0:
                        return (t_score / total_w) * 100
                    return 0"""

content = calc_score_pattern.sub(new_calc_score, content)

# 3. Chèn bảng Chấm điểm Mức 1-2-3 cho Quản lý vào kpi_tab1
df_pattern = re.compile(r"(st\.dataframe\(\s*kpi_month_df\[\[.*?hide_index=True\s*\))", re.DOTALL)

editor_code = """\\1
                
                if is_manager_view and not kpi_df.empty:
                    st.markdown("### ✍️ Bảng Chấm Điểm KPI (Quản lý chấm Mức Đạt)")
                    st.info("💡 Chọn Mức đạt cho từng công việc: Mức 4 (125%), Mức 3 (100%), Mức 2 (75%), Mức 1 (50%), Mức 0 (0%), Mức Âm (Phạt).")
                    
                    edit_df = kpi_df[['ID', 'TenCongViec', 'NguoiChuTri', 'TyTrongKPI', 'MucDoGhiNhan']].copy()
                    
                    # Chuẩn hóa cột MucDoGhiNhan
                    valid_levels = ["Mức 4 (125%)", "Mức 3 (100%)", "Mức 2 (75%)", "Mức 1 (50%)", "Mức 0 (0%)", "Mức -1 (-50%)", "Mức -2 (-75%)", "Mức -3 (-100%)"]
                    edit_df['MucDoGhiNhan'] = edit_df['MucDoGhiNhan'].apply(lambda x: x if x in valid_levels else "Mức 3 (100%)")
                    
                    edited_data = st.data_editor(
                        edit_df,
                        column_config={
                            "ID": st.column_config.TextColumn("Mã CV", disabled=True),
                            "TenCongViec": st.column_config.TextColumn("Tên công việc", disabled=True),
                            "NguoiChuTri": st.column_config.TextColumn("Người làm", disabled=True),
                            "TyTrongKPI": st.column_config.NumberColumn("Tỷ trọng (%)", disabled=True),
                            "MucDoGhiNhan": st.column_config.SelectboxColumn("Đánh giá (Mức đạt)", options=valid_levels, required=True)
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="kpi_eval_editor"
                    )
                    
                    if st.button("💾 Lưu Đánh Giá Mức Đạt", type="primary"):
                        with acquire_db_lock():
                            fresh_df = read_db()
                            for idx, row in edited_data.iterrows():
                                mask = fresh_df['ID'] == row['ID']
                                fresh_df.loc[mask, 'MucDoGhiNhan'] = row['MucDoGhiNhan']
                            if save_db(fresh_df):
                                st.success("✅ Đã lưu kết quả đánh giá thành công!")
                                st.rerun()"""

content = df_pattern.sub(editor_code, content)

# 4. Cập nhật Bảng xếp hạng cuối năm (Xếp loại Năm)
grade_pattern = re.compile(
    r"# Logic xếp loại năm mới.*?bonus = f\"\{bonus_val\}%\"",
    re.DOTALL
)

new_grade_logic = """# Logic xếp loại năm Cảng Đà Nẵng
                        evaluated = count_a_star + count_a + count_b + count_c + count_d
                        if evaluated == 0:
                            final_grade = "-"
                            bonus_val = 0
                        elif evaluated < 12 and selected_year_full >= today.year:
                            final_grade = "Đang tích lũy"
                            bonus_val = 0
                        else:
                            # Tính điểm trung bình cả năm để xếp loại Cảng Đà Nẵng
                            t_score = f_score # Lấy điểm tháng gần nhất hoặc trung bình
                            if f_score >= 90:
                                final_grade = "A"
                                bonus_val = 110
                            elif f_score >= 80:
                                final_grade = "B"
                                bonus_val = 105
                            elif f_score >= 70:
                                final_grade = "C"
                                bonus_val = 100
                            elif f_score >= 50:
                                final_grade = "D"
                                bonus_val = 95
                            else:
                                final_grade = "E"
                                bonus_val = 90
                            
                            bonus = f"{bonus_val}%\""""

content = grade_pattern.sub(new_grade_logic, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully!")
