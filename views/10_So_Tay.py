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

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



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
    **1️⃣ Xem xét và Đánh giá lý do Khách quan**
    - 🖱️ Vào mục **✅ Duyệt việc Khách quan**.
    - Hệ thống liệt kê các công việc nhân viên báo cáo trễ hạn với lý do **Khách quan**.
    - Bạn xem xét giải trình, click trực tiếp vào ô *Mức độ KPI ghi nhận* để chọn điểm phù hợp (Miễn trừ, 50%, 80%, 90%...).
    - Nhấn **💾 Lưu toàn bộ phê duyệt** ở cuối danh sách.
    """)
    
    st.info("""
    **2️⃣ Xem Báo cáo Xếp loại KPI (Ngày 1-3 đầu tháng)**
    - 🕒 **Thời gian:** Từ ngày 1 đến ngày 3 hàng tháng.
    - 🎯 **Mục đích:** Xác nhận điểm số KPI của tháng trước để Phòng HCNS lưu kết quả.
    - Xem biểu đồ tổng quan và Bảng dữ liệu tự động Xếp loại cho từng nhân sự.
    """)

with tab_tc:
    st.info("""
    **🌟 TIÊU CHÍ ĐÁNH GIÁ VÀ XẾP LOẠI KPI**
    
    🧮 **1. Công thức tính điểm KPI Tổng:**
    > :blue[**Điểm KPI**] = (:green[**Điểm trung bình công việc Định kỳ**] × **70%**) + (:orange[**Điểm trung bình công việc Giao ban**] × **30%**) + :red[**Điểm thưởng/phạt**]
    
    *(Lưu ý: Nếu không có công việc Giao ban, hệ thống sẽ tự động điều chỉnh 100% trọng số cho công việc Định kỳ).*
    
    📊 **2. Phân loại và Quy đổi Điểm Xếp loại:**
    - Tổng điểm **> 100**: Xếp loại **A\*** (Xuất sắc - > 100 điểm): Đạt mức 110–120% lương, nhằm khích lệ tinh thần làm việc vượt trội.
    - Tổng điểm **> 91**: Xếp loại **A** (Xuất sắc)
    - Tổng điểm **> 81**: Xếp loại **B** (Tốt)
    - Tổng điểm **> 71**: Xếp loại **C** (Khá)
    - Tổng điểm **<= 71**: Xếp loại **D** (Kém)
    
    ⚖️ **3. Về Điểm Thưởng / Phạt:**
    - **Cộng điểm (+):** Áp dụng cho các công việc hoàn thành xuất sắc vượt tiến độ, hoặc có sáng kiến mang lại hiệu quả cao.
    - **Trừ điểm (-):** Áp dụng khi vi phạm nội quy, chậm trễ báo cáo, hoặc có sai sót nghiệp vụ gây ảnh hưởng.
    - *Quản lý trực tiếp hoặc HCNS sẽ rà soát và cập nhật quỹ điểm Thưởng/Phạt này trước thời điểm chốt sổ cuối tháng.*
    """)

