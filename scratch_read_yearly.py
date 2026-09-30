with open(r"views\5_Danh_Gia_KPI.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if "with kpi_tab2:" in line:
        start = i
    if "with kpi_tab3:" in line and start != -1:
        end = i
        break

with open("scratch_yearly.txt", "w", encoding="utf-8") as f:
    f.write("".join(lines[start:end]))
