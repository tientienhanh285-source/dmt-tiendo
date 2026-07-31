import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
import os
from datetime import datetime

def render_analytics_dashboard(yearly_data_df):
    st.markdown("### 📈 Phân tích Xu hướng & Thống kê KPI")
    if yearly_data_df.empty:
        st.warning("Chưa có dữ liệu tổng kết năm để vẽ biểu đồ. Vui lòng sang tab 'Tổng kết KPI Cả Năm' và chạy báo cáo trước.")
        return
    
    st.markdown("#### 1. Biểu đồ Tổng kết Phân bổ Xếp Loại (Toàn công ty)")
    # Group by grade
    grade_cols = ['Loại A', 'Loại B', 'Loại C', 'Loại D']
    grade_counts = yearly_data_df[grade_cols].sum().reset_index()
    grade_counts.columns = ['Xếp loại', 'Số lượng']
    
    fig1 = px.pie(grade_counts, names='Xếp loại', values='Số lượng', title="Tỷ lệ Xếp loại các tháng trong Năm", color='Xếp loại', 
                 color_discrete_map={'Loại A':'#2ca02c', 'Loại B':'#1f77b4', 'Loại C':'#ff7f0e', 'Loại D':'#d62728'})
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### 2. Biểu đồ So sánh Điểm Trung bình giữa các Nhân viên")
    # We don't have exact numerical scores in yearly_data_df (only grades). 
    # Let's approximate score: A=95, B=85, C=75, D=60
    def approx_score(row):
        total = row['Loại A']*95 + row['Loại B']*85 + row['Loại C']*75 + row['Loại D']*60
        count = row['Loại A'] + row['Loại B'] + row['Loại C'] + row['Loại D']
        return total / count if count > 0 else 0
    
    yearly_data_df['Điểm TB (Ước tính)'] = yearly_data_df.apply(approx_score, axis=1)
    
    fig2 = px.bar(yearly_data_df, x='Nhân viên', y='Điểm TB (Ước tính)', color='Xếp loại Cả Năm',
                 title="Điểm KPI Trung bình (Ước tính) theo Nhân viên",
                 color_discrete_map={'A (100%)':'#2ca02c', 'B (80%)':'#1f77b4', 'C (60%)':'#ff7f0e'})
    st.plotly_chart(fig2, use_container_width=True)

def generate_department_excel(company_name, month, year, data_rows):
    # data_rows is a list of dicts: STT, HoTen, ChucVu, SoLanTre, SoLanSom, SoLanKhongCC, DiemTruTre, DiemTruSom, DiemTruKhongCC, TongTru, DiemConLai, XepLoai, GhiChu
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{month:02d}.{year}"
    
    # Headers
    ws.merge_cells('A1:D1')
    ws['A1'] = company_name
    ws['A1'].font = Font(bold=True)
    
    ws.merge_cells('A2:M2')
    ws['A2'] = f"BẢNG CHẤM ĐIỂM TÍNH LƯƠNG CBNV THÁNG {month:02d}/{year}"
    ws['A2'].font = Font(bold=True, size=14)
    ws['A2'].alignment = Alignment(horizontal='center')
    
    headers_row1 = ['STT', 'Họ và tên', 'Chức vụ', 'Số lần', '', '', 'Điểm trừ đi trễ', 'Điểm trừ về sớm', 'Điểm trừ không chấm công', 'Tổng điểm trừ', 'Tổng điểm còn lại', 'Xếp loại', 'Ghi chú']
    headers_row2 = ['', '', '', 'Đi trễ', 'Về Sớm', 'Không chấm công', '', '', '', '', '', '', '']
    
    ws.append(headers_row1)
    ws.append(headers_row2)
    
    # Merging headers
    ws.merge_cells('A4:A5')
    ws.merge_cells('B4:B5')
    ws.merge_cells('C4:C5')
    ws.merge_cells('D4:F4')
    ws.merge_cells('G4:G5')
    ws.merge_cells('H4:H5')
    ws.merge_cells('I4:I5')
    ws.merge_cells('J4:J5')
    ws.merge_cells('K4:K5')
    ws.merge_cells('L4:L5')
    ws.merge_cells('M4:M5')
    
    thin = Side(border_style="thin", color="000000")
    border = Border(top=thin, left=thin, right=thin, bottom=thin)
    
    for row in ws['A4:M5']:
        for cell in row:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
            cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
            
    # Data
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
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
    # Column widths
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 15
    for col in ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']:
        ws.column_dimensions[col].width = 12

    out = BytesIO()
    wb.save(out)
    return out.getvalue()

