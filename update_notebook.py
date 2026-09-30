import json

try:
    with open("Nghien_Cuu_KPI_DMT.ipynb", "r", encoding="utf-8") as f:
        notebook = json.load(f)
except FileNotFoundError:
    notebook = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}

new_cells = [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "---\n",
    "## 4. Nghiên cứu Mở rộng: Các Mô hình KPI chuyên biệt cho Quản lý Dự án (Project-based KPIs)\n",
    "\n",
    "Nếu công ty hoạt động mạnh theo hình thức dự án (phát triển phần mềm, triển khai khách hàng, xây dựng,...), mô hình Task-BSC ở trên có thể chưa phản ánh đủ bức tranh tổng thể về tài nguyên và ngân sách. Dưới đây là 3 mô hình/giải pháp KPI dự án tiên tiến có thể áp dụng hoặc kết hợp:\n",
    "\n",
    "### 4.1. Mô hình Quản lý Giá trị Thu được (Earned Value Management - EVM)\n",
    "- **Đặc điểm:** Đây là tiêu chuẩn vàng trong quản trị dự án. Thay vì chỉ hỏi \"Đã làm xong việc chưa?\" (như Task-based), EVM hỏi \"Với số thời gian/tiền đã bỏ ra, chúng ta đã tạo ra được bao nhiêu giá trị thực tế?\".\n",
    "- **Các chỉ số KPI chính (EVM Metrics):**\n",
    "  - **SPI (Schedule Performance Index):** Chỉ số hiệu suất tiến độ. (SPI > 1: Vượt tiến độ; SPI < 1: Trễ tiến độ).\n",
    "  - **CPI (Cost Performance Index):** Chỉ số hiệu suất chi phí/nhân công. (CPI > 1: Tiết kiệm; CPI < 1: Vượt ngân sách).\n",
    "- **Phù hợp cho:** Các dự án lớn có ngân sách hoặc số giờ công (man-hours) được định lượng rõ ràng.\n",
    "\n",
    "### 4.2. Mô hình KPI Tam Giác Vàng (Time - Cost - Quality/Scope)\n",
    "- **Đặc điểm:** Đánh giá KPI của thành viên/team dự án dựa trên sự cân bằng của 3 yếu tố khắt khe này.\n",
    "- **Cách tính điểm KPI:**\n",
    "  - *Time (Thời gian):* Số ngày hoàn thành thực tế so với Baseline (Kế hoạch).\n",
    "  - *Cost (Chi phí/Nỗ lực):* Số giờ công đã tiêu tốn so với kế hoạch.\n",
    "  - *Quality (Chất lượng):* Số lượng lỗi (Bugs/Defects), hoặc tỷ lệ Rework (Làm lại).\n",
    "- **Phù hợp cho:** Các dự án linh hoạt nhưng có yêu cầu khắt khe về chất lượng bàn giao.\n",
    "\n",
    "### 4.3. Mô hình Agile / Scrum Metrics (KPI theo chặng - Sprints)\n",
    "- **Đặc điểm:** Bỏ qua các KPI cồng kềnh, đánh giá team dựa trên tốc độ và khả năng thích ứng.\n",
    "- **Các chỉ số KPI chính:**\n",
    "  - **Velocity (Tốc độ):** Số lượng Story Points (Điểm độ khó) team giải quyết được trong 1 tuần/tháng.\n",
    "  - **Say/Do Ratio:** Tỷ lệ Cam kết / Thực hiện (Cam kết làm 10 việc, làm được 8 việc => 80%).\n",
    "  - **Lead Time / Cycle Time:** Thời gian từ lúc nhận yêu cầu đến lúc khách hàng dùng được.\n",
    "- **Phù hợp cho:** Team R&D, Phát triển phần mềm, Marketing - nơi yêu cầu thay đổi liên tục."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Code mô phỏng đánh giá KPI Dự án theo mô hình EVM (Earned Value Management)\n",
    "import pandas as pd\n",
    "\n",
    "project_data = {\n",
    "    'TenDuAn': ['Dự án ERP', 'App Mobile KH', 'Marketing Q3'],\n",
    "    'NganSach_GioCong (PV)': [500, 300, 200],      # Planned Value: Số giờ công dự kiến\n",
    "    'GiaTri_HoanThanh (EV)': [200, 300, 150],      # Earned Value: Giá trị quy đổi thực tế đã làm\n",
    "    'ThucChi_GioCong (AC)': [250, 280, 200]        # Actual Cost: Số giờ thực tế đã bỏ ra\n",
    "}\n",
    "\n",
    "df_project = pd.DataFrame(project_data)\n",
    "\n",
    "# Tính toán KPI dự án\n",
    "df_project['SPI (Tiến độ)'] = df_project['GiaTri_HoanThanh (EV)'] / df_project['NganSach_GioCong (PV)']\n",
    "df_project['CPI (Chi phí)'] = df_project['GiaTri_HoanThanh (EV)'] / df_project['ThucChi_GioCong (AC)']\n",
    "\n",
    "def danh_gia_du_an(row):\n",
    "    status = []\n",
    "    if row['SPI (Tiến độ)'] < 1.0:\n",
    "        status.append('🔴 Trễ tiến độ')\n",
    "    else:\n",
    "        status.append('🟢 Đúng/Vượt tiến độ')\n",
    "        \n",
    "    if row['CPI (Chi phí)'] < 1.0:\n",
    "        status.append('🔴 Vượt ngân sách(Giờ công)')\n",
    "    else:\n",
    "        status.append('🟢 Tiết kiệm(Giờ công)')\n",
    "    return ' | '.join(status)\n",
    "\n",
    "df_project['DanhGia_KPI'] = df_project.apply(danh_gia_du_an, axis=1)\n",
    "df_project"
   ]
  }
]

notebook['cells'].extend(new_cells)

with open("Nghien_Cuu_KPI_DMT.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
