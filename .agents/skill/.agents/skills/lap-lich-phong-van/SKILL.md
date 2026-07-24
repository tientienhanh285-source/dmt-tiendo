---

name: lap-lich-phong-van

description: >

  Xếp lịch PV theo slot chuẩn VÀ/HOẶC tạo câu hỏi STAR cá nhân hóa — tùy bối cảnh.

  Nhận data đã được Workflow chuẩn bị. Tự phân tích tín hiệu để kích hoạt khả năng phù hợp.

---



# Skill: Lập Lịch Phỏng Vấn & Câu Hỏi STAR



## Input nhận từ Workflow



> W3 (lịch) hoặc W4 (câu hỏi + lịch) load và truyền vào. Skill không tự load lại.



| Data | Bắt buộc | Mô tả |
|------|:--------:|-------|
| `ds_uv_pass` | Có thể null | DS UV Pass + điểm (từ W3 chấm CV) |
| `slot_config` | Có thể null | `{sang:[slot1,slot2], chieu:[slot1,slot2], max_ngay:4, tg_phut:N, nghi_phut:N}` từ K0-tu-dien-he-thong.md G |
| `nguong_pass_plus` | Có thể null | Giá trị từ K0-tu-dien-he-thong.md Nhóm G |
| `ds_cv_data` | Có thể null | Nội dung CV từng UV (W4 truyền vào để tạo câu hỏi) |
| `jd_text` | Có thể null | Nội dung JD vị trí (W4 truyền vào) |
| `core_values` | Có thể null | Danh sách giá trị cốt lõi từ K5 (W4 truyền vào) |
| `thanh_phan_pv` | Có thể null | Thành phần người PV theo vòng (từ K6 §4 — W4 truyền vào) |
| `range_ngay` | Có thể null | Ngày bắt đầu/kết thúc xếp lịch (user cung cấp qua W) |



---



## Phân tích bối cảnh



| Tín hiệu trong input | Khả năng kích hoạt |
|----------------------|-------------------|
| `ds_uv_pass` có data + `slot_config` có data | → Khả năng A (xếp lịch) |
| `ds_cv_data` có data + `jd_text` có data + `core_values` có data | → Khả năng B (câu hỏi STAR) |
| Cả hai nhóm trên đều có | → A + B |
| `ds_cv_data` null nhưng cần câu hỏi | → Khả năng B fallback: câu hỏi chung theo `jd_text`; header ghi "Chưa cá nhân hóa" |
| `thanh_phan_pv` null | → Xếp lịch bình thường; cột Người PV ghi "⚠️ Cần xác nhận" |
| `ds_uv_pass` > 8 UV | → Đề xuất chia 2+ ngày; nếu `range_ngay` null thì hỏi user xác nhận |



---



## Khả năng A — Xếp lịch phỏng vấn



```

Logic phân bổ:

1. UV điểm ≥ nguong_pass_plus → ưu tiên slot sáng ngày đầu tiên trong range_ngay

2. UV còn lại → xếp theo điểm giảm dần

3. Mỗi slot: slot_config.tg_phut phút + slot_config.nghi_phut phút nghỉ giữa

4. Tối đa slot_config.max_ngay UV/ngày

5. Chỉ slot trong slot_config.sang + slot_config.chieu; chỉ Thứ 2–Thứ 6

```



## Khả năng B — Câu hỏi STAR cá nhân hóa



**Phần I — Chuyên môn (4–5 câu/UV):**

Format: *"Tôi thấy trong CV [tên UV] có [điểm X từ ds_cv_data]. Hãy kể tình huống khi [thách thức từ jd_text]..."*



Điều chỉnh theo bối cảnh:

- CV chi tiết → khai thác thành tích/con số cụ thể

- CV sơ sài → hỏi rộng về tiềm năng học hỏi

- Vị trí kỹ thuật → nghiêng về hard skill; Vị trí kinh doanh → cân bằng KN + kết quả



**Phần II — Core Values (3–4 câu từ `core_values`):**

Format: *"[Tên công ty] đề cao [value.ten]. Hãy kể tình huống bạn đã thể hiện điều này."*



---



## Tiêu chuẩn chất lượng đầu ra



**Khả năng A:**

- [ ] Không có slot nào nằm ngoài `slot_config.sang` + `slot_config.chieu`

- [ ] UV Pass+ ở slot sáng sớm nhất

- [ ] Không quá `slot_config.max_ngay` UV/ngày

- [ ] Cột Người PV: có tên thật HOẶC "⚠️ Cần xác nhận" — không để trống

- [ ] Không có slot nào rơi vào T7, CN



**Khả năng B:**

- [ ] Phần I: mỗi câu có tham chiếu cụ thể từ `ds_cv_data` (tên công ty/dự án/con số thực)

- [ ] Phần II: đủ câu hỏi cho mỗi giá trị trong `core_values` được chọn (≥3)

- [ ] Không câu hỏi phân biệt cá nhân (hôn nhân, tôn giáo, kế hoạch con)

- [ ] Fallback ghi rõ "Chưa cá nhân hóa" ở header nếu không có `ds_cv_data`

