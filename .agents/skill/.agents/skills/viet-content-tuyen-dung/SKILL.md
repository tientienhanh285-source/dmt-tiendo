---
name: viet-content-tuyen-dung
description: >
  Viết nội dung đăng tuyển đa nền tảng (Facebook, Threads, LinkedIn) từ JD có sẵn,
  đảm bảo đúng tone từng kênh, không tiết lộ lương cứng, đủ 4 thành phần bắt buộc.
  Kích hoạt khi user đề cập 'viết content tuyển dụng', 'đăng tuyển', 'bài tuyển dụng';
  trong tình huống đã có JD và cần nội dung đăng lên các kênh truyền thông.
  KHÔNG dùng để viết JD (→ viet-jd-mtcv), email nội bộ (→ soan-thu-tuyen-dung).
---

# Skill: Viết Content Tuyển Dụng

## Bước 1 — Trích xuất từ JD

Từ `JD_[MaViTri]_FINAL.docx` (hoặc từ kho `thu-vien/jd/`) lấy:
- Tên vị trí chính xác
- Top 3 yêu cầu quan trọng nhất
- Top 3 quyền lợi nổi bật
- Thông tin nộp hồ sơ ({{EMAIL_HR}} + deadline)

Từ `K5-gia-tri-cot-loi.md`: tone thương hiệu, giá trị muốn truyền tải.
Từ `K1-company-profile.md`: USP công ty cho phần giới thiệu.

---

## Bước 2 — Viết theo chuẩn từng nền tảng

### Facebook (≤300 từ)
**Tone:** Chuyên nghiệp, thân thiện, rõ ràng. Dùng emoji vừa phải (1–2 cái/đoạn).

**Cấu trúc:**
```
[HOOK] — Câu đầu gây chú ý
[GIỚI THIỆU] — Tên vị trí + {{TEN_CONG_TY}} một câu
[YÊU CẦU] — 3 bullet points
[QUYỀN LỢI] — 3 bullet points nổi bật
[CTA] — "Gửi CV về {{EMAIL_HR}} trước [deadline]"
```

**Quy tắc:** Không viết lương cứng → dùng "Thu nhập X–Y triệu" hoặc range.

**Template:** `templates/mau-content-facebook.md`

### Threads (≤150 từ)
**Tone:** Casual, gần gũi. Không dùng heading.

**Cấu trúc:**
```
[HOOK ngắn] 1–2 câu
[Vị trí + 2 yêu cầu chính]
[1–2 quyền lợi chính]
[CTA] "DM hoặc gửi CV về {{EMAIL_HR}}"
```

**Template:** `templates/mau-content-threads.md`

### LinkedIn (≤400 từ)
**Tone:** Formal, nhấn mạnh cơ hội phát triển nghề nghiệp.

**Cấu trúc:**
```
[Giới thiệu {{TEN_CONG_TY}} + tầm nhìn] 2–3 câu
[Vị trí + Mục tiêu vị trí]
[Nhiệm vụ chính] 3–4 bullet
[Yêu cầu] đầy đủ hơn Facebook
[Quyền lợi + văn hóa]
[CTA] {{EMAIL_HR}}
```

**Template:** `templates/mau-content-linkedin.md`

---

## Bước 3 — Kiểm tra trước khi xuất

- [ ] Không có mức lương cứng cụ thể
- [ ] Không có ngôn ngữ phân biệt giới tính/tuổi/ngoại hình (trừ khi JD ghi rõ)
- [ ] Mỗi bài có CTA rõ ràng
- [ ] Độ dài đúng chuẩn từng nền tảng
- [ ] Tone phù hợp từng kênh

## Templates
- `templates/mau-content-facebook.md`
- `templates/mau-content-threads.md`
- `templates/mau-content-linkedin.md`

## Registry Block

```
### viet-content-tuyen-dung
Viết content đăng tuyển chuẩn tone cho Facebook, Threads, LinkedIn từ JD.
💡 **Prompt Mẫu:** "Làm bài đăng tuyển Sales cho Facebook và LinkedIn."
```
