import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

t = """                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        yearly_df.to_excel(writer, index=False, sheet_name="KPI_TongKet")
                    st.download_button("📥 Xuất Báo cáo Excel", data=output.getvalue(), file_name=f"TongKet_KPI_{selected_year_full}.xlsx")"""

r = """                    excel_data = kpi_reports.generate_yearly_excel(yearly_df, selected_year_full)
                    st.download_button("📥 Xuất Báo cáo Excel", data=excel_data, file_name=f"TongKet_KPI_{selected_year_full}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")"""

if t in content:
    content = content.replace(t, r)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched app.py OK")
else:
    print("Failed to patch app.py")
