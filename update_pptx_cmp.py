# -*- coding: utf-8 -*-
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def update_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    NAVY = RGBColor(10, 37, 64)
    ROYAL = RGBColor(0, 82, 204)
    GOLD = RGBColor(245, 158, 11)
    GREEN = RGBColor(16, 185, 129)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED_TEXT = RGBColor(100, 116, 139)
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(248, 250, 252)
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240)
    ALERT_RED = RGBColor(225, 29, 72)
    SOFT_BLUE = RGBColor(239, 246, 255)
    SOFT_RED = RGBColor(255, 241, 242)
    SOFT_GREEN = RGBColor(240, 253, 244)

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="DMT GROUP • BAN HÀNH CHÍNH NHÂN SỰ"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = 'Arial'
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ROYAL
        p_cat.space_after = Pt(2)
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = 'Arial'
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
        divider.fill.solid()
        divider.fill.fore_color.rgb = CARD_BORDER
        divider.line.fill.background()

    def add_footer(slide, current_slide, total_slides=14):
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.4))
        tf = footer_box.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"DMT Group — Hệ Thống Quản Lý Tiến Độ & Đánh Giá KPI  |  Trang {current_slide}/{total_slides}"
        p.font.name = 'Arial'
        p.font.size = Pt(9)
        p.font.color.rgb = MUTED_TEXT

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.2)
        else:
            card.line.fill.background()
        return card

    # ========================================================
    # SLIDE 1: COVER
    # ========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY)

    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), prs.slide_width, Inches(0.3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()

    logo_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.333), Inches(0.5))
    tf_logo = logo_box.text_frame
    p_logo = tf_logo.paragraphs[0]
    p_logo.text = "TỔNG CÔNG TY DMT GROUP — BAN HÀNH CHÍNH NHÂN SỰ"
    p_logo.font.name = 'Arial'
    p_logo.font.size = Pt(13)
    p_logo.font.bold = True
    p_logo.font.color.rgb = GOLD

    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(2.6))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    
    p_t = tf_t.paragraphs[0]
    p_t.text = "HƯỚNG DẪN SỬ DỤNG HỆ THỐNG\nQUẢN LÝ TIẾN ĐỘ & ĐÁNH GIÁ KPI"
    p_t.font.name = 'Arial'
    p_t.font.size = Pt(34)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    p_t.space_after = Pt(10)

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Dành Cho Các Anh Chị Trưởng Ban & Toàn Thể Cán Bộ Nhân Viên"
    p_sub.font.name = 'Arial'
    p_sub.font.size = Pt(19)
    p_sub.font.color.rgb = RGBColor(147, 197, 253)
    p_sub.space_after = Pt(8)

    p_motto = tf_t.add_paragraph()
    p_motto.text = "⚡ Tập trung thực hành   •   🎯 Nắm vững 5 nguyên tắc vận hành   •   🤝 An tâm trải nghiệm Quý 4"
    p_motto.font.name = 'Arial'
    p_motto.font.size = Pt(13.5)
    p_motto.font.italic = True
    p_motto.font.color.rgb = RGBColor(226, 232, 240)

    cover_card = add_card(s1, Inches(1.0), Inches(4.8), Inches(11.333), Inches(1.8), bg_color=RGBColor(17, 49, 84), border_color=ROYAL)
    tf_cc = cover_card.text_frame
    tf_cc.word_wrap = True
    p_c1 = tf_cc.paragraphs[0]
    p_c1.text = "MỤC TIÊU BUỔI HƯỚNG DẪN"
    p_c1.font.name = 'Arial'
    p_c1.font.bold = True
    p_c1.font.size = Pt(14)
    p_c1.font.color.rgb = GOLD
    p_c1.space_after = Pt(4)

    p_c2 = tf_cc.add_paragraph()
    p_c2.text = "• Không đi sâu lý thuyết suông -> Tập trung 100% vào thao tác thực tế và xử lý tình huống phát sinh.\n• Quý 4/2026: Giai đoạn chạy thử (Pilot) — Thoải mái làm quen tay, Ban HCNS hỗ trợ trực tiếp 24/7!"
    p_c2.font.name = 'Arial'
    p_c2.font.size = Pt(12)
    p_c2.font.color.rgb = WHITE

    # ========================================================
    # SLIDE 2: PHẦN 1 - MỤC TIÊU & QUÝ 4 (5 PHÚT)
    # ========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Phần 1: Khai Mạc & 3 Trọng Tâm Buổi Hướng Dẫn (5 Phút)")
    add_footer(s2, 2)

    c2_1 = add_card(s2, Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.8))
    tf2_1 = c2_1.text_frame
    tf2_1.word_wrap = True
    p = tf2_1.paragraphs[0]
    p.text = "🎯 3 NỘI DUNG TRỌNG TÂM HÔM NAY"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    items2_1 = [
        ("1. Hiểu đúng vai trò & trách nhiệm:", "Rõ ràng chức năng của Nhân viên (thực thi, cập nhật) và Quản lý (phân rã việc, nghiệm thu)."),
        ("2. Hướng dẫn thao tác trực tiếp:", "Cầm tay chỉ việc: Tạo việc, cập nhật tiến độ, duyệt việc và nghiệm thu Chỉ tiêu theo đúng quyền."),
        ("3. Thống nhất xử lý tình huống:", "Giải quyết nhanh các tình huống thực tế thường gặp khi chạy thử.")
    ]
    for h, b in items2_1:
        p_i = tf2_1.add_paragraph()
        p_i.text = f"{h}\n{b}"
        p_i.font.name = 'Arial'
        p_i.font.size = Pt(11)
        p_i.font.color.rgb = DARK_TEXT
        p_i.space_after = Pt(8)

    c2_2 = add_card(s2, Inches(7.1), Inches(1.8), Inches(5.4), Inches(4.8), bg_color=SOFT_BLUE, border_color=ROYAL)
    tf2_2 = c2_2.text_frame
    tf2_2.word_wrap = True
    p = tf2_2.paragraphs[0]
    p.text = "🌱 TINH THẦN QUÝ 4: CHẠY THỬ (PILOT)"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)

    points2_2 = [
        "• Hệ thống dùng chung: Đăng nhập chọn đúng Công ty -> Tên -> Vai trò, dữ liệu hiển thị gọn gàng, không rối mắt.",
        "• Mục tiêu chạy thử Quý 4:\n  - Trưởng ban làm quen kỹ năng chia nhỏ mục tiêu trên máy.\n  - Nhân viên tập thói quen cập nhật tiến độ liên tục.",
        "• An tâm dùng thử: Bỡ ngỡ hay bấm nhầm là bình thường, tuyệt đối không bị phạt hay trừ lương.",
        "• Đồng hành 24/7: Ban HCNS tiếp nhận phản hồi tức thì để hoàn thiện hệ thống tốt nhất cho mọi người!"
    ]
    for pt in points2_2:
        p_pt = tf2_2.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(11)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(8)

    # ========================================================
    # SLIDE 3: BẢNG SO SÁNH CÁCH LÀM CŨ VS NGUYÊN TẮC MỚI (MỚI BỔ SUNG)
    # ========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Phần 2: Đối Chiếu Nhanh — Cách Làm Cũ vs 5 Nguyên Tắc Mới (7 Phút)")
    add_footer(s3, 3)

    # Left card: Cách làm cũ (Red tone)
    card_old = add_card(s3, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=SOFT_RED, border_color=ALERT_RED)
    tf_old = card_old.text_frame
    tf_old.word_wrap = True
    p = tf_old.paragraphs[0]
    p.text = "❌ CÁCH LÀM CŨ (THỦ CÔNG / TRUYỀN THỐNG)"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = ALERT_RED
    p.space_after = Pt(10)

    points_old = [
        "1. Tự nghĩ việc rời rạc: Nhân viên tự liệt kê việc trên Word/Excel, không rõ phục vụ mục tiêu nào của phòng.",
        "2. Báo cáo một chiều: Coi báo cáo là làm nộp cho sếp; sếp giao việc miệng qua Zalo/email dễ thất lạc.",
        "3. 'Dồn toa' cuối tháng: Cả tháng không cập nhật, đến sát ngày mới cuống cuồng làm; vướng mắc để cuối kỳ mới vỡ lở.",
        "4. Duyệt miệng, thiếu minh chứng: Khai báo 'Đã xong' chung chung trên giấy tờ; duyệt theo cảm tính, tin tưởng miệng.",
        "5. Ngộ nhận cấp độ: Thấy xong hết việc cá nhân là tưởng phòng hoàn thành; tạo tỷ lệ ảo dù dự án chung bị trễ!"
    ]
    for pt in points_old:
        p_pt = tf_old.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(10)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(6)

    # Right card: Nguyên tắc mới (Green tone)
    card_new = add_card(s3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=SOFT_GREEN, border_color=GREEN)
    tf_new = card_new.text_frame
    tf_new.word_wrap = True
    p = tf_new.paragraphs[0]
    p.text = "✅ 5 NGUYÊN TẮC MỚI TRÊN PHẦN MỀM"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = GREEN
    p.space_after = Pt(10)

    points_new = [
        "1. Trục dọc liên kết: Dự án ➔ Chỉ tiêu Ban ➔ Việc cá nhân. Làm việc nào rõ đích đến mục tiêu đó.",
        "2. Trách nhiệm 2 chiều: Cả sếp và nhân viên đều làm việc; sếp phân rã chỉ tiêu và tự cập nhật việc của mình.",
        "3. Cập nhật Real-time: Cập nhật liên tục ngay khi làm; có nguy cơ trễ / vướng mắc báo sớm để sếp hỗ trợ.",
        "4. Minh chứng thực tế: Báo hoàn thành bắt buộc đính kèm File/Link; nghiệm thu dựa trên kết quả thực tế ngoài đời.",
        "5. Rạch ròi 2 cấp độ: Việc cá nhân xong KHÔNG MẶC NHIÊN là xong Chỉ tiêu; Quản lý phải nghiệm thu Master View!"
    ]
    for pt in points_new:
        p_pt = tf_new.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(10)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(6)

    # Save
    out_file = "Ban_Thuyet_Trinh_Toan_The_Nhan_Vien.pptx"
    backup_file = "Ban_Thuyet_Trinh_Toan_The_Nhan_Vien_Moi.pptx"
    try:
        prs.save(out_file)
        print(f"Presentation saved to: {out_file}")
    except PermissionError:
        prs.save(backup_file)
        print(f"File locked. Saved presentation to: {backup_file}")

if __name__ == "__main__":
    update_pptx()
