---

name: lap-ke-hoach-td

description: >

  Tính ngân sách, phân loại hình thức tuyển, tính SLA deadline và xuất bảng kế hoạch

  + đề nghị tuyển dụng. Nhận data đã được W1 chuẩn bị — tự phân tích bối cảnh.

---



# Skill: Lập Kế Hoạch Tuyển Dụng



## Input nhận từ Workflow



> W1 có trách nhiệm load K2, K3, K6, K0-tu-dien-he-thong.md và truyền vào. Skill không tự load lại.



| Data | Mô tả |
|------|-------|
| `ds_vi_tri` | Danh sách vị trí cần tuyển (tên, mã, SL, ngày cần người) |
| `gap_analysis` | Kết quả phân tích gap từ K2 (W1 đã làm ở bước trước) |
| `khung_luong` | Bảng khung lương theo mã vị trí (từ K3 — W1 đã extract) |
| `sla_config` | `{director: N, leader: N, staff: N}` từ K0-tu-dien-he-thong.md Nhóm G |
| `hinh_thuc_policy` | Quy định phân loại hình thức tuyển (từ K6 §1 — W1 đã extract) |
| `nguoi_duyet` | Thẩm quyền phê duyệt theo cấp (từ R2.3 + K6 §3 — W1 đã extract) |
| `budget_duoc_duyet` | Ngân sách được duyệt (nếu user cung cấp) — nullable |
| `ke_hoach_kd` | Dữ liệu kế hoạch kinh doanh (nếu user cung cấp) — nullable |



---



## Phân tích bối cảnh



| Tín hiệu trong input | Phương án |
|----------------------|----------|
| `budget_duoc_duyet` có giá trị | → Kiểm tra tổng ngân sách vs budget; cảnh báo nếu vượt |
| `budget_duoc_duyet` null | → Tính ngân sách từ `khung_luong`, ghi chú "Ngân sách chưa xác nhận" |
| `ke_hoach_kd` có giá trị | → Phân tích workload tăng thêm để justify tuyển mới |
| `ke_hoach_kd` null | → Dựa thuần vào `gap_analysis`; cảnh báo "KH dựa trên gap nhân sự" |
| Vị trí không có trong `khung_luong` | → Cảnh báo "Vị trí mới — cần bổ sung K3 + K4"; để ô lương trống |
| Có vị trí yêu cầu tuyển gấp (<SLA) | → Highlight đỏ dòng đó, đề xuất kênh đăng tuyển nhanh |



---



## Xử lý



**Với mỗi vị trí trong `ds_vi_tri`:**



```

1. Phân loại hình thức = đọc từ `hinh_thuc_policy` theo điều kiện vị trí

2. Lương gross = mức giữa của khung_luong[ma_vi_tri]

   - Nếu lương > Max Range → gắn cờ R2.2: cần nguoi_duyet.cao_nhat phê duyệt

3. Chi phí tuyển ước tính = lương tháng đầu + phí đăng JD (ước 0–2 triệu)

4. Deadline = Ngày cần người - sla_config[cap_bac]

   - Nếu deadline < hôm nay → "⚠️ Đã quá SLA — cần escalate"

5. Thẩm quyền = đọc từ nguoi_duyet theo hình thức + mức lương

```



**Tổng ngân sách** = Σ (lương × SL) + Σ chi phí tuyển



**Điền vào 2 file output:**

- `W1_[DATE]_KH_TuyenDung-[Dot]_v1.xlsx` (3 sheet: Tổng quan | Ngân sách | Cảnh báo)

- `W1_[DATE]_DN_[MaViTri]_v1.xlsx` (1 file/vị trí)



---



## Tiêu chuẩn chất lượng đầu ra



- [ ] Mỗi vị trí đã có hình thức tuyển dụng (không để trống)

- [ ] Lương gross trong khung — vượt khung phải có cờ cảnh báo + tên người duyệt

- [ ] SLA deadline tính đúng từ `sla_config` theo cấp bậc thực tế của vị trí

- [ ] Tổng ngân sách = đúng phép cộng các dòng (có thể verify bằng công thức)

- [ ] Sheet "Cảnh báo" có đủ: vượt ngân sách + vượt khung lương + quá SLA

- [ ] Vị trí mới (thiếu khung lương/tiêu chí) có cảnh báo rõ "Cần cập nhật K3/K4"

- [ ] Cột thẩm quyền không trống (ghi đúng tên/chức danh từ `nguoi_duyet`)

