# RULE R4 — LỊCH PHỎNG VẤN (Scheduling Rules)

# Nguồn biến: K0-tu-dien-he-thong.md — Nhóm G

# Áp dụng trong: W3 (lên lịch), W4 (xác nhận) | Skill: lap-lich-phong-van



---



## R4.1 — Khung giờ hợp lệ



Chỉ xếp lịch phỏng vấn trong các khung giờ:

- **Buổi sáng:** {{SLOT_PV_SANG_1}} — {{SLOT_PV_SANG_2}}

- **Buổi chiều:** {{SLOT_PV_CHIEU_1}} — {{SLOT_PV_CHIEU_2}}

- **Ngày làm việc:** Thứ Hai đến Thứ Sáu



**KHÔNG xếp lịch:** Thứ Bảy, Chủ Nhật, ngày lễ quốc gia.



---



## R4.2 — Thời lượng và khoảng nghỉ



- Mỗi ca phỏng vấn: **{{THOI_LUONG_PV_PHUT}} phút**

- Khoảng nghỉ bắt buộc giữa 2 ứng viên: **tối thiểu {{NGHI_GIUA_PV_PHUT}} phút**

- Tối đa 1 buổi sáng: 2 ứng viên

- Tối đa 1 buổi chiều: 2 ứng viên

- Tối đa 1 ngày: **4 ứng viên**



---



## R4.3 — Thành phần phỏng vấn bắt buộc



| Vòng | Thành phần | Ghi chú |
|------|-----------|---------|
| Vòng 1 (Phone Screening) | Chuyên viên Tuyển dụng | Qua điện thoại |
| Vòng 2 (Trực tiếp) | {{TEN_PHONG_HCNS}} + Trưởng BP tiếp nhận | Bắt buộc có đủ 2 người |
| Vòng 3 (Cấp cao) | Ban Giám Đốc ({{CHUC_DANH_CEO}}/{{CHUC_DANH_COO}}) | Chỉ áp dụng Leader trở lên |



*(Nguồn: K6-quy-dinh-tuyen-dung.md §4)*



---



## R4.4 — Ưu tiên slot theo điểm



- UV có điểm **Pass+ (≥{{DIEM_PASS_PLUS}}đ)** → ưu tiên slot sáng ngày đầu tiên

- UV có điểm **Pass ({{DIEM_PASS}}–{{DIEM_PASS_PLUS|trừ 1}}đ)** → xếp theo thứ tự điểm giảm dần



---



## R4.5 — Cảnh báo thành phần thiếu



Nếu không xác định được tên Trưởng BP hoặc đại diện HCNS → gắn cảnh báo `⚠️ Cần xác nhận thành phần PV` vào ô tương ứng, không để trống.



*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*

