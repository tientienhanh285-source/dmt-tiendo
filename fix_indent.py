import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_kpi_tab4 = False

for i, line in enumerate(lines):
    if "st.markdown(\"### Tùy chọn Xuất Báo Cáo & Phân tích\")" in line:
        new_lines.append(line)
        in_kpi_tab4 = True
        continue
        
    if in_kpi_tab4 and "st.markdown(\"##### Lịch sử Thưởng / Phạt\")" in line:
        in_kpi_tab4 = False
        new_lines.append("        with kpi_tab3:\n")
        new_lines.append("            st.divider()\n")
        new_lines.append(line)
        continue

    if in_kpi_tab4:
        # Add 4 spaces of indentation
        if line.strip() == "":
            new_lines.append(line)
        else:
            # wait, what if it's the divider?
            if "st.divider()" in line and "Để xem Biểu đồ Phân tích" in lines[i+1]:
                new_lines.append("                st.divider()\n")
            elif "Để xem Biểu đồ Phân tích" in line and "st.divider()" in lines[i-1]:
                new_lines.append("                st.info(\"Để xem Biểu đồ Phân tích, vui lòng qua tab 'Tổng kết KPI Cả Năm' và bấm 'Chạy / Cập nhật' trước.\")\n")
            else:
                new_lines.append("    " + line)
    else:
        # if we are not in kpi_tab4, check if these are the original unindented divider/info, and skip them since they were handled inside tab4 or removed
        if "st.divider()" in line and i+1 < len(lines) and "Để xem Biểu đồ Phân tích" in lines[i+1]:
            pass
        elif "Để xem Biểu đồ Phân tích" in line and i-1 >= 0 and "st.divider()" in lines[i-1]:
            pass
        else:
            new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
