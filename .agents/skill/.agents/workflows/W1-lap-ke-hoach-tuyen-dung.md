---
description: Phân tích gap nhân sự, tính ngân sách, tạo kế hoạch tuyển dụng và JD. Kích hoạt khi user yêu cầu lập kế hoạch tuyển dụng theo quý/đợt/nhu cầu phát sinh.
---

# W1 — LẬP KẾ HOẠCH TUYỂN DỤNG

> **Trigger:** User yêu cầu lập kế hoạch tuyển dụng

---

## LOAD (Workflow tải trước khi xử lý)

```
K2  → Đọc toàn bộ cơ cấu tổ chức + headcount hiện tại
K3  → Đọc bảng khung lương theo mã vị trí
K6  → Đọc: §1 (hình thức tuyển), §2 (SLA deadline), §3 (thẩm quyền)
K0-tu-dien-he-thong.md Nhóm G → {SLA_NOD_DIRECTOR, SLA_NOD_LEADER, SLA_NOD_STAFF}
K0-tu-dien-he-thong.md Nhóm D → Bảng mã vị trí
R2.1, R2.2, R2.3 → Quy tắc lương + thẩm quyền
```

**Từ user:**
- Danh sách vị trí + số lượng + ngày cần người
- Ngân sách được duyệt *(nếu có)*
- Kế hoạch kinh doanh Q/Năm *(nếu có)*

---

## PROCESS

**B0.** Gọi **skill `khoi-tao-ho-so-tuyen-dung`**
→ Pass: `{ten_dot, ngay_tao, ds_ma_vitri}`

**B1.** Phân tích gap nhân sự từ K2 + yêu cầu user
→ Xuất: `gap_analysis` (vị trí trống/quá tải/thay thế + phân loại hình thức)

**B2.** Gọi **skill `lap-ke-hoach-td`**
→ Pass:
```
ds_vi_tri     = Danh sách từ B1
gap_analysis  = Kết quả B1
khung_luong   = Bảng từ K3
sla_config    = {director: N, leader: N, staff: N} từ K0-tu-dien-he-thong.md G
hinh_thuc_policy = Nội dung K6 §1 đã extract
nguoi_duyet   = Mapping từ R2.3 + K6 §3
budget_duoc_duyet = Từ user (nullable)
ke_hoach_kd   = Từ user (nullable)
```
→ Output: `W1_KH_*.xlsx` + `W1_DN_*.xlsx`

**B3.** Với từng vị trí: Gọi **skill `viet-jd-mtcv`**
→ Pass:
```
ma_vi_tri     = Mã từ K0-tu-dien-he-thong.md Nhóm D
tieu_chi      = Dữ liệu từ K4 của vị trí đó
khung_luong   = Range từ K3 (không ghi số cứng)
phuc_loi      = Từ K3 §3 (phụ cấp, phép, v.v.)
usp_cty       = Từ K1 (USP công ty)
thong_tin_ung_tuyen = {email_hr, ten_hr, sdt_hr} từ K0-tu-dien-he-thong.md Nhóm B
```
→ Output: `JD_[MaViTri]_FINAL.docx` → lưu vào `thu-vien/jd/[MaViTri]/`

---

## FALLBACK

- Thiếu K4 cho vị trí → skill viet-jd-mtcv sẽ cảnh báo "Vị trí mới — cần bổ sung K4"
- Thiếu ngân sách user → skill lap-ke-hoach-td tự tính từ K3 + ghi chú
- Lương vượt khung → skill xuất cờ cảnh báo → W1 hiển thị trong Sheet "Cảnh báo"

---

## OUTPUT

```
du-an/[YYYYMM]-[TenDot]/
  W1_[DATE]_KH_TuyenDung-[Dot]_v1.xlsx
  W1_[DATE]_DN_[MaViTri]_v1.xlsx  (1 file/vị trí)

thu-vien/jd/[MaViTri]/
  JD_[MaViTri]_FINAL.docx
```

*Cập nhật lần cuối: {{NGAY_TAO}} | v1*
