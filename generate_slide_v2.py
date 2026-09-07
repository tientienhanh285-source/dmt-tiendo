import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_mockup_charts():
    # Set style
    sns.set_theme(style="whitegrid")
    
    # Chart 1: KPI Dashboard
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    depts = ["BLĐ", "HCNS", "Kế toán", "Kỹ thuật", "Dự án"]
    scores = [105, 98, 92, 85, 110]
    sns.barplot(x=depts, y=scores, ax=ax, palette="Blues_d")
    ax.axhline(100, color="red", linestyle="--", label="Mục tiêu (100đ)")
    ax.set_title("Dashboard: Biểu đồ Năng suất (Real-time)", fontsize=14, fontweight='bold', color='#003399')
    ax.set_ylabel("Điểm KPI")
    ax.legend()
    plt.tight_layout()
    plt.savefig("chart_dashboard.png", bbox_inches='tight', transparent=True)
    plt.close()
    
    # Chart 2: AI JD Matching
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    labels = ['Khớp chuyên môn (JD)', 'Công việc ngoài JD']
    sizes = [85, 15]
    colors = ['#22c55e', '#f97316']
    explode = (0, 0.1)
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
    ax.axis('equal')
    ax.set_title("AI Phân tích: Độ phủ JD", fontsize=14, fontweight='bold', color='#003399')
    plt.tight_layout()
    plt.savefig("chart_ai.png", bbox_inches='tight', transparent=True)
    plt.close()

