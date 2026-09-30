import os

with open('app_backup_full_16_09.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = """import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from core_logic import *

# Khôi phục các biến dùng chung nếu có
if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config(selected_company)
db_conn = get_gsheets_conn()

"""

def extract(start_line, end_line, filename):
    # lines are 0-indexed, start_line is 1-indexed
    content = lines[start_line-1 : end_line]
    # remove 1 level of indent (4 spaces) if needed
    cleaned = []
    for line in content:
        if line.startswith("    "):
            cleaned.append(line[4:])
        else:
            cleaned.append(line)
            
    with open(os.path.join('views', filename), 'w', encoding='utf-8') as out:
        out.write(header)
        out.write("".join(cleaned))

extract(2589, 2746, '1_Tong_Quan.py')
extract(2003, 2587, '2_Tien_Do.py')
extract(4341, 4525, '4_Nghiem_Thu.py')

print("Extracted missing views!")
