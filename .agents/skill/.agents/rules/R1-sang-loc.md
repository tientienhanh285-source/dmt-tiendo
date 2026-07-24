# RULE R1 — SÀNG LỌC HỒ SƠ (Screening Rules)

# Nguồn biến: K0-tu-dien-he-thong.md — Nhóm D, F, G

# Áp dụng trong: W3 (Sàng lọc hồ sơ) | Skill: cham-diem-cv



---



## R1.1 — Điểm liệt (Hard Reject)



Nếu ứng viên KHÔNG đáp ứng mức kinh nghiệm tối thiểu quy định trong `K4-tieu-chi-tuyen-dung.md` cho vị trí đó → **tự động Reject**, bất kể điểm các tiêu chí khác cao bao nhiêu.



**Cách kiểm tra:** Đọc số năm KN + ngành KN từ CV → đối chiếu với mục "Kinh nghiệm tối thiểu" trong K4.



**Ghi nhận:** Cột "Lý do Reject" ghi: *"R1.1 — Chưa đủ kinh nghiệm tối thiểu ([X] tháng/năm, yêu cầu [Y])"*



---



## R1.2 — Ngưỡng đỗ (Pass Mark)



Tổng điểm chấm CV **≥ {{DIEM_PASS}}/100** mới được chuyển sang trạng thái **Pass** để sắp xếp phỏng vấn.



| Tổng điểm | Phân loại |
|:---------:|----------|
| ≥ {{DIEM_PASS_PLUS}} | Pass+ (Ưu tiên cao) |
| {{DIEM_PASS}}–{{DIEM_PASS_PLUS|trừ 1}} | Pass (Đạt yêu cầu) |
| < {{DIEM_PASS}} | Fail |



---



## R1.3 — Bonus kinh nghiệm ngành đặc thù



Chỉ áp dụng cho các vị trí có danh sách từ khóa ưu tiên trong **K0-tu-dien-he-thong.md Nhóm F**.



Nếu CV có chứa bất kỳ từ khóa nào trong danh sách Nhóm F → **cộng 10% vào điểm Tiêu chí 1 (Kinh nghiệm)**



> **Lấy danh sách từ khóa từ:** `K0-tu-dien-he-thong.md` → Nhóm F → hàng tương ứng với mã vị trí đang sàng lọc.

> **KHÔNG tự suy diễn** từ khóa nếu chưa có trong Nhóm F.



**Công thức:** Điểm TC1 sau bonus = min(TC1 × 1.1, 30)



**Ghi nhận:** Cột "Bonus R1.3" ghi từ khóa tìm thấy.



---



## R1.4 — Hồ sơ không đầy đủ



Nếu CV thiếu **số điện thoại HOẶC email** → đánh dấu **"Hồ sơ không đầy đủ"**, không chấm điểm, không xếp lịch PV.



**Ghi nhận:** Cột "Phân loại" ghi: *"Hồ sơ không đầy đủ — Thiếu [SĐT/Email]"*



---



*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*

