with open(r"views\5_Danh_Gia_KPI.py", "r", encoding="utf-8") as f:
    content = f.read()

old_str = "    with kpi_tab3:"
new_str = """
is_hr = is_hr_view
is_manager = is_manager_view
if is_hr or is_manager:
    with kpi_tab3:"""

if old_str in content:
    content = content.replace(old_str, new_str, 1)
    with open(r"views\5_Danh_Gia_KPI.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed is_manager error")
else:
    print("Could not find kpi_tab3")
