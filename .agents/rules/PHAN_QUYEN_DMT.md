# QUY CHUẨN PHÂN QUYỀN & CÂY QUẢN LÝ DMT GROUP (SHEET MARINA 3)

Tài liệu này là **Nguồn dữ liệu gốc (Single Source of Truth)** về phân quyền duyệt công việc, nghiệm thu và đánh giá KPI của Tập đoàn DMT Group, được trích xuất chính thức từ file `Phân quyền mới nhất.xls` (Sheet `MARINA (3)`).

## I. NGUYÊN TẮC VẬN HÀNH
1. **Duyệt nghiệm thu (Tab 1) & Khách quan (Tab 2):**
   - Áp dụng cơ chế Hàng chờ (First-come First-served).
   - Khi bất kỳ Người quản lý nào bấm duyệt $\rightarrow$ Trạng thái chuyển thành "Đã hoàn thành / Đã duyệt" và lập tức biến mất khỏi hàng chờ duyệt.
   - Người quản lý thứ 2/3 vào sau chỉ duyệt các công việc còn lại.
2. **Tự động tính điểm KPI:**
   - Hệ thống tự động tính toán điểm KPI (A, B, C) theo công thức toán học từ tỷ trọng và kết quả công việc đã hoàn thành trong tháng. Không có xung đột chấm điểm thủ công.
3. **Quy tắc vàng về Quản lý thuộc Ban Lãnh đạo (BLĐ):**
   - Các Quản lý thuộc BLĐ (`Trần Quốc Thể`, `Đoàn Thị Ngọc Nữ`, `Đặng Ngọc Hoàng`, `Nguyễn Ngọc Tôn`, `Thái Văn Thành`, `Trần Văn Trọng`):
     + **CHỈ** nằm ở dropdown Quản lý của **BLĐ** (`Đặng Ngọc Hoàng` thuộc BLĐ, không nằm trong HĐQT).
     + **KHÔNG** nằm ở dropdown "Nhân viên" của BLĐ (phòng BLĐ không có nhân viên trực thuộc).
     + **KHÔNG** nằm ở mục Quản lý của các Ban khác (HĐQT, KT, XN DTBD, SÀN, ĐBGT, DA, BCH CT, Mỏ, XN XMTB đều không có Lãnh đạo BLĐ kiêm nhiệm).
     + Hệ thống tự động mặc định quản lý đó vẫn duyệt việc và theo dõi KPI cho các cá nhân được phân quyền thông qua `HIERARCHY_MARINA_3` và bộ lọc tập trung `setup_manager_db_filters(...)`.

---

## II. BẢNG PHÂN QUYỀN QUẢN LÝ (MANAGER -> SUBORDINATES)

### 1. Ban Lãnh đạo Tập đoàn & HĐQT
- **Đặng Thanh Bình** & **Đặng Thị Lan Ngọc** (Cấp HĐQT):
  - Toàn quyền xem và duyệt toàn hệ thống tất cả các đơn vị.
- **Trần Quốc Thể** (Tổng Giám đốc Tập đoàn), **Đoàn Thị Ngọc Nữ** (Phó TGĐ), **Nguyễn Ngọc Tôn** (Phó TGĐ):
  - *Hiện tại chưa ai quản lý / đánh giá (Cấp điều hành cao nhất).*
- **Đặng Ngọc Hoàng** (Ban Lãnh đạo DMT):
  - Quản lý / Đánh giá trực tiếp:
    + `Trần Cường` (Giám đốc Marina)
    + `Nguyễn Thị Hạnh Tiên` (Trưởng Ban HCTH Marina / Trưởng Ban HCNS)
    + `Ngô Thị Tâm` (Thư ký Sàn BĐS)
- **Trần Quốc Thể** (Tổng Giám đốc Tập đoàn):
  - Quản lý & Duyệt trực tiếp:
    + `Nguyễn Văn Bồn` (Nhân viên Ban KT - chỉ duy nhất TGĐ Trần Quốc Thể duyệt)
    + `Hồ Văn Khoa` (Giám đốc Ban CBĐT)
    + `Nguyễn Trần Thức` (Giám đốc Ban KHĐT)
    + `Mai Văn Châu` (Nhân viên XNDTBD - chỉ duy nhất TGĐ Trần Quốc Thể duyệt)
    + Ban Dự án: `Nguyễn Đình Thắng`, `Nguyễn Đình Hiếu` (TGĐ Trần Quốc Thể quản lý & duyệt việc)
- **Đoàn Thị Ngọc Nữ** (Phó TGĐ phụ trách Tài chính - Kế toán):
  - Quản lý & Duyệt trực tiếp:
    + `Đồng Thị Nguyệt Nga` (Giám đốc Ban TCKT DMT)
    *(Lưu ý: Không duyệt `Nguyễn Thị Ngọc Hà` vì chị Hà ở Cienco do TGĐ `Thái Văn Thành` duyệt)*
- **Nguyễn Ngọc Tôn** (Phó TGĐ Tập đoàn):
  - Nằm duy nhất ở vai trò Quản lý của **BLĐ DMT** (không để làm quản lý ở dropdown Ban ĐBGT).
  - Quản lý & Duyệt trực tiếp các nhân sự Ban ĐBGT:
    + `Đặng Công Nhựt`
    + `Đặng Thị Mỹ Hạnh`
    + `Đặng Thanh Quang`

