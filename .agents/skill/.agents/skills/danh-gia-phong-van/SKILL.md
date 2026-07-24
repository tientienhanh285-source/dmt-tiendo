---

name: danh-gia-phong-van

description: >

  Tạo phiếu đánh giá PV điền sẵn (trước khi phỏng vấn) VÀ/HOẶC tổng hợp điểm

  từ nhiều phiếu đã điền (sau phỏng vấn) — tùy bối cảnh W4 hay W5 gọi.

  Kích hoạt khi user đề cập 'phiếu đánh giá', 'tổng hợp kết quả PV', 'điểm phỏng vấn'.

  KHÔNG dùng để tạo câu hỏi (→ lap-lich-phong-van), gửi email (→ soan-thu-tuyen-dung).

---



# SKILL: Đánh Giá Phỏng Vấn



## 1. Bối cảnh kích hoạt



| Tín hiệu bối cảnh | Khả năng kích hoạt |
|-------------------|-------------------|
| W4 gọi + chưa có phiếu | → Khả năng A: tạo phiếu trống điền sẵn |
| W5 gọi + có phiếu đã điền | → Khả năng B: tổng hợp điểm |
| Phiếu chưa đủ (N1 chưa điền) | → Cảnh báo "Phiếu [UV] chưa đủ", bỏ qua UV đó |
| N1 và N2 bất đồng quyết định | → Gắn cờ "⚠️ Cần họp thống nhất", KHÔNG tự ra kết luận |
| User muốn xem nhanh điểm | → Chỉ xuất bảng điểm, bỏ qua phần quyết định |



---



## 2. Nguồn dữ liệu tham chiếu (KHÔNG hardcode)



- **Ngưỡng trúng tuyển:** `K0-tu-dien-he-thong.md` Nhóm G (`{{DIEM_TRUNG_TUYEN_PV}}`)

- **Khung lương đề xuất:** `K3-bang-luong-phuc-loi.md`

- **Giới hạn lương offer:** `R2.1 + R2.2`

- **Tiêu chí chuyên môn Phần A:** `K4-tieu-chi-tuyen-dung.md` cho vị trí đang PV

- **Giá trị cốt lõi Phần B:** `K5-gia-tri-cot-loi.md`



---



## 3. Khả năng A — Tạo phiếu trống (W4 gọi)



Cấu trúc file `W4_[DATE]_PV_[TenUV]_v1.xlsx` — 4 sheet:



**Sheet "Thông tin"** (AI điền sẵn từ snapshot/dữ liệu đã có):

```

Tên ứng viên | Vị trí | Ngày PV | Người PV 1 | Người PV 2

Lương tham khảo: Mid range theo K3 (để người PV biết baseline)

```



**Sheet "Câu hỏi"** — copy từ file `W4_..._CQ_*.docx` (do lap-lich-phong-van tạo)



**Sheet "Đánh giá"** (người PV điền sau buổi phỏng vấn — thang 1–4):



Phần A — Chuyên môn (tổng 60đ):

Đọc từ `K4` → lấy 5 tiêu chí chuyên môn của vị trí đó



| Tiêu chí | 1=Kém | 2=Cần cải thiện | 3=Đạt | 4=Xuất sắc | Nhận xét |
|----------|:-----:|:---------------:|:-----:|:----------:|---------|
| [TC từ K4] | | | | | |



Phần B — Giá trị cốt lõi (tổng 40đ):

Đọc từ `K5` → 4 giá trị cốt lõi công ty



**Sheet "Kết luận"** (AI điền đề xuất, người PV điền quyết định):

```

Điểm Phần A = (Trung bình 5 tiêu chí) × 3

Điểm Phần B = (Trung bình 4 giá trị) × 2.5

Tổng = A + B

Lương đề xuất AI = [dựa trên điểm + K3, tham chiếu R2.1/R2.2]

Quyết định N1 + Quyết định N2: [để trống cho người PV điền]

```



**Điều chỉnh bối cảnh:**

- Vị trí chưa có trong K4 → tạo phiếu với tiêu chí placeholder, cảnh báo cần điền K4

- PV online → thêm cột "Chất lượng kết nối" vào thông tin



---



## 4. Khả năng B — Tổng hợp điểm (W5 gọi)



```

Với mỗi file W4_..._PV_[UV].xlsx:

1. Đọc Sheet "Kết luận": điểm N1, điểm N2, quyết định N1, quyết định N2

2. Tính điểm TB = (Tổng N1 + Tổng N2) / 2

3. Áp điều kiện từ K0-tu-dien-he-thong.md Nhóm G:

   Pass: TB ≥ {{DIEM_TRUNG_TUYEN_PV}} VÀ N1="Đề xuất" VÀ N2="Đề xuất"

4. Kiểm tra lương đề xuất → R2.1/R2.2 → gắn cờ nếu vượt khung

```



Điều chỉnh bối cảnh:

- Chỉ có 1 người PV điền → cảnh báo "Thiếu đánh giá N2", không ra kết luận cuối

- UV bỏ buổi PV → ghi "Vắng mặt", không tính điểm



Output: `W5_[DATE]_KQ_[MaViTri]-[Dot]_v1.xlsx` — 3 sheet:

```

Sheet "Tổng hợp": Tên UV | TB | Lương đề xuất | Kết quả | Ghi chú

Sheet "Xếp hạng": DS trúng tuyển theo điểm giảm dần

Sheet "Cảnh báo": Bất đồng N1/N2 | Lương vượt khung | Phiếu chưa đủ

```



---



## 5. Tiêu chuẩn chất lượng đầu ra



**Khả năng A (tạo phiếu):**

- [ ] Thông tin UV điền sẵn đúng (tên, vị trí, ngày PV, lương tham khảo)

- [ ] Tiêu chí Phần A lấy đúng từ K4 của vị trí đó (không dùng tiêu chí vị trí khác)

- [ ] Tiêu chí Phần B lấy đúng từ K5 (không tự nghĩ giá trị)

- [ ] Lương đề xuất trong Sheet Kết luận ≤ Max Range (R2.1)

- [ ] Không ra quyết định trúng tuyển — Sheet Kết luận chỉ có đề xuất AI



**Khả năng B (tổng hợp):**

- [ ] Đọc đủ tất cả phiếu PV trong dự án (không bỏ sót)

- [ ] Điểm TB tính đúng = (N1 + N2) / 2

- [ ] UV bất đồng N1/N2 → bắt buộc có trong Sheet Cảnh báo

- [ ] UV phiếu chưa điền đủ → không ra kết quả, có trong Sheet Cảnh báo

- [ ] Gắn cờ R2.2 nếu lương đề xuất vượt Max Range



## Templates

- `templates/phieu-danh-gia-pv.xlsx`



## Scripts

- `scripts/gen_phieu_pv.py`



## Registry Block



```

### danh-gia-phong-van

Tạo phiếu PV điền sẵn (W4) VÀ/HOẶC tổng hợp điểm ra kết quả (W5).

Tự đọc bối cảnh: có phiếu chưa hay đã điền xong?

💡 **Prompt Mẫu:** "Tổng hợp kết quả PV từ mấy phiếu này, ai trúng tuyển?"

```

