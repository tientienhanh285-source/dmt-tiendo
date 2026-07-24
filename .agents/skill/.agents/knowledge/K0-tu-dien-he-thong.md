# TỪ ĐIỂN CHUẨN HÓA — HR AI WORKFORCE FRAMEWORK

> *Canonical Variable Dictionary — HR AI Workforce Framework*

> [!IMPORTANT]
> ⭐ MỌI FILE trong framework chỉ được **THAM CHIẾU** các biến tại đây.
> Không tự định nghĩa lại ở bất kỳ nơi nào khác.

**Cách dùng:** Tìm & thay thế toàn bộ `{{TEN_BIEN}}` bằng giá trị thực.

**Ký hiệu mức độ ưu tiên:**
- ⭐ Bắt buộc — hệ thống không hoạt động nếu thiếu
- ✅ Khuyến nghị — nên điền để đầy đủ
- ⬜ Tùy chọn — có thể để trống hoặc giữ giá trị mặc định

*Ngày tạo: {{NGAY_TAO}}  ·  Phiên bản framework: v1.0*



---



## NHÓM A — THÔNG TIN CÔNG TY (Company Identity)



| Mã biến (Variable Key)          | Giá trị (Value) | Mức | Ghi chú / Hướng dẫn |
|---------------------------------|-----------------|:---:|----------------------|
| `{{TEN_CONG_TY}}`               |                 | ⭐  | Tên giao dịch thông dụng. VD: "HomeStyle Việt Nam" |
| `{{TEN_PHAP_LY}}`               |                 | ⭐  | Tên đầy đủ theo đăng ký kinh doanh. VD: "Công ty TNHH Nội Thất & Gia Dụng HomeStyle" |
| `{{NAM_THANH_LAP}}`             |                 | ✅  | Năm thành lập. VD: "2019" |
| `{{NGANH_HANG}}`                |                 | ⭐  | Lĩnh vực hoạt động chính. VD: "Bán lẻ nội thất và thiết bị gia dụng" |
| `{{MO_HINH_KD}}`                |                 | ✅  | VD: "B2C (showroom) và B2B (đại lý, nhà thầu)" |
| `{{QMNS_TONG}}`                 |                 | ✅  | Tổng nhân sự hiện tại. VD: "~60 nhân sự" |
| `{{DIA_CHI_TRU_SO}}`            |                 | ⭐  | Địa chỉ trụ sở chính đầy đủ |
| `{{DIA_CHI_CN_1}}`              |                 | ⬜  | Chi nhánh / Showroom 1 (nếu có) |
| `{{DIA_CHI_CN_2}}`              |                 | ⬜  | Chi nhánh / Showroom 2 (nếu có) |
| `{{GIO_LAM_VP}}`                |                 | ✅  | Khối văn phòng. VD: "8h15 – 17h30, Thứ 2 – Sáng Thứ 7" |
| `{{GIO_LAM_TRUC_TIEP}}`         |                 | ⬜  | Khối showroom/sản xuất (nếu có). VD: "Ca 1: 8h–15h | Ca 2: 14h–21h" |
| `{{KHACH_HANG_MUC_TIEU}}`       |                 | ✅  | Đối tượng khách hàng chính. VD: "Hộ gia đình trẻ, dự án chung cư" |
| `{{USP_CONG_TY}}`               |                 | ✅  | 2–3 lợi thế cạnh tranh nổi bật, dùng trong JD và content đăng tuyển |



---



## NHÓM B — NHÂN SỰ LÃNH ĐẠO (Leadership)



| Mã biến                           | Giá trị | Mức | Ghi chú |
|-----------------------------------|---------|:---:|---------|
| `{{CHUC_DANH_CEO}}`               |         | ⭐  | VD: "Tổng Giám Đốc" |
| `{{TEN_CEO}}`                     |         | ✅  | Họ tên người ký văn bản cao nhất |
| `{{CHUC_DANH_COO}}`               |         | ⬜  | VD: "Giám Đốc Vận Hành" |
| `{{TEN_COO}}`                     |         | ⬜  | |
| `{{CHUC_DANH_TRUONG_PHONG_HCNS}}` |         | ✅  | VD: "Trưởng phòng Hành chính Nhân sự" |
| `{{TEN_TRUONG_PHONG_HCNS}}`       |         | ⭐  | Người ký văn bản HR, ghi trong email và hợp đồng |
| `{{EMAIL_HR}}`                    |         | ⭐  | Email tiếp nhận CV và liên lạc ứng viên |
| `{{SDT_HR}}`                      |         | ⭐  | SĐT phòng HCNS để UV liên hệ |
| `{{TEN_PHONG_HCNS}}`              |         | ✅  | VD: "Phòng Hành chính – Nhân sự" hoặc "Bộ phận Tuyển dụng" |



