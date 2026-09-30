import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# NGHIÊN CỨU & ĐỀ XUẤT MÔ HÌNH KPI GẮN VỚI CÔNG VIỆC TẠI DOANH NGHIỆP\n",
    "\n",
    "Tài liệu này phân tích thực trạng, khó khăn và đề xuất mô hình đánh giá KPI chuyên sâu, kết hợp giữa Quản lý Công việc (Task-based) và Thẻ điểm cân bằng (Balanced Scorecard - BSC) hoặc OKR để phù hợp với bối cảnh doanh nghiệp."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Phân Tích Thực Trạng & Khó Khăn Hiện Tại\n",
    "\n",
    "Dựa trên các dữ liệu và quy trình hiện có (như báo cáo vướng mắc, đánh giá tiến độ): \n",
    "\n",
    "- **Đánh giá mang tính Cảm tính / Checklist:** Việc chỉ đánh giá dựa trên trạng thái (Đã hoàn thành / Trễ hạn / Có vướng mắc) dẫn đến tình trạng nhân viên chỉ làm để \"đủ số lượng\" mà bỏ qua chất lượng thực tế (Outcome).\n",
    "- **Xử lý Vướng mắc (Bottlenecks):** Nhiều công việc bị kẹt ở trạng thái \"Có vướng mắc\" nhưng thiếu cơ chế leo thang (escalation) hoặc phân tích nguyên nhân gốc rễ, làm sai lệch kết quả KPI tổng thể.\n",
    "- **Thiếu Tỷ trọng (Weighting) Rõ ràng:** Một công việc hành chính nhỏ đôi khi được tính ngang bằng với một dự án mang lại doanh thu lớn.\n",
    "- **Chưa liên kết với Mục tiêu chiến lược:** Các công việc (Tasks) chưa được mapping (gắn kết) rõ ràng vào các góc độ chiến lược của công ty (Ví dụ: BSC - Tài chính, Khách hàng, Vận hành, Phát triển)."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Đề Xuất Mô Hình KPI Phù Hợp: \"Hybrid Task-BSC\"\n",
    "\n",
    "Mô hình này không loại bỏ việc giao việc hàng ngày, mà nâng cấp nó lên:\n",
    "1. **Phân loại Công việc theo 4 khía cạnh BSC:** Mỗi công việc giao xuống phải thuộc 1 trong 4 nhóm (Tài chính, Khách hàng, Quy trình nội bộ, Học tập/Phát triển).\n",
    "2. **Hệ số Độ khó / Tỷ trọng (Weight):** Công việc A (Tỷ trọng 30%), Công việc B (Tỷ trọng 5%).\n",
    "3. **Tiêu chí Đánh giá (Rubric):** Không chỉ \"Xong/Chưa xong\" mà đánh giá theo (Tiến độ - 40%, Chất lượng - 60%).\n",
    "4. **Cơ chế trừ điểm khi Trễ hạn / Vướng mắc do chủ quan:** Trễ hạn trừ 10% điểm của task đó."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# Mock data: Mô phỏng dữ liệu KPI theo mô hình mới\n",
    "data = {\n",
    "    'TenCongViec': ['Mở rộng thị trường', 'Bảo trì server', 'Đào tạo nhân sự', 'Cập nhật báo cáo', 'Sửa lỗi phần mềm'],\n",
    "    'NhomBSC': ['Khách hàng', 'Quy trình', 'Học tập', 'Quy trình', 'Quy trình'],\n",
    "    'TyTrong(%)': [40, 20, 15, 10, 15],\n",
    "    'TienDo(%)': [80, 100, 100, 50, 100],\n",
    "    'DiemChatLuong (1-10)': [8, 9, 7, 5, 10],\n",
    "    'TrangThai': ['Đang thực hiện', 'Hoàn thành', 'Hoàn thành', 'Trễ hạn', 'Hoàn thành']\n",
    "}\n",
    "\n",
    "df = pd.DataFrame(data)\n",
    "df"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.1 Thuật toán Tính điểm KPI Tổng hợp\n",
    "Điểm của mỗi task = Tiêu chí Tiến độ * TyTrong + Tiêu chí Chất lượng * TyTrong\n",
    "Ở đây ta giả sử: Điểm KPI = (TienDo/100 * 0.4 + DiemChatLuong/10 * 0.6) * TyTrong"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calculate_kpi(row):\n",
    "    # Tính điểm chuẩn hóa trên 100 cho từng task\n",
    "    score = (row['TienDo(%)'] / 100.0 * 0.4) + (row['DiemChatLuong (1-10)'] / 10.0 * 0.6)\n",
    "    \n",
    "    # Áp dụng hình phạt nếu trễ hạn (giảm 20% số điểm)\n",
    "    if row['TrangThai'] == 'Trễ hạn':\n",
    "        score *= 0.8\n",
    "        \n",
    "    # Điểm đóng góp vào tổng KPI (tối đa bằng TyTrong)\n",
    "    return score * row['TyTrong(%)']\n",
    "\n",
    "df['Diem_KPI_Gop'] = df.apply(calculate_kpi, axis=1)\n",
    "\n",
    "total_kpi = df['Diem_KPI_Gop'].sum()\n",
    "print(f\"Tổng điểm KPI cuối cùng của nhân viên: {total_kpi:.2f} / 100\")\n",
    "\n",
    "df[['TenCongViec', 'TyTrong(%)', 'TrangThai', 'Diem_KPI_Gop']]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Khuyến nghị Kế hoạch Triển khai (Roadmap)\n",
    "\n",
    "1. **Giai đoạn 1 (Tháng 1-2): Số hóa Task Management.** (Công ty đang ở bước này). Chuyển hoàn toàn giao việc từ Zalo/Excel lên phần mềm. Bắt buộc có Hạn chót và Ghi chú vướng mắc.\n",
    "2. **Giai đoạn 2 (Tháng 3-4): Áp dụng Tỷ trọng & BSC.** Các Trưởng bộ phận khi giao việc phải gán Tỷ trọng (%) và phân loại theo BSC.\n",
    "3. **Giai đoạn 3 (Tháng 5-6): Đánh giá chất lượng 360 độ.** Thay vì tự đánh giá, phần mềm có nút \"Yêu cầu nghiệm thu\", người giao việc (hoặc QA) sẽ chấm điểm chất lượng (1-10) làm cơ sở tính KPI cuối.\n",
    "4. **Giai đoạn 4: Liên kết Thưởng/Phạt tự động.** Xuất báo cáo từ phần mềm trực tiếp sang hệ thống Tính lương (C&B)."
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("Nghien_Cuu_KPI_DMT.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
