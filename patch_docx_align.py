import sys

with open('kpi_reports.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("def generate_individual_docx"):
        start_idx = i
        break

if start_idx != -1:
    end_idx = start_idx + 1
    while end_idx < len(lines) and (lines[end_idx].startswith(" ") or lines[end_idx].startswith("\t") or lines[end_idx].strip() == ""):
        end_idx += 1
        
    new_func = """def set_cell_center(cell):
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell.vertical_alignment = 1 # Center

def generate_individual_docx(employee_name, month, year, kpi_score, list_tasks, penalties):
    doc = Document()
    
    # Adjust margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        
    # --- Style definitions ---
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    
    # --- Title ---
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BẢNG ĐÁNH GIÁ CÔNG VIỆC CỦA CBNV\\n")
    r.bold = True
    r.font.size = Pt(14)
    r2 = p.add_run(f"THÁNG {month:02d}/{year}")
    r2.bold = True
    r2.font.size = Pt(14)
    
    # --- Info ---
    doc.add_paragraph(f"Họ và tên: {employee_name}       - Chức danh: .....................      - Ban: .....................")
    
    # Calculate score
    total_penalty_c1 = sum(float(adj.get('DiemDieuChinh', 0)) for adj in penalties if 'chuyên cần' in adj.get('LoaiHanhVi', '').lower() or 'trễ' in adj.get('LoaiHanhVi', '').lower() or 'sớm' in adj.get('LoaiHanhVi', '').lower() or 'công' in adj.get('LoaiHanhVi', '').lower())
    total_penalty_c2 = sum(float(t.get('DiemTru', 0)) for t in list_tasks)
    total_penalty_other = sum(float(adj.get('DiemDieuChinh', 0)) for adj in penalties) - total_penalty_c1
    
    total_penalty_all = abs(total_penalty_c1) + abs(total_penalty_c2) + abs(total_penalty_other)
    final_score = 100 - total_penalty_all
    
    doc.add_paragraph(f"Số điểm trừ cả 2 tiêu chí : {round(total_penalty_all, 1)}            Số điểm hoàn thành cả 2 tiêu chí: {round(final_score, 1)}")
    
    # --- Signatures (using invisible table for perfect alignment) ---
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.autofit = True
    
    c00 = sig_table.cell(0, 0)
    c00.text = "NHÂN VIÊN:__________________"
    c00.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c01 = sig_table.cell(0, 1)
    c01.text = "GIÁM ĐỐC BAN:_________________"
    c01.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c10 = sig_table.cell(1, 0)
    c10.text = "Kiểm tra từ Ban HCNS: ____________"
    c10.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c11 = sig_table.cell(1, 1)
    c11.text = f"Tổng điểm để tính lương: {round(final_score, 1)} % lương"
    c11.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c20 = sig_table.cell(2, 0)
    c20.text = "Phê duyệt của Tổng giám đốc:_______"
    c20.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c21 = sig_table.cell(2, 1)
    c21.text = "Phó Tổng giám đốc phụ trách: _________"
    c21.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    p_note = doc.add_paragraph()
    p_note.add_run("*Cơ sở đánh giá kết quả tính lương và xếp loại lao động hàng tháng:\\n").bold = True
    p_note.add_run("Mức 1:Từ >91 – 100 điểm : 100% lương, xếp loại A trong tháng.\\n")
    p_note.add_run("Mức 2:Từ >81 – 91 điểm : 90% lương, xếp loại B trong tháng.\\n")
    p_note.add_run("Mức 3:Từ >71 – 81 điểm : 80% lương, xếp loại C trong tháng.\\n")
    p_note.add_run("Mức 4: Dưới 71 điểm : 60% lương, xem xét kỷ luật.")
    
    # --- TABLE 1 ---
    t1 = doc.add_table(rows=2, cols=5)
    t1.style = 'Table Grid'
    t1.autofit = False
    for row in t1.rows:
        row.cells[0].width = Inches(0.5)
        row.cells[1].width = Inches(3.5)
        row.cells[2].width = Inches(1.2)
        row.cells[3].width = Inches(1.2)
        row.cells[4].width = Inches(1.2)
    
    cell_0_0 = t1.cell(0, 0)
    cell_0_0.merge(t1.cell(1, 0))
    cell_0_0.text = "TT"
    set_cell_center(cell_0_0)
    
    cell_0_1 = t1.cell(0, 1)
    cell_0_1.merge(t1.cell(1, 1))
    cell_0_1.text = "Tiêu chí 1: Đánh giá việc thực hiện thời gian làm việc"
    set_cell_center(cell_0_1)
    
    cell_0_2 = t1.cell(0, 2)
    cell_0_2.merge(t1.cell(0, 4))
    cell_0_2.text = "Chi tiết từ máy Chấm công"
    set_cell_center(cell_0_2)
    
    t1.cell(1, 2).text = "Đi trễ về sớm (lần)"
    set_cell_center(t1.cell(1, 2))
    t1.cell(1, 3).text = "Quên bấm (lần)"
    set_cell_center(t1.cell(1, 3))
    t1.cell(1, 4).text = "Tổng điểm trừ đtc1"
    set_cell_center(t1.cell(1, 4))
    
    row_cells = t1.add_row().cells
    row_cells[0].text = "1"
    set_cell_center(row_cells[0])
    row_cells[1].text = "Tổng số điểm bị trừ (đtc1) tối đa không quá 15 điểm."
    
    # Count penalties for C1
    tre_som = 0
    quen_bam = 0
    for p in penalties:
        lv = p.get('LoaiHanhVi', '').lower()
        if 'trễ' in lv or 'sớm' in lv: tre_som += 1
        if 'công' in lv: quen_bam += 1
    
    row_cells[2].text = str(tre_som)
    set_cell_center(row_cells[2])
    row_cells[3].text = str(quen_bam)
    set_cell_center(row_cells[3])
    row_cells[4].text = str(abs(total_penalty_c1))
    set_cell_center(row_cells[4])
    
    doc.add_paragraph()
    
    # --- TABLE 2 ---
    t2 = doc.add_table(rows=2, cols=5)
    t2.style = 'Table Grid'
    t2.autofit = False
    for row in t2.rows:
        row.cells[0].width = Inches(0.5)
        row.cells[1].width = Inches(3.5)
        row.cells[2].width = Inches(1.2)
        row.cells[3].width = Inches(1.2)
        row.cells[4].width = Inches(1.2)
    
    cell2_0_0 = t2.cell(0, 0)
    cell2_0_0.merge(t2.cell(1, 0))
    cell2_0_0.text = "TT"
    set_cell_center(cell2_0_0)
    
    cell2_0_1 = t2.cell(0, 1)
    cell2_0_1.merge(t2.cell(1, 1))
    cell2_0_1.text = "Tiêu chí 2: Đánh giá mức độ hoàn thành công việc"
    set_cell_center(cell2_0_1)
    
    cell2_0_2 = t2.cell(0, 2)
    cell2_0_2.merge(t2.cell(0, 4))
    cell2_0_2.text = "Điểm trừ nhiệm vụ ko hoàn thành"
    set_cell_center(cell2_0_2)
    
    t2.cell(1, 2).text = "Tgian y/c hoàn thành"
    set_cell_center(t2.cell(1, 2))
    t2.cell(1, 3).text = "Kết quả"
    set_cell_center(t2.cell(1, 3))
    t2.cell(1, 4).text = "Tổng điểm trừ đtc2"
    set_cell_center(t2.cell(1, 4))
    
    for i, t in enumerate(list_tasks, 1):
        r_cells = t2.add_row().cells
        r_cells[0].text = str(i)
        set_cell_center(r_cells[0])
        r_cells[1].text = t.get('TenCV', '')
        r_cells[2].text = str(t.get('TgianYC', ''))
        set_cell_center(r_cells[2])
        r_cells[3].text = str(t.get('KetQua', ''))
        set_cell_center(r_cells[3])
        r_cells[4].text = str(t.get('DiemTru', '0'))
        set_cell_center(r_cells[4])
        
    for i in range(3):
        r_cells = t2.add_row().cells
    
    last_row = t2.add_row().cells
    last_row[0].merge(last_row[2])
    last_row[0].text = "Tổng điểm"
    set_cell_center(last_row[0])
    last_row[3].text = "100"
    set_cell_center(last_row[3])
    last_row[4].text = str(abs(total_penalty_c2))
    set_cell_center(last_row[4])
    
    out = BytesIO()
    doc.save(out)
    return out.getvalue()
"""
    new_content = "".join(lines[:start_idx]) + new_func + "".join(lines[end_idx:])
    with open('kpi_reports.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Patched docx alignment")
else:
    print("Function not found")
