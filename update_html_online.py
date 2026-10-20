# -*- coding: utf-8 -*-
html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Hướng Dẫn Sử Dụng Hệ Thống Quản Lý Tiến Độ & Đánh Giá KPI — DMT Group</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Reveal.js core CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reset.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    
    <style>
        :root {
            --navy-dark: #071527;
            --navy-primary: #0a2540;
            --navy-surface: #0f355c;
            --navy-card: rgba(255, 255, 255, 0.06);
            --navy-border: rgba(255, 255, 255, 0.12);
            --royal-blue: #0066ff;
            --royal-light: #38bdf8;
            --gold-accent: #f59e0b;
            --gold-light: #fef08a;
            --emerald: #10b981;
            --rose: #f43f5e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        body {
            background-color: var(--navy-dark);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
        }

        .reveal {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: var(--text-main);
        }

        .reveal h1, .reveal h2, .reveal h3, .reveal h4 {
            text-transform: none;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .reveal h1 {
            font-size: 2.2em;
            color: #ffffff;
            line-height: 1.15;
            margin-bottom: 16px;
        }

        .reveal h2 {
            font-size: 1.55em;
            color: #ffffff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .badge-cat {
            display: inline-block;
            background: rgba(0, 102, 255, 0.2);
            color: var(--royal-light);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 9999px;
            padding: 4px 14px;
            font-size: 0.45em;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .badge-gold {
            background: rgba(245, 158, 11, 0.15);
            color: var(--gold-accent);
            border-color: rgba(245, 158, 11, 0.4);
        }

        .badge-green {
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald);
            border-color: rgba(16, 185, 129, 0.4);
        }

        .badge-red {
            background: rgba(244, 63, 94, 0.15);
            color: var(--rose);
            border-color: rgba(244, 63, 94, 0.4);
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 22px;
            margin-top: 12px;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 18px;
            margin-top: 12px;
        }

        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 12px;
        }

        .grid-5 {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
            margin-top: 12px;
        }

        .card {
            background: var(--navy-card);
            border: 1px solid var(--navy-border);
            border-radius: 16px;
            padding: 22px;
            backdrop-filter: blur(12px);
            text-align: left;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--royal-light);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 102, 255, 0.15);
        }

        .card-highlight {
            background: rgba(0, 102, 255, 0.12);
            border-color: rgba(56, 189, 248, 0.4);
        }

        .card-gold {
            background: rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.35);
        }

        .card-green {
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.35);
        }

        .card-red {
            background: rgba(244, 63, 94, 0.1);
            border-color: rgba(244, 63, 94, 0.35);
        }

        .card-title {
            font-size: 1.05em;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card ul {
            margin: 0;
            padding-left: 18px;
        }

        .card li {
            font-size: 0.73em;
            line-height: 1.6;
            color: #cbd5e1;
            margin-bottom: 8px;
        }

        .card p {
            font-size: 0.75em;
            line-height: 1.6;
            color: #cbd5e1;
            margin: 0 0 8px 0;
        }

        .icon-large {
            font-size: 2em;
            margin-bottom: 10px;
            display: inline-block;
        }

        .highlight-text {
            color: var(--gold-accent);
            font-weight: 700;
        }

        .green-text {
            color: var(--emerald);
            font-weight: 700;
        }

        .red-text {
            color: var(--rose);
            font-weight: 700;
        }

        .banner-bar {
            background: linear-gradient(90deg, #0052cc 0%, #0284c7 100%);
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
            margin-top: 18px;
            font-size: 0.78em;
            font-weight: 600;
            color: #ffffff;
            box-shadow: 0 4px 20px rgba(0, 82, 204, 0.3);
        }

        .reveal .controls { color: var(--royal-light); }
        .reveal .progress { color: var(--royal-light); height: 4px; }

        /* Comparison table */
        .cmp-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 10px;
            font-size: 0.72em;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--navy-border);
        }
        .cmp-table th {
            background: #0a2540;
            color: #ffffff;
            font-weight: 700;
            padding: 10px 14px;
            text-align: left;
            border-bottom: 2px solid rgba(0, 102, 255, 0.4);
        }
        .cmp-table td {
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            vertical-align: middle;
            background: rgba(255, 255, 255, 0.03);
            color: #cbd5e1;
            line-height: 1.5;
        }
        .cmp-table tr:last-child td { border-bottom: none; }
        .cmp-table tr:hover td { background: rgba(0, 102, 255, 0.08); }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">

            <!-- SLIDE 1: COVER -->
            <section data-transition="zoom">
                <span class="badge-cat badge-gold">DMT GROUP • BAN HÀNH CHÍNH NHÂN SỰ</span>
                <h1>HƯỚNG DẪN SỬ DỤNG HỆ THỐNG<br><span style="color: var(--royal-light);">QUẢN LÝ TIẾN ĐỘ & ĐÁNH GIÁ KPI</span></h1>
                <p style="font-size: 0.95em; color: var(--gold-accent); font-weight: 600; margin-bottom: 22px;">
                    Dành Cho Các Anh Chị Trưởng Ban & Toàn Thể Cán Bộ Nhân Viên
                </p>
                <div class="grid-3" style="max-width: 950px; margin: 0 auto 20px auto;">
                    <div class="card card-highlight" style="text-align: center; padding: 16px;">
                        <span class="icon-large">⚡</span>
                        <div style="font-weight: 700; font-size: 0.85em; color: #fff;">Tập Trung Thực Hành</div>
                        <p style="font-size: 0.65em; margin-top: 4px;">Không lý thuyết, làm việc thực tế</p>
                    </div>
                    <div class="card card-green" style="text-align: center; padding: 16px;">
                        <span class="icon-large">🎯</span>
                        <div style="font-weight: 700; font-size: 0.85em; color: #fff;">5 Nguyên Tắc Vận Hành</div>
                        <p style="font-size: 0.65em; margin-top: 4px;">Đối chiếu rõ ràng Cũ vs Mới</p>
                    </div>
                    <div class="card card-gold" style="text-align: center; padding: 16px;">
                        <span class="icon-large">🌱</span>
                        <div style="font-weight: 700; font-size: 0.85em; color: #fff;">Quý 4 Chạy Thử (Pilot)</div>
                        <p style="font-size: 0.65em; margin-top: 4px;">Yên tâm làm quen tay, không áp lực</p>
                    </div>
                </div>
                <div class="banner-bar">
                    🤝 <strong>Ban HCNS đồng hành 24/7 bên cạnh anh chị em — Hoàn thiện hệ thống vì người dùng!</strong>
                </div>
                <aside class="notes">
                    Kính chào các anh chị Trưởng Ban và toàn thể anh chị em. Buổi hôm nay tập trung vào thao tác thực tế và giải quyết vướng mắc, tinh thần Quý 4 chạy thử thoải mái làm quen.
                </aside>
            </section>

            <!-- SLIDE 2: PHẦN 1 - MỤC TIÊU & QUÝ 4 (5 PHÚT) -->
            <section data-transition="slide">
                <span class="badge-cat">PHẦN 1 • 5 PHÚT</span>
                <h2>Khai Mạc: Giới Thiệu Mục Tiêu & Tinh Thần Quý 4</h2>
                <div class="grid-2">
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">🎯 3 NỘI DUNG TRỌNG TÂM</div>
                        <ul>
                            <li><strong>1. Hiểu đúng vai trò & trách nhiệm:</strong> Xác định rõ nhiệm vụ của từng người trên hệ thống.</li>
                            <li><strong>2. Hướng dẫn thao tác trực tiếp:</strong> Cầm tay chỉ việc: Tạo việc, cập nhật tiến độ, duyệt việc và nghiệm thu Chỉ tiêu theo đúng quyền.</li>
                            <li><strong>3. Thống nhất cách xử lý tình huống:</strong> Giải quyết nhanh các vướng mắc phát sinh trong quá trình vận hành.</li>
                        </ul>
                    </div>
                    <div class="card card-gold">
                        <div class="card-title" style="color: var(--gold-accent);">🌱 QUÝ 4: GIAI ĐOẠN CHẠY THỬ (PILOT)</div>
                        <ul>
                            <li><strong>Đăng nhập thông minh:</strong> Chọn đúng Công ty ➔ đúng Tên ➔ đúng Vai trò, hệ thống tự lọc dữ liệu gọn gàng.</li>
                            <li><strong>Mục tiêu Quý 4:</strong> Trưởng ban tập chia nhỏ mục tiêu; Nhân viên tập thói quen cập nhật tiến độ liên tục.</li>
                            <li><strong>Yên tâm trải nghiệm:</strong> Bỡ ngỡ hay bấm nhầm là bình thường, <span class="green-text">tuyệt đối không bị phạt hay trừ lương</span>!</li>
                            <li><strong>HCNS hỗ trợ tức thì:</strong> Có khó khăn nhắn lại là được giải quyết ngay.</li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Nhấn mạnh 3 nội dung trọng tâm. Khẳng định Quý 4 chạy thử là để làm quen tay, giải tỏa tâm lý lo sợ của nhân viên.
                </aside>
            </section>

            <!-- SLIDE 3: SO SÁNH CÁCH LÀM CŨ VS NGUYÊN TẮC MỚI -->
            <section data-transition="slide">
                <span class="badge-cat badge-green">PHẦN 2 • TỔNG QUAN ĐỐI CHIẾU</span>
                <h2>Đối Chiếu Nhanh: Cách Làm Cũ vs 5 Nguyên Tắc Mới</h2>
                <table class="cmp-table">
                    <thead>
                        <tr>
                            <th style="width: 20%;">Nội dung</th>
                            <th style="width: 40%; color: #fca5a5;">❌ Cách làm cũ (Thủ công / Truyền thống)</th>
                            <th style="width: 40%; color: #86efac;">✅ Nguyên tắc mới trên phần mềm</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>1. Nguồn gốc việc</strong></td>
                            <td>Tự nghĩ và liệt kê việc rời rạc; nhiều việc không rõ phục vụ mục tiêu nào của phòng.</td>
                            <td><strong class="green-text">Liên kết trục dọc:</strong> Dự án ➔ Chỉ tiêu Ban ➔ Việc cá nhân. Làm việc nào rõ đích đến việc đó.</td>
                        </tr>
                        <tr>
                            <td><strong>2. Trách nhiệm</strong></td>
                            <td>Coi báo cáo là làm cho sếp xem; sếp giao việc miệng qua Zalo/email dễ quên, không theo dõi việc của sếp.</td>
                            <td><strong class="green-text">Trách nhiệm 2 chiều:</strong> Cả sếp và nhân viên đều làm việc; sếp phân rã chỉ tiêu và tự cập nhật việc của mình.</td>
                        </tr>
                        <tr>
                            <td><strong>3. Thời điểm cập nhật</strong></td>
                            <td>'Dồn toa' cuối tháng mới cuống cuồng ngồi nhớ lại; vướng mắc để dồn cuối kỳ mới vỡ lở.</td>
                            <td><strong class="green-text">Cập nhật Real-time:</strong> Báo cáo ngay khi làm; có nguy cơ trễ / vướng mắc báo sớm để sếp hỗ trợ.</td>
                        </tr>
                        <tr>
                            <td><strong>4. Nghiệm thu</strong></td>
                            <td>Khai báo 'Đã xong' chung chung trên giấy; duyệt theo cảm tính hoặc tin tưởng miệng, thiếu đối chứng.</td>
                            <td><strong class="green-text">Minh chứng thực tế:</strong> Bắt buộc đính kèm File/Link; nghiệm thu dựa trên kết quả thực tế ngoài đời.</td>
                        </tr>
                        <tr>
                            <td><strong>5. Cấp độ đánh giá</strong></td>
                            <td>Ngộ nhận: Thấy xong việc cá nhân là tưởng Chỉ tiêu của Ban xong; dẫn đến tỷ lệ ảo dù dự án chung chậm.</td>
                            <td><strong class="green-text">Rạch ròi 2 cấp độ:</strong> Việc cá nhân xong KHÔNG mặc nhiên là xong Chỉ tiêu; sếp phải nghiệm thu Master View.</td>
                        </tr>
                    </tbody>
                </table>
                <aside class="notes">
                    Chiếu bảng so sánh để khán phòng thấy ngay sự khác biệt. Nói với giọng đồng cảm khi nhắc về thói quen cũ và dứt khoát khi nêu lợi ích của nguyên tắc mới.
                </aside>
            </section>

            <!-- SLIDE 4: CHI TIẾT NGUYÊN TẮC 1 & 2 -->
            <section data-transition="slide">
                <span class="badge-cat badge-green">PHẦN 2 • NGUYÊN TẮC 1 & 2</span>
                <h2>Nguyên Tắc 1 & 2: Xuất Phát Điểm & Trách Nhiệm Hai Chiều</h2>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title" style="color: var(--royal-light);">1️⃣ XUẤT PHÁT TỪ KẾ HOẠCH NĂM & CHỈ TIÊU BAN</div>
                        <p style="font-size: 0.7em; color: var(--rose); margin-bottom: 6px;"><em>(Khác cách cũ: Không tự nghĩ việc rời rạc, thiếu căn cứ)</em></p>
                        <ul>
                            <li>Công việc cá nhân bắt buộc gắn liền với Kế hoạch năm và Chỉ tiêu của Ban.</li>
                            <li><strong>Trình tự tạo việc 3 bước chuẩn:</strong><br>
                                <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 8px; margin: 8px 0; font-weight: 700; color: var(--gold-accent);">
                                    Chọn Dự án ➔ Chọn Chỉ tiêu ➔ Nhập tên việc
                                </div>
                            </li>
                            <li><strong>Ý nghĩa:</strong> Giúp công việc có căn cứ và theo dõi được công việc đang đóng góp vào mục tiêu lớn nào.</li>
                        </ul>
                    </div>
                    <div class="card card-green">
                        <div class="card-title" style="color: var(--emerald);">2️⃣ TRÁCH NHIỆM HAI CHIỀU (QUẢN LÝ & NHÂN VIÊN)</div>
                        <p style="font-size: 0.7em; color: var(--rose); margin-bottom: 6px;"><em>(Khác cách cũ: Không chỉ nhân viên nộp báo cáo cho sếp)</em></p>
                        <ul>
                            <li><strong>Cả hai đều tạo việc & làm việc:</strong><br>
                                • <strong class="green-text">Nhân viên:</strong> Nhận việc được giao, chủ động tạo việc theo trách nhiệm, cập nhật tiến độ và báo cáo kết quả.<br>
                                • <strong class="highlight-text">Quản lý:</strong> Không chỉ theo dõi cấp dưới mà <em>phải tạo & làm việc của chính mình</em>; phân rã Chỉ tiêu thành đầu việc cụ thể, phân công và nghiệm thu.
                            </li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Phân tích Nguyên tắc 1 (Trình tự 3 bước tạo việc) và Nguyên tắc 2 (Trách nhiệm hai chiều: Quản lý và nhân viên đều làm việc trên máy).
                </aside>
            </section>

            <!-- SLIDE 5: CHI TIẾT NGUYÊN TẮC 3, 4, 5 -->
            <section data-transition="slide">
                <span class="badge-cat badge-green">PHẦN 2 • NGUYÊN TẮC 3, 4 & 5</span>
                <h2>Nguyên Tắc 3, 4 & 5: Cập Nhật, Minh Chứng & 2 Cấp Độ Đánh Giá</h2>
                <div class="grid-3">
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">3️⃣ CẬP NHẬT REAL-TIME</div>
                        <p style="font-size: 0.65em; color: var(--rose); margin-bottom: 4px;"><em>(Khác cách cũ: Chấm dứt 'dồn toa' cuối tháng)</em></p>
                        <ul>
                            <li>Cập nhật trong quá trình làm, không đợi dồn đến cuối tháng.</li>
                            <li>Báo cáo sớm vướng mắc hoặc nguy cơ trễ hạn.</li>
                            <li>Nêu rõ tình trạng, nguyên nhân (khách quan/chủ quan) và đề xuất hướng xử lý.</li>
                        </ul>
                    </div>
                    <div class="card card-green">
                        <div class="card-title" style="color: var(--emerald);">4️⃣ MINH CHỨNG THỰC TẾ</div>
                        <p style="font-size: 0.65em; color: var(--rose); margin-bottom: 4px;"><em>(Khác cách cũ: Không khai 'Đã xong' bằng miệng)</em></p>
                        <ul>
                            <li>Báo hoàn thành bắt buộc đính kèm File hoặc Link minh chứng phù hợp.</li>
                            <li>Quản lý kiểm tra nội dung & minh chứng trước khi duyệt việc.</li>
                            <li>Thước đo nghiệm thu là <strong>kết quả thực tế ngoài đời</strong>, không chỉ nhìn trạng thái trên máy.</li>
                        </ul>
                    </div>
                    <div class="card card-gold">
                        <div class="card-title" style="color: var(--gold-accent);">5️⃣ PHÂN BIỆT 2 CẤP ĐỘ</div>
                        <p style="font-size: 0.65em; color: var(--rose); margin-bottom: 4px;"><em>(Khác cách cũ: Không ngộ nhận việc cá nhân = Chỉ tiêu Ban)</em></p>
                        <ul>
                            <li><strong>Cấp độ 1:</strong> Kết quả việc cá nhân (thực hiện việc thế nào).</li>
                            <li><strong>Cấp độ 2:</strong> Kết quả Chỉ tiêu Ban (tổng hợp việc có đạt Kế hoạch năm/quý chưa).</li>
                            <li><strong class="highlight-text">Việc cá nhân xong KHÔNG mặc nhiên là xong Chỉ tiêu!</strong> Quản lý phải nghiệm thu tổng thể!</li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Nhấn mạnh Nguyên tắc 3 (cập nhật liên tục), Nguyên tắc 4 (có minh chứng thực tế) và đặc biệt Nguyên tắc 5 (2 cấp độ đánh giá: việc cá nhân xong không có nghĩa là Chỉ tiêu của Ban xong).
                </aside>
            </section>

            <!-- SLIDE 6: TẠO VIỆC & TÁI TẠO ĐỊNH KỲ -->
            <section data-transition="slide">
                <span class="badge-cat badge-gold">TIỆN ÍCH ĐỘT PHÁ</span>
                <h2>Tạo Việc Nhanh & Tính Năng 'Tái Tạo Định Kỳ' (1-Click)</h2>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">⚡ ĐĂNG KÝ CÔNG VIỆC SIÊU TỐC</div>
                        <ul>
                            <li><strong>Menu Dropdown thông minh:</strong> Chọn Ban/Phòng là tự động gợi ý danh sách nhân sự, không cần gõ tay.</li>
                            <li><strong>Đầu tháng chủ động đăng ký:</strong> Lên kế hoạch cho các đầu việc trọng tâm trong tháng.</li>
                            <li><strong>Linh hoạt thêm việc phát sinh:</strong> Sếp giao việc đột xuất sau họp giao ban, vào thêm việc chỉ mất 15 giây.</li>
                        </ul>
                    </div>
                    <div class="card card-gold">
                        <div class="card-title" style="color: var(--gold-accent);">🌟 TÁI TẠO ĐỊNH KỲ (1-CLICK)</div>
                        <ul>
                            <li>💡 <em>Áp dụng cho 80% công việc lặp lại hàng tháng</em> (Tính lương, báo cáo thuế, kiểm tra công trường, bảo trì...).</li>
                            <li>👉 Sang tháng mới: Chỉ cần bấm <strong>ĐÚNG 1 NÚT: 'TÁI TẠO ĐỊNH KỲ'</strong>.</li>
                            <li>✨ Toàn bộ danh mục việc chuẩn tự nhân bản sang tháng mới trong <strong>30 GIÂY!</strong></li>
                            <li>⏱️ <strong>Tiết kiệm 90% thời gian nhập liệu!</strong></li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Demo tính năng tạo việc và nút 'Tái tạo định kỳ' 1-click giúp nhân viên và quản lý tiết kiệm tối đa thời gian lập kế hoạch đầu tháng.
                </aside>
            </section>

            <!-- SLIDE 7: BẢO VỆ VƯỚNG MẮC KHÁCH QUAN -->
            <section data-transition="slide">
                <span class="badge-cat badge-green">TÂM ĐIỂM QUYỀN LỢI</span>
                <h2>Cơ Chế Nhân Văn: Bảo Vệ Khi Gặp Vướng Mắc Khách Quan</h2>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title" style="color: var(--emerald);">✅ HOÀN THÀNH & CHỈNH SỬA LINH HOẠT</div>
                        <ul>
                            <li><strong>Báo cáo kết quả nhanh:</strong> Chọn 'Hoàn thành' và đính kèm link tài liệu/file hoặc ảnh nghiệm thu.</li>
                            <li><strong>Minh chứng bảo vệ bạn:</strong> Tài liệu đính kèm là bằng chứng rõ nhất cho chất lượng công việc của bạn.</li>
                            <li><strong>Nút 'Sửa đổi' linh hoạt:</strong> Lỡ bấm nhầm trạng thái hoặc dán nhầm link? Chỉnh sửa lại dễ dàng mọi lúc.</li>
                        </ul>
                    </div>
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">🛡️ BẢO VỆ KHI CHẬM TIẾN ĐỘ KHÁCH QUAN</div>
                        <ul>
                            <li>⚠️ <strong>Chậm do lý do khách quan:</strong> Đối tác chậm phản hồi, chờ thủ tục cơ quan nhà nước, mưa bão...</li>
                            <li>👉 <strong>Thao tác:</strong> Bấm nút <span class="highlight-text">'VƯỚNG MẮC KHÁCH QUAN'</span> & giải trình ngắn gọn.</li>
                            <li>✔️ <strong>Quản lý thẩm định:</strong> Xác nhận khối lượng thực tế và duyệt mức hoàn thành (50%, 80%...).</li>
                            <li>🎯 <strong>KẾT QUẢ:</strong> Điểm số được bảo lưu nguyên vẹn trong kết quả KPI! <span class="green-text">KHÔNG BỊ TRỪ ĐIỂM OAN!</span></li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Giải thích nút Vướng mắc khách quan. Nhấn mạnh việc báo cáo sớm khó khăn để sếp duyệt bảo toàn điểm số, không ai bị trừ điểm oan.
                </aside>
            </section>

            <!-- SLIDE 8: DUYỆT VIỆC & NGHIỆM THU CHỈ TIÊU -->
            <section data-transition="slide">
                <span class="badge-cat">QUYỀN HẠN QUẢN LÝ</span>
                <h2>Quyền Quản Lý: Duyệt Việc & Nghiệm Thu Chỉ Tiêu (Master View)</h2>
                <div class="grid-2">
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">✔️ CẤP ĐỘ 1: DUYỆT VIỆC (APPROVE TASK)</div>
                        <ul>
                            <li>Nhân viên báo Hoàn thành ➔ Quản lý nhận thông báo.</li>
                            <li>Bắt buộc kiểm tra kỹ minh chứng trước khi bấm duyệt.</li>
                            <li>Duyệt việc khách quan: Xác nhận % khối lượng thực tế khi nhân viên gặp khó khăn ngoài tầm kiểm soát.</li>
                            <li>Chuẩn hóa dữ liệu: Xóa các việc tạo nhầm, trùng lặp.</li>
                        </ul>
                    </div>
                    <div class="card card-gold">
                        <div class="card-title" style="color: var(--gold-accent);">🎯 CẤP ĐỘ 2: NGHIỆM THU CHỈ TIÊU (MASTER VIEW)</div>
                        <ul>
                            <li>Tiến độ Chỉ tiêu tự động chạy theo tỷ lệ % các task đã duyệt.</li>
                            <li><strong>KHÔNG tự động đóng:</strong> Dù tiến độ 100%, Chỉ tiêu vẫn không tự hoàn thành.</li>
                            <li><strong>Trưởng ban thẩm định cuối cùng:</strong> Trực tiếp bấm nút 'Nghiệm thu Chỉ tiêu (Close Objective)'.</li>
                            <li>Chốt chặn chất lượng đảm bảo đạt mục tiêu Kế hoạch năm/quý của Công ty!</li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Phân biệt rõ 2 nút quyền lực của Quản lý: Duyệt task cá nhân vs Nghiệm thu Chỉ tiêu (Close Objective trên Master View).
                </aside>
            </section>

            <!-- SLIDE 9: BẢNG TIẾN ĐỘ & BÁO CÁO GIAO BAN -->
            <section data-transition="slide">
                <span class="badge-cat">GIẢI PHÓNG ÁP LỰC HỌP HÀNH</span>
                <h2>Bảng Tiến Độ: Quản Lý Thời Gian & Báo Cáo Giao Ban Tự Động</h2>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title" style="color: var(--royal-light);">📅 TRỢ LÝ NHẮC VIỆC THÔNG MINH</div>
                        <ul>
                            <li><strong>Màu sắc trực quan:</strong> Đã xong (Xanh), Đang làm (Xanh dương), Cảnh báo sắp trễ (Đỏ).</li>
                            <li><strong>Nhắc nhở Deadline:</strong> Không bao giờ sót việc quan trọng giữa bộn bề công việc.</li>
                            <li><strong>Bộ lọc đa năng (Sort):</strong> Tra cứu bất kỳ công việc nào chỉ trong 1 giây.</li>
                        </ul>
                    </div>
                    <div class="card card-green">
                        <div class="card-title" style="color: var(--emerald);">☕ TẠM BIỆT ÁP LỰC BÁO CÁO GIAO BAN</div>
                        <ul>
                            <li><strong>Tự động sinh báo cáo:</strong> Số liệu trọng tâm có sẵn trên màn hình lớn phòng họp.</li>
                            <li><strong>Không làm slide riêng:</strong> Tạm biệt cảnh nháo nhào chuẩn bị báo cáo mỗi sáng thứ Hai.</li>
                            <li><strong>Rút ngắn 50% thời gian họp:</strong> Tập trung bàn giải pháp tháo gỡ vướng mắc.</li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Nhấn mạnh tiện ích giảm tải áp lực họp giao ban. Dữ liệu đã có sẵn trên hệ thống, không ai phải thức đêm làm báo cáo.
                </aside>
            </section>

            <!-- SLIDE 10: CƠ CẤU ĐIỂM -->
            <section data-transition="slide">
                <span class="badge-cat">QUY CHẾ TÍNH ĐIỂM</span>
                <h2>Cơ Cấu Điểm: 100 Điểm Xuất Phát & Quỹ Thưởng Khích Lệ</h2>
                <div class="grid-2">
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">💯 XUẤT PHÁT ĐIỂM: 100 ĐIỂM TRỌN VẸN</div>
                        <ul>
                            <li>Bạn không cần leo dốc từ số 0: <strong>Đầu tháng, mỗi người đều có sẵn 100 ĐIỂM TRỌN VẸN</strong>.</li>
                            <li>Công thức tính toán rõ ràng:<br>
                                <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 8px; margin: 8px 0; font-weight: 700; color: var(--gold-accent);">
                                    TỔNG ĐIỂM = 100Đ - ĐIỂM TRỪ + ĐIỂM THƯỞNG
                                </div>
                            </li>
                            <li>Hoàn thành tốt công việc đã đăng ký là bạn đã giữ vững 100 điểm Loại A!</li>
                        </ul>
                    </div>
                    <div class="card card-green">
                        <div class="card-title" style="color: var(--emerald);">🎁 CƠ CHẾ ĐIỂM THƯỞNG & ĐIỂM PHẠT</div>
                        <ul>
                            <li><strong class="green-text">CỘNG ĐIỂM THƯỞNG (+5 ĐIỂM):</strong><br>
                                • Hoàn thành vượt tiến độ nhiệm vụ trọng điểm.<br>
                                • Có sáng kiến, cải tiến quy trình nâng cao hiệu suất.<br>
                                • Quản lý đề xuất và biểu dương trực tiếp trên hệ thống.
                            </li>
                            <li><strong style="color: var(--rose);">ĐIỂM TRỪ KỶ LUẬT (Minh bạch):</strong><br>
                                • Chỉ áp dụng cho vi phạm nội quy, đi trễ về sớm không lý do.<br>
                                • Trễ hạn không có giải trình lý do khách quan.
                            </li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Thông báo tin vui: Ai cũng có sẵn 100 điểm trong tay đầu tháng, và có cơ hội nhận thêm +5 điểm thưởng nếu làm tốt.
                </aside>
            </section>

            <!-- SLIDE 11: XẾP LOẠI & THU NHẬP (A*) -->
            <section data-transition="slide">
                <span class="badge-cat badge-gold">QUYỀN LỢI THU NHẬP</span>
                <h2>Xếp Loại Thi Đua: Cơ Hội Bứt Phá Thu Nhập Cùng A*</h2>
                <div class="grid-5">
                    <div class="card card-red" style="text-align: center;">
                        <span class="icon-large">🔴</span>
                        <div class="card-title" style="justify-content: center; color: var(--rose);">HẠNG D</div>
                        <div style="font-weight: 700; font-size: 0.8em; color: #fff;">&lt; 71 ĐIỂM</div>
                        <p style="font-size: 0.65em; margin-top: 8px;">Chưa đạt yêu cầu.<br>Được đồng hành đào tạo lại.</p>
                    </div>
                    <div class="card" style="text-align: center;">
                        <span class="icon-large">🟠</span>
                        <div class="card-title" style="justify-content: center; color: #fb923c;">HẠNG C</div>
                        <div style="font-weight: 700; font-size: 0.8em; color: #fff;">72 - 81 ĐIỂM</div>
                        <p style="font-size: 0.7em; margin-top: 8px; color: var(--gold-accent);"><strong>80% LƯƠNG KPI</strong></p>
                    </div>
                    <div class="card" style="text-align: center;">
                        <span class="icon-large">🟡</span>
                        <div class="card-title" style="justify-content: center; color: #facc15;">HẠNG B</div>
                        <div style="font-weight: 700; font-size: 0.8em; color: #fff;">82 - 91 ĐIỂM</div>
                        <p style="font-size: 0.7em; margin-top: 8px; color: var(--gold-accent);"><strong>90% LƯƠNG KPI</strong></p>
                    </div>
                    <div class="card card-green" style="text-align: center;">
                        <span class="icon-large">🟢</span>
                        <div class="card-title" style="justify-content: center; color: var(--emerald);">HẠNG A</div>
                        <div style="font-weight: 700; font-size: 0.8em; color: #fff;">92 - 100 ĐIỂM</div>
                        <p style="font-size: 0.7em; margin-top: 8px; color: var(--emerald);"><strong>100% LƯƠNG KPI</strong></p>
                    </div>
                    <div class="card card-gold" style="text-align: center; border-width: 2px;">
                        <span class="icon-large">⭐</span>
                        <div class="card-title" style="justify-content: center; color: var(--gold-accent);">HẠNG A*</div>
                        <div style="font-weight: 700; font-size: 0.8em; color: #fff;">&gt; 100 ĐIỂM</div>
                        <p style="font-size: 0.75em; margin-top: 8px; color: var(--gold-accent);"><strong>110% - 120% LƯƠNG!</strong></p>
                    </div>
                </div>
                <div class="banner-bar" style="background: rgba(245, 158, 11, 0.2); border: 1px solid var(--gold-accent);">
                    💰 Cam kết từ DMT Group: <strong>Công ty sẵn sàng chi trả thu nhập vượt trội cho những ai cống hiến vượt trội!</strong>
                </div>
                <aside class="notes">
                    Nhấn mạnh con số 110% - 120% LƯƠNG cho hạng A*. Cơ hội tăng thu nhập nằm trong tay mỗi người, công ty sẵn sàng chi trả xứng đáng cho ai nỗ lực vượt trội!
                </aside>
            </section>

            <!-- SLIDE 12: AI RÀ SOÁT JD -->
            <section data-transition="slide">
                <span class="badge-cat">CÔNG NGHỆ BẢO VỆ NHÂN VIÊN</span>
                <h2>Trợ Lý AI & Bản Mô Tả Công Việc (JD): Bảo Vệ Chuyên Môn</h2>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title" style="color: var(--royal-light);">📋 BẢN JD — TẤM KHIÊN BẢO VỆ CHUYÊN MÔN</div>
                        <ul>
                            <li><strong>Định rõ chức trách:</strong> Nhân viên biết rõ phạm vi công việc và quyền hạn chuyên môn của mình.</li>
                            <li><strong>Chấm dứt 'ôm đồm':</strong> Tránh tình trạng bị giao những việc không tên vượt ngoài chuyên môn.</li>
                            <li><strong>Giúp Trưởng ban giao việc chính xác:</strong> Đảm bảo nguyên tắc 'Đúng người — Đúng việc'.</li>
                            <li><strong>Định hướng thăng tiến:</strong> Nhìn vào JD để biết mình cần phát triển kỹ năng gì tiếp theo.</li>
                        </ul>
                    </div>
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--emerald);">🤖 AI — NGƯỜI CỐ VẤN THÔNG MINH</div>
                        <ul>
                            <li>✨ <strong>Nhận diện ngữ nghĩa thông minh:</strong> AI hiểu tính chất công việc thực tế, không bắt bẻ câu chữ máy móc.</li>
                            <li>⚠️ <strong>Trợ lý cảnh báo:</strong> Nếu phát hiện nhân sự kỹ thuật phải làm quá nhiều việc sự vụ hành chính ngoài JD, AI sẽ báo động cho Quản lý.</li>
                            <li>🛡️ <strong>Mục đích bảo vệ:</strong> Giúp Quản lý điều chỉnh lại công việc cho nhân viên, tránh lãng phí năng lực chuyên môn.</li>
                            <li>❌ <em>AI là công cụ bảo vệ bạn làm đúng nghề, đúng nghiệp!</em></li>
                        </ul>
                    </div>
                </div>
                <aside class="notes">
                    Giải tỏa hoàn toàn nỗi sợ AI soi mói. Khẳng định AI và JD là để bảo vệ nhân viên khỏi bị ôm đồm việc không tên, giúp sếp giao đúng người đúng việc.
                </aside>
            </section>

            <!-- SLIDE 13: LỘ TRÌNH ĐỒNG HÀNH -->
            <section data-transition="slide">
                <span class="badge-cat badge-green">LỘ TRÌNH TRIỂN KHAI</span>
                <h2>Chạy Thử Nghiệm Quý 4 — Hoàn Toàn Không Áp Lực</h2>
                <div class="grid-2">
                    <div class="card card-highlight">
                        <div class="card-title" style="color: var(--royal-light);">🧪 GIAI ĐOẠN 1: THỬ NGHIỆM (QUÝ IV/2026)</div>
                        <ul>
                            <li>Chạy thử nghiệm Pilot để toàn thể anh chị em làm quen hệ thống.</li>
                            <li>Tổ chức đào tạo 'Cầm tay chỉ việc' tận nơi cho từng phòng ban.</li>
                            <li><strong class="green-text">TUYỆT ĐỐI KHÔNG ÁP DỤNG TRỪ ĐIỂM / TRỪ LƯƠNG</strong> trong thời gian làm quen!</li>
                            <li>Thu thập 100% phản hồi để tinh chỉnh phần mềm theo ý kiến người dùng.</li>
                        </ul>
                    </div>
                    <div class="card card-green">
                        <div class="card-title" style="color: var(--emerald);">🚀 GIAI ĐOẠN 2: CHÍNH THỨC</div>
                        <ul>
                            <li>Vận hành chính thức khi mọi người đã hoàn toàn thành thạo và thoải mái.</li>
                            <li>Dừng hoàn toàn việc làm báo cáo giấy và file Word/Excel.</li>
                            <li>Áp dụng cơ chế Thưởng A* (110% - 120% lương).</li>
                            <li>Môi trường làm việc số hóa, hiện đại, minh bạch và chuyên nghiệp.</li>
                        </ul>
                    </div>
                </div>
                <div class="banner-bar">
                    🤝 CAM KẾT VÀNG TỪ BAN HCNS: <strong>"Đồng hành 24/7 bên cạnh anh chị em — Không ai bị bỏ lại phía sau!"</strong>
                </div>
                <aside class="notes">
                    Đưa ra cam kết vàng: Giai đoạn thử nghiệm Quý IV là để làm quen, hoàn toàn KHÔNG áp dụng xử phạt hay cắt giảm tiền lương của bất kỳ ai. Tổ dự án sẽ cầm tay chỉ việc.
                </aside>
            </section>

            <!-- SLIDE 14: LỜI KẾT & Q&A -->
            <section data-transition="zoom">
                <h1 style="color: var(--gold-accent); margin-bottom: 22px;">CẢM ƠN CÁC ANH CHỊ TRƯỞNG BAN<br>& TOÀN THỂ ANH CHỊ EM!</h1>
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid var(--navy-border); border-radius: 20px; padding: 30px; max-width: 850px; margin: 0 auto 25px auto;">
                    <p style="font-size: 1.1em; font-style: italic; color: #ffffff; line-height: 1.6; margin: 0;">
                        “Công nghệ không sinh ra để kiểm soát con người.<br>
                        Công nghệ sinh ra để <span style="color: var(--royal-light); font-weight: 700;">giải phóng sức lao động</span> & <span style="color: var(--gold-accent); font-weight: 700;">tôn vinh giá trị</span> của mỗi chúng ta!”
                    </p>
                </div>
                <div class="card card-highlight" style="display: inline-block; padding: 16px 36px;">
                    <span style="font-size: 1.05em; font-weight: 700; color: #ffffff;">💬 PHẦN TRAO ĐỔI & GIẢI ĐÁP THẮC MẮC (Q&A)</span>
                    <p style="font-size: 0.78em; margin: 4px 0 0 0; color: var(--text-muted);">Ban HCNS sẵn sàng lắng nghe & giải đáp mọi câu hỏi từ các anh chị em!</p>
                </div>
                <aside class="notes">
                    Cảm ơn toàn thể hội trường, mở phần Q&A và giải đáp các câu hỏi thắc mắc. Sẵn sàng sử dụng bộ 6 câu hỏi FAQ trong tài liệu Word để đối đáp khéo léo và thuyết phục.
                </aside>
            </section>

        </div>
    </div>

    <!-- Reveal.js core & Plugins -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/notes/notes.min.js"></script>
    <script>
        Reveal.initialize({
            controls: true,
            progress: true,
            center: true,
            hash: true,
            transition: 'slide',
            plugins: [ RevealNotes ]
        });
    </script>
</body>
</html>
"""

with open("Ban_Thuyet_Trinh_Online.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated Ban_Thuyet_Trinh_Online.html successfully with comparison slide")
