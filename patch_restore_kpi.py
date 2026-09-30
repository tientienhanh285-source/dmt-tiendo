import sys
import re

file_path = "app.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Restore task weight
weight_target = """            task_weight = st.number_input("Tỷ trọng KPI cho công việc này (%)", value=0)
            st.caption("💡 Mẹo: Quản lý tự chia tỷ trọng cho các việc trong tháng (Tổng có thể là 100%).")"""

weight_replace = """            if is_local:
                task_weight = st.number_input("Tỷ trọng KPI cho công việc này (%)", value=0)
                st.caption("💡 Mẹo: Quản lý tự chia tỷ trọng cho các việc trong tháng (Tổng có thể là 100%).")
            else:
                # --- 🚀 TÍNH NĂNG MỚI: TỪ ĐIỂN HỆ SỐ A-B-C ---
                abc_options = {
                    "Loại A (Đặc biệt quan trọng - Hệ số 2.0)": 2.0,
                    "Loại B (Quan trọng - Hệ số 1.5)": 1.5,
                    "Loại C (Bình thường - Hệ số 1.0)": 1.0
                }
                selected_abc = st.selectbox("Phân loại tính chất công việc (A,B,C)", list(abc_options.keys()), index=2)
                task_weight = abc_options[selected_abc]"""

content = content.replace(weight_target, weight_replace)

# 2. Restore calc_score_for_group
calc_target = """def calc_score_for_group(grp):
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

calc_replace = """def calc_score_for_group(grp):
                    if grp.empty: return 0
                    t_score = 0
                    total_w = 0
                    for idx, row in grp.iterrows():
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        
                        if is_local:
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
                                is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                                p = 100 if is_comp else 0
                        else:
                            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                            p = 100 if is_comp else 0

                        t_score += (p / 100.0) * w
                        total_w += w
                        
                    if total_w > 0:
                        return (t_score / total_w) * 100
                    return 0"""
                    
content = content.replace(calc_target, calc_replace)

# 3. Hide data editor
editor_target = "if is_manager_view and not kpi_df.empty:"
editor_replace = "if is_manager_view and not kpi_df.empty and is_local:"
content = content.replace(editor_target, editor_replace)

# 4. Restore final grade logic
grade_target = """# Logic xếp loại năm Cảng Đà Nẵng
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

grade_replace = """if is_local:
                            # Logic xếp loại năm Cảng Đà Nẵng
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
                                
                                bonus = f"{bonus_val}%"
                        else:
                            # Logic xếp loại năm cũ
                            if count_a_star >= 8 and count_b == 0 and count_c == 0 and count_d == 0:
                                final_grade = "A+"
                                bonus_val = 120
                            elif (count_a_star + count_a) >= 8 and count_c == 0 and count_d == 0:
                                final_grade = "A"
                                bonus_val = 110
                            elif (count_a_star + count_a + count_b) >= 8 and count_d == 0:
                                final_grade = "B"
                                bonus_val = 105
                            elif (count_a_star + count_a + count_b + count_c) >= 8 and count_d <= 2:
                                final_grade = "C"
                                bonus_val = 100
                            else:
                                final_grade = "D"
                                bonus_val = 90
                            
                            evaluated = count_a_star + count_a + count_b + count_c + count_d
                            if evaluated == 0:
                                final_grade = "-"
                                bonus = "-"
                            elif evaluated < 12 and selected_year_full >= today.year:
                                final_grade = "Đang tích lũy"
                                bonus = "-"
                            else:
                                bonus = f"{bonus_val}%\""""
                                
content = content.replace(grade_target, grade_replace)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Restored original KPI logic for production!")
