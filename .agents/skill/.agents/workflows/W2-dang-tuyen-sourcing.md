---

description: Viết nội dung đăng tuyển đa nền tảng (Facebook, Threads, LinkedIn) từ JD. Kích hoạt sau khi W1 hoàn thành và JD đã lưu trong thư viện.

---



# W2 — ĐĂNG TUYỂN & SOURCING



> **Trigger:** User yêu cầu viết content đăng tuyển sau khi có JD



---



## INPUT



| Nguồn | Dùng để |
|-------|---------|
| `thu-vien/jd/[MaViTri]/JD_*.docx` | Nội dung JD để tạo content |
| `K5-gia-tri-cot-loi.md` | Tone thương hiệu |
| `K1-company-profile.md` | USP công ty |
| `K0-tu-dien-he-thong.md` — Nhóm A | Email HR, tên công ty |



---



## PROCESS



**B1.** Đọc JD từ `thu-vien/jd/[MaViTri]/`

→ Trích xuất: Tên vị trí | Top 3 YC | Top 3 quyền lợi | Thông tin ứng tuyển



**B2.** Gọi **skill `viet-content-tuyen-dung`**

→ Viết 3 bài: Facebook | Threads | LinkedIn

→ Không ghi lương cứng (range hoặc "thỏa thuận")



**B3.** Xuất file với lịch đề xuất đăng:



---



## OUTPUT



Lưu vào: `du-an/[YYYYMM]-[TenDot]/` (phẳng, prefix W2_)



```

W2_[DATE]_CT_[MaViTri]-[Dot]_v1.xlsx

  → Sheet "Facebook":  Nội dung ≤300 từ

  → Sheet "Threads":   Nội dung ≤150 từ

  → Sheet "LinkedIn":  Nội dung ≤400 từ

  → Sheet "Lịch đăng": Kênh | Ngày đăng | Người đăng | Trạng thái

```



> 📌 Tên file theo R6 với prefix W2_



*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*

