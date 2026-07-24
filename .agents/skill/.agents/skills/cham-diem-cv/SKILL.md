---

name: cham-diem-cv

description: >

  Chấm điểm CV theo 5 tiêu chí (100đ), phân loại Pass+/Pass/Fail, xuất bảng xếp hạng.

  Nhận data đã được Workflow chuẩn bị — tự phân tích bối cảnh và chọn phương án xử lý.

---



# Skill: Chấm Điểm CV



## Input nhận từ Workflow



> Workflow (W3) có trách nhiệm load và truyền vào. Skill không tự load lại.



| Data | Mô tả |
|------|-------|
| `snapshot_data` | Danh sách UV đã qua filter R1.1/R1.4 (hồ sơ đủ điều kiện chấm) |
| `loai_data` | DS UV bị loại kèm lý do (thiếu liên lạc / thiếu KN) — để ghi vào output |
| `tieu_chi` | Tiêu chí tuyển dụng của vị trí (từ K4 — W3 đã extract) |
| `tu_khoa_bonus` | Danh sách từ khóa ngành ưu tiên (từ K0-tu-dien-he-thong.md Nhóm F — W3 đã extract) |
| `nguong` | `{pass: N, pass_plus: N}` từ K0-tu-dien-he-thong.md Nhóm G |
| `jd_text` | Nội dung JD (nếu có — W3 truyền nếu tìm được) |



---



## Phân tích bối cảnh



| Tín hiệu trong input | Phương án |
|----------------------|----------|
| `jd_text` có đầy đủ | → Chấm TC3 dựa trên JD chi tiết |
| `jd_text` null/rỗng | → Chấm TC3 dựa trên `tieu_chi.ky_nang`; cảnh báo "Kết quả TC3 ước tính" |
| `snapshot_data` ≤ 5 UV | → Nhận xét dài, phân tích sâu (≤100 từ/UV) |
| `snapshot_data` ≥ 10 UV | → Nhận xét ngắn, ưu tiên tốc độ (≤50 từ/UV) |
| `nguong` khác giá trị K0-tu-dien-he-thong.md | → Dùng giá trị được truyền vào, thêm ghi chú "Ngưỡng tùy chỉnh" |



---



## Xử lý



### Ghi nhận hồ sơ loại (không chấm điểm)

Với mỗi dòng trong `loai_data`: ghi nguyên vào Sheet "Đánh giá" với cột Phân loại = lý do loại.



### Chấm 5 tiêu chí (với hồ sơ trong `snapshot_data`)



**TC1 — Kinh nghiệm (30đ)**

| 25–30 | ≥3 năm ngành liên quan trực tiếp |
| 18–24 | 1–2 năm ngành liên quan / ≥3 năm ngành tương đồng |
| 10–17 | <1 năm ngành liên quan |
| 0–9   | Chưa có KN thực tế |



*Bonus từ `tu_khoa_bonus`: tìm thấy từ khóa → TC1 × 1.1, tối đa 30đ. Ghi từ khóa vào cột "Bonus".*



**TC2 — Học vấn (15đ)**

| 13–15 | ĐH đúng chuyên ngành trong `tieu_chi.hoc_van` |
| 9–12  | ĐH liên quan / CĐ đúng chuyên ngành |
| 5–8   | TC/CĐ bất kỳ |
| 0–4   | Chưa tốt nghiệp / không rõ |



**TC3 — Kỹ năng chuyên môn (25đ)**

So khớp với `tieu_chi.ky_nang` (hoặc `jd_text` nếu có):

| 20–25 | ≥80% khớp | 13–19 | 50–79% | 6–12 | 30–49% | 0–5 | <30% |



**TC4 — Mục tiêu nghề nghiệp (15đ)**

| 13–15 | Gắn rõ với vị trí, có định hướng dài hạn |
| 8–12  | Chung chung, không mâu thuẫn |
| 3–7   | Không liên quan / mơ hồ |
| 0–2   | Không có |



**TC5 — Hình thức CV (15đ)**

| 13–15 | Rõ ràng, chuyên nghiệp, không lỗi chính tả |
| 8–12  | Đủ thông tin, trình bày bình thường |
| 4–7   | Thiếu thông tin / nhiều lỗi |
| 0–3   | Rất sơ sài |



### Phân loại & nhận xét

```

Pass+  : Tổng ≥ nguong.pass_plus

Pass   : nguong.pass ≤ Tổng < nguong.pass_plus

Fail   : Tổng < nguong.pass

```

Nhận xét: "[Điểm mạnh nổi bật]. [Rủi ro / câu hỏi nên hỏi khi PV]."

Độ dài: tùy phương án đã chọn ở phần Phân tích bối cảnh.



---



## Tiêu chuẩn chất lượng đầu ra



- [ ] **Đầy đủ:** Mọi UV trong cả `snapshot_data` lẫn `loai_data` đều có dòng trong output

- [ ] **Nhất quán:** Cùng vị trí → cùng thang điểm TC1–TC5

- [ ] **Không bịa:** TC3 chỉ chấm khi có `tieu_chi.ky_nang` hoặc `jd_text`

- [ ] **Bonus ghi rõ nguồn:** Cột "Bonus" ghi từ khóa cụ thể tìm thấy

- [ ] **Tổng chính xác:** TC1+TC2+TC3+TC4+TC5 (kiểm tra phép cộng)

- [ ] **Nhận xét không lặp điểm số**

- [ ] **Sắp xếp:** Sheet "Đánh giá" — hồ sơ loại xuống cuối, hồ sơ chấm xếp theo điểm giảm dần

- [ ] **Cảnh báo hiển thị:** Nếu dùng ngưỡng tùy chỉnh hoặc thiếu JD → ghi chú ở header sheet

