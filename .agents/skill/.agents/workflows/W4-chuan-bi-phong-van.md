---
description: Chuẩn bị tài liệu phỏng vấn: email mời, câu hỏi STAR, phiếu đánh giá. Kích hoạt khi user yêu cầu chuẩn bị tài liệu trước đợt phỏng vấn.
---

# W4 — CHUẨN BỊ PHỎNG VẤN

> **Trigger:** User yêu cầu chuẩn bị tài liệu trước đợt phỏng vấn

---

## LOAD (Workflow tải trước khi xử lý)

```
W3_..._SL_*.xlsx    → Sheet "Lịch PV": DS UV Pass + slot + điểm
W3_..._LP_*.xlsx    → Lịch phỏng vấn chi tiết
CV từng UV          → thu-vien/cv-nguon/[MaViTri]/[TenUV].md
JD vị trí           → thu-vien/jd/[MaViTri]/JD_*.docx
K3[ma_vi_tri]       → Khung lương (mid range) để điền đề xuất trong phiếu
K4[ma_vi_tri]       → 5 tiêu chí chuyên môn để tạo Phần A phiếu đánh giá
K5                  → Danh sách giá trị cốt lõi + hành vi đánh giá
K6 §4               → Thành phần người PV theo vòng
K0-tu-dien-he-thong.md Nhóm B      → {email_hr, ten_hr, sdt_hr, ten_phong_hcns}
R2.1, R2.2          → Giới hạn lương offer cho phiếu đánh giá
```

---

## PROCESS

**B1.** Gọi **skill `lap-lich-phong-van`** (Khả năng B — Câu hỏi STAR)
→ Pass:
```
ds_uv_pass      = DS UV Pass từ W3_SL Sheet "Lịch PV"
ds_cv_data      = {[TenUV]: nội dung .md} từ thu-vien/cv-nguon/
jd_text         = Nội dung JD từ thu-vien/jd/
core_values     = Danh sách từ K5
slot_config     = null  ← không cần xếp lịch (đã có từ W3)
thanh_phan_pv   = Mapping từ K6 §4
```
→ Output: `W4_[DATE]_CQ_[MaViTri]_v1.docx`

**B2.** Gọi **skill `danh-gia-phong-van`** (Khả năng A — Tạo phiếu)
→ Pass:
```
ds_uv          = DS UV từ Sheet "Lịch PV"
lich_pv        = Slot + người PV từ W4_LP
tieu_chi_a     = 5 tiêu chí từ K4[ma_vi_tri]
core_values    = Danh sách từ K5 (cho Phần B phiếu)
luong_tham_khao = Mid range từ K3[ma_vi_tri]
rules_luong    = {max_range: từ K3, canh_bao: R2.2}
```
→ Output: `W4_[DATE]_PV_[TenUV]_v1.xlsx` (1 file/UV)

**B3.** Gọi **skill `soan-thu-tuyen-dung`** (Email 1: Mời PV)
→ Pass:
```
loai_email = "moi_pv"
uv_info    = {ten, email, vi_tri, slot, nguoi_pv, dia_diem}
lien_lac   = {ten_hr, sdt_hr} từ K0-tu-dien-he-thong.md Nhóm B
deadline_xac_nhan = Trước PV 1 ngày
```
→ Output: `W5_[DATE]_EM_MoiPV-[TenUV]_v1.md`

---

## FALLBACK

- Không tìm thấy CV của UV → skill tạo câu hỏi chung theo JD (fallback Khả năng B)
- Chưa xác định người PV → phiếu ghi "⚠️ Cần xác nhận"; không block
- K4 không có tiêu chí cho vị trí → skill danh-gia-phong-van tạo phiếu với Phần A placeholder

---

## OUTPUT

```
du-an/[YYYYMM]-[TenDot]/
  W4_[DATE]_CQ_[MaViTri]_v1.docx      (câu hỏi STAR tất cả UV)
  W4_[DATE]_PV_[TenUV]_v1.xlsx        (phiếu đánh giá — 1 file/UV)
  W5_[DATE]_EM_MoiPV-[TenUV]_v1.md   (email mời — 1 file/UV)
```

*Cập nhật lần cuối: {{NGAY_TAO}} | v1*
