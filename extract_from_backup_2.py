import re
import os

def extract_pages():
    with open('app_backup_full_16_09.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    pages_dir = 'views'
    os.makedirs(pages_dir, exist_ok=True)
    
    current_page = None
    page_content = []
    
    header_imports = """import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

"""
    
    page_mapping = {
        "BẢNG TỔNG QUAN": "1_Tong_Quan.py",
        "Bảng theo dõi tiến độ": "2_Tien_Do.py",
        "Thêm / Cập Nhật": "3_Cap_Nhat.py",
        "Duyệt & Nghiệm thu": "4_Nghiem_Thu.py",
        "Duyệt việc Khách quan": "4_Nghiem_Thu.py",
        "Đánh giá KPI": "5_Danh_Gia_KPI.py",
        "Quản lý & Đối chiếu JD": "6_Quan_Ly_JD.py",
        "Quản Lý Cấu Hình": "7_Cau_Hinh.py",
        "Quản trị BSC": "8_Quan_Tri_BSC.py",
        "Lập & Duyệt KPI": "9_Lap_Duyet_KPI.py",
        "Sổ tay Hướng dẫn": "10_So_Tay.py"
    }

    # Match `if menu == "..."` or `elif menu == "..."` or `if menu in ["...", "..."]` or `elif menu in ["...", "..."]`
    menu_pattern_eq = re.compile(r'^(?:if|elif)\s+menu\s*==\s*["\'](.*?)["\']\s*:')
    menu_pattern_in = re.compile(r'^(?:if|elif)\s+menu\s+in\s+\[(.*?)\]\s*:')
    
    for line in lines:
        match_eq = menu_pattern_eq.match(line)
        match_in = menu_pattern_in.match(line)
        
        matched_str = None
        if match_eq:
            matched_str = match_eq.group(1)
        elif match_in:
            matched_str = match_in.group(1) # e.g. '"🚀 Bảng theo dõi tiến độ công việc", "📋 Bảng theo dõi tiến độ công việc"'
            
        if matched_str:
            if current_page:
                filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
                with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
                    out.write(header_imports)
                    out.write("".join(page_content))
            
            current_page = matched_str
            page_content = []
        elif current_page:
            if line.startswith("    "):
                page_content.append(line[4:])
            else:
                page_content.append(line)
                
    if current_page:
        filename = next((v for k, v in page_mapping.items() if k in current_page), "unknown.py")
        with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as out:
            out.write(header_imports)
            out.write("".join(page_content))

if __name__ == "__main__":
    extract_pages()
    print("Xong!")
