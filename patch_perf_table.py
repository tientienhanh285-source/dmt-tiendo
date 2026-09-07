import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

t1 = """    st.markdown("*Hiệu suất trung bình (%) hoàn thành công việc theo từng Phòng ban & Chu kỳ:*")"""
r1 = """    st.markdown("*Hiệu suất trung bình (%) hoàn thành công việc theo từng Phòng ban:*")"""

t2 = """        # Calculate pivot table
        try:
            perf_pivot = perf_df.pivot_table(
                index="PhongBan",
                columns="ChuKyTheoDoi",
                values="PhanTramHoanThanh",
                aggfunc="mean"
            ).fillna(0).astype(int)
            
            # Ensure all cycles are present
            for col in ["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]:
                if col not in perf_pivot.columns:
                    perf_pivot[col] = 0
            
            perf_pivot = perf_pivot[["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]]
            perf_pivot = perf_pivot.reset_index()
            perf_pivot.columns = ["Phòng ban", "Chu kỳ Tuần (%)", "Chu kỳ Tháng (%)", "Chu kỳ Quý (%)", "Dự án / Tự do (%)"]
            
            st.dataframe(
                perf_pivot,
                column_config={
                    "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                    "Chu kỳ Tuần (%)": st.column_config.ProgressColumn("Chu kỳ Tuần", format="%d%%", min_value=0, max_value=100),
                    "Chu kỳ Tháng (%)": st.column_config.ProgressColumn("Chu kỳ Tháng", format="%d%%", min_value=0, max_value=100),
                    "Chu kỳ Quý (%)": st.column_config.ProgressColumn("Chu kỳ Quý", format="%d%%", min_value=0, max_value=100),
                    "Dự án / Tự do (%)": st.column_config.ProgressColumn("Dự án / Tự do", format="%d%%", min_value=0, max_value=100)
                },
                use_container_width=True,
                hide_index=True
            )
        except Exception as pe:"""

r2 = """        # Calculate summary table
        try:
            perf_summary = perf_df.groupby("PhongBan").agg(
                Tổng_Việc=("ID", "count"),
                Đã_Xong=("TrangThai", lambda x: (x == "Hoàn thành").sum()),
                Hiệu_Suất=("PhanTramHoanThanh", "mean")
            ).fillna(0)
            perf_summary["Hiệu_Suất"] = perf_summary["Hiệu_Suất"].astype(int)
            perf_summary = perf_summary.reset_index()
            perf_summary.columns = ["Phòng ban", "Tổng số việc", "Số việc đã xong", "Hiệu suất Trung bình (%)"]
            
            st.dataframe(
                perf_summary,
                column_config={
                    "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                    "Tổng số việc": st.column_config.NumberColumn("Tổng số việc", width="small"),
                    "Số việc đã xong": st.column_config.NumberColumn("Số việc đã xong", width="small"),
                    "Hiệu suất Trung bình (%)": st.column_config.ProgressColumn("Hiệu suất Trung bình", format="%d%%", min_value=0, max_value=100)
                },
                use_container_width=True,
                hide_index=True
            )
        except Exception as pe:"""

c = 0
for t, r in [(t1, r1), (t2, r2)]:
    if t in content:
        content = content.replace(t, r)
        c += 1
    else:
        print("Missing:", t[:30])

if c > 0:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Replaced {c}")