def generate_individual_docx(employee_name, month, year, kpi_score, list_tasks, penalties):
    doc = Document()
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"PHIẾU ĐÁNH GIÁ KPI CÁ NHÂN\nTháng {month}/{year}")
    r.bold = True
    r.font.size = Pt(16)
    
    # Info
    doc.add_paragraph(f"Họ và tên: {employee_name}")
    doc.add_paragraph(f"Thời gian đánh giá: Tháng {month} năm {year}")
    
    # Tiêu chí 1
    doc.add_heading("TIÊU CHÍ 1: KẾT QUẢ CÔNG VIỆC (Tổng: 100 điểm)", level=2)
    t1 = doc.add_table(rows=1, cols=4)
    t1.style = 'Table Grid'
    hdr_cells = t1.rows[0].cells
    hdr_cells[0].text = 'STT'
    hdr_cells[1].text = 'Mục tiêu/Công việc'
    hdr_cells[2].text = 'Tỷ trọng (%)'
    hdr_cells[3].text = 'Điểm Đạt'
    
    for i, task in enumerate(list_tasks, 1):
        row_cells = t1.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = task.get('TenCV', '')
        row_cells[2].text = str(task.get('TyTrong', ''))
        row_cells[3].text = str(task.get('Diem', ''))
        
    doc.add_paragraph(f"Tổng điểm Tiêu chí 1: {kpi_score} điểm").bold = True
    
    # Tiêu chí 2
    doc.add_heading("TIÊU CHÍ 2: KỶ LUẬT LÀO ĐỘNG (Thưởng / Phạt)", level=2)
    if not penalties:
        doc.add_paragraph("Không có vi phạm hoặc thưởng điểm trong tháng.")
        total_adj = 0
    else:
        t2 = doc.add_table(rows=1, cols=3)
        t2.style = 'Table Grid'
        hdr2 = t2.rows[0].cells
        hdr2[0].text = 'Phân loại'
        hdr2[1].text = 'Lý do chi tiết'
        hdr2[2].text = 'Điểm'
        
        total_adj = 0
        for adj in penalties:
            row_cells = t2.add_row().cells
            row_cells[0].text = adj.get('LoaiHanhVi', '')
            row_cells[1].text = adj.get('LyDo', '')
            row_cells[2].text = str(adj.get('DiemDieuChinh', ''))
            try: total_adj += float(adj.get('DiemDieuChinh', 0))
            except: pass
            
    doc.add_paragraph(f"Tổng điểm Tiêu chí 2 (Thưởng/Phạt): {total_adj} điểm").bold = True
    
    # Kết luận
    final_score = kpi_score + total_adj
    if final_score > 91: grade = "A"
    elif final_score > 81: grade = "B"
    elif final_score > 71: grade = "C"
    else: grade = "D"
    
    doc.add_heading("KẾT LUẬN", level=2)
    doc.add_paragraph(f"Tổng điểm KPI cuối cùng: {final_score} điểm")
    doc.add_paragraph(f"Xếp loại: {grade}")
    
    # Signatures
    doc.add_paragraph("\n")
    p_sig = doc.add_paragraph()
    p_sig.add_run("TRƯỞNG BỘ PHẬN").bold = True
    p_sig.add_run("\t\t\t\t\t\t\t").bold = False
    p_sig.add_run("NGƯỜI LAO ĐỘNG").bold = True
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    out = BytesIO()
    doc.save(out)
    return out.getvalue()
