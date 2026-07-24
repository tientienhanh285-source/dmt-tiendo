---
name: viet-jd-mtcv
description: >
  Viết Job Description chuẩn 5 mục và MTCV định lượng cho các vị trí tuyển dụng.
  Kích hoạt khi user đề cập 'viết JD', 'mô tả công việc', 'job description';
  trong tình huống có vị trí cần tuyển và chưa có tài liệu mô tả.
  KHÔNG dùng để viết content đăng tuyển (→ viet-content-tuyen-dung).
---

# Skill: Viết JD & MTCV

## Input

- **Vị trí cần tuyển** (từ Nhóm D trong K0-tu-dien-he-thong.md)
- **`K4-tieu-chi-tuyen-dung.md`** — Tiêu chí tuyển dụng vị trí đó
- **`K3-bang-luong-phuc-loi.md`** — Khung lương (để điền range thay vì số cứng)
- **`K5-gia-tri-cot-loi.md`** — Văn hóa doanh nghiệp (Mục 4)

---

## Cấu trúc JD chuẩn 5 mục

### Mục 1 — Mô tả vị trí & Mục tiêu
```
Tên vị trí: [Tên đầy đủ từ K0-tu-dien-he-thong.md Nhóm D]
Phòng ban / Bộ phận: [Phòng ban từ K2]
Báo cáo cho: [Chức danh quản lý trực tiếp]
Địa điểm làm việc: [Từ K1]

Mục tiêu vị trí: [2-3 câu mô tả vị trí này tồn tại để làm gì]
```

### Mục 2 — Nhiệm vụ chính (MTCV)

> Phải **định lượng** — không viết chung chung.
> VD ✅: "Chăm sóc tối thiểu 30 khách hàng/tuần, đạt tỷ lệ chuyển đổi ≥ 15%"
> VD ❌: "Thực hiện công việc bán hàng theo yêu cầu"

- **Nhiệm vụ 1:** [Động từ hành động] + [Đối tượng] + [Chỉ tiêu đo được]
- **Nhiệm vụ 2:** [...]
- **Nhiệm vụ 3:** [...]
- **Nhiệm vụ 4:** [...]
- **Nhiệm vụ 5:** [...]

### Mục 3 — Yêu cầu ứng viên

Lấy từ `K4-tieu-chi-tuyen-dung.md` cho vị trí đó:

- **Kinh nghiệm:** [Từ K4 — mức tối thiểu + mức ưu tiên]
- **Học vấn:** [Từ K4]
- **Kỹ năng chuyên môn:** [Danh sách từ K4]
- **Kỹ năng mềm:** [Từ K4]
- **Ngoại ngữ / Chứng chỉ:** [Từ K4 nếu có]
- **Điều kiện khác:** [Từ K4 nếu có]

### Mục 4 — Quyền lợi

Lấy từ `K3-bang-luong-phuc-loi.md`:
- **Thu nhập:** [Range từ K3 — KHÔNG ghi số cứng] + Hoa hồng/Thưởng KPI (nếu có)
- **Bảo hiểm:** Đóng đầy đủ theo quy định pháp luật
- **Phụ cấp:** {{PC_AN_TRUA}} | {{PC_GUI_XE}} | {{PC_DIEN_THOAI}}
- **Phép năm:** {{NGAY_PHEP_NAM}} ngày/năm
- **Thưởng:** {{LUONG_THANG_13}}
- **Môi trường:** [Lấy từ K5 và K1 — USP]

### Mục 5 — Thông tin ứng tuyển

```
Cách ứng tuyển: Gửi CV về {{EMAIL_HR}}
Tiêu đề email: "[Tên vị trí] — [Họ tên UV]"
Hạn nộp: [Điền theo timeline dự án]
Liên hệ: {{TEN_TRUONG_PHONG_HCNS}} | {{SDT_HR}}
```

---

## Checklist chất lượng

- [ ] Tên vị trí khớp với K0-tu-dien-he-thong.md Nhóm D
- [ ] MTCV có ít nhất 5 nhiệm vụ và có chỉ tiêu định lượng
- [ ] Yêu cầu lấy đúng từ K4 (không tự thêm)
- [ ] Lương ghi dạng range (không ghi số cứng)
- [ ] Có đủ 5 mục

## Templates
- `templates/jd-TEMPLATE.docx`

## Registry Block

```
### viet-jd-mtcv
Viết JD chuẩn 5 mục và MTCV định lượng cho mọi vị trí.
💡 **Prompt Mẫu:** "Viết JD cho vị trí Sales Showroom, dựa theo K4."
```
