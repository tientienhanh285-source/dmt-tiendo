import os

file_path = r"views\5_Danh_Gia_KPI.py"
with open(file_path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Add score accumulators before the quarter loop
old_init = """                    count_c = 0
                    count_d = 0
                
                    for q in range(1, 5):"""
new_init = """                    count_c = 0
                    count_d = 0
                    total_year_score = 0
                    evaluated_quarters = 0
                
                    for q in range(1, 5):"""
c = c.replace(old_init, new_init)

# 2. Accumulate f_score
old_fscore = """                        f_score = min(115, max(0, round(t_score + (q_adj_df['DiemDieuChinh'].sum() if not q_adj_df.empty else 0), 2)))
                    
                        if f_score > 100:"""
new_fscore = """                        f_score = min(115, max(0, round(t_score + (q_adj_df['DiemDieuChinh'].sum() if not q_adj_df.empty else 0), 2)))
                        total_year_score += f_score
                        evaluated_quarters += 1
                    
                        if f_score > 100:"""
c = c.replace(old_fscore, new_fscore)

# 3. Add to row_data
old_row = """                    actual_bonus = f"{int(bonus_val * k_factor)}%" if bonus != "-" else "-"
                        
                    row_data = {
                        "Người thực hiện": person,
                        "Phòng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else ""
                    }"""
new_row = """                    actual_bonus = f"{int(bonus_val * k_factor)}%" if bonus != "-" else "-"
                    
                    avg_score = total_year_score / evaluated_quarters if evaluated_quarters > 0 else 0
                        
                    row_data = {
                        "Người thực hiện": person,
                        "Phòng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else "",
                        "Điểm TB Năm": round(avg_score, 1)
                    }"""
c = c.replace(old_row, new_row)

# 4. Add the A* list expander under the dataframe
old_df_render = """                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Không có dữ liệu.")"""
new_df_render = """                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    with st.expander("🌟 Danh sách Đề xuất Hạng A* (Lao động Xuất sắc)", expanded=True):
                        st.info("Danh sách các cá nhân có tổng điểm trung bình KPI từ tháng 1 đến tháng 12 đạt trên 100 điểm.")
                        if "Điểm TB Năm" in yearly_df.columns:
                            astar_df = yearly_df[pd.to_numeric(yearly_df["Điểm TB Năm"], errors="coerce") > 100].copy()
                            if not astar_df.empty:
                                st.dataframe(astar_df, use_container_width=True, hide_index=True)
                            else:
                                st.warning("Năm nay chưa có nhân sự nào đạt hạng A* (> 100 điểm).")
                else:
                    st.info("Không có dữ liệu.")"""
c = c.replace(old_df_render, new_df_render)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(c)

print("Added Yearly Avg Score and A* list successfully!")