---



## NHÓM C — CHÍNH SÁCH LƯƠNG & PHÚC LỢI (Compensation & Benefits)



| Mã biến                           | Giá trị mặc định | Mức | Ghi chú |
|-----------------------------------|-----------------|:---:|---------|
| `{{PC_AN_TRUA}}`                  |                 | ✅  | Phụ cấp ăn trưa. VD: "30.000 VNĐ/ngày làm việc thực tế" |
| `{{PC_GUI_XE}}`                   |                 | ✅  | VD: "Hỗ trợ 100% phí gửi xe tại văn phòng/showroom" |
| `{{PC_DIEN_THOAI}}`               |                 | ⬜  | Nếu có, VD: "200.000 VNĐ/tháng" |
| `{{NGAY_PHEP_NAM}}`               | 12              | ✅  | Số ngày phép năm hưởng lương. Mặc định: 12 ngày/năm |
| `{{TI_LE_LUONG_THU_VIEC}}`        | 85%             | ⭐  | Luật định tối thiểu 85%. Không thay đổi trừ có thỏa thuận đặc biệt |
| `{{THOI_GIAN_THU_VIEC_THANG}}`    | 2               | ⭐  | Số tháng thử việc tối đa. Mặc định: 2 tháng (theo BLLĐ) |
| `{{FORMAT_SO_HD}}`                |                 | ⭐  | Format số hợp đồng thử việc. VD: "[STT]/[Năm]/HĐTV-[MÃ_CONG_TY]" |
| `{{MA_CONG_TY_HD}}`               |                 | ✅  | Mã công ty trong số HĐ. VD: "HS" cho HomeStyle |
| `{{LUONG_THANG_13}}`              |                 | ✅  | Mô tả chính sách lương tháng 13. VD: "Chi trả trước Tết Âm lịch" |
| `{{CHINH_SACH_TANG_LUONG}}`       |                 | ✅  | VD: "Đánh giá định kỳ 12 tháng/lần" |



---



## NHÓM D — VỊ TRÍ TUYỂN DỤNG (Position Registry)



> **Hướng dẫn:** Thêm dòng khi có vị trí mới. Mã vị trí (Code): chữ in hoa, 2–6 ký tự, không trùng.

> Bảng này thay thế "Bảng R2 — Mã Vị Trí" trong R6-dat-ten-file.md.



| STT | Tên vị trí đầy đủ | Mã (Code) | Phòng ban | Tên thư mục (no dấu) |
|-----|-------------------|-----------|-----------|----------------------|
| 1   |                   |           |           |                      |
| 2   |                   |           |           |                      |
| 3   |                   |           |           |                      |
| 4   |                   |           |           |                      |
| 5   |                   |           |           |                      |
| 6   |                   |           |           |                      |



> **VD:** Tư vấn Kinh doanh Showroom | TVKD | Kinh doanh | TuVanKinhDoanh



---



## NHÓM E — GIÁ TRỊ CỐT LÕI (Core Values)



> **Hướng dẫn:** Điền đủ 3–5 giá trị. Hành vi đánh giá dùng trong câu hỏi PV (Phần II) và phiếu chấm.



| Mã biến                 | Tên giá trị | Mô tả 1 câu | Hành vi đánh giá 1 | Hành vi đánh giá 2 |
|-------------------------|-------------|-------------|--------------------|--------------------|
| `{{GIA_TRI_COT_LOI_1}}` |             |             |                    |                    |
| `{{GIA_TRI_COT_LOI_2}}` |             |             |                    |                    |
| `{{GIA_TRI_COT_LOI_3}}` |             |             |                    |                    |
| `{{GIA_TRI_COT_LOI_4}}` |             |             |                    |                    |
| `{{GIA_TRI_COT_LOI_5}}` |             |             |                    | *(tùy chọn)*       |