def create_presentation():
    prs = Presentation()
    
    # Define colors
    DMT_BLUE = RGBColor(0, 51, 153)
    DMT_GOLD = RGBColor(255, 192, 0)
    DARK_GRAY = RGBColor(64, 64, 64)
    WHITE = RGBColor(255, 255, 255)
    
    # Helper to add a colored header banner
    def add_header_banner(slide, title_text):
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = DMT_BLUE
        banner.line.color.rgb = DMT_BLUE
        
        # Add logo text in top left
        txBox = slide.shapes.add_textbox(Inches(0.2), Inches(0.2), Inches(2), Inches(0.5))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = "DMT GROUP"
        p.font.bold = True
        p.font.color.rgb = DMT_GOLD
        p.font.size = Pt(20)
        
        # Add Title in center
        title_box = slide.shapes.add_textbox(Inches(2), Inches(0.2), Inches(7.8), Inches(0.5))
        tf_title = title_box.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text.upper()
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE
        p_title.font.size = Pt(24)
        p_title.alignment = PP_ALIGN.RIGHT

    # ---------------------------------------------------
    # Slide 1: Title Slide (Customized)
    # ---------------------------------------------------
    slide1 = prs.slides.add_slide(prs.slide_layouts[6]) # Blank layout
    
    # Background
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DMT_BLUE
    
    # Gold accent
    accent = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.5), Inches(10), Inches(0.5))
    accent.fill.solid()
    accent.fill.fore_color.rgb = DMT_GOLD
    accent.line.fill.background()
    
    # Logo
    txBox = slide1.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "DMT GROUP"
    p.font.bold = True
    p.font.color.rgb = DMT_GOLD
    p.font.size = Pt(40)
    p.alignment = PP_ALIGN.CENTER
    
    # Title
    txBox2 = slide1.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(2))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = "CHUYỂN ĐỔI SỐ TRONG QUẢN TRỊ NHÂN SỰ\n& ĐÁNH GIÁ KPI"
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.font.size = Pt(36)
    p2.alignment = PP_ALIGN.CENTER
    
    # Subtitle
    txBox3 = slide1.shapes.add_textbox(Inches(1), Inches(4.5), Inches(8), Inches(1.5))
    tf3 = txBox3.text_frame
    tf3.text = "Đơn vị trình bày: Ban Hành chính Nhân sự\nMục tiêu: Minh bạch hóa năng suất - Tối ưu hóa nguồn lực"
    for p in tf3.paragraphs:
        p.font.color.rgb = WHITE
        p.font.size = Pt(20)
        p.alignment = PP_ALIGN.CENTER

    # ---------------------------------------------------
    # Slide 2: Problem Statement
    # ---------------------------------------------------
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_header_banner(slide2, "Thực trạng & Những bất cập hiện tại")
    
    content_box = slide2.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    p = tf.add_paragraph()
    p.text = "Quy trình đánh giá hiện tại đang gặp các khó khăn:"
    p.font.bold = True
    p.font.size = Pt(24)
    p.font.color.rgb = DMT_BLUE
    
    points = [
        "❌ Chấm điểm cảm tính: Phụ thuộc nhiều vào trí nhớ và đánh giá chủ quan.",
        "❌ Giao việc chồng chéo: Khó kiểm soát việc nhân sự làm sai chuyên môn (ngoài JD).",
        "❌ Thiếu dữ liệu tổng quan: Ban Lãnh đạo không có cái nhìn tức thời (Real-time) về tỷ lệ hoàn thành công việc của từng phòng ban.",
        "❌ Mất nhiều thời gian: HCNS và Kế toán mất quá nhiều ngày để gom nhặt báo cáo, tính toán Excel dễ xảy ra sai sót."
    ]
    
    for pt in points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.size = Pt(20)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(14)

    # ---------------------------------------------------
    # Slide 3: Solution & Architecture
    # ---------------------------------------------------
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_header_banner(slide3, "Giải pháp - Hệ thống Quản trị KPI Mới")
    
    # Text on left
    content_box = slide3.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(4.5), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    p = tf.add_paragraph()
    p.text = "Thay đổi cách vận hành - Số hóa 100%"
    p.font.bold = True
    p.font.size = Pt(22)
    p.font.color.rgb = DMT_BLUE
    
    points = [
        "✅ Chấm điểm tự động: Điểm số tính toán tự động dựa trên Khối lượng, Tiến độ (Gantt Chart) và Trọng số.",
        "✅ Dashboard Trực quan: Lãnh đạo theo dõi biểu đồ năng suất của từng Công ty/Phòng ban mọi lúc, mọi nơi.",
        "✅ Minh bạch & Công bằng: Cơ chế ghi nhận Điểm thưởng/Phạt rõ ràng trên hệ thống."
    ]
    
    for pt in points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.size = Pt(18)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(10)
        
    # Image on right
    if os.path.exists("chart_dashboard.png"):
        slide3.shapes.add_picture("chart_dashboard.png", Inches(5.0), Inches(2.0), width=Inches(4.5))

    # ---------------------------------------------------
    # Slide 4: Live Demo - AI Focus
    # ---------------------------------------------------
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_header_banner(slide4, "Đột phá Công nghệ: Trí tuệ Nhân tạo (AI)")
    
    # Text on left
    content_box = slide4.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(5.0), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    p = tf.add_paragraph()
    p.text = "Tích hợp AI đối chiếu chuyên môn (JD)"
    p.font.bold = True
    p.font.size = Pt(22)
    p.font.color.rgb = DMT_BLUE
    
    points = [
        "1️⃣ Quét AI Hàng loạt (Magic Feature): Tự động đọc danh sách công việc của từng nhân sự.",
        "2️⃣ Đối chiếu thông minh: AI đóng vai Giám đốc Nhân sự để phân tích xem công việc đó có khớp với Mô tả công việc (JD) hay không.",
        "3️⃣ Nhận xét tự động: Đưa ra lời giải thích chi tiết tại sao công việc đó bị coi là 'Ngoài JD'."
    ]
    
    for pt in points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.size = Pt(18)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(10)
        
    # Image on right
    if os.path.exists("chart_ai.png"):
        slide4.shapes.add_picture("chart_ai.png", Inches(5.8), Inches(2.5), width=Inches(3.8))

    # ---------------------------------------------------
    # Slide 5: Rollout Plan
    # ---------------------------------------------------
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_header_banner(slide5, "Lộ trình Triển khai (Kế hoạch hành động)")
    
    # Create two rounded rectangle shapes for phases
    shape1 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(2), Inches(3.5), Inches(3))
    shape1.fill.solid()
    shape1.fill.fore_color.rgb = RGBColor(230, 240, 255)
    shape1.line.color.rgb = DMT_BLUE
    
    tf1 = shape1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "GIAI ĐOẠN 1: THỬ NGHIỆM"
    p1.font.bold = True
    p1.font.color.rgb = DMT_BLUE
    p1.font.size = Pt(18)
    p1.alignment = PP_ALIGN.CENTER
    
    p1_1 = tf1.add_paragraph()
    p1_1.text = "• Chạy song song tại 2 phòng ban: HCNS & Kế toán."
    p1_1.font.size = Pt(16)
    p1_1.font.color.rgb = DARK_GRAY
    
    p1_2 = tf1.add_paragraph()
    p1_2.text = "• Thu thập phản hồi và tinh chỉnh phần mềm."
    p1_2.font.size = Pt(16)
    p1_2.font.color.rgb = DARK_GRAY
    
    # Arrow
    arrow = slide5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.7), Inches(3.2), Inches(0.6), Inches(0.6))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = DMT_GOLD
    arrow.line.fill.background()
    
    # Phase 2
    shape2 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.5), Inches(2), Inches(3.5), Inches(3))
    shape2.fill.solid()
    shape2.fill.fore_color.rgb = DMT_BLUE
    shape2.line.color.rgb = DMT_BLUE
    
    tf2 = shape2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = "GIAI ĐOẠN 2: CHÍNH THỨC"
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.font.size = Pt(18)
    p2.alignment = PP_ALIGN.CENTER
    
    p2_1 = tf2.add_paragraph()
    p2_1.text = "• Đóng hoàn toàn quy trình báo cáo Excel cũ."
    p2_1.font.size = Pt(16)
    p2_1.font.color.rgb = WHITE
    
    p2_2 = tf2.add_paragraph()
    p2_2.text = "• Áp dụng cho 100% nhân sự toàn công ty."
    p2_2.font.size = Pt(16)
    p2_2.font.color.rgb = WHITE
    
    # Commitment
    commit_box = slide5.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(1))
    tfc = commit_box.text_frame
    pc = tfc.paragraphs[0]
    pc.text = "🎯 CAM KẾT: Tăng 40% hiệu suất quản lý báo cáo, giảm 100% sai sót do tính toán thủ công."
    pc.font.bold = True
    pc.font.color.rgb = RGBColor(200, 0, 0)
    pc.font.size = Pt(20)
    pc.alignment = PP_ALIGN.CENTER

    # Save presentation
    output_file = "Kế_Hoạch_Số_Hóa_KPI_V2_Premium.pptx"
    prs.save(output_file)
    print(f"Presentation saved as '{output_file}'")

if __name__ == "__main__":
    create_mockup_charts()
    create_presentation()
