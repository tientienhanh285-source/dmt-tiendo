---
description: Tổng hợp kết quả phỏng vấn, ra quyết định trúng tuyển và tạo email offer/từ chối. Kích hoạt sau khi tất cả buổi PV hoàn thành và phiếu đã được điền.
---

# W5 — ĐÁNH GIÁ KẾT QUẢ & THÔNG BÁO

> **Trigger:** User yêu cầu tổng hợp kết quả sau khi phiếu PV đã được điền đầy đủ

---

## INPUT

| Nguồn | Dùng để |
|-------|---------|
| `K3-bang-luong-phuc-loi.md` | Phúc lợi điền vào email offer |
| `K6-quy-dinh-tuyen-dung.md §3, §5` | Thẩm quyền offer + SLA gửi thư |
| Files `W4_..._PV_*.xlsx` trong dự án | Phiếu PV đã điền |

> ⚠️ Phiếu chưa điền xong → cảnh báo, bỏ qua UV đó
> ⚠️ N1 và N2 bất đồng → gắn cờ *"Cần họp thống nhất"*, không tự kết luận

---

## PROCESS

**B1.** Gọi **skill `danh-gia-phong-van`** (Chế độ 2 — Tổng hợp)
→ Đọc từng file W4_..._PV_*.xlsx → tính điểm TB
→ Áp điều kiện: ≥{{DIEM_TRUNG_TUYEN_PV}}đ + N1 và N2 đều "Đề xuất" → Trúng tuyển
→ Kiểm tra R2.1/R2.2 → gắn cờ nếu vượt khung
→ Xuất: `W5_[DATE]_KQ_[MaViTri]-[Dot]_v1.xlsx`

**B2.** Với UV Trúng tuyển: gọi **skill `soan-thu-tuyen-dung`** (Email 3: Offer)
→ Lương = Lương đề xuất trong phiếu PV (đã qua R2.1)
→ Phúc lợi từ K3
→ Áp R3.1 (24h), R3.2, R3.3

**B3.** Với UV Không đạt: gọi **skill `soan-thu-tuyen-dung`** (Email 4: Từ chối)
→ Không lý do, không điểm số, để ngỏ tương lai (R3.3)

**B4.** Kiểm tra SLA R3.1 — tất cả email tạo trong 24h sau quyết định

---

## OUTPUT

Lưu vào: `du-an/[YYYYMM]-[TenDot]/` (phẳng, prefix W5_)

```
W5_[DATE]_KQ_[MaViTri]-[Dot]_v1.xlsx   (3 sheet: Tổng hợp | Xếp hạng | Cảnh báo)
W5_[DATE]_OL_[TenUV]_FINAL.md          ← Offer letter (1 file/UV trúng tuyển)
W5_[DATE]_TC_[TenUV]_v1.md             ← Email từ chối (1 file/UV không đạt)
```

> ⚡ Sau W5, gọi **W6** cho UV đã xác nhận offer
> ⚡ Sau W6, gọi **W0-Process D** để cập nhật _MASTER.csv

*Cập nhật lần cuối: {{NGAY_TAO}} | Phiên bản: v1*
