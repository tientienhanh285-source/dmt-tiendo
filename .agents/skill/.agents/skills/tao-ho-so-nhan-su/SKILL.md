---

name: tao-ho-so-nhan-su

description: >

  Tạo bộ hồ sơ pháp lý onboarding (HĐTV, NDA, Phiếu NS) điền sẵn từ dữ liệu ứng viên.

  Tự điều chỉnh theo bối cảnh: đủ hay thiếu thông tin, tạo toàn bộ hay từng document.

  Kích hoạt khi user đề cập 'hợp đồng thử việc', 'hồ sơ nhân sự', 'HĐTV', 'NDA'.

  KHÔNG chạy khi offer chưa được xác nhận (R5.1).

---



# SKILL: Tạo Hồ Sơ Nhân Sự



## 1. Bối cảnh kích hoạt



| Tín hiệu bối cảnh | Phương án xử lý |
|-------------------|----------------|
| Có đủ: Offer Letter + CV/CCCD + JD | → Tạo đầy đủ HĐTV + NDA + Phiếu NS |
| Thiếu số CCCD | → Tạo HĐTV với ô trống [CCCD — chờ xác nhận], cảnh báo |
| Thiếu JD hoặc không xác định chức danh | → Dừng, yêu cầu bổ sung: "Cần xác nhận chức danh chính xác" |
| Chưa có xác nhận Offer | → Dừng hoàn toàn: "R5.1 — Cần xác nhận Offer trước" |
| User chỉ muốn HĐTV (không cần NDA) | → Tạo chỉ HĐTV, bỏ qua NDA |
| UV nước ngoài | → Cảnh báo: "Cần kiểm tra thêm điều kiện pháp lý — xử lý thủ công" |



---



## 2. Nguồn dữ liệu tham chiếu (KHÔNG hardcode)



> Skill chỉ ĐỌC và ÁP DỤNG các giá trị từ nguồn chính thức:



- **Tỷ lệ lương thử việc:** `K0-tu-dien-he-thong.md` Nhóm C (`{{TI_LE_LUONG_THU_VIEC}}`)

- **Thời gian thử việc:** `K0-tu-dien-he-thong.md` Nhóm C (`{{THOI_GIAN_THU_VIEC_THANG}}`)

- **Format số hợp đồng:** `K0-tu-dien-he-thong.md` Nhóm C (`{{FORMAT_SO_HD}}`)

- **Kiểm tra nhất quán lương:** `R2.4` + `R2.5` (áp dụng, không định nghĩa lại)

- **Kiểm tra điều kiện onboarding:** `R5.1` → `R5.5` (áp dụng, không định nghĩa lại)



---



## 3. Khả năng xử lý



### Bước 1 — Thu thập và xác minh dữ liệu



| Trường | Nguồn ưu tiên | Fallback |
|--------|--------------|----------|
| Họ tên đầy đủ (theo CCCD) | CV hoặc snapshot CSV | Hỏi user trực tiếp |
| Số CCCD 12 chữ số | CV | Để ô trống + cảnh báo |
| Ngày/Nơi cấp CCCD | CV | Để ô trống + cảnh báo |
| Địa chỉ thường trú | CV | Để ô trống |
| Lương cứng đã xác nhận | `W5_..._OL_[TenUV]_FINAL.md` | Hỏi user |
| Ngày bắt đầu | Offer Letter | Hỏi user |
| Chức danh chính xác | JD (`thu-vien/jd/`) | K4 → Nhóm D K0-tu-dien-he-thong.md |



### Bước 2 — Tính toán từ nguồn tham chiếu



```

Lương thử việc  = Lương offer × {{TI_LE_LUONG_THU_VIEC}} (áp R2.4)

Ngày kết thúc TV = Ngày bắt đầu + {{THOI_GIAN_THU_VIEC_THANG}} tháng - 1 ngày

Số HĐ           = Áp format {{FORMAT_SO_HD}} — hỏi user số thứ tự nếu chưa có

```



### Bước 3 — Điền template



Điền vào templates có sẵn — **không soạn từ đầu**:

- HĐTV: `templates/hop-dong-thu-viec.docx`

- NDA: `templates/hop-dong-bao-mat.docx` (không sửa điều khoản)

- Phiếu NS: `templates/phieu-thong-tin-ns.xlsx` (điền phần AI có thể, để trống phần UV tự điền)



---



## 4. Tiêu chuẩn chất lượng đầu ra



- [ ] **R5.1:** Xác nhận offer tồn tại trước khi tạo bất kỳ file nào

- [ ] **Số HĐ đúng format:** Khớp `{{FORMAT_SO_HD}}` và không trùng với HĐ khác

- [ ] **Tên Bên B nhất quán:** HĐTV = NDA = CV (đúng theo CCCD, không viết tắt)

- [ ] **Lương TV đúng:** = Lương Offer × `{{TI_LE_LUONG_THU_VIEC}}` (R2.4)

- [ ] **Ngày kết thúc TV chính xác:** Đúng `{{THOI_GIAN_THU_VIEC_THANG}}` tháng

- [ ] **Chức danh nhất quán:** HĐ = Offer = JD (R2.5)

- [ ] **HĐTV và NDA cùng ngày lập** (R5.2)

- [ ] **Phiếu NS:** Phần AI điền không có ô trống không rõ lý do; phần UV tự điền để nguyên trống

- [ ] **Ô trống có cảnh báo:** Mọi ô thiếu dữ liệu đều có nhãn "[Cần xác nhận: tên trường]"



## Templates

- `templates/hop-dong-thu-viec.docx`

- `templates/hop-dong-bao-mat.docx`

- `templates/phieu-thong-tin-ns.xlsx`

- `templates/checklist-onboard.xlsx`



## Scripts

- `scripts/gen_hop_dong.py`



## Registry Block



```

### tao-ho-so-nhan-su

Điền HĐTV + NDA + Phiếu NS từ dữ liệu UV — tự xử lý khi thiếu thông tin.

💡 **Prompt Mẫu:** "Làm hồ sơ onboarding cho [Tên UV], bắt đầu [ngày]."

```

