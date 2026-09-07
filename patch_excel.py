import sys
with open('kpi_reports.py', 'r', encoding='utf-8') as f:
    content = f.read()

t1 = """    for row in ws['A4:M5']:
        for cell in row:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")"""

r1 = """    # Áp dụng font Times New Roman, size 13 cho toàn bộ worksheet
    font_default = Font(name='Times New Roman', size=13)
    font_bold = Font(name='Times New Roman', size=13, bold=True)
    
    ws['A1'].font = Font(name='Times New Roman', size=14, bold=True)
    ws['A2'].font = Font(name='Times New Roman', size=16, bold=True)
    
    for row in ws['A4:M5']:
        for cell in row:
            cell.font = font_bold
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            cell.fill = PatternFill(start_color="C6E0B4", end_color="C6E0B4", fill_type="solid") # Light green"""

t2 = """    # Data
    for i, row in enumerate(data_rows, 1):
        r = [
            i, row.get('HoTen', ''), row.get('ChucVu', ''),
            row.get('SoLanTre', ''), row.get('SoLanSom', ''), row.get('SoLanKhongCC', ''),
            row.get('DiemTruTre', ''), row.get('DiemTruSom', ''), row.get('DiemTruKhongCC', ''),
            row.get('TongTru', ''), row.get('DiemConLai', ''), row.get('XepLoai', ''), row.get('GhiChu', '')
        ]
        ws.append(r)
        for cell in ws[ws.max_row]:
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')"""

r2 = """    # Data
    for i, row in enumerate(data_rows, 1):
        r = [
            i, row.get('HoTen', ''), row.get('ChucVu', ''),
            row.get('SoLanTre', ''), row.get('SoLanSom', ''), row.get('SoLanKhongCC', ''),
            row.get('DiemTruTre', ''), row.get('DiemTruSom', ''), row.get('DiemTruKhongCC', ''),
            row.get('TongTru', ''), row.get('DiemConLai', ''), row.get('XepLoai', ''), row.get('GhiChu', '')
        ]
        ws.append(r)
        for cell in ws[ws.max_row]:
            cell.font = font_default
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')"""

if t1 in content and t2 in content:
    content = content.replace(t1, r1).replace(t2, r2)
    with open('kpi_reports.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched Excel OK')
else:
    print('Failed to patch Excel')
