---

name: boc-tach-cv

description: >

  Bóc tách dữ liệu từ CV PDF thành bảng tổng hợp XLSX có cấu trúc — chuyển đổi

  PDF → Markdown, sau đó AI phân tích ngữ nghĩa trích xuất thông tin cá nhân và

  nghề nghiệp, xuất ra file XLSX format chuẩn với 7 cột bắt buộc + cột mở rộng.

  Kích hoạt khi user đề cập 'bóc tách CV', 'trích xuất CV', 'tổng hợp CV';

  yêu cầu 'đọc mấy cái CV này ra bảng', 'lấy thông tin từ CV', 'số hóa CV';

  nói 'tổng hợp thông tin ứng viên', 'bảng danh sách UV';

  trong tình huống có folder CV PDF cần chuyển thành dữ liệu có cấu trúc.

  KHÔNG dùng để chấm điểm CV (→ cham-diem-cv), bóc tách PDF chung (→ boc-tach-pdf).

---



# Skill: Bóc Tách CV



## Vai trò trong pipeline



Skill này là **bước đầu tiên** khi nhập CV vào kho (W0-Process A).

Output là nguồn dữ liệu cho `_MASTER.csv` và cho W3 khi sàng lọc từ snapshot.



```

CV PDF ──→ [boc-tach-cv] ──→ [TenUV].md + dòng trong _MASTER.csv

                                    │

                              snapshot CSV ──→ W3 sàng lọc

```



---



## Quy trình 2 bước



### Bước 1 — PDF → Markdown (Script xử lý)



Script `scripts/gen_boc_tach_cv.py` thực hiện:

1. Duyệt toàn bộ file `*.pdf` trong folder CV chỉ định

2. Chạy `pdftotext -layout` → text thô

3. Nếu text rỗng (PDF scan) → cảnh báo, cần dùng skill `boc-tach-pdf` (AI Vision)

4. Ghi text thô vào file `.md` cho từng CV (lưu vào `thu-vien/cv-nguon/[MaViTri]/`)

5. Gộp tất cả vào 1 file `All_CVs.md` tạm (mỗi CV cách nhau bằng `---`)



### Bước 2 — AI phân tích ngữ nghĩa → dữ liệu JSON



AI agent đọc `All_CVs.md` và trích xuất theo bảng cấu trúc:



**7 cột bắt buộc:**



| # | Cột | Ghi nếu thiếu |
|---|-----|---------------|
| 1 | Họ và tên | "Thiếu" |
| 2 | SĐT | → **Hồ sơ không đầy đủ** (R1.4) |
| 3 | Email | → **Hồ sơ không đầy đủ** (R1.4) |
| 4 | Ngày sinh | "Không rõ" |
| 5 | Giới tính | "Không rõ" |
| 6 | Địa chỉ | "Không rõ" |
| 7 | File CV | Tên file PDF gốc |



**Cột mở rộng:**



| # | Cột | Format | Ghi nếu thiếu |
|---|-----|--------|---------------|
| 8 | Trình độ học vấn | "ĐH / CĐ / TC / THPT" | "Không rõ" |
| 9 | Trường | Tên trường | "Không rõ" |
| 10 | Chuyên ngành | Ngành học | "Không rõ" |
| 11 | Năm tốt nghiệp | YYYY | "Không rõ" |
| 12 | Kinh nghiệm tổng (năm) | Số năm | 0 |
| 13 | Công ty gần nhất | Tên công ty | "Chưa có KN" |
| 14 | Chức danh gần nhất | Chức danh | "Chưa có KN" |
| 15 | Thời gian gần nhất | "MM/YYYY - MM/YYYY" | "" |
| 16 | Kỹ năng chuyên môn | Liệt kê, cách nhau "; " | "Không đề cập" |
| 17 | Ngoại ngữ / Chứng chỉ | TOEIC XXX, IELTS X.X | "Không đề cập" |
| 18 | Mục tiêu nghề nghiệp | Tóm tắt ≤50 từ | "Không có" |



> ⚠️ **Quy tắc Không bịa dữ liệu:** Nếu CV không ghi trường nào, ghi đúng giá trị mặc định. KHÔNG suy đoán hoặc ngoại suy.



---



## Output



```

[TenUV].md              → Lưu vào thu-vien/cv-nguon/[MaViTri]/

All_CVs.md              → File tạm (xóa sau khi xử lý xong)

_MASTER.csv             → Cập nhật thêm dòng mới (W0 xử lý)

```



---



## Cách dùng script



```bash

python scripts/gen_boc_tach_cv.py \

    --cv_dir   <đường dẫn folder CV PDF> \

    --out_dir  <đường dẫn thu-vien/cv-nguon/[MaViTri]/> \

    --ma_vitri <mã vị trí từ K0-tu-dien-he-thong.md Nhóm D>

```



---



## Checklist chất lượng



- [ ] Mỗi CV PDF đều có file `.md` tương ứng

- [ ] 7 cột bắt buộc không bị trống (ghi giá trị mặc định nếu thiếu)

- [ ] SĐT/Email thiếu → gắn nhãn "Hồ sơ không đầy đủ"

- [ ] Không bịa dữ liệu (Quy tắc toàn cục)



## Registry Block



```

### boc-tach-cv

Bóc tách CV PDF → file Markdown + cập nhật _MASTER.csv trong kho.

💡 **Prompt Mẫu:** "Bóc tách mấy cái CV trong folder này vào kho."

```

