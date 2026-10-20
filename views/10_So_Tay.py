import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

st.markdown("## 📖 Sổ tay Hướng dẫn sử dụng phần mềm KPI")
st.markdown("Chọn vai trò của bạn để xem hướng dẫn chi tiết:")

tab_nv, tab_ql, tab_tc = st.tabs(["👨‍💼 Hướng dẫn Nhân viên", "👔 Hướng dẫn Quản lý", "🌟 Tiêu chí Đánh giá & Xếp loại"])

with tab_nv:
    st.info("""
    **1️⃣ Đăng ký công việc (Đầu tháng)**
    - 🕒 **Thời gian:** Từ ngày 30 tháng trước đến ngày 3 tháng này.
    - 🖱️ **Thao tác:** Vào mục **Thêm / Cập nhật công việc**.
    - 📝 **Nội dung:** Tự khai báo các đầu việc chính trong tháng. Hệ thống sẽ tự động tính toán và chia đều tỷ trọng KPI cho tất cả các công việc của bạn.
    """)
    
    st.success("""
    **2️⃣ Báo cáo tiến độ và Hoàn thành**
    - 🖱️ Khi thực hiện xong công việc, vào mục **Thêm / Cập nhật công việc**, đánh dấu tick vào ô **☑️ Công việc đã hoàn thành**.
    - 📌 **Lưu ý quan trọng:** Bạn cần dán kèm Link minh chứng kết quả (từ Google Drive, OneDrive...) hoặc ghi tên/số hiệu văn bản vào ô khai báo kết quả.
    """)
    
    st.warning("""
    **3️⃣ Xử lý Trễ hạn / Có vướng mắc**
    - Nếu rủi ro trễ hạn, đổi trạng thái thành **Có vướng mắc** và ghi rõ lý do tại ô *Giải trình / Đề xuất*.
    - 🌍 **Do khách quan**: Hệ thống gửi yêu cầu để Quản lý xem xét lý do và đánh giá lại mức điểm (50%, 80%, 90%...).
    - 🌧️ **Do chủ quan**: Công việc bị tính là chưa hoàn thành và nhận 0 điểm KPI.
    """)
    
    st.error("""
    **4️⃣ Theo dõi công việc hàng ngày**
    - 🖱️ Vào mục **Bảng theo dõi tiến độ công việc**.
    - Xem thẻ **CÔNG VIỆC TỚI HẠN** để biết việc nào sắp đến hạn (màu vàng) hoặc đã trễ hạn (màu đỏ) để ưu tiên xử lý.
    """)
    
with tab_ql:
    st.success("""
    **1️⃣ Xem xét và Duyệt việc hoàn thành**
    - 🖱️ Vào mục **✅ Duyệt nghiệm thu**.
    - Hệ thống liệt kê các công việc nhân viên đã đánh dấu hoàn thành cần quản lý nghiệm thu.
    - Bạn xem xét kết quả/minh chứng, chọn kết quả **Đạt** hoặc **Không đạt**, hoặc để lại nhận xét.
    - Nhấn **💾 Lưu toàn bộ phê duyệt** ở cuối danh sách.
    """)

    st.success("""
    **2️⃣ Xem xét và Đánh giá lý do Khách quan**
    - 🖱️ Vào mục **✅ Duyệt việc Khách quan** (nếu có công việc trễ hạn do nguyên nhân khách quan).
    - Hệ thống liệt kê các công việc nhân viên báo cáo trễ hạn với lý do **Khách quan**.
    - Bạn xem xét giải trình, click trực tiếp vào ô *Mức độ KPI ghi nhận* để chọn điểm phù hợp (Miễn trừ, 50%, 80%, 90%...).
    - Nhấn **💾 Lưu toàn bộ phê duyệt** ở cuối danh sách.
    """)
    
    st.info("""
    **3️⃣ Xem Báo cáo Xếp loại KPI (Ngày 1-3 đầu tháng)**
    - 🕒 **Thời gian:** Từ ngày 1 đến ngày 3 hàng tháng.
    - 🎯 **Mục đích:** Xác nhận điểm số KPI của tháng trước để Phòng HCNS lưu kết quả.
    - Xem biểu đồ tổng quan và Bảng dữ liệu tự động Xếp loại cho từng nhân sự.
    """)
    
    st.warning("""
    **4️⃣ Báo cáo Đánh giá và Xếp loại KPI cuối quý**
    - 🕒 **Thời gian:** Đầu quý sau (khi tổ chức họp KPI).
    - 🎯 **Mục đích:** Xuất báo cáo tổng hợp các công việc đã thực hiện trong quý vừa qua để làm tài liệu cho cuộc họp đánh giá, xếp loại KPI đầu quý sau.
    - Xem biểu đồ tổng quan, dữ liệu thống kê theo quý để đưa ra các quyết định khen thưởng hoặc cải thiện hiệu suất.
    """)

with tab_tc:
    st.info("""
    **🌟 TIÊU CHÍ ĐÁNH GIÁ VÀ XẾP LOẠI KPI**
    
    🎯 **1. Điểm gốc:** 
    > :blue[**100 điểm/người/tháng.**]
    
    🧮 **2. Điểm công việc:** 
    > :green[**100 điểm**] được chia đều trên tổng số nhiệm vụ phát sinh trong tháng.
    
    📊 **3. Công thức tính điểm:**
    > :orange[**Tổng điểm = 100 điểm - Điểm phạt + Điểm thưởng.**]
    
    ⚠️ **4. Một số trường hợp trừ điểm theo quy chế:**
    - Không cập nhật báo cáo KPI đúng hạn: trừ **3 điểm/lần**.
    - Không hoàn thành tốt liên tục/bị cảnh cáo: trừ **10 điểm** theo quy chế.
    - Các trường hợp vi phạm nội quy, đi trễ/về sớm, quên chấm công... thực hiện trừ điểm theo quy chế hiện hành.
    
    🎁 **5. Điểm thưởng:** 
    - Áp dụng đối với trường hợp hoàn thành xuất sắc công việc trọng điểm theo đánh giá/đề xuất của Quản lý.
    """)

