import os

app_file = 'app.py'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_ui = '''            st.markdown("##### Lịch sử Thưởng / Phạt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                st.dataframe(hist_df.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)'''

new_ui = '''            st.markdown("##### Lịch sử Thưởng / Phạt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                def _get_pb(name):
                    for d, p_list in config.get("personnel_by_department", {}).items():
                        if name in p_list: return d
                    return "Khác"
                hist_df["Phòng ban"] = hist_df["TenNhanVien"].apply(_get_pb)
                
                # Reorder columns to put Phòng ban next to TenNhanVien
                cols = list(hist_df.columns)
                if "Phòng ban" in cols:
                    cols.insert(cols.index("TenNhanVien") + 1, cols.pop(cols.index("Phòng ban")))
                    hist_df = hist_df[cols]
                
                # Lọc (Filter)
                col_flt1, col_flt2 = st.columns(2)
                with col_flt1:
                    f_pb = st.selectbox("Lọc Phòng Ban", ["Tất cả"] + sorted(list(set(hist_df["Phòng ban"]))), key="flt_adj_pb")
                with col_flt2:
                    f_thang = st.selectbox("Lọc Tháng", ["Tất cả"] + sorted(list(set(hist_df["Thang"])), reverse=True), key="flt_adj_thang")
                
                display_df = hist_df.copy()
                if f_pb != "Tất cả":
                    display_df = display_df[display_df["Phòng ban"] == f_pb]
                if f_thang != "Tất cả":
                    display_df = display_df[display_df["Thang"] == f_thang]
                
                st.dataframe(display_df.sort_values(by=["Phòng ban", "Thang", "ID"], ascending=[True, False, False]), use_container_width=True, hide_index=True)'''

if old_ui in content:
    content = content.replace(old_ui, new_ui)
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("old_ui not found")
