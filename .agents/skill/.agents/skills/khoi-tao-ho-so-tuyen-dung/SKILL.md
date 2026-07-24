---

name: khoi-tao-ho-so-tuyen-dung

description: >

  Khởi tạo cấu trúc thư mục dự án tuyển dụng mới bằng cách clone từ _mau-du-an/,

  tạo file OVERVIEW.md và tạo folder cv-raw/ cho từng vị trí cần tuyển.

  Kích hoạt khi user đề cập 'tạo folder tuyển dụng', 'khởi tạo đợt tuyển', 'bắt đầu dự án tuyển dụng';

  yêu cầu 'tạo thư mục cho đợt này', 'set up dự án tuyển dụng'.

  Dùng cho MỌI yêu cầu khởi tạo cấu trúc thư mục dự án mới.

---



# Skill: Khởi Tạo Hồ Sơ Tuyển Dụng



## Khi nào kích hoạt



W1 gọi skill này ở bước đầu để tạo thư mục dự án.

Cấu trúc phẳng đảm bảo tất cả W2–W6 biết chính xác đặt file ở đâu — không nhầm vị trí.



---



## Bước 1 — Xác định thông tin đợt



| Thông tin | Lấy từ | Ví dụ |
|-----------|--------|-------|
| Tên đợt | User / kế hoạch | `Q3-2026` |
| Năm-tháng | Tự tính | `202608` |
| Danh sách vị trí | Kế hoạch W1 | Lấy Mã vị trí từ K0-tu-dien-he-thong.md Nhóm D |
| Ngày tạo | Hệ thống | `20260801` |



---



## Bước 2 — Clone cấu trúc từ `_mau-du-an/`



Tạo thư mục dự án mới:

```

du-an/[YYYYMM]-[TenDot]/

├── OVERVIEW.md                  ← Điền thông tin đợt

└── cv-raw/

    └── [MaViTri]/               ← 1 folder/vị trí (từ K0-tu-dien-he-thong.md Nhóm D)

```



**Quy tắc đặt tên:**

- Thư mục gốc đợt: `[YYYYMM]-[TenDot]` → VD: `202608-Q3-2026`

- Tên vị trí trong cv-raw: Tên thư mục từ K0-tu-dien-he-thong.md Nhóm D (PascalCase, không dấu)



---



## Bước 3 — Điền OVERVIEW.md



```markdown

# DỰ ÁN TUYỂN DỤNG: [TenDot]



**Ngày khởi tạo:** [YYYYMMDD]

**Người phụ trách:** [Tên HR]

**Vị trí tuyển:**

- [Vị trí 1] (Mã: [CODE]): [SL] người

- [Vị trí 2] (Mã: [CODE]): [SL] người



**Trạng thái W0→W6:**

- [ ] W0 — Snapshot kho tại T0

- [ ] W1 — Kế hoạch & JD

- [ ] W2 — Content đăng tuyển

- [ ] W3 — Sàng lọc hồ sơ

- [ ] W4 — Phỏng vấn

- [ ] W5 — Kết quả & Offer

- [ ] W6 — Onboarding

```



---



## Bước 4 — Gọi W0-Process C



Sau khi tạo cấu trúc xong → gọi W0-Process C để lấy snapshot CSV từ kho vào dự án.



---



## Checklist chất lượng



- [ ] Thư mục dự án đúng định dạng `[YYYYMM]-[TenDot]`

- [ ] Có `OVERVIEW.md` với tracking W0→W6

- [ ] Có `cv-raw/[MaViTri]/` cho từng vị trí cần tuyển

- [ ] Mã vị trí khớp với K0-tu-dien-he-thong.md Nhóm D



## Scripts

- `scripts/gen_folder_structure.py` — Tạo cấu trúc thư mục tự động



## Registry Block



```

### khoi-tao-ho-so-tuyen-dung

Clone cấu trúc thư mục dự án phẳng từ mẫu, tạo OVERVIEW.md và cv-raw/.

💡 **Prompt Mẫu:** "Tạo dự án tuyển dụng Q3/2026, cần tuyển 2 Sales và 1 Marketing."

```

