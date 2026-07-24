---
description: Sàng lọc hồ sơ CV từ snapshot kho — chấm điểm và xếp lịch phỏng vấn. Kích hoạt khi có đủ CV sau deadline nộp hồ sơ.
---

# W3 — SÀNG LỌC HỒ SƠ

> **Trigger:** Có đủ CV trong kho sau deadline, cần sàng lọc

---

## LOAD (Workflow tải trước khi xử lý)

```
Snapshot CSV      → W3_[DATE]_SNAP_[MaViTri]_v1.csv (đã tạo bởi W0-Process C)
K4[ma_vi_tri]     → Tiêu chí tuyển dụng: kinh nghiệm tối thiểu + kỹ năng yêu cầu
K0-tu-dien-he-thong.md Nhóm F    → Từ khóa ưu tiên ngành cho vị trí
K0-tu-dien-he-thong.md Nhóm G    → {DIEM_PASS, DIEM_PASS_PLUS, SLOT config}
R1.1              → Ngưỡng loại: kinh nghiệm tối thiểu
R1.4              → Điều kiện loại: thiếu SĐT/email
JD (nếu có)       → thu-vien/jd/[MaViTri]/JD_*.docx
K6 §4             → Thành phần người phỏng vấn theo vòng
```

**Từ user:**
- Xác nhận khoảng thời gian xếp lịch (range ngày)
- Tên người phỏng vấn *(nếu đã biết)*

---

## PROCESS

**B1.** Đọc snapshot CSV → kiểm tra số lượng UV, thông báo:
*"Kho có [N] UV cho vị trí [Tên]. Gồm: [X] mới, [Y] tiềm năng từ đợt trước."*

**B2.** Áp R1.4 và R1.1 để tạo 2 danh sách:
```
loai_data    = DS UV bị loại + lý do cụ thể
snapshot_clean = DS UV đủ điều kiện chấm điểm
```

**B3.** Gọi **skill `cham-diem-cv`**
→ Pass:
```
snapshot_data  = snapshot_clean (từ B2)
loai_data      = loai_data (từ B2)
tieu_chi       = {ky_nang, hoc_van, kn_toi_thieu} từ K4[ma_vi_tri]
tu_khoa_bonus  = Danh sách từ K0-tu-dien-he-thong.md Nhóm F[ma_vi_tri]
nguong         = {pass: DIEM_PASS, pass_plus: DIEM_PASS_PLUS} từ K0-tu-dien-he-thong.md G
jd_text        = Nội dung JD (nullable — nếu tìm thấy trong thu-vien/jd/)
```
→ Output: Sheet "Đánh giá" trong `W3_[DATE]_SL_*.xlsx`

**B4.** Gọi **skill `lap-lich-phong-van`** (chỉ Khả năng A)
→ Pass:
```
ds_uv_pass      = DS UV Pass + điểm (từ B3 output)
slot_config     = {sang:[...], chieu:[...], max_ngay:4, tg_phut:N, nghi_phut:N} từ K0-tu-dien-he-thong.md G
nguong_pass_plus = DIEM_PASS_PLUS từ K0-tu-dien-he-thong.md G
range_ngay      = Từ user (nếu đã cung cấp)
thanh_phan_pv   = Mapping vòng → thành phần (từ K6 §4) — nullable
ds_cv_data      = null  ← không truyền, W3 chỉ cần lịch
core_values     = null  ← không truyền, W4 sẽ làm câu hỏi
```
→ Output: Sheet "Lịch PV" + `W4_[DATE]_LP_*.xlsx`

**B5.** Gọi **skill `soan-thu-tuyen-dung`** (Email mời PV)
→ Pass: Từng UV Pass + slot đã xếp + thông tin liên lạc từ K0-tu-dien-he-thong.md Nhóm B

---

## FALLBACK

- Snapshot rỗng (0 UV) → cảnh báo + đề xuất nhập CV mới qua W0-Process A
- Tất cả UV bị loại R1.1/R1.4 → dừng, không gọi skill cham-diem-cv, báo cáo lý do
- Chưa xác định người PV → skill gắn "⚠️ Cần xác nhận" (không block)

---

## OUTPUT

```
du-an/[YYYYMM]-[TenDot]/
  W3_[DATE]_SL_[MaViTri]-[Dot]_v1.xlsx
    → Sheet "Thông tin UV"   (từ snapshot)
    → Sheet "Đánh giá"       (skill cham-diem-cv)
    → Sheet "Lịch PV"        (skill lap-lich-phong-van)
  W4_[DATE]_LP_[MaViTri]-[Dot]_v1.xlsx
  W5_[DATE]_EM_MoiPV-[TenUV]_v1.md  (1 file/UV Pass)
```

*Cập nhật lần cuối: {{NGAY_TAO}} | v1*
