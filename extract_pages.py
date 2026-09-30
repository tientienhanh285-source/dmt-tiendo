import re
import os

def extract_pages():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    pages_dir = 'pages'
    os.makedirs(pages_dir, exist_ok=True)
    
    current_page = None
    page_content = []
    
    # Prefix imports that need to be in every page
    header_imports = """import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from core_logic import *

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

    # Regex to match `if menu == "..."` or `elif menu == "..."`
    menu_pattern = re.compile(r'^(?:if|elif)\s+menu\s*==\s*["\'](.*?)["\']\s*:')
    
    for line in lines:
        match = menu_pattern.match(line)
        if match:
            # Save previous page
            if current_page:
                filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
                filename = filename.replace("?", "").replace(" ", "_")
                with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
                    out.write(header_imports)
                    out.write("".join(page_content))
            
            # Start new page
            current_page = match.group(1)
            page_content = []
        elif current_page:
            # We are inside a page block. Remove 1 level of indentation (4 spaces) if applicable
            if line.startswith("    "):
                page_content.append(line[4:])
            else:
                page_content.append(line)
                
    # Save last page
    if current_page:
        filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
        filename = filename.replace("?", "").replace(" ", "_")
        with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
            out.write(header_imports)
            out.write("".join(page_content))

if __name__ == "__main__":
    extract_pages()
    print("Xong!")