---



## NHÓM F — TỪ KHÓA ƯU TIÊN SÀNG LỌC (Screening Priority Keywords — R1.3)



> **Hướng dẫn:** Danh sách từ khóa ngành ưu tiên cho từng vị trí. Nếu CV có từ khóa này → cộng 10% điểm TC1.

> Chỉ áp dụng cho vị trí cần kinh nghiệm ngành cụ thể.



| Mã vị trí (từ Nhóm D) | Từ khóa ưu tiên (cách nhau bằng dấu phẩy) |
|-----------------------|-------------------------------------------|
|                       |                                           |
|                       |                                           |
|                       |                                           |



> **VD:** TVKD | nội thất, gia dụng, bất động sản, vật liệu xây dựng, VLXD



---



## NHÓM G — QUY ĐỊNH PHỎNG VẤN & SLA (Interview & SLA Policy)



> **Hướng dẫn:** Các giá trị này đã được mặc định theo thông lệ. Chỉ thay đổi nếu công ty có quy định khác.



| Mã biến                           | Giá trị mặc định | Mức | Ghi chú |
|-----------------------------------|-----------------|:---:|---------|
| `{{SLA_NOD_DIRECTOR}}`            | 90              | ✅  | Ngày nộp đề nghị tuyển trước khi cần người — cấp Giám đốc |
| `{{SLA_NOD_LEADER}}`              | 45              | ✅  | Cấp Quản lý / Trưởng nhóm |
| `{{SLA_NOD_STAFF}}`               | 30              | ✅  | Cấp Nhân viên / Chuyên viên |
| `{{SLA_EMAIL_KQ}}`                | 1               | ✅  | Ngày làm việc để gửi email kết quả sau quyết định cuối |
| `{{SLA_EMAIL_ONBOARDING}}`        | 3               | ✅  | Ngày làm việc gửi email onboarding trước ngày nhận việc |
| `{{DIEM_PASS_PLUS}}`              | 80              | ✅  | Ngưỡng điểm Pass+ (ưu tiên cao) khi chấm CV |
| `{{DIEM_PASS}}`                   | 60              | ✅  | Ngưỡng điểm Pass (đạt yêu cầu) |
| `{{DIEM_TRUNG_TUYEN_PV}}`         | 70              | ✅  | Ngưỡng điểm tổng PV để trúng tuyển |
| `{{SLOT_PV_SANG_1}}`              | 09:00           | ✅  | Slot phỏng vấn buổi sáng thứ nhất |
| `{{SLOT_PV_SANG_2}}`              | 10:00           | ✅  | Slot phỏng vấn buổi sáng thứ hai |
| `{{SLOT_PV_CHIEU_1}}`             | 14:30           | ✅  | Slot phỏng vấn buổi chiều thứ nhất |
| `{{SLOT_PV_CHIEU_2}}`             | 15:30           | ✅  | Slot phỏng vấn buổi chiều thứ hai |
| `{{THOI_LUONG_PV_PHUT}}`          | 45              | ✅  | Thời lượng mỗi ca phỏng vấn (phút) |
| `{{NGHI_GIUA_PV_PHUT}}`           | 15              | ✅  | Khoảng nghỉ bắt buộc giữa 2 ứng viên (phút) |



---



## HƯỚNG DẪN TRIỂN KHAI (Setup Checklist)



### Bước 1 — Điền K0-tu-dien-he-thong.md (file này)

1. Điền tất cả biến ⭐ Bắt buộc trước

2. Điền biến ✅ Khuyến nghị

3. Bỏ qua biến ⬜ Tùy chọn nếu không liên quan



### Bước 2 — Tìm & thay thế toàn framework

Dùng chức năng "Find & Replace" trong VS Code / Notepad++ / bất kỳ editor nào:

- Tìm: `{{TEN_CONG_TY}}` → Thay bằng: [giá trị thực]

- Lặp lại cho tất cả biến đã điền



### Bước 3 — Kiểm tra chéo

- Chạy tìm kiếm `{{` trong toàn folder framework

- Nếu còn kết quả → còn placeholder chưa điền

- Chỉ chấp nhận `{{` trong file `K0-tu-dien-he-thong.md` này



### Bước 4 — Kích hoạt

Xem `SETUP_GUIDE.md` để biết các bước tiếp theo.

