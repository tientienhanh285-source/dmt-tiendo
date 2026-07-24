# W0 — QUẢN LÝ KHO (Library Management)

# Vai trò: Biên tập và kiểm tra dữ liệu trong thư viện CV + JD

# Trigger: User yêu cầu nhập CV mới | chuẩn bị dự án | đóng dự án | cập nhật JD



---



## Tổng quan



W0 là workflow điều phối **thư viện dữ liệu** (`workspace/thu-vien/`).

Không tuyển dụng. Không đánh giá. Chỉ quản lý dữ liệu thô.



```

thu-vien/

├── cv-nguon/

│   ├── _MASTER.csv          ← W0 duy trì file này

│   └── [MaViTri]/

│       ├── [TenUV].pdf      ← CV gốc

│       └── [TenUV].md       ← Đã bóc tách

└── jd/

    └── [MaViTri]/

        └── JD_[MaViTri]_FINAL.docx

```



---



## PROCESS A — Nhập CV mới vào kho



**Trigger:** Nhận được CV mới, chưa biết gán vào đợt tuyển nào



**Bước 1:** Xác định vị trí ứng tuyển → lấy MaViTri từ K0-tu-dien-he-thong.md Nhóm D



**Bước 2:** Gọi skill `boc-tach-cv`:

```

Input:  File PDF mới

Output: [TenUV].md → lưu vào thu-vien/cv-nguon/[MaViTri]/

```



**Bước 3:** Kiểm tra trùng lặp trong `_MASTER.csv`:

- Kiểm tra SĐT + Email

- Nếu trùng → cảnh báo: *"CV của [TenUV] đã có trong kho (ngày nhập: [DATE]). Tiếp tục hay bỏ qua?"*

- Chờ xác nhận trước khi thêm dòng mới



**Bước 4:** Thêm dòng vào `_MASTER.csv` với TrangThai = "Moi"



**Output:**

```

_MASTER.csv cập nhật

Báo cáo: "Đã nhập [N] CV. [X] trùng cần xác nhận."

```



---



## PROCESS B — Biên tập kho (Audit)



**Trigger:** User yêu cầu kiểm tra kho hoặc trước khi bắt đầu đợt tuyển mới



**Kiểm tra 4 loại vấn đề:**



| Vấn đề | Điều kiện | Cờ |
|--------|-----------|-----|
| Hồ sơ không đầy đủ | Thiếu SĐT hoặc Email | `⚠️ Thiếu thông tin liên lạc` |
| Chưa xử lý lâu | TrangThai="Moi" + ngày nhập > 30 ngày | `⚠️ Chưa xử lý [X] ngày` |
| File MD thiếu | Có PDF nhưng không có .md tương ứng | `⚠️ Chưa bóc tách` |
| Dòng trùng | SĐT hoặc Email giống nhau | `⚠️ Trùng lặp` |



**Quy trình:**

1. Đọc `_MASTER.csv` + quét thư mục

2. Xuất danh sách vấn đề với gợi ý xử lý

3. Chờ user quyết định từng vấn đề

4. Cập nhật `_MASTER.csv` theo quyết định



**Output:** `_MASTER.csv` sạch + báo cáo tình trạng kho



---



## PROCESS C — Snapshot cho dự án mới



**Trigger:** Bắt đầu đợt tuyển mới, trước W1



**Input:**

- Vị trí cần tuyển (MaViTri từ K0-tu-dien-he-thong.md)

- Trạng thái muốn đưa vào: thường là `Moi` + `TiemNang`



**Bước 1:** Lọc `_MASTER.csv` theo điều kiện:

```

ViTri = [MaViTri] VÀ TrangThai IN ["Moi", "TiemNang"]

```



**Bước 2:** Xuất CSV snapshot với đầy đủ cột _MASTER:

```

W3_[YYYYMMDD]_SNAP_[MaViTri]_v1.csv

```



**Bước 3:** Copy vào `du-an/[YYYYMM]-[TenDot]/`



**Output:**

```

W3_[DATE]_SNAP_[MaViTri]_v1.csv trong thư mục dự án

Báo cáo: "[N] ứng viên đã có trong kho cho vị trí [Tên vị trí]"

```



---



## PROCESS D — Cập nhật sau khi đóng dự án



**Trigger:** W5 hoàn thành, có file `W5_..._KQ_[MaViTri]-[Dot]_v1.xlsx`



**Bước 1:** Đọc Sheet "Tổng hợp" của file KQ → lấy danh sách UV + kết quả



**Bước 2:** Cập nhật TrangThai trong `_MASTER.csv`:



| Kết quả W5 | TrangThai mới | GhiChu |
|-----------|--------------|--------|
| Trúng tuyển | `DaTuyen` | "Đã tuyển - [TenDot]" |
| Pass+ nhưng chưa có slot | `TiemNang` | "Pass+ [Dot], gọi lại đợt sau" |
| Pass nhưng thua UV khác | `TiemNang` | "Pass [Dot], chưa có slot" |
| Fail / Không phù hợp | `KhongPhuHop` | "Fail [Dot]" |
| Rút lui | `KhongPhuHop` | "Rút lui [Dot]" |



**Bước 3:** Xuất báo cáo cập nhật để HR xác nhận trước khi lưu



**Output:** `_MASTER.csv` cập nhật đầy đủ + báo cáo thay đổi



---



## PROCESS E — Cập nhật JD vào kho



**Trigger:** Sau W1, JD đã được duyệt lần cuối



**Bước 1:** Kiểm tra `thu-vien/jd/[MaViTri]/` đã có JD chưa

- Nếu chưa có → tạo thư mục + copy file

- Nếu đã có (JD cũ) → ghi đè và ghi chú ngày cập nhật



**Bước 2:** Đặt tên file chuẩn: `JD_[MaViTri]_FINAL.docx`



---



## Checklist W0



- [ ] Không thêm dòng vào _MASTER.csv khi thiếu SĐT/Email (chỉ gắn cờ)

- [ ] Không thay đổi cột FilePDF / FileMD (chỉ cập nhật TrangThai và GhiChu)

- [ ] Chờ xác nhận user trước khi ghi đè JD đã tồn tại

- [ ] Snapshot chỉ export, không xóa dữ liệu gốc trong _MASTER.csv



*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*