---

### 2. Công ty CP Xây dựng Công trình Giao thông ĐN-MT (Cienco)
*(Lưu ý: TGĐ Thái Văn Thành và Phó TGĐ Trần Văn Trọng nằm DUY NHẤT ở mục Quản lý của **BLĐ Cienco**, không nằm rải rác ở các phòng ban khác).*
- **Thái Văn Thành** (Tổng Giám đốc Cienco):
  - Quản lý trực tiếp 9 nhân sự Cienco:
    + `Trần Văn Trọng` (Phó TGĐ Cienco)
    + `Nguyễn Thị Ngọc Hà` (PGĐ Ban TCKT Cienco)
    + `Nguyễn Thị Mỹ Phương` (PGĐ Ban HCNS Cienco)
    + Khối kỹ thuật & hiện trường Cienco: `Phạm Quang Nghĩa`, `Nguyễn Phong Trung`, `Lê Đông`, `Phạm Văn Long`, `Lê Văn Thành`, `Ngô Văn Hoàng`.
    *(Lưu ý: Công việc của `Nguyễn Văn Bồn` do TGĐ `Trần Quốc Thể` duyệt; `Đặng Hiền` do Phó TGĐ `Trần Văn Trọng` duyệt)*
- **Trần Văn Trọng** (Phó Tổng Giám đốc Cienco):
  - Quản lý trực tiếp:
    + `Lê Nho Tân` (Giám đốc mỏ)
    + `Đặng Hiền` (Xí nghiệp Xe máy Thiết bị)
    + Khối kỹ thuật & hiện trường Cienco: `Phạm Quang Nghĩa`, `Nguyễn Phong Trung`, `Lê Đông`, `Phạm Văn Long`, `Lê Văn Thành`, `Ngô Văn Hoàng`.
- **Nguyễn Thị Ngọc Hà** (PGĐ Ban TCKT Cienco):
  - Quản lý:
    + `Nguyễn Thị Như Can` (Nhân viên Ban TCKT Cienco)
- **Ban Kỹ thuật (KT) Cienco:**
  - Cả 3 nhân sự: `Phạm Quang Nghĩa`, `Lê Văn Thành`, `Ngô Văn Hoàng` đều là **Nhân viên**, đăng nhập ở quyền "Nhân viên" (không có Quản lý riêng), do Ban TGĐ Cienco quản lý và duyệt công việc.
- **Ban Chỉ huy Công trường (BCH CT) Cienco:**
  - Gồm 3 **Nhân viên**: `Nguyễn Phong Trung`, `Lê Đông`, `Phạm Văn Long`, do Ban TGĐ Cienco quản lý và duyệt công việc.
- **Nguyễn Thị Mỹ Phương** (Phó Giám đốc Ban HCNS Cienco):
  - Ở chế độ Quản lý Ban HCNS Cienco, không duyệt công việc cho ai (nhân sự `Nguyễn Hoài Trung` đã loại ra khỏi hệ thống).

---

### 3. Công ty CP DMT-Marina (Du thuyền Happy Yacht)
- **Trần Cường** (Giám đốc Marina):
  - Nhân sự duy nhất tại Marina, trực tiếp do PCT HĐQT `Đặng Ngọc Hoàng` quản lý và đánh giá; không có cấp dưới (toàn bộ nhân sự `Nguyễn Thị Hạnh Tiên`, `Nguyễn Băng Trinh`, `Lê Ngọc Tú Uyên`, `Lê Thị Hải` đã chuyển hẳn sang Cty Mẹ DMT).

---

### 4. Khối Phòng Ban Cty CP Đầu tư Đà Nẵng (Cty Mẹ)
- **Đồng Thị Nguyệt Nga** (Giám đốc Ban TCKT):
  - Quản lý & Duyệt DUY NHẤT cho:
    + `Huỳnh Thị Hoàng Hà` (Phó Giám đốc Ban TCKT)
    + `Nguyễn Thị Nhật Sang` (Nhân viên Ban TCKT)
    + `Lê Thị Hải` (Nhân viên Ban TCKT — đã đưa hẳn vào DMT để chị Nga duyệt thẳng)
- **Hồ Văn Khoa** (Giám đốc Ban CBĐT):
  - Quản lý:
    + `Phan Thị Mỹ Hạnh` (Phó Giám đốc Ban)
    + `Cao Thuỷ Tiên` (Nhân viên)
- **Nguyễn Trần Thức** (Giám đốc Ban KHĐT):
  - Quản lý:
    + `Nguyễn Đức Lợi` (Phó Giám đốc Ban)
    + `Phan Thị Kim Cúc` (Nhân viên)
    + `Trần Tin` (Nhân viên)
- **Ban Dự án (DA):**
  - Cả `Nguyễn Đình Thắng` và `Nguyễn Đình Hiếu` đều là **Nhân viên**, do TGĐ `Trần Quốc Thể` trực tiếp quản lý và duyệt công việc.
