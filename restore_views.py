import os

# First, run the original extract_pages.py logic to get the others
def extract_pages():
    with open('app_backup_full_16_09.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    pages_dir = 'views'
    os.makedirs(pages_dir, exist_ok=True)
    
    current_page = None
    page_content = []
    
    header_imports = """import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from core_logic import *

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()
"""
    
    page_mapping = {
        "BẢNG TỔNG QUAN": "1_Tong_Quan.py",
        "Bảng theo dõi tiến độ": "2_Tien_Do.py",
        "Thêm / Cập Nhật": "3_Cap_Nhat.py",
        "Duyệt & Nghiệm thu": "4_Nghiem_Thu.py",
        "Duyệt việc Khách quan": "4_Nghiem_Thu_KQ.py",
        "Đánh giá KPI": "5_Danh_Gia_KPI.py",
        "Quản lý & Đối chiếu JD": "6_Quan_Ly_JD.py",
        "Quản Lý Cấu Hình": "7_Cau_Hinh.py",
        "Quản trị BSC": "8_Quan_Tri_BSC.py",
        "Lập & Duyệt KPI": "9_Lap_Duyet_KPI.py",
        "Sổ tay Hướng dẫn": "10_So_Tay.py"
    }

    import re
    menu_pattern = re.compile(r'^(?:if|elif)\s+menu\s*==\s*["\'](.*?)["\']\s*:')
    
    for line in lines:
        match = menu_pattern.match(line)
        if match:
            if current_page:
                filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
                filename = filename.replace("?", "").replace(" ", "_")
                with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
                    out.write(header_imports)
                    out.write("".join(page_content))
            
            current_page = match.group(1)
            page_content = []
        elif current_page:
            if line.startswith("    "):
                page_content.append(line[4:])
            else:
                page_content.append(line)
                
    if current_page:
        filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
        filename = filename.replace("?", "").replace(" ", "_")
        with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
            out.write(header_imports)
            out.write("".join(page_content))

extract_pages()

# Second, extract the missing ones specifically from the exact line numbers
with open('app_backup_full_16_09.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header2 = """import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from core_logic import *

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Mock df if not present
if 'display_df' not in locals():
    display_df = read_db()
"""

def extract_missing(start_line, end_line, filename):
    content = lines[start_line-1 : end_line]
    cleaned = []
    for line in content:
        if line.startswith("    "):
            cleaned.append(line[4:])
        else:
            cleaned.append(line)
            
    with open(os.path.join('views', filename), 'w', encoding='utf-8') as out:
        out.write(header2)
        out.write("".join(cleaned))

extract_missing(2589, 2746, '1_Tong_Quan.py')
extract_missing(2003, 2587, '2_Tien_Do.py')
extract_missing(4341, 4525, '4_Nghiem_Thu.py')

print("Khôi phục thành công!")
