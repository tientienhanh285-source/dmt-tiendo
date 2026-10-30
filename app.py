import streamlit as st
import importlib
import core_logic
importlib.reload(core_logic)
from core_logic import *

# Force calendar header visible to fix caching issues
st.markdown('''
    <style>
        div[data-baseweb="calendar"] header {
            visibility: visible !important;
            display: flex !important;
        }
    </style>
''', unsafe_allow_html=True)

from datetime import date
import kpi_reports
import pandas as pd
import os
import re
import json
import plotly.express as px
import sqlite3

# Persistent Settings



try:
    import google.generativeai as genai
except ImportError:
    st.error("Thư viện google-generativeai chưa được cài đặt. Vui lòng kiểm tra file requirements.txt.")

from datetime import datetime, date, timedelta


from contextlib import contextmanager
import time

st.set_page_config(
    page_title="Hệ thống Quản lý Tiến độ Công việc & KPI - DMT Group",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chống dịch tự động của Google (gây lỗi chính tả) và chuẩn hóa Font chữ tiếng Việt
st.markdown("""
    <style>
        /* Cố định Font chuẩn hỗ trợ đầy đủ tiếng Việt và tăng kích thước chữ an toàn (không ghi đè icon) */
        html, body, p, label, div.stMarkdown, div.stText {
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 1.08rem;
        }
        /* Ngăn Google Translate tự động dịch làm hỏng văn bản tiếng Việt */
        html {
            translate: no;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
components.html(
    """
    <script>
        // Set ngôn ngữ trang thành tiếng Việt và gắn thẻ meta chống dịch
        
        const meta = window.parent.document.createElement('meta');
        meta.name = 'google';
        meta.content = 'notranslate';
        window.parent.document.getElementsByTagName('head')[0].appendChild(meta);
    </script>
    """,
    height=0,
    width=0,
)

# Standardized companies based on CIENCO, DMT Group, and DMT Marina documents

# Configuration JSON logic for dynamic Projects and Departments











config = load_config()

DEPT_ABBR = {
    "Hội đồng quản trị": "HĐQT",
    "Ban Lãnh đạo": "BLĐ",
    "Ban Hành chính Nhân sự": "HCNS",
    "Ban Tài chính Kế toán": "TCKT",
    "Ban Kế hoạch Đầu tư": "KHĐT",
    "Ban Chuẩn bị Đầu tư": "CBĐT",
    "Ban Kỹ thuật": "KT",
    "Ban Đền bù Giải tỏa": "ĐBGT",
    "Ban Dự án": "DA",
    "Xí nghiệp DTBD": "XN DTBD",
    "Sàn GDBĐS": "Sàn GDBĐS",
    "Ban chỉ huy Công trường": "BCH CT",
    "Xí nghiệp xe máy thiết bị": "XN XMTB",
    "Ban TCKT": "TCKT",
    "Ban HCNS": "HCNS",
    "Ban KHĐT": "KHĐT",
    "Ban CBĐT": "CBĐT",
    "Ban KT": "KT",
    "Ban ĐBGT": "ĐBGT",
    "Ban DA": "DA",
    "BCH Công trường": "BCH CT",
    "XN Xe máy thiết bị": "XN XMTB",
}

for comp_name, comp_data in config.get("companies", {}).items():
    if "departments" in comp_data:
        comp_data["departments"] = [DEPT_ABBR.get(d, d) for d in comp_data["departments"]]
    if "personnel_by_department" in comp_data:
        new_personnel = {}
        for d, p in comp_data["personnel_by_department"].items():
            new_personnel[DEPT_ABBR.get(d, d)] = p
        
        if comp_name in ["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG", "CÔNG TY CỔ PHẦN ĐẦU TƯ ĐÀ NẴNG MIỀN TRUNG", "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"]:
            comp_data["departments"] = ["HĐQT", "BLĐ", "HCNS", "TCKT", "KHĐT", "CBĐT", "KT", "ĐBGT", "DA", "XN DTBD", "Sàn GDBĐS"]
            new_personnel = {
                "HĐQT": ["Đặng Thanh Bình"],
                "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
                "TCKT": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Lê Thị Hải"],
                "KT": ["Nguyễn Văn Bồn"],
                "HCNS": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"],
                "KHĐT": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Phan Thị Kim Cúc", "Trần Tin"],
                "CBĐT": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],
                "ĐBGT": ["Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
                "DA": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
                "XN DTBD": ["Mai Văn Châu"],
                "Sàn GDBĐS": ["Ngô Thị Tâm"]
            }

        elif comp_name in ["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]:
            comp_data["departments"] = ["HĐQT", "BLĐ", "KT", "BCH CT", "XN XMTB", "HCNS", "TCKT", "Mỏ"]
            new_personnel = {
                "HĐQT": ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"],
                "BLĐ": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
                "KT": ["Phạm Quang Nghĩa", "Lê Văn Thành", "Ngô Văn Hoàng"],
                "BCH CT": ["Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long"],
                "XN XMTB": ["Đặng Hiền"],
                "TCKT": ["Nguyễn Thị Ngọc Hà", "Nguyễn Thị Như Can"],
                "HCNS": ["Nguyễn Thị Mỹ Phương"],
                "Mỏ": ["Lê Nho Tân"]
            }
            
        elif comp_name in ["CTY CP DMT - MARINA (Du thuyền Happy Yacht)", "CÔNG TY CỔ PHẦN DMT-MARINA"]:
            comp_data["departments"] = ["BLĐ"]
            new_personnel = {
                "BLĐ": ["Trần Cường"]
            }

        comp_data["personnel_by_department"] = new_personnel








# Gantt DB Configuration

























# CSS DMT GROUP Branding Theme (Navy Blue & Orange Gold Accent)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], .stApp {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }
    
    /* Make Tab headers bolder and clearer */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    button[data-baseweb="tab"] p {
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #e65100 !important;
    }
    
    /* Hide Streamlit top-right icons */
    .stDeployButton {display:none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}
    
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 3rem !important;
    }
    .main-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
        letter-spacing: -0.5px;
    }
    /* Style Streamlit primary button to have brand orange-to-gold gradient */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f97316 0%, #f59e0b 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3) !important;
    }
    
    /* Style Streamlit download button to have brand Navy-Blue gradient and White text */
    div.stDownloadButton > button:first-child {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stDownloadButton > button:first-child:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3) !important;
    }
    
    /* Style metrics cards to feel premium with Navy Blue border */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1.8px solid #1e3a8a;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 2px 5px rgba(30, 58, 138, 0.05);
    }
    div[data-testid="stMetric"] div[data-testid="stMetricLabel"] p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #f97316 !important;
    }
    
    /* Input field labels - bold and larger font */
    div[data-testid="stWidgetLabel"] p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    
    /* Headers styling */
    h1, h2, h3, h4 {
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }
    
    /* Style sidebar with Navy theme styling & high contrast text */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] span[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #ffd700 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        border-bottom: 2px solid #f97316;
        padding-bottom: 5px;
    }
    
    /* Pull logo up to the very top of Sidebar */
    [data-testid="stSidebarContent"] {
        padding-top: 10px !important;
    }
    [data-testid="stSidebarContent"] img {
        margin-top: -30px !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Header Title with DMT branding
st.markdown('<div class="main-title">DMT GROUP — QUẢN LÝ TIẾN ĐỘ</div>', unsafe_allow_html=True)

# Sidebar layout with logo image and fallback
logo_path = "logo.png" if os.path.exists("logo.png") else ("INPUT/logo.png" if os.path.exists("INPUT/logo.png") else None)
if logo_path:
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("💡 Vui lòng đặt file logo.png vào thư mục gốc của dự án để hiển thị logo.")
    st.sidebar.markdown("### DMT GROUP")
st.sidebar.markdown("---")

# Link Google Sheets Config (Silently initialize for all users)
if "gsheet_url" not in st.session_state:
    st.session_state["gsheet_url"] = load_settings().get("gsheet_url", "")

company_options = ["Tất cả đơn vị"] + list(COMPANIES.keys())
current_comp = st.session_state.get('selected_company', company_options[1])
try:
    comp_idx = company_options.index(current_comp)
except ValueError:
    comp_idx = 1

selected_company = st.sidebar.selectbox(
    "CHỌN CÔNG TY / THÀNH VIÊN", 
    company_options, 
    index=comp_idx,
    format_func=lambda x: str(x).replace("CTY CP", "CÔNG TY CP")
)
st.session_state['selected_company'] = selected_company

# Quick access / URL testing support for mobile demonstration & guide screenshots
if hasattr(st, "query_params"):
    if "user" in st.query_params:
        st.session_state.is_personal_authenticated = True
        st.session_state.personal_user = st.query_params["user"]
        st.session_state['role_mode'] = "Nhân viên"
        st.session_state['_prev_role_mode'] = "Nhân viên"
        if "dept" in st.query_params:
            st.session_state.auth_user_dept = st.query_params["dept"]
    elif "manager" in st.query_params:
        st.session_state.is_manager_authenticated = True
        st.session_state.manager_user = st.query_params["manager"]
        st.session_state.manager_dept = DEPT_ABBR.get(st.query_params.get("dept", "BLĐ"), "BLĐ")
        if st.session_state.manager_user in ["Thái Văn Thành", "Trần Văn Trọng"]:
            st.session_state['selected_company'] = "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
        st.session_state['role_mode'] = "Quản lý"
        st.session_state['_prev_role_mode'] = "Quản lý"
    elif "role" in st.query_params:
        st.session_state['role_mode'] = st.query_params["role"]
        st.session_state['_prev_role_mode'] = st.query_params["role"]

if 'role_mode' not in st.session_state:
    st.session_state['role_mode'] = "Nhân viên"

# Tìm index hiện tại
roles = ["Nhân viên", "Quản lý", "HR"]
try:
    current_index = roles.index(st.session_state['role_mode'])
except ValueError:
    current_index = 0

role_mode = st.sidebar.selectbox("QUYỀN TRUY CẬP", roles, index=current_index, key="role_mode_select")
if st.session_state.get('_prev_role_mode') != role_mode:
    st.session_state['_prev_role_mode'] = role_mode
    st.session_state['role_mode'] = role_mode
    # Reset authentication states when switching roles to avoid leftover data
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.manager_user = None
    st.session_state.manager_dept = None
    st.session_state.auth_user_dept = None
    st.session_state.auth_user_company = None
    st.session_state.pop("login_user", None)
    st.session_state.pop("login_dept", None)
    st.session_state.pop("mgr_login_user", None)
    st.session_state.pop("mgr_login_dept", None)
else:
    st.session_state['role_mode'] = role_mode

if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False
if "is_manager_authenticated" not in st.session_state:
    st.session_state.is_manager_authenticated = False
if "is_personal_authenticated" not in st.session_state:
    st.session_state.is_personal_authenticated = False
if "personal_user" not in st.session_state:
    st.session_state.personal_user = None

if role_mode == "Quản lý":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_admin_authenticated = False
    if not st.session_state.is_manager_authenticated:
        st.sidebar.markdown("### 🏢 Xác thực Quản lý")
        valid_depts = get_departments_for_company(selected_company, config)
        dept_idx = 0
        if "login_dept" in st.query_params and st.query_params["login_dept"] in valid_depts:
            dept_idx = valid_depts.index(st.query_params["login_dept"]) + 1
        sel_login_dept = st.sidebar.selectbox("1. Chọn Phòng ban", ["-- Chọn --"] + valid_depts, index=dept_idx, key="mgr_login_dept")
        
        if sel_login_dept != "-- Chọn --":
            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list or selected_company == "Tất cả đơn vị":
                if selected_company == "Tất cả đơn vị":
                    dept_leads = []
                    for comp_leads in DEPT_LEADS.values():
                        dept_leads.extend(comp_leads.get(sel_login_dept, []))
                        dept_leads.extend(comp_leads.get(DEPT_ABBR.get(sel_login_dept, sel_login_dept), []))
                    dept_leads = list(dict.fromkeys(dept_leads))
                else:
                    dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                    if not dept_leads:
                        dept_leads = DEPT_LEADS.get(selected_company, {}).get(DEPT_ABBR.get(sel_login_dept, sel_login_dept), [])
                
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                
                valid_leads = dept_leads
                
                # Bức tường lửa: Quản lý thuộc BLĐ chỉ nằm duy nhất ở mục Quản lý của BLĐ
                bld_only_managers = ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn", "Thái Văn Thành", "Trần Văn Trọng"]
                if sel_login_dept not in ["BLĐ", "Ban Lãnh đạo"]:
                    valid_leads = [x for x in valid_leads if x not in bld_only_managers]
                
                if valid_leads:
                    user_idx = 0
                    if "login_user" in st.query_params and st.query_params["login_user"] in valid_leads:
                        user_idx = valid_leads.index(st.query_params["login_user"]) + 1
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên Quản lý", ["-- Chọn --"] + valid_leads, index=user_idx, key="mgr_login_user")
                else:
                    st.sidebar.info("Phòng ban này tạm thời chưa có quản lý.")
                    sel_login_user = "-- Chọn --"
                
                if sel_login_user != "-- Chọn --":
                    mgr_pwd = st.sidebar.text_input("3. Nhập Mật khẩu Quản lý", type="password")
                    if st.sidebar.button("Xác nhận Đăng nhập"):
                        if mgr_pwd == "quanly123":
                            st.session_state.is_manager_authenticated = True
                            st.session_state.manager_dept = DEPT_ABBR.get(sel_login_dept, sel_login_dept)
                            st.session_state.manager_user = sel_login_user
                            st.session_state.manager_company = selected_company
                            if sel_login_user in ["Thái Văn Thành", "Trần Văn Trọng"]:
                                st.session_state['selected_company'] = "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"
                            st.session_state.just_logged_in = True
                            st.rerun()
                        else:
                            st.sidebar.error("Mật khẩu không đúng!")
            else:
                st.sidebar.warning("Phòng ban này chưa có dữ liệu nhân sự.")

    
    if st.session_state.is_manager_authenticated:
        st.sidebar.success(f"👋 Xin chào Quản lý, {st.session_state.get('manager_user', '')}!")
        
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_manager_authenticated = False
            st.session_state.manager_dept = None
            st.session_state.manager_user = None
            st.session_state.manager_company = None
            st.session_state.pop("mgr_login_dept", None)
            st.session_state.pop("mgr_login_user", None)
            st.rerun()
        
        # Hiển thị phạm vi quản lý
        if is_hr_equivalent_leader(st.session_state.get('manager_user')):
            st.sidebar.markdown("**Phòng/Ban phụ trách:** Toàn bộ các Ban (Quyền HR)")
        else:
            st.sidebar.markdown(f"**Phòng/Ban phụ trách:** {st.session_state.get('manager_dept', '')}")

elif role_mode == "HR":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_manager_authenticated = False
    if not st.session_state.is_admin_authenticated:
        admin_pwd = st.sidebar.text_input("Nhập Mật khẩu HR", type="password")
        if admin_pwd:
            if admin_pwd == "admindmt123":
                st.session_state.is_admin_authenticated = True
                st.session_state.just_logged_in = True
                st.rerun()
            else:
                st.sidebar.error("Mật khẩu không đúng!")
    
    

    if st.session_state.is_admin_authenticated:
        st.sidebar.success("Đã xác thực toàn quyền (HR)!")
        
        if st.sidebar.button("Đăng xuất", key="logout_hr"):
            st.session_state.is_admin_authenticated = False
            st.rerun()

elif role_mode == "Nhân viên":
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    
    if not st.session_state.is_personal_authenticated:
        st.sidebar.markdown("### 👤 Xác thực Nhân viên")
        valid_depts = get_departments_for_company(selected_company, config)
        sel_login_dept = st.sidebar.selectbox("1. Chọn Phòng ban", ["-- Chọn --"] + valid_depts, key="login_dept")
        
        if sel_login_dept != "-- Chọn --":
            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list:
                dept_leads = DEPT_LEADS.get(selected_company, {}).get(sel_login_dept, [])
                if not dept_leads:
                    dept_leads = DEPT_LEADS.get(selected_company, {}).get(DEPT_ABBR.get(sel_login_dept, sel_login_dept), [])
                if isinstance(dept_leads, str):
                    dept_leads = [dept_leads] if dept_leads else []
                
                # Quản lý/Trưởng Ban đăng nhập ở quyền "Quản lý", không xuất hiện ở danh sách "Nhân viên"
                # Quản lý thuộc BLĐ chỉ nằm ở mục Quản lý của BLĐ, không nằm ở mục Nhân viên
                bld_all_leads = []
                for comp_leads in DEPT_LEADS.values():
                    bld_all_leads.extend(comp_leads.get("BLĐ", []))
                    bld_all_leads.extend(comp_leads.get("Ban Lãnh đạo", []))
                    bld_all_leads.extend(comp_leads.get("HĐQT", []))
                    bld_all_leads.extend(comp_leads.get("Hội đồng quản trị", []))
                bld_all_leads = list(dict.fromkeys(bld_all_leads))
                
                nhan_vien_list = [p for p in personnel_list if p not in dept_leads and p not in bld_all_leads]
                
                if nhan_vien_list:
                    sel_login_user = st.sidebar.selectbox("2. Chọn Tên của bạn", ["-- Chọn --"] + nhan_vien_list, key="login_user")
                else:
                    st.sidebar.info("Phòng ban này không có nhân viên trực thuộc (các Quản lý/Lãnh đạo vui lòng chọn quyền 'Quản lý' để đăng nhập).")
                    sel_login_user = "-- Chọn --"
                if sel_login_user != "-- Chọn --":
                    if st.sidebar.button("Xác nhận Đăng nhập"):
                        st.session_state.is_personal_authenticated = True
                        st.session_state.personal_user = sel_login_user
                        st.session_state.auth_user_dept = DEPT_ABBR.get(sel_login_dept, sel_login_dept)
                        st.session_state.auth_user_company = selected_company
                        st.session_state['selected_company'] = selected_company
                        st.rerun()
            else:
                st.sidebar.warning("Phòng ban này chưa có dữ liệu nhân sự.")
    else:
        st.sidebar.success(f"👋 Xin chào, {st.session_state.personal_user}!")
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_personal_authenticated = False
            st.session_state.personal_user = None
            st.session_state.auth_user_dept = None
            st.session_state.auth_user_company = None
            st.session_state.pop("login_dept", None)
            st.session_state.pop("login_user", None)
            st.rerun()
else:
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
st.sidebar.markdown("---")

is_mobile = False
try:
    if hasattr(st, "context") and hasattr(st.context, "headers"):
        ua = st.context.headers.get("User-Agent", "").lower()
        if "mobi" in ua or "android" in ua or "iphone" in ua:
            is_mobile = True
except Exception:
    pass

menu_options = [
    "🚀 Bảng theo dõi tiến độ công việc",
    "➕ Thêm / Cập Nhật Công Việc",
    "📖 Sổ tay Hướng dẫn"
]
if is_mobile:
    menu_options.insert(0, "👀 BẢNG TỔNG QUAN (View)")

if st.session_state.get('is_manager_authenticated', False):
    menu_options = [
        "📋 Bảng theo dõi tiến độ công việc",
        "➕ Thêm / Cập Nhật Công Việc",
        "⚖️ Duyệt việc Khách quan",
        "🏆 Đánh giá KPI & Xếp loại",
        "📖 Sổ tay Hướng dẫn"
    ]
    if is_mobile:
        menu_options.insert(0, "📊 BẢNG TỔNG QUAN (View)")


p_nhat_ky = st.Page('views/11_Nhat_Ky_He_Thong.py', title='Nhật ký Hệ thống', icon='🕵️‍♂️')

if st.session_state.is_admin_authenticated:
    menu_options = [
        "👀 BẢNG TỔNG QUAN (View)",
        "🚀 Bảng theo dõi tiến độ công việc",
        "➕ Thêm / Cập Nhật Công Việc",
        "✅ Duyệt & Nghiệm thu công việc",
        "🏆 Đánh giá KPI & Xếp loại",
        "🔍 Quản lý & Đối chiếu JD",
        "⚙️ Quản Lý Cấu Hình",
        "📖 Sổ tay Hướng dẫn"
    ]

import socket
is_local = (socket.gethostname() == "thuyhc")


# --- MULTIPAGE NAVIGATION ---
p_tong_quan = st.Page('views/1_Tong_Quan.py', title='Bảng Tổng Quan', icon='👀')
p_tien_do = st.Page('views/2_Tien_Do.py', title='Bảng theo dõi tiến độ công việc', icon='🚀')
p_cap_nhat = st.Page('views/3_Cap_Nhat.py', title='Thêm / Cập Nhật Công Việc', icon='➕')
p_nghiem_thu = st.Page('views/4_Nghiem_Thu.py', title='Duyệt & Nghiệm thu công việc', icon='✅')
p_danh_gia = st.Page('views/5_Danh_Gia_KPI.py', title='Đánh giá KPI & Xếp loại', icon='🏆')
p_quan_ly_jd = st.Page('views/6_Quan_Ly_JD.py', title='Quản lý & Đối chiếu JD', icon='🔍')
p_cau_hinh = st.Page('views/7_Cau_Hinh.py', title='Quản Lý Cấu Hình', icon='⚙️')
p_so_tay = st.Page('views/10_So_Tay.py', title='Sổ tay Hướng dẫn', icon='📖')


p_nhat_ky = st.Page('views/11_Nhat_Ky_He_Thong.py', title='Nhật ký Hệ thống', icon='🕵️‍♂️')

if st.session_state.is_admin_authenticated:
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_quan_ly_jd, p_cau_hinh, p_nhat_ky, p_so_tay]
    }
elif st.session_state.get('is_manager_authenticated', False):
    pages = {
        'CÔNG VIỆC & TIẾN ĐỘ': [p_tong_quan, p_tien_do, p_cap_nhat, p_nghiem_thu],
        'ĐÁNH GIÁ & KPI': [p_danh_gia],
        'QUẢN TRỊ & HỆ THỐNG': [p_so_tay]
    }
else:
    # Nhân viên chưa đăng nhập hoặc đã đăng nhập
    pages = {
        'PHÂN HỆ CHỨC NĂNG': [p_tien_do, p_cap_nhat, p_so_tay]
    }


# Ghi lại các biến toàn cục quan trọng vào session_state để các trang có thể truy cập
st.session_state['role_mode'] = role_mode if 'role_mode' in locals() else 'Nhân viên'
st.session_state['is_local'] = is_local if 'is_local' in locals() else False

pg = st.navigation(pages)

if st.session_state.pop("just_logged_in", False):
    st.switch_page(p_tong_quan)

pg.run()
