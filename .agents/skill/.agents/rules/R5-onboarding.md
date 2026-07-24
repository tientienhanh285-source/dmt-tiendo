# RULE R5 — ONBOARDING (Onboarding Rules)
# Nguồn biến: K0-tu-dien-he-thong.md — Nhóm B, C, G
# Áp dụng trong: W6 | Skill: tao-ho-so-nhan-su, soan-thu-tuyen-dung

---

## R5.1 — Điều kiện kích hoạt W6

Workflow Onboarding **chỉ được kích hoạt** khi trạng thái Offer Letter của ứng viên được xác nhận là **"Đã ký / Accepted"**.

Nếu chưa có xác nhận → AI thông báo: *"⚠️ Chưa đủ điều kiện kích hoạt W6 — Cần ứng viên xác nhận Offer trước."*

---

## R5.2 — Gửi hồ sơ pháp lý trước ngày nhận việc

HĐTV và NDA phải được gửi cho ứng viên **ĐỌC TRƯỚC ít nhất 1 ngày làm việc** trước ngày onboard.

---

## R5.3 — Gửi email onboarding trước {{SLA_EMAIL_ONBOARDING}} ngày

Email hướng dẫn onboarding phải gửi **trước ngày bắt đầu tối thiểu {{SLA_EMAIL_ONBOARDING}} ngày làm việc**.

---

## R5.4 — Nhất quán thông tin hồ sơ

Mọi thông tin trong bộ hồ sơ (HĐTV, NDA, email onboarding) phải **đồng nhất** với email offer đã xác nhận:
- Lương thử việc = Lương offer × {{TI_LE_LUONG_THU_VIEC}} (không điền khác)
- Chức danh = Chức danh trong JD và Offer
- Ngày onboard = Ngày đã xác nhận trong email

Nếu phát hiện mâu thuẫn → dừng xử lý và cảnh báo người dùng.

---

## R5.5 — Số thứ tự Hợp đồng

Format số HĐTV: `{{FORMAT_SO_HD}}`

Ví dụ nếu format là `[STT]/[Năm]/HĐTV-[MÃ]`: `001/2026/HĐTV-HS`

STT tăng tuần tự theo thứ tự ký trong năm. AI phải hỏi số HĐ tiếp theo nếu không có thông tin hoặc tự giả định và cảnh báo.

*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*
