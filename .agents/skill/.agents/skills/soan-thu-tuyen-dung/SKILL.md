---
name: soan-thu-tuyen-dung
description: >
  Soạn thảo 6 loại email tuyển dụng cá nhân hóa (mời PV, nhắc xác nhận, offer,
  từ chối, phê duyệt nội bộ, onboarding) đầy đủ thông tin, đúng SLA và tuân thủ
  R3.1/R3.2/R3.3 — mỗi email đọc như do con người viết, không cứng nhắc.
  Kích hoạt khi user đề cập 'viết email tuyển dụng', 'thư mời phỏng vấn', 'email offer';
  KHÔNG dùng để viết content đăng mạng xã hội (→ viet-content-tuyen-dung).
---

# SKILL: Soạn Thư Tuyển Dụng

## 6 Loại Email

### Email 1: Mời Phỏng Vấn
**Thông tin bắt buộc:** Họ tên UV | Vị trí | Ngày+Giờ+Địa điểm PV | Người PV | {{SDT_HR}} | Deadline xác nhận
**Không được viết:** Điểm sàng lọc, lý do được chọn (R3.3)
**Template:** `templates/email-moi-phong-van.md`

### Email 2: Nhắc Xác Nhận
**Khi dùng:** Trước PV 1 ngày, UV chưa phản hồi
**Tone:** Nhẹ nhàng, không gây áp lực
**Template:** `templates/email-nhac-xac-nhan.md`

### Email 3: Trúng Tuyển / Offer
**Thông tin bắt buộc:** Họ tên UV | Vị trí | Lương cứng (VNĐ/tháng) | Hoa hồng/KPI | Phúc lợi (từ K3) | Ngày bắt đầu | Deadline xác nhận (3 ngày làm việc) | {{SDT_HR}}

**Quy tắc đặc biệt (R2.1/R2.2):**
- Lương ghi trong email = Lương đề xuất trong phiếu PV (đã qua kiểm tra khung)
- Nếu vượt khung → gắn cờ, chờ {{TEN_CEO}} duyệt

**Template:** `templates/email-trung-tuyen-offer.md`

### Email 4: Cảm Ơn / Từ Chối
**Quy tắc (R3.3):** KHÔNG nêu điểm số | KHÔNG nêu lý do cụ thể | Để ngỏ cơ hội tương lai
**Tone:** Ấm áp, tôn trọng, không lạnh lùng
**Template:** `templates/email-cam-on-fail.md`

### Email 5: Phê Duyệt Nội Bộ
**Gửi cho:** Trưởng BP + {{TEN_TRUONG_PHONG_HCNS}}
**Nội dung:** Tên UV | Vị trí | Điểm PV | Lương đề xuất | Ngày onboard dự kiến
**Template:** `templates/email-phe-duyet-tuyen-dung.md`

### Email 6: Hướng Dẫn Onboarding
**Khi dùng:** W6, trước ngày onboard {{SLA_EMAIL_ONBOARDING}} ngày làm việc
**Thông tin bắt buộc:** Tên UV | Ngày+Giờ đến (08:30) | Địa chỉ + tầng | Tên+SĐT người đón | Checklist giấy tờ | Lịch ngày đầu
**Template:** `templates/email-onboarding.md`

---

## Quy trình thực hiện

```
1. Xác định loại email
2. Mở template tương ứng
3. Thu thập đủ trường thông tin bắt buộc
4. Điền vào template — viết lại câu để tự nhiên
5. Kiểm tra checklist chất lượng
6. Xuất file theo R6 naming
```

---

## Checklist chất lượng (mọi loại email)

- [ ] Dùng họ tên đầy đủ UV
- [ ] Đề cập vị trí ứng tuyển cụ thể
- [ ] Không có thông tin sai lệch (lương, ngày giờ)
- [ ] Không tiết lộ điểm số (R3.3)
- [ ] Ngôn ngữ trang trọng, có lời cảm ơn (R3.2)
- [ ] Có CTA rõ ràng
- [ ] Có thông tin liên lạc {{SDT_HR}}

## Templates
- `templates/email-moi-phong-van.md`
- `templates/email-nhac-xac-nhan.md`
- `templates/email-trung-tuyen-offer.md`
- `templates/email-cam-on-fail.md`
- `templates/email-phe-duyet-tuyen-dung.md`
- `templates/email-onboarding.md`

## Registry Block

```
### soan-thu-tuyen-dung
Soạn 6 loại email tuyển dụng cá nhân hóa, đúng SLA và R3.
💡 **Prompt Mẫu:** "Viết email mời phỏng vấn cho [Tên UV], PV sáng T2 lúc 9h."
```
