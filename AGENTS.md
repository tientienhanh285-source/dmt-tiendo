# DMT GROUP — PROJECT MEMORY & GUIDELINES

## 1. Single Source of Truth về Phân quyền & Quản lý
Toàn bộ logic phân quyền, cấp trên - cấp dưới, nghiệm thu công việc và đánh giá KPI của hệ thống DMT Group tuân thủ nghiêm ngặt theo Sheet `MARINA (3)` trong file `Phân quyền.xls`.

Chi tiết quy chuẩn phân quyền được lưu trữ tại:
👉 [.agents/rules/PHAN_QUYEN_DMT.md](file:///.agents/rules/PHAN_QUYEN_DMT.md)

### Các nguyên tắc cốt lõi:
1. **Ban Lãnh đạo cao nhất:**
   - `Đặng Thanh Bình`, `Đặng Thị Lan Ngọc`: HĐQT toàn quyền xem và duyệt toàn bộ hệ thống.
   - `Trần Quốc Thể`, `Đoàn Thị Ngọc Nữ`, `Nguyễn Ngọc Tôn`: Cấp điều hành cao nhất, hiện tại chưa ai quản lý.
2. **Quản lý Marina & BĐS:**
   - `Đặng Ngọc Hoàng`: Quản lý trực tiếp `Trần Cường`, `Nguyễn Thị Hạnh Tiên`, `Ngô Thị Tâm`.
   - `Trần Cường`: Quản lý trực tiếp `Lê Thị Hải`.
   - `Nguyễn Thị Hạnh Tiên`: Quản lý trực tiếp `Nguyễn Băng Trinh`, `Lê Ngọc Tú Uyên`.
3. **Quản lý Cienco & Kỹ thuật:**
   - `Thái Văn Thành`: Quản lý 11 nhân sự Cienco và Ban KT (`Trần Văn Trọng`, `Nguyễn Thị Ngọc Hà`, `Nguyễn Thị Mỹ Phương`, `Nguyễn Văn Bồn`, `Phạm Quang Nghĩa`, `Nguyễn Phong Trung`, `Lê Đông`, `Phạm Văn Long`, `Lê Văn Thành`, `Ngô Văn Hoàng`, `Đặng Hiền`).
   - `Trần Văn Trọng`: Quản lý `Lê Nho Tân` và 7 nhân sự kỹ thuật, hiện trường.
   - `Phạm Quang Nghĩa`: Quản lý `Mai Văn Châu`.
4. **Quản lý Cty Mẹ:**
   - `Đồng Thị Nguyệt Nga`: Quản lý `Huỳnh Thị Hoàng Hà`, `Nguyễn Thị Nhật Sang`, `Lê Thị Hải` (Marina - liên công ty).
   - `Nguyễn Thị Ngọc Hà`: Quản lý liên đơn vị (`Huỳnh Thị Hoàng Hà`, `Lê Thị Hải`, `Nguyễn Thị Như Can`).
   - `Hồ Văn Khoa`: Quản lý `Phan Thị Mỹ Hạnh`, `Phan Thị Kim Cúc`.
   - `Nguyễn Trần Thức`: Quản lý `Nguyễn Đức Lợi`, `Cao Thuỷ Tiên`, `Trần Tin`.
   - `Nguyễn Ngọc Tôn`: Quản lý Ban ĐBGT (`Đặng Công Nhựt`, `Đặng Thị Mỹ Hạnh`, `Đặng Thanh Quang`).
5. **Cơ chế duyệt & lọc dữ liệu:**
   - Không được dùng điều kiện lọc `DonVi` cứng khi quản lý có cấp dưới ở công ty khác (cross-company). Luôn sử dụng hàm tập trung `setup_manager_db_filters(...)`.
   - Hàng chờ duyệt nghiệm thu hoạt động theo cơ chế FIFO (công việc đã duyệt biến mất khỏi danh sách chờ, người quản lý khác vào sau chỉ thấy việc còn lại).
   - Tuyệt đối không thêm các khối override cục bộ (`GLOBAL OVERRIDES`) ở các views. Mọi logic phân quyền phải truy xuất từ `HIERARCHY_MARINA_3` trong `core_logic.py`.
