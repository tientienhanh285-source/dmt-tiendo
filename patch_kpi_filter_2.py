import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

t2 = """            if personnel_kpi:
                kpi_month_df = pd.DataFrame(personnel_kpi)
                st.dataframe("""

r2 = """            if personnel_kpi:
                kpi_month_df = pd.DataFrame(personnel_kpi)
                if selected_dept_m != "Tất cả phòng ban":
                    kpi_month_df = kpi_month_df[kpi_month_df["Phòng ban"] == selected_dept_m]
                st.dataframe("""

t3 = """        selected_year_full = st.selectbox("Chọn Năm Tổng Kết", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
        
        if st.button("🔄 Chạy / Cập nhật Báo cáo Tổng kết Năm", type="primary"):"""

r3 = """        col_y1, col_y2 = st.columns(2)
        with col_y1:
            selected_year_full = st.selectbox("Chọn Năm Tổng Kết", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
        with col_y2:
            allowed_depts_y = get_departments_for_company(selected_company, OFFICIAL_DEPARTMENTS)
            dept_options_y = ["Tất cả phòng ban"] + allowed_depts_y
            selected_dept_y = st.selectbox("Lọc theo Phòng ban", dept_options_y, key="kpi_y_dept")
        
        if st.button("🔄 Chạy / Cập nhật Báo cáo Tổng kết Năm", type="primary"):"""

c = 0
for t, r in [(t2, r2), (t3, r3)]:
    if t in content:
        content = content.replace(t, r)
        c += 1
    else:
        print("Missing:", t[:30])

if c > 0:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Replaced {c}")
