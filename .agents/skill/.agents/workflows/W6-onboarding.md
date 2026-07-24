# W6 — ONBOARDING
# Input: Offer đã xác nhận + CV UV + JD vị trí
# Output: Bộ hồ sơ pháp lý cá nhân trong thư mục riêng + Email onboarding
# Trigger: Ứng viên xác nhận Offer Letter (reply email "Tôi đồng ý")

---

## IPO Summary

```
INPUT:
  - W5_[DATE]_OL_[TenUV]_FINAL.md     (Offer đã xác nhận)
  - CV / snapshot CSV của UV
  - thu-vien/jd/[MaViTri]/JD_*.docx
  - K3-bang-luong-phuc-loi.md
  - K1-company-profile.md (địa chỉ, người đón)

PROCESS:
  1. Kiểm tra R5.1 — Offer đã xác nhận?
  2. Tạo bộ hồ sơ pháp lý (skill: tao-ho-so-nhan-su)
  3. Gửi email onboarding (skill: soan-thu-tuyen-dung)
  4. Gọi W0-Process D — cập nhật kho sau đợt

OUTPUT:
  du-an/[Đợt]/[TenUV]/           ← Thư mục cá nhân
  ├── HDTV_[TenUV]_FINAL.docx
  ├── NDA_[TenUV]_FINAL.docx
  ├── NS_[TenUV]_v1.xlsx
  └── EM_Onboarding-[TenUV]_v1.md
```

---

## Bước 1 — Kiểm tra điều kiện (R5.1)

Xác nhận: Offer Letter đã được UV reply xác nhận?
- Nếu chưa → dừng: *"⚠️ Cần UV xác nhận offer trước khi tạo hồ sơ (R5.1)."*
- Nếu đã xác nhận → tiếp tục

---

## Bước 2 — Tạo bộ hồ sơ pháp lý

Với **từng UV trúng tuyển đã xác nhận**:

1. Tạo thư mục `du-an/[Đợt]/[TenUV]/`
2. Gọi skill `tao-ho-so-nhan-su`:
   - HĐTV → `YYYYMMDD_HDTV_[TenUV]_FINAL.docx`
   - NDA → `YYYYMMDD_NDA_[TenUV]_FINAL.docx`
   - Phiếu NS → `YYYYMMDD_NS_[TenUV]_v1.xlsx`
3. Tất cả lưu vào `du-an/[Đợt]/[TenUV]/`

---

## Bước 3 — Gửi email Onboarding (R5.3)

Gửi trước ngày bắt đầu **{{SLA_EMAIL_ONBOARDING}} ngày làm việc**:

→ Gọi skill `soan-thu-tuyen-dung` (Email 6: Onboarding)

Output: `du-an/[Đợt]/[TenUV]/YYYYMMDD_EM_Onboarding-[TenUV]_v1.md`

---

## Bước 4 — Gọi W0-Process D

Sau khi tất cả UV trong đợt đã xử lý W6 xong:
→ Gọi `W0-Process D` để cập nhật TrangThai trong `_MASTER.csv`

---

## Checklist W6

- [ ] R5.1: Có xác nhận offer trước khi tạo hồ sơ
- [ ] Mỗi UV trúng tuyển có thư mục riêng `[TenUV]/`
- [ ] HĐTV và NDA cùng ngày lập (R5.2)
- [ ] Email onboarding gửi trước {{SLA_EMAIL_ONBOARDING}} ngày làm việc (R5.3)
- [ ] Lương TV = Lương offer × {{TI_LE_LUONG_THU_VIEC}} (R5.4)
- [ ] W0-Process D đã được gọi để đóng dự án

*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*
