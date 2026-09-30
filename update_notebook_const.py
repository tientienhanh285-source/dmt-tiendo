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
    "## 5. Phân tích KPI chuyên biệt cho Ngành Xây dựng, Kỹ thuật & Giải tỏa Đền bù\n",
    "\n",
    "Với đặc thù dự án xây dựng, giải phóng mặt bằng (GPMB) và kỹ thuật hạ tầng, dự án thường có ngân sách lớn (CAPEX), tiến độ phụ thuộc nhiều vào yếu tố bên ngoài (pháp lý, chính quyền, người dân) và phải tuân thủ nghiêm ngặt theo các giai đoạn (Milestones). Việc áp dụng KPI cần tập trung vào **Quản trị Rủi ro (Risk Management)**, **Pháp lý/GPMB** và **Hiệu quả thi công** thay vì các chỉ số Agile/Khách hàng.\n",
    "\n",
    "### 5.1. Nhóm KPI Quản lý Giải phóng mặt bằng (GPMB) & Pháp lý\n",
    "Khâu này thường xuyên bị \"Có vướng mắc\". KPI không nên chỉ là \"Đã xong thủ tục chưa?\" mà phải lượng hóa:\n",
    "- **Tỷ lệ hộ dân ký biên bản bàn giao / Tổng số hộ (%):** Đo lường trực tiếp hiệu quả của team đền bù.\n",
    "- **Tiến độ giải ngân vốn đền bù:** Tỷ lệ % số tiền đã chi trả thành công so với ngân sách GPMB được duyệt.\n",
    "- **Thời gian trung bình xử lý khiếu nại (Lead time of grievance resolution):** Số ngày từ lúc nhận đơn thư đến lúc giải quyết xong.\n",
    "- **Tỷ lệ hồ sơ pháp lý được phê duyệt đúng hạn (Right-First-Time):** Đánh giá năng lực của ban pháp lý/dự án khi làm việc với cơ quan nhà nước.\n",
    "\n",
    "### 5.2. Nhóm KPI Quản lý Thi công & Kỹ thuật (Áp dụng EVM Khối lượng)\n",
    "- **Tỷ lệ hoàn thành khối lượng (Physical Progress %):** Số lượng cọc đã ép, khối lượng bê tông đã đổ, hoặc số km đường đã thảm nhựa.\n",
    "- **Chỉ số Hiệu suất Tiến độ (SPI) và Chi phí (CPI) trong EVM:**\n",
    "  - *Ví dụ:* Kế hoạch tháng này phải tiêu hết 10 tỷ (PV) và hoàn thành 20% móng. Thực tế làm được 15% móng (EV = 7.5 tỷ) nhưng tiêu hết 9 tỷ (AC) => Trễ tiến độ (SPI < 1) và Vượt chi phí (CPI < 1).\n",
    "- **Tỷ lệ Rework (Làm lại) / Sai sót kỹ thuật:** Khối lượng phải đập đi làm lại do lỗi kỹ thuật tư vấn/thi công.\n",
    "- **An toàn Lao động (HSE):** Số ngày không xảy ra tai nạn lao động (Zero Lost Time Injury).\n",
    "\n",
    "### 5.3. Xử lý Trạng thái \"Có vướng mắc\" trong Xây dựng/GPMB\n",
    "- Trong xây dựng, vướng mắc (mưa bão, dân không nhận tiền) là chuyện bình thường. Do đó, hệ thống KPI cần có **Tiêu chí loại trừ (Excusable Delays)**.\n",
    "- **Quy tắc:** Nếu vướng mắc do khách quan (Thiên tai, Chính quyền chậm duyệt) => Không trừ điểm KPI tiến độ của cá nhân, nhưng yêu cầu KPI về **\"Tốc độ báo cáo và đề xuất phương án giải quyết\"**.\n",
    "- Nếu vướng mắc do chủ quan (quên nộp hồ sơ, thi công sai bản vẽ) => Trừ 30-50% điểm KPI của hạng mục đó."
   ]
  }
]

notebook['cells'].extend(new_cells)

with open("Nghien_Cuu_KPI_DMT.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
