# THƯ VIỆN CV NGUỒN

# (CV Source Library)

# Quản lý bởi: W0-quan-ly-kho.md



---



## Cấu trúc



```

thu-vien/cv-nguon/

├── _MASTER.csv            ← Single Source of Truth toàn bộ ứng viên

└── [MaViTri]/             ← 1 thư mục/vị trí (lấy mã từ K0-tu-dien-he-thong.md Nhóm D)

    ├── [TenUV].pdf        ← CV gốc (bất biến)

    └── [TenUV].md         ← Đã bóc tách (skill boc-tach-cv)

```



---



## `_MASTER.csv` — Cấu trúc cột



| Cột | Mô tả | Giá trị mẫu |
|-----|-------|-------------|
| `TenUV` | Họ và tên đầy đủ | NguyenThiLan |
| `ViTri` | Tên vị trí đầy đủ | Tư vấn Kinh doanh Showroom |
| `MaViTri` | Mã vị trí từ K0-tu-dien-he-thong.md Nhóm D | TVKD |
| `TrangThai` | Trạng thái hiện tại | Moi / TiemNang / DaTuyen / KhongPhuHop / DaLienHe |
| `NgayNhan` | Ngày nhận CV | 2026-08-01 |
| `DiemSL` | Điểm sàng lọc CV (nếu đã chấm) | 75 |
| `FilePDF` | Tên file PDF | NguyenThiLan.pdf |
| `FileMD` | Tên file Markdown | NguyenThiLan.md |
| `GhiChu` | Ghi chú tình trạng | Pass+ Q3-2026, gọi lại đợt sau |



---



## Giá trị TrangThai



| Giá trị | Ý nghĩa |
|---------|---------|
| `Moi` | CV mới nhận, chưa qua sàng lọc |
| `TiemNang` | Đã sàng lọc, đạt nhưng chưa có slot |
| `DaTuyen` | Đã trúng tuyển ở một đợt |
| `KhongPhuHop` | Không phù hợp hoặc đã rút lui |
| `DaLienHe` | Đã liên hệ, đang trong quy trình |



---



## Quy trình vận hành



Xem: `.agents/workflows/W0-quan-ly-kho.md`



- **Nhập CV mới:** W0-Process A

- **Kiểm tra & biên tập kho:** W0-Process B

- **Lấy snapshot cho dự án:** W0-Process C

- **Cập nhật sau dự án:** W0-Process D



---



## Lưu ý quan trọng



- ❌ KHÔNG xóa file PDF hoặc MD — chỉ cập nhật `TrangThai` trong _MASTER.csv

- ❌ KHÔNG sửa thẳng _MASTER.csv khi đang có dự án đang chạy

- ✅ Mọi thay đổi trạng thái phải qua W0



*Cập nhật lần cuối: {{NGAY_TAO}}*

