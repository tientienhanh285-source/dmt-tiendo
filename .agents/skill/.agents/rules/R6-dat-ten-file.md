# R6 — QUY TẮC ĐẶT TÊN FILE & THƯ MỤC

# (File & Folder Naming Convention)

# Nguồn biến: K0-tu-dien-he-thong.md — Nhóm D (Bảng mã vị trí)

# Phạm vi áp dụng: Toàn bộ file output trong hệ thống (W0→W6)

# Nguyên tắc: Tên file = Metadata — đọc tên file là biết nội dung, bước, thời điểm, phiên bản



---



## Cấu trúc tên file trong DỰ ÁN (có prefix workflow)



```

[Wx]_[YYYYMMDD]_[PHÂN-LOẠI]_[NỘI-DUNG]_[PHIÊN-BẢN].[ext]

```



| Thành phần | Định dạng | Ví dụ | Bắt buộc |
|-----------|-----------|-------|:--------:|
| `[Wx]` | Mã workflow (W0–W6) | `W3`, `W5` | ✅ (chỉ trong dự án) |
| `[YYYYMMDD]` | Ngày tạo/xuất file | `20260801` | ✅ |
| `[PHÂN-LOẠI]` | Mã 2–4 chữ in hoa | `KH`, `SL`, `PV`, `OL` | ✅ |
| `[NỘI-DUNG]` | Tên vị trí / đợt / người (PascalCase, không dấu) | `Q3-2026`, `NguyenThiLan` | ✅ |
| `[PHIÊN-BẢN]` | `v1`, `v2`, `FINAL` | `v1`, `FINAL` | ✅ |



> **Ngoại lệ:** File trong thư mục nhân viên (W6/TenNV/) dùng R6 gốc không có prefix Wx_.



---



## Cấu trúc tên file trong THƯ VIỆN (không prefix workflow)



```

[YYYYMMDD]_[PHÂN-LOẠI]_[NỘI-DUNG]_[PHIÊN-BẢN].[ext]

```



---



## Bảng mã phân loại (Prefix chuẩn)



| Mã | Loại tài liệu | Ví dụ tên file |
|----|--------------|----------------|
| `KH` | Kế hoạch tuyển dụng | `W1_20260801_KH_TuyenDung-Q3_v1.xlsx` |
| `DN` | Đề nghị tuyển dụng | `W1_20260801_DN_[MaViTri]_v1.xlsx` |
| `CT` | Content đăng tuyển | `W2_20260805_CT_[MaViTri]-Q3_v1.xlsx` |
| `SNAP` | Snapshot kho UV | `W3_20260810_SNAP_[MaViTri]_v1.csv` |
| `SL` | Kết quả sàng lọc | `W3_20260815_SL_[MaViTri]-Q3_v1.xlsx` |
| `LP` | Lịch phỏng vấn | `W4_20260818_LP_[MaViTri]-Q3_v1.xlsx` |
| `CQ` | Câu hỏi STAR cá nhân hóa | `W4_20260818_CQ_[MaViTri]_v1.docx` |
| `PV` | Phiếu đánh giá PV (đã điền) | `W4_20260820_PV_[TenUV]_v1.xlsx` |
| `KQ` | Báo cáo kết quả PV | `W5_20260825_KQ_[MaViTri]-Q3_v1.xlsx` |
| `OL` | Offer letter | `W5_20260826_OL_[TenUV]_FINAL.md` |
| `TC` | Email từ chối | `W5_20260826_TC_[TenUV]_v1.md` |
| `HDTV` | Hợp đồng thử việc | `20260901_HDTV_[TenUV]_FINAL.docx` |
| `NDA` | Hợp đồng bảo mật | `20260901_NDA_[TenUV]_FINAL.docx` |
| `NS` | Phiếu thông tin nhân sự | `20260901_NS_[TenUV]_v1.xlsx` |
| `EM` | Email (các loại khác) | `20260901_EM_Onboarding-[TenUV]_v1.md` |
| `JD` | Job Description | `20260801_JD_[MaViTri]_FINAL.docx` |



---



## Bảng mã vị trí (Lấy từ K0-tu-dien-he-thong.md — Nhóm D)



> **KHÔNG hardcode bảng này trong file R6.**

> Tra cứu trực tiếp từ `K0-tu-dien-he-thong.md` → Nhóm D khi cần mã vị trí.

> Lý do: Nhóm D là nguồn duy nhất, cập nhật một nơi áp dụng toàn hệ thống.



**Ví dụ cách dùng:** Để tìm mã vị trí "Tư vấn Kinh doanh" → mở K0-tu-dien-he-thong.md → Nhóm D → lấy cột "Mã (Code)".



---



## Quy tắc viết phần [NỘI-DUNG]



```

✅ NguyenThiLan         (tên người — PascalCase)

✅ [MaViTri]-Q3-2026    (vị trí + đợt — gạch ngang)

✅ TuyenDung-Q3         (kết hợp — gạch ngang phân tách)

❌ Nguyen Thi Lan        (có khoảng trắng)

❌ sales_showroom        (snake_case)

```



### Quy tắc phiên bản

```

v1, v2, v3...   → Bản nháp (chưa được duyệt)

FINAL           → Bản đã duyệt, sẵn sàng ký/gửi

```



---



## Cấu trúc thư mục DỰ ÁN



```

du-an/

└── [YYYYMM]-[TenDot]/           ← VD: 202608-Q3-2026/

    ├── OVERVIEW.md

    ├── cv-raw/[MaViTri]/

    ├── W3_..._SNAP_*.csv         ← Snapshot kho tại T0

    ├── W1_..._KH_*.xlsx

    ├── W1_..._DN_*.xlsx

    ├── W2_..._CT_*.xlsx

    ├── W3_..._SL_*.xlsx

    ├── W4_..._LP / CQ / PV_*

    ├── W5_..._KQ / OL / TC_*

    └── [TenUV]/                  ← Thư mục W6 — mỗi người 1 folder

        ├── HDTV_*.docx

        ├── NDA_*.docx

        ├── NS_*.xlsx

        └── EM_Onboarding_*.md

```



---



## Checklist AI Rà soát



Khi được yêu cầu kiểm tra cấu trúc dự án, AI xác minh:



- [ ] Thư mục dự án đúng định dạng `[YYYYMM]-[TenDot]`

- [ ] File W1→W5 có prefix `Wx_` ở đầu tên

- [ ] File trong thư mục nhân viên (W6) không cần prefix Wx_

- [ ] Mã vị trí trong tên file khớp với Nhóm D của K0-tu-dien-he-thong.md

- [ ] Mã phân loại khớp bảng prefix ở trên

- [ ] Phiên bản kết thúc bằng `_v[N]` hoặc `_FINAL`

- [ ] Không có file lạc ngoài quy định



*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*

