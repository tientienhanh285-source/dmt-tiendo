# -*- coding: utf-8 -*-
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation_v2():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Color palette
    NAVY = RGBColor(10, 37, 64)       # #0A2540
    ROYAL = RGBColor(0, 82, 204)      # #0052CC
    GOLD = RGBColor(245, 158, 11)     # #F59E0B
    GREEN = RGBColor(16, 185, 129)    # #10B981
    DARK_TEXT = RGBColor(30, 41, 59)  # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
    ALERT_RED = RGBColor(225, 29, 72)
    SOFT_BLUE = RGBColor(239, 246, 255)

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

    def add_footer(slide, current_slide, total_slides=13):
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

    def add_speaker_note(slide, note_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = note_text

    # ========================================================
    # SLIDE 1: COVER
    # ========================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, NAVY)

    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), prs.slide_width, Inches(0.3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background()

    logo_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.333), Inches(0.5))
    tf_logo = logo_box.text_frame
    p_logo = tf_logo.paragraphs[0]
    p_logo.text = "TỔNG CÔNG TY DMT GROUP — BAN HÀNH CHÍNH NHÂN SỰ"
    p_logo.font.name = 'Arial'
    p_logo.font.size = Pt(13)
    p_logo.font.bold = True
    p_logo.font.color.rgb = GOLD

    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(2.6))
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

    cover_card = add_card(slide1, Inches(1.0), Inches(4.8), Inches(11.333), Inches(1.8), bg_color=RGBColor(17, 49, 84), border_color=ROYAL)
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

    add_speaker_note(slide1, "Chào mừng các anh chị Trưởng Ban và toàn thể anh chị em. Tuyên bố rõ phương châm: không lý thuyết, tập trung thao tác thực tế và cam kết Quý 4 chạy thử an tâm làm quen.")

    # ========================================================
    # SLIDE 2: PHẦN 1 - MỤC TIÊU & TINH THẦN QUÝ 4 (5 PHÚT)
    # ========================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, LIGHT_BG)
    add_header(slide2, "Phần 1: Khai Mạc & 3 Trọng Tâm Buổi Hướng Dẫn (5 Phút)")
    add_footer(slide2, 2)

    c2_1 = add_card(slide2, Inches(0.8), Inches(1.8), Inches(6.0), Inches(4.8))
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

    c2_2 = add_card(slide2, Inches(7.1), Inches(1.8), Inches(5.4), Inches(4.8), bg_color=SOFT_BLUE, border_color=ROYAL)
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
        "• An tâm dùng thử: Bỡ ngỡ hay bấm nhầm là chuyện bình thường, tuyệt đối không bị phạt hay trừ lương.",
        "• Đồng hành 24/7: Ban HCNS tiếp nhận phản hồi tức thì để hoàn thiện hệ thống tốt nhất cho mọi người!"
    ]
    for pt in points2_2:
        p_pt = tf2_2.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(11)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(8)

    add_speaker_note(slide2, "Nêu rõ 3 mục tiêu. Nhấn mạnh việc Quý 4 chạy thử là để làm quen tay, không tạo áp lực, HCNS đồng hành hỗ trợ.")

    # ========================================================
    # SLIDE 3: PHẦN 2 - NGUYÊN TẮC 1 & 2
    # ========================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, LIGHT_BG)
    add_header(slide3, "Phần 2: Nguyên Tắc 1 & 2 — Xuất Phát Điểm & Trách Nhiệm Hai Chiều")
    add_footer(slide3, 3)

    c3_1 = add_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), bg_color=CARD_BG)
    tf3_1 = c3_1.text_frame
    tf3_1.word_wrap = True
    p = tf3_1.paragraphs[0]
    p.text = "1️⃣ NGUYÊN TẮC 1: XUẤT PHÁT TỪ KẾ HOẠCH NĂM & CHỈ TIÊU BAN"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points3_1 = [
        "• Công việc cá nhân không tạo tự phát: Phải gắn liền với Kế hoạch năm và Chỉ tiêu của Ban.",
        "• Trình tự tạo việc 3 bước chuẩn:\n  1. Chọn Dự án\n  2. Chọn Chỉ tiêu\n  3. Nhập tên Công việc",
        "• Ý nghĩa cốt lõi: Giúp công việc có căn cứ vững chắc, theo dõi được từng công việc đang đóng góp vào Chỉ tiêu nào của tổ chức."
    ]
    for pt in points3_1:
        p_pt = tf3_1.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(11)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(8)

    c3_2 = add_card(slide3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=CARD_BG)
    tf3_2 = c3_2.text_frame
    tf3_2.word_wrap = True
    p = tf3_2.paragraphs[0]
    p.text = "2️⃣ NGUYÊN TẮC 2: TRÁCH NHIỆM HAI CHIỀU (QUẢN LÝ & NHÂN VIÊN)"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = GREEN
    p.space_after = Pt(10)

    points3_2 = [
        "• Cả Nhân viên và Quản lý đều tạo việc & làm việc trên hệ thống!",
        "• Trách nhiệm Nhân viên:\n  - Tiếp nhận công việc được giao.\n  - Chủ động tạo các việc thường nhật thuộc trách nhiệm.\n  - Cập nhật tiến độ & báo cáo kết quả.",
        "• Trách nhiệm Quản lý:\n  - Tạo & cập nhật công việc của chính mình.\n  - Phân rã Chỉ tiêu thành các đầu việc cụ thể.\n  - Phân công đúng người, theo sát tiến độ và nghiệm thu."
    ]
    for pt in points3_2:
        p_pt = tf3_2.add_paragraph()
        p_pt.text = pt
        p_pt.font.name = 'Arial'
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = DARK_TEXT
        p_pt.space_after = Pt(6)

    add_speaker_note(slide3, "Phân tích Nguyên tắc 1 (Trình tự 3 bước: Dự án -> Chỉ tiêu -> Việc) và Nguyên tắc 2 (Trách nhiệm hai chiều: Sếp và nhân viên đều làm việc trên hệ thống).")

    # ========================================================
    # SLIDE 4: PHẦN 2 - NGUYÊN TẮC 3, 4, 5
    # ========================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, LIGHT_BG)
    add_header(slide4, "Phần 2: Nguyên Tắc 3, 4 & 5 — Cập Nhật, Minh Chứng & 2 Cấp Độ Đánh Giá")
    add_footer(slide4, 4)

    col_w3 = Inches(3.7)
    gap3 = Inches(0.3)
    
    rules = [
        ("3️⃣ CẬP NHẬT REAL-TIME", [
            "• Cập nhật ngay trong quá trình làm, không đợi cuối tháng.",
            "• Báo cáo sớm vướng mắc hoặc nguy cơ trễ hạn.",
            "• Nêu rõ tình trạng, nguyên nhân (khách quan/chủ quan) và đề xuất hướng xử lý."
        ], ROYAL, "⏱️"),
        ("4️⃣ MINH CHỨNG THỰC TẾ", [
            "• Báo hoàn thành bắt buộc đính kèm File hoặc Link minh chứng phù hợp.",
            "• Quản lý kiểm tra kỹ minh chứng trước khi duyệt.",
            "• Thước đo nghiệm thu là KẾT QUẢ THỰC TẾ, không chỉ nhìn trạng thái trên máy."
        ], GREEN, "📎"),
        ("5️⃣ PHÂN BIỆT 2 CẤP ĐỘ", [
            "• Cấp độ 1: Kết quả việc cá nhân (thực hiện việc thế nào).",
            "• Cấp độ 2: Kết quả Chỉ tiêu Ban (tổng hợp việc có đạt Kế hoạch năm/quý chưa).",
            "• Hoàn thành việc cá nhân KHÔNG MẶC NHIÊN là xong Chỉ tiêu! Quản lý phải nghiệm thu tổng thể!"
        ], GOLD, "🎯")
    ]

    for i, (r_title, r_bullets, r_color, r_icon) in enumerate(rules):
        c_left = Inches(0.8) + i * (col_w3 + gap3)
        card = add_card(slide4, c_left, Inches(1.8), col_w3, Inches(4.8))
        tf = card.text_frame
        tf.word_wrap = True
        
        p_ic = tf.paragraphs[0]
        p_ic.text = f"{r_icon}\n"
        p_ic.font.size = Pt(28)
        p_ic.alignment = PP_ALIGN.CENTER
        
        p_t = tf.add_paragraph()
        p_t.text = r_title
        p_t.font.name = 'Arial'
        p_t.font.bold = True
        p_t.font.size = Pt(12)
        p_t.font.color.rgb = r_color
        p_t.alignment = PP_ALIGN.CENTER
        p_t.space_after = Pt(12)
        
        for b in r_bullets:
            p_b = tf.add_paragraph()
            p_b.text = b
            p_b.font.name = 'Arial'
            p_b.font.size = Pt(10)
            p_b.font.color.rgb = DARK_TEXT
            p_b.space_after = Pt(6)

    add_speaker_note(slide4, "Nhấn mạnh Nguyên tắc 3 (cập nhật liên tục), Nguyên tắc 4 (có minh chứng thực tế) và đặc biệt Nguyên tắc 5 (2 cấp độ đánh giá: việc cá nhân xong không có nghĩa là Chỉ tiêu của Ban xong).")

    # ========================================================
    # SLIDE 5: TẠO VIỆC & TÁI TẠO ĐỊNH KỲ
    # ========================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, LIGHT_BG)
    add_header(slide5, "Thao Tác Thực Tế: Tạo Việc Nhanh & 'Tái Tạo Định Kỳ' (1-Click)")
    add_footer(slide5, 5)

    c5_1 = add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf5_1 = c5_1.text_frame
    tf5_1.word_wrap = True
    p = tf5_1.paragraphs[0]
    p.text = "⚡ ĐĂNG KÝ CÔNG VIỆC NHANH GỌN"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points5_1 = [
        "• Danh mục thả xuống (Dropdown): Chọn Ban/Phòng là tự động gợi ý danh sách nhân sự.",
        "• Đầu tháng chủ động lập kế hoạch: Đăng ký các đầu việc trọng tâm trong tháng.",
        "• Việc phát sinh sau họp giao ban: Thêm việc phát sinh chỉ mất 15 giây, chọn đúng Chỉ tiêu liên kết.",
        "• Tránh tình trạng sót việc: Mọi chỉ đạo bằng lời nói đều được lưu thành đầu việc rõ ràng trên phần mềm."
    ]
    for pt in points5_1:
        p_p = tf5_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c5_2 = add_card(slide5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=RGBColor(254, 243, 199), border_color=GOLD)
    tf5_2 = c5_2.text_frame
    tf5_2.word_wrap = True
    p2 = tf5_2.paragraphs[0]
    p2.text = "🌟 TÁI TẠO ĐỊNH KỲ (1-CLICK)"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(13.5)
    p2.font.color.rgb = RGBColor(180, 83, 9)
    p2.space_after = Pt(10)

    points5_2 = [
        "💡 Giải bài toán việc lặp lại hàng tháng:\n(Ví dụ: Tính lương, báo cáo thuế, kiểm tra công trường, bảo trì...)",
        "👉 Sang tháng mới: Chỉ cần bấm ĐÚNG 1 NÚT: 'TÁI TẠO ĐỊNH KỲ'.",
        "✨ Kết quả tức thì: Toàn bộ danh mục việc chuẩn của tháng trước tự động nhân bản sang tháng mới trong 30 GIÂY!",
        "⏱️ TIẾT KIỆM 90% THỜI GIAN NHẬP LIỆU: Dành thời gian làm chuyên môn thay vì ngồi gõ lại danh sách việc."
    ]
    for pt in points5_2:
        p_p = tf5_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide5, "Demo tính năng tạo việc và nút 'Tái tạo định kỳ' 1-click giúp nhân viên và quản lý tiết kiệm tối đa thời gian lập kế hoạch đầu tháng.")

    # ========================================================
    # SLIDE 6: BẢO VỆ VƯỚNG MẮC KHÁCH QUAN
    # ========================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, LIGHT_BG)
    add_header(slide6, "Cơ Chế Nhân Văn: Bảo Vệ Khi Gặp Vướng Mắc Khách Quan")
    add_footer(slide6, 6)

    c6_1 = add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf6_1 = c6_1.text_frame
    tf6_1.word_wrap = True
    p = tf6_1.paragraphs[0]
    p.text = "✅ BÁO CÁO TIẾN ĐỘ & SỬA ĐỔI"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = GREEN
    p.space_after = Pt(10)

    points6_1 = [
        "• Báo cáo kết quả dễ dàng: Chọn 'Hoàn thành' và đính kèm link tài liệu/file hoặc ảnh nghiệm thu.",
        "• Minh chứng bảo vệ bạn: Tài liệu đính kèm là bằng chứng rõ nhất cho chất lượng công việc của bạn.",
        "• Nút 'Sửa đổi' linh hoạt: Lỡ chọn nhầm trạng thái hoặc dán nhầm link? Bạn hoàn toàn có thể bấm 'Sửa đổi' để cập nhật lại.",
        "• Không lo bấm nhầm: Mọi thao tác đều cho phép chỉnh sửa trước thời điểm chốt sổ định kỳ."
    ]
    for pt in points6_1:
        p_p = tf6_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c6_2 = add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=SOFT_BLUE, border_color=ROYAL)
    tf6_2 = c6_2.text_frame
    tf6_2.word_wrap = True
    p2 = tf6_2.paragraphs[0]
    p2.text = "🛡️ CƠ CHẾ BẢO VỆ KHI CHẬM TIẾN ĐỘ"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(14)
    p2.font.color.rgb = ROYAL
    p2.space_after = Pt(10)

    points6_2 = [
        "⚠️ Chậm do lý do khách quan:\n(Đối tác chậm phản hồi, cơ quan NN chậm thủ tục, mưa bão...)",
        "👉 Thao tác đơn giản: Bấm nút 'VƯỚNG MẮC KHÁCH QUAN' và ghi chú ngắn gọn tình hình thực tế.",
        "✔️ Quản lý thẩm định ngay: Trưởng bộ phận vào xác nhận khối lượng bạn đã làm và duyệt mức hoàn thành (50%, 80%...).",
        "🎯 KẾT QUẢ CÔNG BẰNG: Điểm số được bảo lưu nguyên vẹn trong kết quả KPI! KHÔNG BỊ TRỪ ĐIỂM OAN!"
    ]
    for pt in points6_2:
        p_p = tf6_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide6, "Giải thích nút Vướng mắc khách quan. Nhấn mạnh việc báo cáo sớm khó khăn để sếp duyệt bảo toàn điểm số, không ai bị trừ điểm oan.")

    # ========================================================
    # SLIDE 7: DUYỆT VIỆC & NGHIỆM THU CHỈ TIÊU (MASTER VIEW)
    # ========================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, LIGHT_BG)
    add_header(slide7, "Quyền Quản Lý: Duyệt Việc & Nghiệm Thu Chỉ Tiêu (Master View)")
    add_footer(slide7, 7)

    c7_1 = add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf7_1 = c7_1.text_frame
    tf7_1.word_wrap = True
    p = tf7_1.paragraphs[0]
    p.text = "✔️ CẤP ĐỘ 1: DUYỆT VIỆC (APPROVE TASK)"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points7_1 = [
        "• Khi nhân viên báo Hoàn thành -> Hệ thống thông báo cho Quản lý.",
        "• Bắt buộc kiểm tra minh chứng: Xem file/ảnh nghiệm thu trước khi bấm duyệt.",
        "• Quyền duyệt việc khách quan: Thẩm định khối lượng thực tế khi nhân viên gặp vướng mắc ngoài tầm kiểm soát.",
        "• Chuẩn hóa dữ liệu: Xóa các việc tạo nhầm, trùng lặp để bảng việc luôn sạch đẹp."
    ]
    for pt in points7_1:
        p_p = tf7_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c7_2 = add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=CARD_BG, border_color=GOLD)
    tf7_2 = c7_2.text_frame
    tf7_2.word_wrap = True
    p2 = tf7_2.paragraphs[0]
    p2.text = "🎯 CẤP ĐỘ 2: NGHIỆM THU CHỈ TIÊU (MASTER VIEW)"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(180, 83, 9)
    p2.space_after = Pt(10)

    points7_2 = [
        "• Tiến độ Chỉ tiêu tự động chạy theo tỷ lệ % các task đã duyệt.",
        "• KHÔNG tự động hoàn thành: Dù tiến độ đạt 100%, Chỉ tiêu vẫn không tự đóng lại.",
        "• Trưởng ban thẩm định cuối cùng: Phải là người trực tiếp bấm nút 'Nghiệm thu Chỉ tiêu (Close Objective)'.",
        "• Chốt chặn chất lượng: Đảm bảo kết quả các công việc nhóm thực sự đáp ứng mục tiêu Kế hoạch năm/quý của Công ty!"
    ]
    for pt in points7_2:
        p_p = tf7_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide7, "Phân biệt rõ 2 nút quyền lực của Quản lý: Duyệt task cá nhân vs Nghiệm thu Chỉ tiêu (Close Objective trên Master View).")

    # ========================================================
    # SLIDE 8: BẢNG TIẾN ĐỘ & BÁO CÁO GIAO BAN
    # ========================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, LIGHT_BG)
    add_header(slide8, "Bảng Tiến Độ Thông Minh: Quản Lý Thời Gian & Giảm Áp Lực Họp Hành")
    add_footer(slide8, 8)

    c8_1 = add_card(slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf8_1 = c8_1.text_frame
    tf8_1.word_wrap = True
    p = tf8_1.paragraphs[0]
    p.text = "📅 TRỢ LÝ NHẮC VIỆC THÔNG MINH"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points8_1 = [
        "• Trực quan theo màu sắc: Đã xong (Xanh), Đang làm (Xanh dương), Cảnh báo sắp trễ (Đỏ).",
        "• Nhắc nhở hạn chót (Deadline): Giúp nhân viên chủ động sắp xếp thời gian, không bao giờ quên việc.",
        "• Bộ lọc đa năng (Sort): Tìm kiếm bất kỳ công việc nào theo dự án, người phối hợp chỉ trong 1 giây.",
        "• Làm chủ thời gian: Giảm căng thẳng, không bị ngập trong mớ việc hỗn độn."
    ]
    for pt in points8_1:
        p_p = tf8_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c8_2 = add_card(slide8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=CARD_BG)
    tf8_2 = c8_2.text_frame
    tf8_2.word_wrap = True
    p2 = tf8_2.paragraphs[0]
    p2.text = "☕ TẠM BIỆT ÁP LỰC HỌP GIAO BAN"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(14)
    p2.font.color.rgb = GREEN
    p2.space_after = Pt(10)

    points8_2 = [
        "• Tự động tổng hợp báo cáo giao ban: Toàn bộ tiến độ trọng tâm đã có sẵn trên màn hình.",
        "• Không cần làm slide/file báo cáo riêng: Nhân viên không phải nháo nhào chuẩn bị tài liệu mỗi sáng thứ Hai.",
        "• Rút ngắn 50% thời gian họp: Tập trung bàn giải pháp tháo gỡ khó khăn thay vì ngồi đọc số liệu.",
        "• Lãnh đạo nắm tiến độ tức thời: Xem trực tiếp trên máy, không cần gọi điện giục báo cáo."
    ]
    for pt in points8_2:
        p_p = tf8_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide8, "Nhấn mạnh tiện ích giảm tải áp lực họp giao ban. Dữ liệu đã có sẵn trên hệ thống, không ai phải thức đêm làm báo cáo.")

    # ========================================================
    # SLIDE 9: CƠ CẤU ĐIỂM (100Đ XUẤT PHÁT)
    # ========================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, LIGHT_BG)
    add_header(slide9, "Cơ Cấu Điểm: 100 Điểm Xuất Phát & Quỹ Thưởng Khích Lệ")
    add_footer(slide9, 9)

    c9_1 = add_card(slide9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), bg_color=SOFT_BLUE, border_color=ROYAL)
    tf9_1 = c9_1.text_frame
    tf9_1.word_wrap = True
    p = tf9_1.paragraphs[0]
    p.text = "💯 XUẤT PHÁT ĐIỂM: 100 ĐIỂM TRỌN VẸN"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points9_1 = [
        "• Không cần leo dốc từ số 0: Đầu tháng, mỗi người đều có sẵn 100 ĐIỂM TRỌN VẸN.",
        "• Công thức tính toán rõ ràng:\nTỔNG ĐIỂM = 100Đ - ĐIỂM TRỪ + ĐIỂM THƯỞNG",
        "• Hoàn thành tốt công việc đã đăng ký là bạn đã giữ vững 100 điểm Loại A!",
        "• Mắt xích đồng đẳng: Mọi công việc đã được đưa vào Kế hoạch đều quan trọng như nhau."
    ]
    for pt in points9_1:
        p_p = tf9_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c9_2 = add_card(slide9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tf9_2 = c9_2.text_frame
    tf9_2.word_wrap = True
    p2 = tf9_2.paragraphs[0]
    p2.text = "🎁 QUỸ ĐIỂM THƯỞNG & ĐIỂM PHẠT KỶ LUẬT"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(14)
    p2.font.color.rgb = GREEN
    p2.space_after = Pt(10)

    points9_2 = [
        "✨ CỘNG ĐIỂM THƯỞNG (+5 ĐIỂM):\n• Hoàn thành vượt tiến độ nhiệm vụ trọng điểm.\n• Có sáng kiến, cải tiến quy trình nâng cao hiệu suất.\n• Quản lý đề xuất và biểu dương trực tiếp trên hệ thống.",
        "📉 ĐIỂM TRỪ KỶ LUẬT (Minh bạch):\n• Chỉ áp dụng cho vi phạm nội quy, đi trễ về sớm không lý do.\n• Trễ hạn không có giải trình lý do khách quan.",
        "🔍 Tự theo dõi Real-time: Nhân viên tự xem được điểm số của mình bất kỳ lúc nào!"
    ]
    for pt in points9_2:
        p_p = tf9_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(10.5)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide9, "Thông báo tin vui: Ai cũng có sẵn 100 điểm trong tay đầu tháng, và có cơ hội nhận thêm +5 điểm thưởng nếu làm tốt.")

    # ========================================================
    # SLIDE 10: XẾP LOẠI & THU NHẬP (A*)
    # ========================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, LIGHT_BG)
    add_header(slide10, "Xếp Loại Thi Đua: Cơ Hội Bứt Phá Thu Nhập Cùng A* (110% - 120%)")
    add_footer(slide10, 10)

    grades = [
        ("HẠNG D", "< 71 ĐIỂM", "Chưa đạt yêu cầu.\nĐược hỗ trợ đào tạo & cải thiện quy trình.", ALERT_RED, "🔴"),
        ("HẠNG C", "72 - 81 ĐIỂM", "80% LƯƠNG KPI\nCần chú ý hơn về tiến độ công việc.", RGBColor(234, 88, 12), "🟠"),
        ("HẠNG B", "82 - 91 ĐIỂM", "90% LƯƠNG KPI\nHoàn thành tốt phần lớn nhiệm vụ.", RGBColor(202, 138, 4), "🟡"),
        ("HẠNG A", "92 - 100 ĐIỂM", "100% LƯƠNG KPI\nHoàn thành xuất sắc nhiệm vụ được giao.", GREEN, "🟢"),
        ("HẠNG A*", "> 100 ĐIỂM", "110% - 120% LƯƠNG KPI!\nVượt trội & Cống hiến bứt phá!", GOLD, "⭐")
    ]

    col_w5 = Inches(2.18)
    col_gap5 = Inches(0.18)
    for i, (g_title, g_score, g_desc, g_color, g_icon) in enumerate(grades):
        c_left = Inches(0.8) + i * (col_w5 + col_gap5)
        bg_c = RGBColor(254, 243, 199) if "A*" in g_title else CARD_BG
        brd_c = GOLD if "A*" in g_title else CARD_BORDER
        card = add_card(slide10, c_left, Inches(1.8), col_w5, Inches(4.8), bg_color=bg_c, border_color=brd_c)
        tf = card.text_frame
        tf.word_wrap = True
        
        p_ic = tf.paragraphs[0]
        p_ic.text = f"{g_icon}\n"
        p_ic.font.size = Pt(26)
        p_ic.alignment = PP_ALIGN.CENTER
        
        p_t = tf.add_paragraph()
        p_t.text = g_title
        p_t.font.name = 'Arial'
        p_t.font.bold = True
        p_t.font.size = Pt(14)
        p_t.font.color.rgb = g_color
        p_t.alignment = PP_ALIGN.CENTER
        
        p_s = tf.add_paragraph()
        p_s.text = g_score
        p_s.font.name = 'Arial'
        p_s.font.bold = True
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = NAVY
        p_s.alignment = PP_ALIGN.CENTER
        p_s.space_after = Pt(10)
        
        p_d = tf.add_paragraph()
        p_d.text = g_desc
        p_d.font.name = 'Arial'
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = DARK_TEXT
        p_d.alignment = PP_ALIGN.CENTER

    add_speaker_note(slide10, "Nhấn mạnh con số 110% - 120% LƯƠNG cho hạng A*. Khẳng định chính sách thưởng vượt trội của DMT Group cho những cá nhân xuất sắc.")

    # ========================================================
    # SLIDE 11: AI RÀ SOÁT JD
    # ========================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, LIGHT_BG)
    add_header(slide11, "Trợ Lý AI & Bản Mô Tả Công Việc (JD): Bảo Vệ Chuyên Môn")
    add_footer(slide11, 11)

    c11_1 = add_card(slide11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tf11_1 = c11_1.text_frame
    tf11_1.word_wrap = True
    p = tf11_1.paragraphs[0]
    p.text = "📋 BẢN JD — TẤM KHIÊN BẢO VỆ CHUYÊN MÔN"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = ROYAL
    p.space_after = Pt(10)

    points11_1 = [
        "• Định rõ chức trách: Nhân viên biết rõ phạm vi công việc và quyền hạn chuyên môn của mình.",
        "• Chấm dứt 'ôm đồm': Tránh tình trạng bị giao những việc không tên vượt ngoài chuyên môn.",
        "• Giúp Trưởng ban giao việc chính xác: Đảm bảo nguyên tắc 'Đúng người — Đúng việc'.",
        "• Định hướng thăng tiến: Nhìn vào JD để biết mình cần phát triển kỹ năng gì tiếp theo."
    ]
    for pt in points11_1:
        p_p = tf11_1.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(11)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    c11_2 = add_card(slide11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), bg_color=SOFT_BLUE, border_color=ROYAL)
    tf11_2 = c11_2.text_frame
    tf11_2.word_wrap = True
    p2 = tf11_2.paragraphs[0]
    p2.text = "🤖 TRÍ TUỆ NHÂN TẠO (AI) — NGƯỜI CỐ VẤN THÔNG MINH"
    p2.font.name = 'Arial'
    p2.font.bold = True
    p2.font.size = Pt(14)
    p2.font.color.rgb = NAVY
    p2.space_after = Pt(10)

    points11_2 = [
        "✨ Nhận diện ngữ nghĩa thông minh: AI hiểu tính chất công việc thực tế, không bắt bẻ câu chữ máy móc.",
        "⚠️ Cảnh báo hỗ trợ nhân viên: Nếu phát hiện một nhân sự kỹ thuật phải làm quá nhiều việc sự vụ hành chính ngoài JD, AI sẽ báo động cho Quản lý.",
        "🛡️ Mục đích bảo vệ: Giúp Quản lý điều chỉnh lại công việc cho nhân viên, tránh lãng phí năng lực chuyên môn.",
        "❌ KHÔNG PHẢI ĐỂ PHẠT: AI là công cụ bảo vệ bạn làm đúng nghề, đúng nghiệp để phát triển tương lai!"
    ]
    for pt in points11_2:
        p_p = tf11_2.add_paragraph()
        p_p.text = pt
        p_p.font.name = 'Arial'
        p_p.font.size = Pt(10.5)
        p_p.font.color.rgb = DARK_TEXT
        p_p.space_after = Pt(8)

    add_speaker_note(slide11, "Giải tỏa nỗi sợ AI. Khẳng định AI giúp phát hiện sai lệch để điều phối việc hợp lý cho nhân viên, không dùng để trừ điểm.")

    # ========================================================
    # SLIDE 12: LỘ TRÌNH QUÝ 4 & CAM KẾT
    # ========================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, LIGHT_BG)
    add_header(slide12, "Lộ Trình Triển Khai: Chạy Thử Nghiệm Đồng Hành — Không Áp Lực")
    add_footer(slide12, 12)

    phases = [
        ("GIAI ĐOẠN 1: THỬ NGHIỆM (QUÝ IV/2026)", [
            "• Chạy thử nghiệm Pilot để toàn thể anh chị em làm quen hệ thống.",
            "• Tổ chức đào tạo 'Cầm tay chỉ việc' tận nơi cho từng phòng ban.",
            "• TUYỆT ĐỐI KHÔNG ÁP DỤNG TRỪ ĐIỂM / TRỪ LƯƠNG trong thời gian làm quen!",
            "• Thu thập 100% phản hồi để tinh chỉnh phần mềm theo ý kiến người dùng."
        ], ROYAL, "🧪"),
        ("GIAI ĐOẠN 2: CHÍNH THỨC", [
            "• Vận hành chính thức khi mọi người đã hoàn toàn thành thạo và thoải mái.",
            "• Dừng hoàn toàn việc làm báo cáo giấy và file Word/Excel.",
            "• Áp dụng cơ chế Thưởng A* (110% - 120% lương).",
            "• Môi trường làm việc số hóa, hiện đại, minh bạch và chuyên nghiệp."
        ], GREEN, "🚀")
    ]

    for i, (p_title, p_bullets, p_color, p_icon) in enumerate(phases):
        c_left = Inches(0.8) + i * Inches(5.9)
        card = add_card(slide12, c_left, Inches(1.8), Inches(5.7), Inches(3.6))
        tf = card.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = f"{p_icon}  {p_title}"
        p_t.font.name = 'Arial'
        p_t.font.bold = True
        p_t.font.size = Pt(13)
        p_t.font.color.rgb = p_color
        p_t.space_after = Pt(12)
        
        for b in p_bullets:
            p_b = tf.add_paragraph()
            p_b.text = b
            p_b.font.name = 'Arial'
            p_b.font.size = Pt(11)
            p_b.font.color.rgb = DARK_TEXT
            p_b.space_after = Pt(8)

    c_banner = add_card(slide12, Inches(0.8), Inches(5.6), Inches(11.733), Inches(1.0), bg_color=SOFT_BLUE, border_color=ROYAL)
    tf_b = c_banner.text_frame
    tf_b.word_wrap = True
    p_b0 = tf_b.paragraphs[0]
    p_b0.text = "🤝 CAM KẾT VÀNG TỪ BAN HCNS: 'Đồng hành 24/7 bên cạnh anh chị em — Không ai bị bỏ lại phía sau!'"
    p_b0.font.name = 'Arial'
    p_b0.font.bold = True
    p_b0.font.size = Pt(12.5)
    p_b0.font.color.rgb = NAVY
    p_b0.alignment = PP_ALIGN.CENTER

    add_speaker_note(slide12, "Tuyên bố cam kết vàng: Quý 4 chạy thử là để hỗ trợ làm quen, tuyệt đối không trừ điểm hay ảnh hưởng lương.")

    # ========================================================
    # SLIDE 13: LỜI KẾT & Q&A
    # ========================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, NAVY)

    bar13 = slide13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), prs.slide_width, Inches(0.3))
    bar13.fill.solid()
    bar13.fill.fore_color.rgb = GOLD
    bar13.line.fill.background()

    box13 = slide13.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.333), Inches(4.5))
    tf13 = box13.text_frame
    tf13.word_wrap = True
    
    p = tf13.paragraphs[0]
    p.text = "CẢM ƠN CÁC ANH CHỊ TRƯỞNG BAN & TOÀN THỂ ANH CHỊ EM!"
    p.font.name = 'Arial'
    p.font.bold = True
    p.font.size = Pt(30)
    p.font.color.rgb = GOLD
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(18)

    p_quote = tf13.add_paragraph()
    p_quote.text = "“Công nghệ không sinh ra để kiểm soát con người.\nCông nghệ sinh ra để giải phóng sức lao động & tôn vinh giá trị của mỗi chúng ta!”"
    p_quote.font.name = 'Arial'
    p_quote.font.italic = True
    p_quote.font.size = Pt(18)
    p_quote.font.color.rgb = WHITE
    p_quote.alignment = PP_ALIGN.CENTER
    p_quote.space_after = Pt(28)

    p_qa = tf13.add_paragraph()
    p_qa.text = "💬 PHẦN TRAO ĐỔI & GIẢI ĐÁP THẮC MẮC (Q&A)\nBan HCNS sẵn sàng lắng nghe & giải đáp mọi câu hỏi từ các anh chị em!"
    p_qa.font.name = 'Arial'
    p_qa.font.bold = True
    p_qa.font.size = Pt(16)
    p_qa.font.color.rgb = RGBColor(147, 197, 253)
    p_qa.alignment = PP_ALIGN.CENTER

    add_speaker_note(slide13, "Cảm ơn toàn thể hội trường, mở phần Q&A và giải đáp các câu hỏi thắc mắc.")

    out_file = "Ban_Thuyet_Trinh_Toan_The_Nhan_Vien.pptx"
    prs.save(out_file)
    print(f"Presentation saved successfully: {out_file}")

if __name__ == "__main__":
    build_presentation_v2()
