import streamlit as st

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
SETTINGS_FILE = 'local_settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

try:
    import google.generativeai as genai
except ImportError:
    st.error("Th¶¶ viﬂ+Án google-generativeai ch¶¶a -Ê¶¶ﬂ+˙c c+·i -Êﬂ¶+t. Vui l+¶ng kiﬂ+‚m tra file requirements.txt.")

from datetime import datetime, date, timedelta

def calculate_time_progress(start_date, deadline_date, is_completed=False):
    """T+°nh % sﬂ+¨c khﬂ+≈e thﬂ+•i gian: -…ang tﬂ+Êt (99), Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn (50), Trﬂ+‡ hﬂ¶Ìn (0)"""
    if is_completed:
        return 100.0
    try:
        today = date.today()
        if isinstance(deadline_date, str):
            deadline_date = datetime.strptime(deadline_date, "%Y-%m-%d").date()
            
        if not deadline_date:
            return 0.0
            
        days_left = (deadline_date - today).days
        
        if days_left < 0:
            return 0.0  # Trﬂ+‡ hﬂ¶Ìn
        elif 0 <= days_left <= 3:
            return 50.0  # Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn
        else:
            return 99.0  # C+¶n nhiﬂ+¸u hﬂ¶Ìn
    except Exception:
        return 0.0

from contextlib import contextmanager
import time

@contextmanager
def acquire_db_lock(timeout=15):
    # Lock local (cho c+¶ng 1 container/server)
    lock_dir = "db_write.lock"
    start_time = time.time()
    locked_local = False
    
    while time.time() - start_time < timeout:
        try:
            os.mkdir(lock_dir)
            locked_local = True
            break
        except FileExistsError:
            time.sleep(0.5)
            
    if not locked_local:
        st.error("G‹·n+≈ Hﬂ+Á thﬂ+Êng -Êang bﬂ¶°n. Vui l+¶ng -Êﬂ+˙i v+·i gi+Ûy v+· thﬂ+° lﬂ¶Ìi.")
        st.stop()
        
    try:
        yield
    finally:
        try:
            os.rmdir(lock_dir)
        except:
            pass

# Page config - Light Theme is handled natively by Streamlit's default settings
st.set_page_config(
    page_title="Hﬂ+Á thﬂ+Êng Quﬂ¶˙n l++ Tiﬂ¶+n -Êﬂ+÷ C+¶ng viﬂ+Ác & KPI - DMT Group",
    page_icon="G‹Ù",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chﬂ+Êng dﬂ+Ôch tﬂ+¶ -Êﬂ+÷ng cﬂ+∫a Google (g+Ûy lﬂ+˘i ch+°nh tﬂ¶˙) v+· chuﬂ¶¨n h+¶a Font chﬂ+ª tiﬂ¶+ng Viﬂ+Át
st.markdown("""
    <style>
        /* Cﬂ+Ê -Êﬂ+Ônh Font chuﬂ¶¨n hﬂ+˘ trﬂ+˙ -Êﬂ¶∫y -Êﬂ+∫ tiﬂ¶+ng Viﬂ+Át v+· t-‚ng k+°ch th¶¶ﬂ+¢c chﬂ+ª an to+·n (kh+¶ng ghi -Ê+ø icon) */
        html, body, p, label, div.stMarkdown, div.stText {
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 1.08rem;
        }
        /* Ng-‚n Google Translate tﬂ+¶ -Êﬂ+÷ng dﬂ+Ôch l+·m hﬂ+≈ng v-‚n bﬂ¶˙n tiﬂ¶+ng Viﬂ+Át */
        html {
            translate: no;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
components.html(
    """
    <script>
        // Set ng+¶n ngﬂ+ª trang th+·nh tiﬂ¶+ng Viﬂ+Át v+· gﬂ¶ªn thﬂ¶+ meta chﬂ+Êng dﬂ+Ôch
        
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
COMPANIES = {
    "CTY CP -…ﬂ¶™U T¶ª -…+« Nﬂ¶¶NG - MIﬂ+«N TRUNG": {},
    "CTY CP X+ÈY Dﬂ+¶NG C+ˆNG TR+ÓNH GIAO TH+ˆNG -…N-MT": {},
    "CTY CP DMT - MARINA (Du thuyﬂ+¸n Happy Yacht)": {}
}

# Configuration JSON logic for dynamic Projects and Departments
CONFIG_FILE = os.path.join("OUTPUT", "CONFIG_PROJECTS.json")

DEFAULT_PERSONNEL = {
    "Ban L+˙nh -Êﬂ¶Ìo": ["Trﬂ¶∫n Quﬂ+Êc Thﬂ+‚", "-…o+·n Thﬂ+Ô Ngﬂ+Ïc Nﬂ+ª", "-…ﬂ¶+ng Ngﬂ+Ïc Ho+·ng"],
    "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶": ["Nguyﬂ+‡n Thﬂ+Ô Hﬂ¶Ình Ti+¨n", "Nguyﬂ+‡n B-‚ng Trinh", "L+¨ Ngﬂ+Ïc T+¶ Uy+¨n"],
    "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn": ["-…ﬂ+Ùng Thﬂ+Ô Nguyﬂ+Át Nga", "Huﬂ+¶nh Thﬂ+Ô Ho+·ng H+·", "Nguyﬂ+‡n Thﬂ+Ô Nhﬂ¶°t Sang"],
    "Ban Kﬂ¶+ hoﬂ¶Ìch -…ﬂ¶∫u t¶¶": ["Nguyﬂ+‡n Trﬂ¶∫n Thﬂ+¨c", "Phan Thﬂ+Ô Mﬂ+¶ Hﬂ¶Ình", "Nguyﬂ+‡n -…ﬂ+¨c Lﬂ+˙i", "Trﬂ¶∫n Tin"],
    "Ban Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶": ["Hﬂ+Ù V-‚n Khoa", "Phan Thﬂ+Ô Mﬂ+¶ Hﬂ¶Ình", "Cao Thuﬂ++ Ti+¨n"],
    "Ban Kﬂ+¶ thuﬂ¶°t": ["Nguyﬂ+‡n V-‚n Bﬂ+Ùn"],
    "Ban -…ﬂ+¸n b+¶ Giﬂ¶˙i tﬂ+≈a": ["Nguyﬂ+‡n Ngﬂ+Ïc T+¶n", "-…ﬂ¶+ng C+¶ng Nhﬂ+¶t", "-…ﬂ¶+ng Thﬂ+Ô Mﬂ+¶ Hﬂ¶Ình", "-…ﬂ¶+ng Thanh Quang"],
    "Ban chﬂ+Î huy C+¶ng tr¶¶ﬂ+•ng": ["Nguyﬂ+‡n Phong Trung", "Phﬂ¶Ìm V-‚n Long", "L+¨ -…+¶ng"],
    "X+° nghiﬂ+Áp xe m+Ìy thiﬂ¶+t bﬂ+Ô": ["-…ﬂ¶+ng Hiﬂ+¸n"],
    "Ban Dﬂ+¶ +Ìn": ["Nguyﬂ+‡n -…+ºnh Thﬂ¶ªng", "Nguyﬂ+‡n -…+ºnh Hiﬂ¶+u"],
    "X+° nghiﬂ+Áp DTBD": ["Mai V-‚n Ch+Ûu"],
    "S+·n GDB-…S": ["Ng+¶ Thﬂ+Ô T+Ûm"],
    "Tﬂ+Ú KPI": []
}

def is_gsheets_configured():
    try:
        # Check if connections.gsheets exists in secrets
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return True
    except Exception:
        pass
    return False

def get_gsheets_conn():
    from supabase import create_client
    SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        import streamlit as st


        st.warning(f"Ch¶¶a cﬂ¶—u h+ºnh Supabase Connection: {e}")
        return None

def _get_table_name(worksheet):
    mapping = {
        "Sheet1": "tasks",
        "GANTT_KHDT": "gantt_tasks",
        "VAN_BAN_DEN": "documents",
        "CONFIG": "kpi_config",
        "KPI_ADJUSTMENTS": "kpi_adjustments"
    }
    return mapping.get(worksheet, worksheet)

@st.cache_resource
def get_global_state():
    return {}

def safe_gsheets_read(conn, worksheet, ttl=15, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    
    import streamlit as st


    import time
    
    cache_key = f"cached_df_{worksheet}"
    

            
    try:
        table_name = _get_table_name(worksheet)
        res = conn.table(table_name).select('*').execute()
        data = res.data
        if not data:
            return fallback_df
            
        import pandas as pd
        df = pd.DataFrame(data)
        
        import numpy as np
        df = df.replace("", np.nan).dropna(how='all')
        
        if worksheet == "Sheet1":
            col_mapping = {
                'ID': 'M+˙ CV',
                'TenCongViec': 'T+¨n c+¶ng viﬂ+Ác',
                'PhanTramHoanThanh': 'Tiﬂ¶+n -Êﬂ+÷ %',
                'TrangThai': 'Trﬂ¶Ìng th+Ìi',
                'Deadline': 'Hﬂ¶Ìn ch+¶t'
            }
            df.rename(columns=col_mapping, inplace=True)
            if "NgayBatDau" in df.columns:
                df["NgayBatDau"] = pd.to_datetime(df["NgayBatDau"], errors="coerce").dt.strftime('%d/%m/%Y')
            if "Hﬂ¶Ìn ch+¶t" in df.columns:
                df["Hﬂ¶Ìn ch+¶t"] = pd.to_datetime(df["Hﬂ¶Ìn ch+¶t"], errors="coerce").dt.strftime('%d/%m/%Y')
                
        elif worksheet == "KPI_ADJUSTMENTS":
            if "SoDiem" in df.columns:
                df.rename(columns={"SoDiem": "DiemDieuChinh"}, inplace=True)
            if "NhanSu" in df.columns:
                df.rename(columns={"NhanSu": "TenNhanVien"}, inplace=True)
            if "LoaiDieuChinh" in df.columns:
                df.rename(columns={"LoaiDieuChinh": "LoaiHanhVi"}, inplace=True)
                

        
        return df
    except Exception as e:
        import streamlit as st


        st.warning(f"Lﬂ+˘i -Êﬂ+Ïc Supabase ({worksheet}): {e}")
        return fallback_df

def safe_gsheets_update(conn, worksheet, data):
    import streamlit as st


    import time
    import pandas as pd
    import numpy as np
    import math
    
    cache_key = f"cached_df_{worksheet}"
    table_name = _get_table_name(worksheet)
    
    try:
        df = data.copy()
        if worksheet == "Sheet1":
            col_mapping = {
                'M+˙ CV': 'ID', 'MaCV': 'ID',
                'T+¨n c+¶ng viﬂ+Ác': 'TenCongViec', 'Nﬂ+÷i dung': 'TenCongViec', 'C+¶ng viﬂ+Ác': 'TenCongViec',
                'Tiﬂ¶+n -Êﬂ+÷ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiﬂ¶+n -Êﬂ+÷': 'PhanTramHoanThanh',
                'Trﬂ¶Ìng th+Ìi': 'TrangThai', 'Status': 'TrangThai',
                'Hﬂ¶Ìn ch+¶t': 'Deadline', 'Ng+·y ho+·n th+·nh': 'Deadline'
            }
            rename_dict = {k: v for k, v in col_mapping.items() if k in df.columns}
            df.rename(columns=rename_dict, inplace=True)
            
            
            allowed_cols = ['ID', 'DonVi', 'PhongBan', 'NguoiChuTri', 'TenDuAn', 'MocTienDo', 'SanPhamBanGiao', 'TenCongViec', 'PhanLoaiChiSo', 'NgayBatDau', 'Deadline', 'DoUuTien', 'PhanTramHoanThanh', 'TrangThai', 'LinkKetQua', 'GiaiTrinhDeXuat', 'NgayCapNhat', 'ChuKyTheoDoi', 'PhanLoaiTreHan', 'TyTrongKPI', 'NguonGiaoViec', 'MucDoGhiNhan']
            df = df[[c for c in df.columns if c in allowed_cols]]
            
        elif worksheet == "KPI_ADJUSTMENTS":
            if "DiemDieuChinh" in df.columns:
                df.rename(columns={"DiemDieuChinh": "SoDiem"}, inplace=True)
            if "TenNhanVien" in df.columns:
                df.rename(columns={"TenNhanVien": "NhanSu"}, inplace=True)
            if "LoaiHanhVi" in df.columns:
                df.rename(columns={"LoaiHanhVi": "LoaiDieuChinh"}, inplace=True)
            allowed_cols = ['ID', 'NhanSu', 'Thang', 'Nam', 'LoaiDieuChinh', 'SoDiem', 'LyDo', 'NguoiCapNhat', 'ThoiGianCapNhat']
            df = df[[c for c in df.columns if c in allowed_cols]]
            
        elif worksheet == "CONFIG":
            allowed_cols = ['PhongBan', 'NhanSu', 'Role', 'config_json']
            df = df[[c for c in df.columns if c in allowed_cols]]
            
        elif worksheet == "GANTT_KHDT":
            allowed_cols = ['ID', 'TenDuAn', 'TenCongViec', 'GiaiDoan', 'NgayBatDau', 'Deadline', 'PhanTramHoanThanh', 'Milestone', 'NgayCapNhat']
            df = df[[c for c in df.columns if c in allowed_cols]]
            
        elif worksheet == "VAN_BAN_DEN":
            allowed_cols = ['ID', 'SoKyHieu', 'NgayBanHanh', 'CoQuanBanHanh', 'TrichYeu', 'NguoiChuTri', 'ThoiHanGiaiQuyet', 'TrangThai', 'GhiChu']
            df = df[[c for c in df.columns if c in allowed_cols]]

        pk = 'NhanSu' if worksheet == 'CONFIG' else 'ID'
        if pk in df.columns:
            df = df[df[pk].notna()]
            df = df[df[pk] != '']

        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        records = df.to_dict(orient='records')
        for r in records:
            for k, v in list(r.items()):
                if isinstance(v, float):
                    if math.isnan(v):
                        r[k] = None
                    elif v.is_integer():
                        r[k] = int(v)
                elif pd.isna(v):
                    r[k] = None
                    
        if records:
            conn.table(table_name).upsert(records).execute()
            
            if pk in df.columns:
                current_ids = [str(x) for x in df[pk].tolist()]
                if len(current_ids) > 0:
                    res = conn.table(table_name).select(pk).execute()
                    db_ids = [(row[pk], str(row[pk])) for row in res.data]
                    ids_to_delete = [orig for orig, string_val in db_ids if string_val not in current_ids]
                    if ids_to_delete:
                        for i in range(0, len(ids_to_delete), 100):
                            batch_del = ids_to_delete[i:i+100]
                            conn.table(table_name).delete().in_(pk, batch_del).execute()

        st.session_state[cache_key] = data.copy()
        st.session_state[cache_key + "_time"] = time.time()
        
        global_state = get_global_state()
        global_state[cache_key] = data.copy()
        global_state[cache_key + "_time"] = time.time()
        
        if worksheet == "Sheet1":
            if hasattr(read_db, "clear"): read_db.clear()
        elif worksheet == "GANTT_KHDT":
            if hasattr(read_gantt_db, "clear"): read_gantt_db.clear()
        elif worksheet == "KPI_ADJUSTMENTS":
            if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
        elif worksheet == "VAN_BAN_DEN":
            if hasattr(read_incoming_docs_db, "clear"): read_incoming_docs_db.clear()
            
        return True
    except Exception as e:
        err_msg = str(e)
        import streamlit as st


        st.error(f"Lﬂ+˘i khi l¶¶u v+·o Supabase ({worksheet}): {err_msg}")
        return False


def save_config(config_data):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Ch¶¶a cﬂ¶—u h+ºnh Google Sheets (secrets.toml).")
        return False
    try:
        import json
        import pandas as pd
        
        config_data_copy = config_data.copy()
        job_descriptions = config_data_copy.pop("job_descriptions", {})
        
        rows = []
        rows.append({
            "NhanSu": "APP_GLOBAL_CONFIG",
            "PhongBan": "SYSTEM",
            "Role": "SYSTEM",
            "config_json": json.dumps(config_data_copy, ensure_ascii=False)
        })
        
        for company, personnel_dict in job_descriptions.items():
            for person, jd_data in personnel_dict.items():
                if jd_data:
                    rows.append({
                        "NhanSu": person,
                        "PhongBan": company,
                        "Role": "JD",
                        "config_json": json.dumps(jd_data, ensure_ascii=False) if isinstance(jd_data, (dict, list)) else json.dumps({"jd_text": jd_data}, ensure_ascii=False)
                    })
                    
        df_save = pd.DataFrame(rows)
        success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        if not success:
            st.error("G‹·n+≈ Lﬂ+˘i: Kh+¶ng t+ºm thﬂ¶—y trang t+°nh 'CONFIG' tr+¨n Google Sheets! Vui l+¶ng mﬂ+É Google Sheets, tﬂ¶Ìo mﬂ+÷t Sheet mﬂ+¢i -Êﬂ¶+t t+¨n l+· 'CONFIG', sau -Ê+¶ l¶¶u lﬂ¶Ìi.")
            return False
            
        st.cache_data.clear()
        config_data["job_descriptions"] = job_descriptions
        return True
    except Exception as e:
        st.error(f'Lﬂ+˘i l¶¶u Google Sheets: {e}')
        return False

def load_config():
    default_config = {
        "companies": {
            "CTY CP -…ﬂ¶™U T¶ª -…+« Nﬂ¶¶NG - MIﬂ+«N TRUNG": {
                "projects_by_category": {
                    "B-…S & KDC": ["KDC B+·u Mﬂ¶Ìc", "KDC Nam B+·u Mﬂ¶Ìc", "K-…T Ph¶¶ﬂ+¢c L++ & Ph¶¶ﬂ+¢c L++ MR", "T-…C Ph¶¶ﬂ+¢c L++ 2 & Ho+· Li+¨n 5", "Dﬂ+¶ +Ìn Phong Nam", "Khu BT ST Ho+· Ninh"],
                    "Hﬂ¶· Tﬂ¶™NG & GIAO TH+ˆNG": ["Tuyﬂ¶+n -Ê¶¶ﬂ+•ng L+¨ Trﬂ+Ïng Tﬂ¶—n", "Tuyﬂ¶+n -Ê¶¶ﬂ+•ng L+¨ Trﬂ+Ïng Tﬂ¶—n - Ho+· Nh¶Ìn", "Tuyﬂ¶+n -Ê¶¶ﬂ+•ng Trﬂ¶∫n H¶¶ng -…ﬂ¶Ìo (BT)", "Trﬂ+—c I T+Ûy Bﬂ¶ªc", "Khu T-…C Ho+· Vang"],
                    "TH¶ª¶·NG Mﬂ¶·I & KH+¸CH Sﬂ¶·N": ["Kh+Ìch sﬂ¶Ìn DMT-Group"]
                },
                "departments": ["Ban L+˙nh -Êﬂ¶Ìo", "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶", "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn", "Ban Kﬂ¶+ hoﬂ¶Ìch -…ﬂ¶∫u t¶¶", "Ban Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶", "Ban Kﬂ+¶ thuﬂ¶°t", "Ban -…ﬂ+¸n b+¶ Giﬂ¶˙i tﬂ+≈a", "Tﬂ+Ú KPI", "Ban chﬂ+Î huy C+¶ng tr¶¶ﬂ+•ng", "X+° nghiﬂ+Áp xe m+Ìy thiﬂ¶+t bﬂ+Ô", "Ban Dﬂ+¶ +Ìn", "X+° nghiﬂ+Áp DTBD", "S+·n GDB-…S"],
                "personnel_by_department": DEFAULT_PERSONNEL.copy()
            },
            "CTY CP DMT - MARINA (Du thuyﬂ+¸n Happy Yacht)": {
                "projects_by_category": {
                    "TH¶ª¶·NG Mﬂ¶·I & KH+¸CH Sﬂ¶·N": ["Du thuyﬂ+¸n Happy Yacht (DMT Marina)", "Du thuyﬂ+¸n Happy Yacht", "HCNS", "TCKT"]
                },
                "departments": ["Ban L+˙nh -Êﬂ¶Ìo", "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶", "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn"],
                "personnel_by_department": {
                    "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶": ["Nguyﬂ+‡n Thﬂ+Ô Hﬂ¶Ình Ti+¨n"],
                    "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn": ["L+¨ Thﬂ+Ô Hﬂ¶˙i"],
                    "Ban L+˙nh -Êﬂ¶Ìo": ["Trﬂ¶∫n C¶¶ﬂ+•ng", "-…ﬂ¶+ng Ngﬂ+Ïc Ho+·ng"],
                    "Tﬂ+Ú KPI": []
                }
            },
            "CTY CP X+ÈY Dﬂ+¶NG C+ˆNG TR+ÓNH GIAO TH+ˆNG -…N-MT": {
                "projects_by_category": {},
                "departments": ["Ban L+˙nh -Êﬂ¶Ìo", "Ban Kﬂ+¶ thuﬂ¶°t", "Ban chﬂ+Î huy C+¶ng tr¶¶ﬂ+•ng", "X+° nghiﬂ+Áp xe m+Ìy thiﬂ¶+t bﬂ+Ô", "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶", "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn"],
                "personnel_by_department": {
                    "Ban L+˙nh -Êﬂ¶Ìo": ["Th+Ìi V-‚n Th+·nh", "Trﬂ¶∫n V-‚n Trﬂ+Ïng", "-…ﬂ¶+ng Thﬂ+Ô Lan Ngﬂ+Ïc"],
                    "Ban Kﬂ+¶ thuﬂ¶°t": ["Trﬂ¶∫n V-‚n Trﬂ+Ïng", "Phﬂ¶Ìm Quang Ngh-¨a"],
                    "Ban chﬂ+Î huy C+¶ng tr¶¶ﬂ+•ng": ["Nguyﬂ+‡n Phong Trung", "Phﬂ¶Ìm V-‚n Long", "L+¨ -…+¶ng"],
                    "X+° nghiﬂ+Áp xe m+Ìy thiﬂ¶+t bﬂ+Ô": ["-…ﬂ¶+ng Hiﬂ+¸n"],
                    "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn": ["Nguyﬂ+‡n Thﬂ+Ô Ngﬂ+Ïc H+·", "Nguyﬂ+‡n Thﬂ+Ô Nh¶¶ Can"],
                    "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶": ["Nguyﬂ+‡n Thﬂ+Ô Mﬂ+¶ Ph¶¶¶Ìng"]
                }
            }
        },
        "cv_gsheet_url": ""
    }
    
    conn = get_gsheets_conn()
    if conn is None:
        return default_config
        
    try:
        import json
        df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=600)
        if df is None or df.empty:
            return default_config
            
        if "config_json" in df.columns:
            config_rows = df[df["config_json"].notna()]
            if not config_rows.empty:
                if "NhanSu" in df.columns:
                    app_row = config_rows[config_rows["NhanSu"] == "APP_GLOBAL_CONFIG"]
                    if not app_row.empty:
                        json_str = app_row.iloc[0]["config_json"]
                    else:
                        json_str = config_rows.iloc[0]["config_json"]
                else:
                    json_str = config_rows.iloc[0]["config_json"]
            else:
                json_str = df.iloc[0]["config_json"]
        else:
            json_str = df.iloc[0]["config_json"]
            
        data = json.loads(json_str)
        
        if "NhanSu" in df.columns and "Role" in df.columns:
            jd_rows = df[df["Role"] == "JD"]
            if not jd_rows.empty:
                if "job_descriptions" not in data:
                    data["job_descriptions"] = {}
                for _, row in jd_rows.iterrows():
                    company = row.get("PhongBan", "")
                    person = row.get("NhanSu", "")
                    jd_json = row.get("config_json", "{}")
                    try:
                        jd_data = json.loads(jd_json)
                        if company not in data["job_descriptions"]:
                            data["job_descriptions"][company] = {}
                        data["job_descriptions"][company][person] = jd_data
                    except:
                        pass
        
        needs_save = False
        if "personnel_by_department" not in data:
            data["personnel_by_department"] = DEFAULT_PERSONNEL.copy()
            needs_save = True
            
        if "cv_gsheet_url" not in data:
            data["cv_gsheet_url"] = ""
            needs_save = True
            
        if "companies" not in data:
            data["companies"] = default_config["companies"]
            needs_save = True
            
        return data
    except Exception as e:
        print("Error parsing DB config:", e)
        return default_config


# Load current config dynamically
config = load_config()

DEPT_ABBR = {
    "Ban L+˙nh -Êﬂ¶Ìo": "BL-…",
    "L+˙nh -Êﬂ¶Ìo": "BL-…",
    "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶": "HCNS",
    "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn": "TCKT",
    "Ban Kﬂ¶+ hoﬂ¶Ìch -…ﬂ¶∫u t¶¶": "KH-…T",
    "Ban Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶": "CB-…T",
    "Ban Kﬂ+¶ thuﬂ¶°t": "KT",
    "Ban -…ﬂ+¸n b+¶ Giﬂ¶˙i tﬂ+≈a": "-…BGT",
    "Ban Dﬂ+¶ +Ìn": "DA",
    "X+° nghiﬂ+Áp DTBD": "XN DTBD",
    "S+·n GDB-…S": "S+·n GDB-…S",
    "Tﬂ+Ú KPI": "Tﬂ+Ú KPI",
    "Ban chﬂ+Î huy C+¶ng tr¶¶ﬂ+•ng": "BCH CT",
    "X+° nghiﬂ+Áp xe m+Ìy thiﬂ¶+t bﬂ+Ô": "XN XMTB",
    "X+° nghiﬂ+Áp xe thiﬂ¶+t bﬂ+Ô": "XN XMTB"
}

for comp_name, comp_data in config.get("companies", {}).items():
    if "departments" in comp_data:
        comp_data["departments"] = [DEPT_ABBR.get(d, d) for d in comp_data["departments"]]
    if "personnel_by_department" in comp_data:
        new_personnel = {}
        for d, p in comp_data["personnel_by_department"].items():
            new_personnel[DEPT_ABBR.get(d, d)] = p
        comp_data["personnel_by_department"] = new_personnel


# Default owners by department and company for autofill
DEPT_ABBR = {
    "Ban L+˙nh -Êﬂ¶Ìo": "BL-…",
    "Ban H+·nh ch+°nh Nh+Ûn sﬂ+¶": "HCNS",
    "Ban T+·i ch+°nh Kﬂ¶+ to+Ìn": "TCKT",
    "Ban Kﬂ¶+ hoﬂ¶Ìch -…ﬂ¶∫u t¶¶": "KH-…T",
    "Ban Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶": "CB-…T",
    "Ban Kﬂ+¶ thuﬂ¶°t": "KT",
    "Ban -…ﬂ+¸n b+¶ Giﬂ¶˙i tﬂ+≈a": "-…BGT",
    "Ban Dﬂ+¶ +Ìn": "DA",
    "X+° nghiﬂ+Áp DTBD": "XN DTBD",
    "S+·n GDB-…S": "S+·n GDB-…S",
    "Tﬂ+Ú KPI": "Tﬂ+Ú KPI"
}

DEPT_LEADS = {
    "CTY CP -…ﬂ¶™U T¶ª -…+« Nﬂ¶¶NG - MIﬂ+«N TRUNG": {
        "BL-…": "Trﬂ¶∫n Quﬂ+Êc Thﬂ+‚",
        "HCNS": "Nguyﬂ+‡n Thﬂ+Ô Hﬂ¶Ình Ti+¨n",
        "TCKT": "-…ﬂ+Ùng Thﬂ+Ô Nguyﬂ+Át Nga",
        "KH-…T": "Nguyﬂ+‡n Trﬂ¶∫n Thﬂ+¨c",
        "CB-…T": "Hﬂ+Ù V-‚n Khoa",
        "KT": "Nguyﬂ+‡n V-‚n Bﬂ+Ùn",
        "-…BGT": "Nguyﬂ+‡n Ngﬂ+Ïc T+¶n",
        "DA": "Nguyﬂ+‡n -…+ºnh Thﬂ¶ªng",
        "XN DTBD": "Mai V-‚n Ch+Ûu",
        "S+·n GDB-…S": "Ng+¶ Thﬂ+Ô T+Ûm",
        "Tﬂ+Ú KPI": ""
    }
}

def get_personnel_for_company_dept(company, dept, config):
    companies = config.get("companies", {})
    if company in companies:
        return companies[company].get("personnel_by_department", {}).get(dept, [])
    # Fallback to global config if any, or empty list
    return config.get("personnel_by_department", {}).get(dept, [])

def get_departments_for_company(company, config):
    companies = config.get("companies", {})
    if company in companies:
        return companies[company].get("departments", [])
    
    # Aggregate all departments from all companies
    all_depts = set()
    for comp_data in companies.values():
        all_depts.update(comp_data.get("departments", []))
    global_depts = config.get("departments", [])
    all_depts.update(global_depts)
    return sorted(list(all_depts))


def get_filtered_projects(company_name, config, db_projs):
    companies = config.get("companies", {})
    projs_by_cat = {}
    if company_name in companies:
        projs_by_cat = companies[company_name].get("projects_by_category", {})
    else:
        projs_by_cat = config.get("projects_by_category", {})
        
    all_projs = []
    for cat, projs in projs_by_cat.items():
        all_projs.extend(projs)
        
    merged = list(set(all_projs + db_projs))
    return sorted(merged)

DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

# Gantt DB Configuration
GANTT_DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

def read_gantt_db():
    required_cols = ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "PhanTramHoanThanh", "Milestone", "QuanTrong", "KhanCap", "NgayCapNhat"]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="GANTT_KHDT", ttl=15)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
        else:
            
            df.columns = [str(c).strip() for c in df.columns]
            
            # 1. Tﬂ+¶ -Êﬂ+÷ng chuﬂ¶¨n h+¶a v+· +Ình xﬂ¶Ì t+¨n cﬂ+÷t
            col_mapping = {
                'M+˙ CV': 'ID', 'MaCV': 'ID',
                'T+¨n c+¶ng viﬂ+Ác': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nﬂ+÷i dung': 'TenCongViec', 'C+¶ng viﬂ+Ác': 'TenCongViec',
                'Tiﬂ¶+n -Êﬂ+÷ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiﬂ¶+n -Êﬂ+÷': 'PhanTramHoanThanh',
                'Trﬂ¶Ìng th+Ìi': 'TrangThai', 'Status': 'TrangThai',
                'Hﬂ¶Ìn ch+¶t': 'Deadline', 'Ng+·y ho+·n th+·nh': 'Deadline'
            }
            new_cols = []
            for c in df.columns:
                matched = c
                for k, v in col_mapping.items():
                    if c.lower() == k.lower():
                        matched = v
                        break
                new_cols.append(matched)
            df.columns = new_cols
            
            # 3. Xﬂ+° l++ dﬂ+ª liﬂ+Áu rﬂ+˘ng / NaN an to+·n
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('-…ang thﬂ+¶c hiﬂ+Án')
                df['TrangThai'] = df['TrangThai'].replace('', '-…ang thﬂ+¶c hiﬂ+Án')

    except Exception as e:
        import streamlit as st


        st.error(f"Lﬂ+˘i khi -Êﬂ+Ïc dﬂ+ª liﬂ+Áu GANTT_KHDT: {e}")
        raise e
        
    # Khﬂ+Éi tﬂ¶Ìo c+Ìc cﬂ+÷t thiﬂ¶+u
    for col in ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]:
        if col not in df.columns:
            df[col] = ""

            
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['NgayCapNhat'] = df['NgayCapNhat'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))
    df['ID'] = df['ID'].astype(str)
    df['TenDuAn'] = df['TenDuAn'].fillna('Dﬂ+¶ +Ìn mﬂ¶+c -Êﬂ+Ônh')
    df['TenCongViec'] = df['TenCongViec'].fillna('')
    df['GiaiDoan'] = df['GiaiDoan'].fillna('Kh+Ìc')
    df['Milestone'] = df['Milestone'].fillna('')
    df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0).astype(int)
    
    phase_mapping = {
        "Concept Dev": "1. Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶ & Nghi+¨n cﬂ+¨u Tiﬂ+¸n khﬂ¶˙ thi",
        "1. Ph+Ìt triﬂ+‚n +• t¶¶ﬂ+Éng & Khﬂ¶˙o s+Ìt": "1. Chuﬂ¶¨n bﬂ+Ô -…ﬂ¶∫u t¶¶ & Nghi+¨n cﬂ+¨u Tiﬂ+¸n khﬂ¶˙ thi",
        "System Design": "2. Ph+Ìp l++ Dﬂ+¶ +Ìn & Quy hoﬂ¶Ìch 1/500",
        "2. Thiﬂ¶+t kﬂ¶+ C¶Ì sﬂ+É & Quy hoﬂ¶Ìch": "2. Ph+Ìp l++ Dﬂ+¶ +Ìn & Quy hoﬂ¶Ìch 1/500",
        "Detail Design": "3. Thiﬂ¶+t kﬂ¶+ C¶Ì sﬂ+É & B+Ìo c+Ìo Tﬂ+¶ -Ê+Ình gi+Ì / -…TM",
        "3. Thiﬂ¶+t kﬂ¶+ Chi tiﬂ¶+t & Lﬂ¶°p B+Ìo c+Ìo": "3. Thiﬂ¶+t kﬂ¶+ C¶Ì sﬂ+É & B+Ìo c+Ìo Tﬂ+¶ -Ê+Ình gi+Ì / -…TM",
        "Legal / Regulatory": "4. Thiﬂ¶+t kﬂ¶+ Bﬂ¶˙n vﬂ¶+ Thi c+¶ng & Thﬂ¶¨m -Êﬂ+Ônh",
        "4. Ph+¨ duyﬂ+Át Ph+Ìp l++ & Thﬂ¶¨m -Êﬂ+Ônh": "4. Thiﬂ¶+t kﬂ¶+ Bﬂ¶˙n vﬂ¶+ Thi c+¶ng & Thﬂ¶¨m -Êﬂ+Ônh",
        "Test & Refine": "5. Cﬂ¶—p ph+¨p X+Ûy dﬂ+¶ng & Lﬂ+¶a chﬂ+Ïn Nh+· thﬂ¶∫u",
        "5. Thﬂ+° nghiﬂ+Ám & Chﬂ+Înh sﬂ+°a": "5. Cﬂ¶—p ph+¨p X+Ûy dﬂ+¶ng & Lﬂ+¶a chﬂ+Ïn Nh+· thﬂ¶∫u",
        "Produce": "6. Thi c+¶ng X+Ûy lﬂ¶ªp & Lﬂ¶ªp -Êﬂ¶+t Thiﬂ¶+t bﬂ+Ô",
        "Produce / Execute": "6. Thi c+¶ng X+Ûy lﬂ¶ªp & Lﬂ¶ªp -Êﬂ¶+t Thiﬂ¶+t bﬂ+Ô",
        "6. Triﬂ+‚n khai & Thﬂ+¶c thi": "6. Thi c+¶ng X+Ûy lﬂ¶ªp & Lﬂ¶ªp -Êﬂ¶+t Thiﬂ¶+t bﬂ+Ô"
    }
    df['GiaiDoan'] = df['GiaiDoan'].replace(phase_mapping)
    
    return df



def read_kpi_adjustments():
    import pandas as pd
    conn = get_gsheets_conn()
    empty_df = pd.DataFrame(columns=["ID", "TenNhanVien", "Thang", "Nam", "LoaiHanhVi", "DiemDieuChinh", "LyDo"])
    if conn is None:
        return empty_df
    try:
        df = safe_gsheets_read(conn, worksheet="KPI_ADJUSTMENTS", ttl=600)
        if df is None or df.empty:
            return empty_df
        for col in ["Thang", "Nam", "DiemDieuChinh"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        import streamlit as st


        st.error(f"Lﬂ+˘i khi -Êﬂ+Ïc trang t+°nh KPI_ADJUSTMENTS: {e}")
        raise e

def add_kpi_adjustment(ten, thang, nam, loai, diem, lydo):
    if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
    import pandas as pd
    df = read_kpi_adjustments()
    if not df.empty:
        dup = df[(df['TenNhanVien'] == ten) & (df['Thang'] == thang) & (df['Nam'] == nam) & (df['LoaiHanhVi'] == loai) & (df['DiemDieuChinh'] == diem) & (df['LyDo'] == lydo)]
        if not dup.empty:
            return True, ""
    if df.empty:
        new_id = 1
    else:
        max_id = pd.to_numeric(df['ID'], errors='coerce').max(skipna=True)
        new_id = 1 if pd.isna(max_id) else int(max_id) + 1
    new_row = {
        "ID": new_id,
        "TenNhanVien": ten,
        "Thang": thang,
        "Nam": nam,
        "LoaiHanhVi": loai,
        "DiemDieuChinh": diem,
        "LyDo": lydo
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            success = safe_gsheets_update(conn, worksheet="KPI_ADJUSTMENTS", data=df)
            if success:
                import streamlit as st


                if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
                return True, ""
            else:
                return False, "Kh+¶ng thﬂ+‚ cﬂ¶°p nhﬂ¶°t l+¨n Google Sheets (lﬂ+˘i -Ê+˙ ghi log)"
        except Exception as e:
            return False, str(e)
    return False, "Kh+¶ng kﬂ¶+t nﬂ+Êi -Ê¶¶ﬂ+˙c Google Sheets"

def edit_kpi_adjustment(adj_id, ten, thang, nam, loai, diem, lydo):
    if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
    import pandas as pd
    df = read_kpi_adjustments()
    if df.empty: return False, "Dﬂ+ª liﬂ+Áu trﬂ+Êng"
    idx = df[df['ID'] == adj_id].index
    if len(idx) == 0: return False, "Kh+¶ng t+ºm thﬂ¶—y ID"
    df.loc[idx[0], 'TenNhanVien'] = ten
    df.loc[idx[0], 'Thang'] = thang
    df.loc[idx[0], 'Nam'] = nam
    df.loc[idx[0], 'LoaiHanhVi'] = loai
    df.loc[idx[0], 'DiemDieuChinh'] = diem
    df.loc[idx[0], 'LyDo'] = lydo
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            success = safe_gsheets_update(conn, worksheet="KPI_ADJUSTMENTS", data=df)
            if success:
                import streamlit as st


                if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
                return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Lﬂ+˘i kﬂ¶+t nﬂ+Êi"

def delete_kpi_adjustment(adj_id):
    if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
    import pandas as pd
    df = read_kpi_adjustments()
    if df.empty: return False, "Dﬂ+ª liﬂ+Áu trﬂ+Êng"
    df = df[df['ID'].astype(str).str.strip() != str(adj_id).strip()]
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            success = safe_gsheets_update(conn, worksheet="KPI_ADJUSTMENTS", data=df)
            if success:
                import streamlit as st


                if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
                return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Lﬂ+˘i kﬂ¶+t nﬂ+Êi"


def save_gantt_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Ch¶¶a kﬂ¶+t nﬂ+Êi Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        
        safe_gsheets_update(conn, worksheet="GANTT_KHDT", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lﬂ+˘i l¶¶u Google Sheets: {e}')
        return False
def read_sqlite_table(table_name):
    try:
        conn = sqlite3.connect("database.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception:
        return None

def save_sqlite_table(df, table_name):
    try:
        conn = sqlite3.connect("database.db")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        
        if hasattr(read_sqlite_table, "clear"): 
            read_sqlite_table.clear()
            
        return True
    except Exception:
        return False

def convert_gsheet_to_csv_url(url):
    url = url.strip()
    if not url:
        return ""
    # Look for /spreadsheets/d/{spreadsheetId}
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        return url
    key = match.group(1)
    
    # Check if there is a gid parameter (specifying sheet ID)
    gid_match = re.search(r"gid=(\d+)", url)
    if gid_match:
        gid = gid_match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{key}/export?format=csv&gid={gid}"
    else:
        return f"https://docs.google.com/spreadsheets/d/{key}/export?format=csv"

def sync_incoming_docs_from_df(import_df, selected_company, today):
    # Normalize column names
    import_df.columns = [str(c).strip() for c in import_df.columns]
    
    # Map columns using a case-insensitive check
    mapping = {}
    fields = {
        "NG+«Y": ["NG+«Y", "Ng+·y", "Ngay"],
        "-…¶·N Vﬂ+Ë": ["-…¶·N Vﬂ+Ë", "-…¶Ìn vﬂ+Ô", "Don vi", "Co quan gui", "C¶Ì quan gﬂ+°i"],
        "Nﬂ+ˇI DUNG": ["Nﬂ+ˇI DUNG", "Nﬂ+÷i dung", "Noi dung", "Trich yeu", "Tr+°ch yﬂ¶+u"],
        "Sﬂ+Ê k++ hiﬂ+Áu": ["Sﬂ+Ê k++ hiﬂ+Áu", "Sﬂ+Ê / K++ hiﬂ+Áu", "So ky hieu", "Sﬂ+… K+• HIﬂ+ÂU", "SoKyHieu"],
        "Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh": ["Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh", "THﬂ+£I Hﬂ¶·N HO+«N TH+«NH", "Ng+·y ho+·n th+·nh", "NG+«Y HO+«N TH+«NH", "Deadline"],
        "Trﬂ¶Ìng th+Ìi": ["Trﬂ¶Ìng th+Ìi", "Trang thai", "TRﬂ¶·NG TH+¸I", "TrangThai"],
        "Ng¶¶ﬂ+•i/ Ban thﬂ+¶c hiﬂ+Án": ["Ng¶¶ﬂ+•i/ Ban thﬂ+¶c hiﬂ+Án", "Nguoi/ Ban thuc hien", "NG¶ªﬂ+£I/ BAN THﬂ+¶C HIﬂ+ÂN", "Bﬂ+÷ phﬂ¶°n chﬂ+∫ tr+º", "Ban chﬂ+∫ tr+º", "BanChuTri"],
        "Ghi ch+¶": ["Ghi ch+¶", "Ghi chu", "GhiChu", "Note", "Ghi ch+¶ kh+Ìc"]
    }
    
    for key, possibilities in fields.items():
        found_col = None
        for col in import_df.columns:
            if col.lower() in [p.lower() for p in possibilities]:
                found_col = col
                break
        mapping[key] = found_col
        
    # Check if critical columns exist
    critical_fields = ["Nﬂ+ˇI DUNG", "Sﬂ+Ê k++ hiﬂ+Áu", "Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh"]
    missing_critical = [f for f in critical_fields if mapping[f] is None]
    if missing_critical:
        return False, f"Thiﬂ¶+u c+Ìc cﬂ+÷t bﬂ¶ªt buﬂ+÷c trong bﬂ¶˙ng dﬂ+ª liﬂ+Áu: {', '.join(missing_critical)}"
        
    # Keep rows where "Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh" and "Nﬂ+ˇI DUNG" are not null / empty
    deadline_col = mapping["Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh"]
    content_col = mapping["Nﬂ+ˇI DUNG"]
    so_ky_hieu_col = mapping["Sﬂ+Ê k++ hiﬂ+Áu"]
    ghi_chu_col = mapping["Ghi ch+¶"]
    
    # Drop rows that are completely empty or have null deadline/content
    valid_df = import_df.dropna(subset=[deadline_col])
    valid_df = valid_df[valid_df[deadline_col].astype(str).str.strip() != ""]
    valid_df = valid_df[valid_df[content_col].notna() & (valid_df[content_col].astype(str).str.strip() != "")]
    
    if valid_df.empty:
        return False, "Kh+¶ng t+ºm thﬂ¶—y d+¶ng hﬂ+˙p lﬂ+Á n+·o chﬂ+¨a -Êﬂ¶∫y -Êﬂ+∫ th+¶ng tin 'Thﬂ+•i hﬂ¶Ìn ho+·n th+·nh' v+· 'Nﬂ+÷i dung'."
        
    with acquire_db_lock():
        
        docs_df = read_incoming_docs_db()
        tasks_df = read_db()
        
        success_count = 0
        update_count = 0
    
        # Convert today to date if it is datetime
        if isinstance(today, datetime):
            today = today.date()
            
        for _, row in valid_df.iterrows():
            # Parse fields
            date_col = mapping["NG+«Y"]
            if date_col and not pd.isna(row[date_col]):
                try:
                    ngay_ban_hanh = pd.to_datetime(row[date_col]).date()
                except Exception:
                    ngay_ban_hanh = today
            else:
                ngay_ban_hanh = today
                
            try:
                deadline_val = pd.to_datetime(row[deadline_col]).date()
            except Exception:
                continue
                
            so_ky_hieu = str(row[so_ky_hieu_col]).strip() if not pd.isna(row[so_ky_hieu_col]) else f"VB-{(datetime.utcnow() + timedelta(hours=7)).strftime('%M%S')}"
            co_quan_gui = str(row[mapping["-…¶·N Vﬂ+Ë"]]).strip() if mapping["-…¶·N Vﬂ+Ë"] and not pd.isna(row[mapping["-…¶·N Vﬂ+Ë"]]) else ""
            trich_yeu = str(row[content_col]).strip()
            
            ban_chu_tri_raw = str(row[mapping["Ng¶¶ﬂ+•i/ Ban thﬂ+¶c hiﬂ+Án"]]).strip() if mapping["Ng¶¶ﬂ+•i/ Ban thﬂ+¶c hiﬂ+Án"] and not pd.isna(row[mapping["Ng¶¶ﬂ+•i/ Ban thﬂ+¶c hiﬂ+Án"]]) else ""
            config = load_settings()
            all_depts = set(config.get("departments", []))
            for comp_data in config.get("companies", {}).values():
                all_depts.update(comp_data.get("departments", []))
                
            if ban_chu_tri_raw in all_depts:
                ban_chu_tri = ban_chu_tri_raw
            else:
                ban_chu_tri = "Ban L+˙nh -Êﬂ¶Ìo"
                
            trang_thai_raw = str(row[mapping["Trﬂ¶Ìng th+Ìi"]]).strip() if mapping["Trﬂ¶Ìng th+Ìi"] and not pd.isna(row[mapping["Trﬂ¶Ìng th+Ìi"]]) else "G≈¶ -…ang xﬂ+° l++"
            ghi_chu = str(row[ghi_chu_col]).strip() if ghi_chu_col and not pd.isna(row[ghi_chu_col]) else ""
            
            is_completed = trang_thai_raw in ["-…+˙ xong", "Ho+·n th+·nh", "-…+˙ ho+·n th+·nh", "G£‡ -…+˙ xong"]
            
            trang_thai = "G≈¶ -…ang xﬂ+° l++"
            if is_completed:
                trang_thai = "G£‡ -…+˙ xong"
            else:
                if pd.notna(deadline_val) and deadline_val < today:
                    days_late = (today - deadline_val).days
                    trang_thai = f"G‹·n+≈ Trﬂ+‡ hﬂ¶Ìn xﬂ+° l++ CV (Trﬂ+‡ {days_late} ng+·y)"
                else:
                    trang_thai = "G≈¶ -…ang xﬂ+° l++"
                    
            # Check duplicate in docs_df
            duplicate_doc = docs_df[docs_df['SoKyHieu'] == so_ky_hieu]
            
            if duplicate_doc.empty:
                # Generate next DOC ID
                next_doc_id = 1
                if not docs_df.empty:
                    ids = docs_df['ID'].tolist()
                    nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                    if nums:
                        next_doc_id = max(nums) + 1
                doc_id = f"DOC-{next_doc_id:03d}"
                
                new_doc_row = {
                    "ID": doc_id,
                    "DonVi": selected_company if selected_company != "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô" else "CTY CP -…ﬂ¶™U T¶ª -…+« Nﬂ¶¶NG - MIﬂ+«N TRUNG",
                    "SoKyHieu": so_ky_hieu,
                    "NgayBanHanh": ngay_ban_hanh,
                    "CoQuanGui": co_quan_gui,
                    "TrichYeu": trich_yeu,
                    "TenDuAn": "Quﬂ¶˙n l++ C+¶ng v-‚n -Êﬂ¶+n",
                    "GanttTaskId": "",
                    "BanChuTri": ban_chu_tri,
                    "Deadline": deadline_val,
                    "LinkFile": "",
                    "TrangThai": trang_thai,
                    "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    "GhiChu": ghi_chu
                }
                docs_df = pd.concat([docs_df, pd.DataFrame([new_doc_row])], ignore_index=True)
                success_count += 1
            else:
                # Update existing document
                doc_id = duplicate_doc.iloc[0]['ID']
                idx = docs_df[docs_df['ID'] == doc_id].index[0]
                docs_df.at[idx, "DonVi"] = selected_company if selected_company != "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô" else docs_df.at[idx, "DonVi"]
                docs_df.at[idx, "NgayBanHanh"] = ngay_ban_hanh
                docs_df.at[idx, "CoQuanGui"] = co_quan_gui
                docs_df.at[idx, "TrichYeu"] = trich_yeu
                docs_df.at[idx, "BanChuTri"] = ban_chu_tri
                docs_df.at[idx, "Deadline"] = deadline_val
                docs_df.at[idx, "TrangThai"] = trang_thai
                docs_df.at[idx, "NgayCapNhat"] = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                docs_df.at[idx, "GhiChu"] = ghi_chu
                update_count += 1
                
            # Update or create the associated Task in tasks_df
            task_name = f"=ÉÙ¨ [C+¶ng v-‚n -Êﬂ¶+n] {trich_yeu} (Sﬂ+Ê: {so_ky_hieu})"
            duplicate_task = tasks_df[tasks_df['TenCongViec'].str.contains(so_ky_hieu, na=False)]
            
            task_status = "-…ang thﬂ+¶c hiﬂ+Án"
            if trang_thai == "G£‡ -…+˙ xong":
                task_status = "Ho+·n th+·nh"
            elif pd.notna(deadline_val) and deadline_val < today:
                task_status = "Qu+Ì hﬂ¶Ìn"
                
            if duplicate_task.empty:
                next_tsk_id = 1
                if not tasks_df.empty:
                    t_ids = tasks_df['ID'].tolist()
                    t_nums = [int(m[0]) for idx in t_ids for m in [re.findall(r'\d+', str(idx))] if m]
                    if t_nums:
                        next_tsk_id = max(t_nums) + 1
                task_id = f"TSK-{next_tsk_id:03d}"
                
                new_task_row = {
                    "ID": task_id,
                    "DonVi": selected_company if selected_company != "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô" else "CTY CP -…ﬂ¶™U T¶ª -…+« Nﬂ¶¶NG - MIﬂ+«N TRUNG",
                    "PhongBan": ban_chu_tri,
                    "NguoiChuTri": "Ban L+˙nh -Êﬂ¶Ìo",
                    "TenDuAn": "Quﬂ¶˙n l++ C+¶ng v-‚n -Êﬂ¶+n",
                    "MocTienDo": "Tﬂ+¶ do",
                    "SanPhamBanGiao": "Xem chi tiﬂ¶+t v-‚n bﬂ¶˙n",
                    "TenCongViec": task_name,
                    "PhanLoaiChiSo": "Chﬂ+Î sﬂ+Ê kﬂ¶+t quﬂ¶˙ (Outcome Metric)",
                    "NgayBatDau": ngay_ban_hanh,
                    "Deadline": deadline_val,
                    "DoUuTien": "Trung b+ºnh",
                    "PhanTramHoanThanh": 100 if task_status == "Ho+·n th+·nh" else 99,
                    "TrangThai": task_status,
                    "LinkKetQua": "",
                    "GiaiTrinhDeXuat": "",
                    "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    "ChuKyTheoDoi": "Theo dﬂ+¶ +Ìn / Tﬂ+¶ do",
                    "PhanLoaiTreHan": "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷" if task_status != "Qu+Ì hﬂ¶Ìn" else "=ÉÊÒ Do chﬂ+∫ quan"
                }
                tasks_df = pd.concat([tasks_df, pd.DataFrame([new_task_row])], ignore_index=True)
            else:
                task_id = duplicate_task.iloc[0]['ID']
                t_idx = tasks_df[tasks_df['ID'] == task_id].index[0]
                tasks_df.at[t_idx, "PhongBan"] = ban_chu_tri
                tasks_df.at[t_idx, "TenCongViec"] = task_name
                tasks_df.at[t_idx, "NgayBatDau"] = ngay_ban_hanh
                tasks_df.at[t_idx, "Deadline"] = deadline_val
                tasks_df.at[t_idx, "TrangThai"] = task_status
                tasks_df.at[t_idx, "PhanTramHoanThanh"] = 100 if task_status == "Ho+·n th+·nh" else 99
            tasks_df.at[t_idx, "NgayCapNhat"] = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            
        if save_incoming_docs_db(docs_df) and save_db(tasks_df):
            return True, f"-…ﬂ+Ùng bﬂ+÷ th+·nh c+¶ng! -…+˙ th+¨m mﬂ+¢i {success_count} v-‚n bﬂ¶˙n v+· cﬂ¶°p nhﬂ¶°t {update_count} v-‚n bﬂ¶˙n."
        else:
            return False, "Kh+¶ng thﬂ+‚ l¶¶u dﬂ+ª liﬂ+Áu v+·o c¶Ì sﬂ+É dﬂ+ª liﬂ+Áu."

def read_incoming_docs_db():
    required_cols = [
        "ID", "DonVi", "SoKyHieu", "NgayBanHanh", "CoQuanGui", "TrichYeu", 
        "TenDuAn", "GanttTaskId", "BanChuTri", "Deadline", "LinkFile", 
        "TrangThai", "NgayCapNhat", "GhiChu"
    ]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="VAN_BAN_DEN", ttl=600)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
        else:
            
            df.columns = [str(c).strip() for c in df.columns]
            
            # 1. Tﬂ+¶ -Êﬂ+÷ng chuﬂ¶¨n h+¶a v+· +Ình xﬂ¶Ì t+¨n cﬂ+÷t
            col_mapping = {
                'M+˙ CV': 'ID', 'MaCV': 'ID',
                'T+¨n c+¶ng viﬂ+Ác': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nﬂ+÷i dung': 'TenCongViec', 'C+¶ng viﬂ+Ác': 'TenCongViec',
                'Tiﬂ¶+n -Êﬂ+÷ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiﬂ¶+n -Êﬂ+÷': 'PhanTramHoanThanh',
                'Trﬂ¶Ìng th+Ìi': 'TrangThai', 'Status': 'TrangThai',
                'Hﬂ¶Ìn ch+¶t': 'Deadline', 'Ng+·y ho+·n th+·nh': 'Deadline'
            }
            new_cols = []
            for c in df.columns:
                matched = c
                for k, v in col_mapping.items():
                    if c.lower() == k.lower():
                        matched = v
                        break
                new_cols.append(matched)
            df.columns = new_cols
            
            # 3. Xﬂ+° l++ dﬂ+ª liﬂ+Áu rﬂ+˘ng / NaN an to+·n
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('-…ang thﬂ+¶c hiﬂ+Án')
                df['TrangThai'] = df['TrangThai'].replace('', '-…ang thﬂ+¶c hiﬂ+Án')

    except Exception as e:
        pass
        df = pd.DataFrame(columns=required_cols)

    # Khﬂ+Éi tﬂ¶Ìo c+Ìc cﬂ+÷t thiﬂ¶+u -Êﬂ+‚ tr+Ình KeyError
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

        
    df['NgayBanHanh'] = pd.to_datetime(df['NgayBanHanh'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, errors='coerce'))).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['NgayCapNhat'] = df['NgayCapNhat'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))
    df['ID'] = df['ID'].astype(str)
    
    today_dt = date.today()
    for idx, row in df.iterrows():
        deadline_val = row['Deadline']
        status_val = str(row['TrangThai']).strip()
        
        if isinstance(deadline_val, str):
            try:
                deadline_val = datetime.strptime(deadline_val, '%Y-%m-%d').date()
            except Exception:
                pass
                
        if isinstance(deadline_val, datetime):
            deadline_val = deadline_val.date()
            
        if isinstance(deadline_val, date):
            if deadline_val < today_dt and "G£‡ -…+˙ xong" not in status_val and "-…+˙ xong" not in status_val:
                days_late = (today_dt - deadline_val).days
                df.at[idx, 'TrangThai'] = f"G‹·n+≈ Trﬂ+‡ hﬂ¶Ìn xﬂ+° l++ CV (Trﬂ+‡ {days_late} ng+·y)"
                
    return df

def save_incoming_docs_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Ch¶¶a kﬂ¶+t nﬂ+Êi Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBanHanh'] = df_save['NgayBanHanh'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        
        safe_gsheets_update(conn, worksheet="VAN_BAN_DEN", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lﬂ+˘i l¶¶u Google Sheets: {e}')
        return False

def read_db():
    # Force cache clear for new progress calculation rules
    required_cols = [
        "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
        "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI", "NguonGiaoViec", "MucDoGhiNhan"
    ]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="Sheet1", ttl=15)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
        else:
            
            df.columns = [str(c).strip() for c in df.columns]
            
            # 1. Tﬂ+¶ -Êﬂ+÷ng chuﬂ¶¨n h+¶a v+· +Ình xﬂ¶Ì t+¨n cﬂ+÷t
            col_mapping = {
                'M+˙ CV': 'ID', 'MaCV': 'ID',
                'T+¨n c+¶ng viﬂ+Ác': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nﬂ+÷i dung': 'TenCongViec', 'C+¶ng viﬂ+Ác': 'TenCongViec',
                'Tiﬂ¶+n -Êﬂ+÷ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiﬂ¶+n -Êﬂ+÷': 'PhanTramHoanThanh',
                'Trﬂ¶Ìng th+Ìi': 'TrangThai', 'Status': 'TrangThai',
                'Hﬂ¶Ìn ch+¶t': 'Deadline', 'Ng+·y ho+·n th+·nh': 'Deadline'
            }
            new_cols = []
            for c in df.columns:
                matched = c
                for k, v in col_mapping.items():
                    if c.lower() == k.lower():
                        matched = v
                        break
                new_cols.append(matched)
            df.columns = new_cols
            
            # 3. Xﬂ+° l++ dﬂ+ª liﬂ+Áu rﬂ+˘ng / NaN an to+·n
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('-…ang thﬂ+¶c hiﬂ+Án')
                df['TrangThai'] = df['TrangThai'].replace('', '-…ang thﬂ+¶c hiﬂ+Án')

    except Exception as e:
        import streamlit as st


        st.error(f"Lﬂ+˘i khi -Êﬂ+Ïc dﬂ+ª liﬂ+Áu Sheet1: {e}")
        raise e

    # Khﬂ+Éi tﬂ¶Ìo c+Ìc cﬂ+÷t thiﬂ¶+u -Êﬂ+‚ tr+Ình KeyError
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""


    # Check and initialize missing columns dynamically
    if "ChuKyTheoDoi" not in df.columns:
        df["ChuKyTheoDoi"] = "Theo dﬂ+¶ +Ìn / Tﬂ+¶ do"
    if "PhanLoaiTreHan" not in df.columns:
        df["PhanLoaiTreHan"] = "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
    if "NguonGiaoViec" not in df.columns:
        df["NguonGiaoViec"] = "C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º"
    if "MucDoGhiNhan" not in df.columns:
        df["MucDoGhiNhan"] = "Ch¶¶a -Ê+Ình gi+Ì"
    else:
        def clean_mucdo(val):
            val_str = str(val).strip()
            if val_str in ['nan', 'None', '', '0% (Kh+¶ng ghi nhﬂ¶°n)']: return "Ch¶¶a -Ê+Ình gi+Ì"
            if val_str == "0.5" or "50" in val_str: return "50%"
            if val_str == "0.8" or "80" in val_str: return "80%"
            if val_str == "0.9" or "90" in val_str: return "90%"
            if "miﬂ+‡n" in val_str.lower() or "loﬂ¶Ìi bﬂ+≈" in val_str.lower(): return "Miﬂ+‡n trﬂ+Ω (Loﬂ¶Ìi bﬂ+≈ KPI)"
            return val_str
        df["MucDoGhiNhan"] = df["MucDoGhiNhan"].apply(clean_mucdo)

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Clean data formats
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['NgayCapNhat'] = df['NgayCapNhat'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))
    df['DonVi'] = df['DonVi'].fillna('CTY CP DMT - MARINA (Du thuyﬂ+¸n Happy Yacht)')
    df['TenDuAn'] = df['TenDuAn'].fillna('')
    df['MocTienDo'] = df['MocTienDo'].fillna('Tﬂ+¶ do')
    df['SanPhamBanGiao'] = df['SanPhamBanGiao'].fillna('Xem chi tiﬂ¶+t')
    df['LinkKetQua'] = df['LinkKetQua'].fillna('')
    df['GiaiTrinhDeXuat'] = df['GiaiTrinhDeXuat'].fillna('')
    df['ChuKyTheoDoi'] = df['ChuKyTheoDoi'].fillna('Theo dﬂ+¶ +Ìn / Tﬂ+¶ do')
    df['PhanLoaiTreHan'] = df['PhanLoaiTreHan'].fillna('=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷')
    df['ID'] = df['ID'].astype(str)
    
    # =É∫¶ Auto-healing: Dﬂ+Ïn dﬂ¶¶p ho+·n to+·n c+Ìc c+¶ng viﬂ+Ác tr+¶ng lﬂ¶+p do lﬂ+˘i mﬂ¶Ìng / click -Ê+¶p (nﬂ¶+u c+¶)
    if 'ID' in df.columns:
        df['ID'] = df['ID'].astype(str).str.strip()
        df = df.drop_duplicates(subset=['ID'], keep='last').reset_index(drop=True)
    
    for idx, row in df.iterrows():
        is_comp = str(row['TrangThai']).strip() == "Ho+·n th+·nh"
        start_d = row['NgayBatDau']
        end_d = row['Deadline']
        df.at[idx, 'PhanTramHoanThanh'] = calculate_time_progress(start_d, end_d, is_comp)
        
    return df

def save_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Ch¶¶a kﬂ¶+t nﬂ+Êi Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['ChuKyTheoDoi'] = df_save['ChuKyTheoDoi'].fillna('Theo dﬂ+¶ +Ìn / Tﬂ+¶ do')
        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷')
        if 'NguonGiaoViec' not in df_save.columns: df_save['NguonGiaoViec'] = 'C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º'
        df_save['NguonGiaoViec'] = df_save['NguonGiaoViec'].fillna('C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º')
        if 'MucDoGhiNhan' not in df_save.columns: df_save['MucDoGhiNhan'] = '0% (Kh+¶ng ghi nhﬂ¶°n)'
        df_save['MucDoGhiNhan'] = df_save['MucDoGhiNhan'].fillna('0% (Kh+¶ng ghi nhﬂ¶°n)')
        
        df_save = df_save.where(pd.notnull(df_save), None)
        return safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)
    except Exception as e:
        st.error(f'Lﬂ+˘i l¶¶u Google Sheets: {e}')
        return False

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
st.markdown('<div class="main-title">DMT GROUP G«ˆ QUﬂ¶ÛN L+• TIﬂ¶+N -…ﬂ+ˇ</div>', unsafe_allow_html=True)

# Sidebar layout with logo image and fallback
logo_path = "logo.png" if os.path.exists("logo.png") else ("INPUT/logo.png" if os.path.exists("INPUT/logo.png") else None)
if logo_path:
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("=É∆Ì Vui l+¶ng -Êﬂ¶+t file logo.png v+·o th¶¶ mﬂ+—c gﬂ+Êc cﬂ+∫a dﬂ+¶ +Ìn -Êﬂ+‚ hiﬂ+‚n thﬂ+Ô logo.")
    st.sidebar.markdown("### DMT GROUP")
st.sidebar.markdown("---")

# Link Google Sheets Config (Silently initialize for all users)
if "gsheet_url" not in st.session_state:
    st.session_state["gsheet_url"] = load_settings().get("gsheet_url", "")

company_options = ["Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô"] + list(COMPANIES.keys())
selected_company = st.sidebar.selectbox(
    "CHﬂ+ÓN C+ˆNG TY / TH+«NH VI+ËN", 
    company_options, 
    index=1,
    format_func=lambda x: str(x).replace("CTY CP", "C+ˆNG TY CP")
)

role_mode = st.sidebar.selectbox("QUYﬂ+«N TRUY Cﬂ¶ºP", ["Nh+Ûn vi+¨n", "Quﬂ¶˙n l++", "HR"], index=0)


if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False
if "is_manager_authenticated" not in st.session_state:
    st.session_state.is_manager_authenticated = False
if "is_personal_authenticated" not in st.session_state:
    st.session_state.is_personal_authenticated = False
if "personal_user" not in st.session_state:
    st.session_state.personal_user = None

if role_mode == "Quﬂ¶˙n l++":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_admin_authenticated = False
    if not st.session_state.is_manager_authenticated:
        mgr_pwd = st.sidebar.text_input("Nhﬂ¶°p Mﬂ¶°t khﬂ¶¨u Quﬂ¶˙n l++", type="password")
        if mgr_pwd:
            if mgr_pwd == "quanly123":
                st.session_state.is_manager_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mﬂ¶°t khﬂ¶¨u kh+¶ng -Ê+¶ng!")
    
    if st.session_state.is_manager_authenticated:
        st.sidebar.success("-…+˙ x+Ìc thﬂ+¶c quyﬂ+¸n Quﬂ¶˙n l++!")
        
        if st.sidebar.button("-…-‚ng xuﬂ¶—t"):
            st.session_state.is_manager_authenticated = False
            st.rerun()
            
        valid_depts = get_departments_for_company(selected_company, config)
        st.sidebar.markdown("### =É≈Û Ph+¶ng/Ban cﬂ+∫a bﬂ¶Ìn")
        current_idx = 0
        if st.session_state.get('manager_dept') in valid_depts:
            current_idx = valid_depts.index(st.session_state.manager_dept)
        if valid_depts:
            st.session_state.manager_dept = st.sidebar.selectbox("Lﬂ+Ïc dﬂ+ª liﬂ+Áu theo Ph+¶ng/Ban:", valid_depts, index=current_idx, label_visibility="collapsed")

elif role_mode == "HR":
    st.session_state.is_personal_authenticated = False
    st.session_state.personal_user = None
    st.session_state.is_manager_authenticated = False
    if not st.session_state.is_admin_authenticated:
        admin_pwd = st.sidebar.text_input("Nhﬂ¶°p Mﬂ¶°t khﬂ¶¨u HR", type="password")
        if admin_pwd:
            if admin_pwd == "admindmt123":
                st.session_state.is_admin_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mﬂ¶°t khﬂ¶¨u kh+¶ng -Ê+¶ng!")
    
    if st.session_state.is_admin_authenticated:
        st.sidebar.success("-…+˙ x+Ìc thﬂ+¶c to+·n quyﬂ+¸n (HR)!")
        
        if st.sidebar.button("-…-‚ng xuﬂ¶—t", key="logout_hr"):
            st.session_state.is_admin_authenticated = False
            st.rerun()

elif role_mode == "Nh+Ûn vi+¨n":
    st.session_state.is_admin_authenticated = False
    st.session_state.is_manager_authenticated = False
    
    if not st.session_state.is_personal_authenticated:
        st.sidebar.markdown("### =ÉÊÒ X+Ìc thﬂ+¶c Nh+Ûn vi+¨n")
        valid_depts = get_departments_for_company(selected_company, config)
        sel_login_dept = st.sidebar.selectbox("1. Chﬂ+Ïn Ph+¶ng ban", ["-- Chﬂ+Ïn --"] + valid_depts, key="login_dept")
        
        if sel_login_dept != "-- Chﬂ+Ïn --":
            personnel_list = get_personnel_for_company_dept(selected_company, sel_login_dept, config)
            if personnel_list:
                sel_login_user = st.sidebar.selectbox("2. Chﬂ+Ïn T+¨n cﬂ+∫a bﬂ¶Ìn", ["-- Chﬂ+Ïn --"] + personnel_list, key="login_user")
                if sel_login_user != "-- Chﬂ+Ïn --":
                    if st.sidebar.button("X+Ìc nhﬂ¶°n -…-‚ng nhﬂ¶°p"):
                        st.session_state.is_personal_authenticated = True
                        st.session_state.personal_user = sel_login_user
                        st.rerun()
            else:
                st.sidebar.warning("Ph+¶ng ban n+·y ch¶¶a c+¶ dﬂ+ª liﬂ+Áu nh+Ûn sﬂ+¶.")
    else:
        st.sidebar.success(f"=ÉÊÔ Xin ch+·o, {st.session_state.personal_user}!")
        if st.sidebar.button("-…-‚ng xuﬂ¶—t"):
            st.session_state.is_personal_authenticated = False
            st.session_state.personal_user = None
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
    "=É‹« Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác",
    "GPÚ Th+¨m / Cﬂ¶°p Nhﬂ¶°t C+¶ng Viﬂ+Ác",
    "=ÉÙË Quﬂ¶˙n trﬂ+Ô BSC - KPI",
        "=ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn"
]
if is_mobile:
    menu_options.insert(0, "=ÉÊ« Bﬂ¶ÛNG Tﬂ+ˆNG QUAN (View)")

if st.session_state.get('is_manager_authenticated', False):
    menu_options = [
        "=ÉÙÔ Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác",
        "GPÚ Th+¨m / Cﬂ¶°p Nhﬂ¶°t C+¶ng Viﬂ+Ác",
        "G‹˚n+≈ Duyﬂ+Át viﬂ+Ác Kh+Ìch quan",
        "=É≈Â -…+Ình gi+Ì KPI & Xﬂ¶+p loﬂ¶Ìi",
        "=ÉÙË Quﬂ¶˙n trﬂ+Ô BSC - KPI",
        "=ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn"
    ]
    if is_mobile:
        menu_options.insert(0, "=ÉÙË Bﬂ¶ÛNG Tﬂ+ˆNG QUAN (View)")

if st.session_state.is_admin_authenticated:
    menu_options = [
        "=ÉÊ« Bﬂ¶ÛNG Tﬂ+ˆNG QUAN (View)",
        "=É‹« Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác",
        "GPÚ Th+¨m / Cﬂ¶°p Nhﬂ¶°t C+¶ng Viﬂ+Ác",
        "G£‡ Duyﬂ+Át & Nghiﬂ+Ám thu c+¶ng viﬂ+Ác",
        "=É≈Â -…+Ình gi+Ì KPI & Xﬂ¶+p loﬂ¶Ìi",
        "=ÉˆÏ Quﬂ¶˙n l++ & -…ﬂ+Êi chiﬂ¶+u JD",
        "G‹÷n+≈ Quﬂ¶˙n L++ Cﬂ¶—u H+ºnh",
        "=ÉÙË Quﬂ¶˙n trﬂ+Ô BSC - KPI",
        "=ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn"
    ]

menu = st.sidebar.radio(
    "PH+ÈN Hﬂ+Â CHﬂ+øC N-ÈNG",
    menu_options,
    index=0
)

st.sidebar.markdown("---")

# Current date
df = read_db()
if not df.empty and "PhongBan" in df.columns:
    df["PhongBan"] = df["PhongBan"].map(lambda x: DEPT_ABBR.get(x, x))

gantt_df = read_gantt_db()
today = date.today()

# Filter display dataframe based on sidebar selected company
if selected_company != "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
    display_df = df[df['DonVi'] == selected_company].copy()
else:
    display_df = df.copy()
    
if 'NguoiChuTri' not in display_df.columns:
    display_df['NguoiChuTri'] = ''

# -------- Lﬂ+ÓC C+¸ NH+ÈN ---------
if role_mode == "Nh+Ûn vi+¨n" and st.session_state.is_personal_authenticated:
    all_owners = sorted(list(display_df['NguoiChuTri'].dropna().astype(str).unique()))
    
    # The user has already selected their identity during login, so no need for 'Bﬂ¶Ìn l+· ai?' selectbox
    pass
    # Filter display_df
    if st.session_state.personal_user:
        display_df = display_df[display_df['NguoiChuTri'] == st.session_state.personal_user].copy()
        
# -------- Lﬂ+ÓC QUﬂ¶ÛN L+• ---------
if role_mode == "Quﬂ¶˙n l++" and st.session_state.get('is_manager_authenticated', False):
    if st.session_state.get('manager_dept'):
        display_df = display_df[display_df['PhongBan'] == st.session_state.manager_dept].copy()

# ------------------------------

# Statistics helpers
total_v = len(display_df)
done_v = len(display_df[display_df['TrangThai'] == 'Ho+·n th+·nh'])
issue_v = len(display_df[display_df['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc'])
overdue_v = len(display_df[(pd.to_datetime(display_df['Deadline'], errors='coerce') < pd.Timestamp(today)) & (display_df['TrangThai'] != 'Ho+·n th+·nh')])
doing_v = total_v - done_v - issue_v - overdue_v
if doing_v < 0:
    doing_v = 0

# Sidebar Excel Download
import io
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_styled_excel(tasks_df, df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Write Sheet1 (Drop ID column if exists)
        tasks_df_copy = tasks_df.copy()
        
        # Format the PhanLoaiTreHan column for Excel
        formatted_causes = []
        for _, row in tasks_df_copy.iterrows():
            is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
            deadline = row.get('Deadline')
            if isinstance(deadline, str):
                try:
                    deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                except Exception:
                    pass
            ref_today = today
            if isinstance(ref_today, datetime):
                ref_today = ref_today.date()
            if isinstance(deadline, datetime):
                deadline = deadline.date()
                
            is_late = False
            if isinstance(deadline, date):
                is_late = (deadline < ref_today) and not is_comp
                
            if not is_late:
                formatted_causes.append("")
            else:
                val = row.get('PhanLoaiTreHan', '')
                if "chﬂ+∫ quan" in str(val).lower():
                    formatted_causes.append("[Do chﬂ+∫ quan]")
                elif "kh+Ìch quan" in str(val).lower():
                    explain = row.get('GiaiTrinhDeXuat', '')
                    if explain and explain != "--" and str(explain).strip():
                        formatted_causes.append(f"[Do kh+Ìch quan] - {str(explain).strip()}")
                    else:
                        formatted_causes.append("[Do kh+Ìch quan]")
                else:
                    formatted_causes.append("")
                    
        tasks_df_copy['PhanLoaiTreHan'] = formatted_causes
        tasks_df_copy = tasks_df_copy.rename(columns={'PhanLoaiTreHan': 'Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn'})
        
        # Column filtering and renaming
        export_cols = {
            'NgayBatDau': 'Ng+·y bﬂ¶ªt -Êﬂ¶∫u',
            'Deadline': 'Hﬂ¶Ìn ch+¶t',
            'TrangThai': 'Trﬂ¶Ìng th+Ìi thﬂ+¶c hiﬂ+Án',
            'NguoiChuTri': 'Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án',
            'PhongBan': 'Ph+¶ng ban',
            'TenDuAn': 'Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c',
            'TenCongViec': 'T+¨n c+¶ng viﬂ+Ác',
            'GiaiTrinhDeXuat': 'Ghi ch+¶ / Giﬂ¶˙i tr+ºnh v¶¶ﬂ+¢ng mﬂ¶ªc'
        }
        
        cols_to_keep = [c for c in export_cols.keys() if c in tasks_df_copy.columns]
        tasks_df_copy = tasks_df_copy[cols_to_keep]
        tasks_df_copy = tasks_df_copy.rename(columns=export_cols)
        tasks_df_copy.insert(0, 'STT', range(1, len(tasks_df_copy) + 1))
        
        desired_order = ['STT', 'Ng+·y bﬂ¶ªt -Êﬂ¶∫u', 'Hﬂ¶Ìn ch+¶t', 'Trﬂ¶Ìng th+Ìi thﬂ+¶c hiﬂ+Án', 'Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án', 'Ph+¶ng ban', 'Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c', 'T+¨n c+¶ng viﬂ+Ác', 'Ghi ch+¶ / Giﬂ¶˙i tr+ºnh v¶¶ﬂ+¢ng mﬂ¶ªc']
        final_cols = [c for c in desired_order if c in tasks_df_copy.columns]
        tasks_df_copy = tasks_df_copy[final_cols]
        
        for col in ['Ng+·y bﬂ¶ªt -Êﬂ¶∫u', 'Hﬂ¶Ìn ch+¶t']:
            if col in tasks_df_copy.columns:
                tasks_df_copy[col] = pd.to_datetime(tasks_df_copy[col], errors='coerce').dt.strftime('%d/%m/%Y').fillna('')
                
        tasks_df_copy.to_excel(writer, sheet_name="Sheet1", index=False)
        
        # Write GANTT_KHDT (Drop ID column if exists)
        df_copy = df.copy()
        if 'ID' in df_copy.columns:
            df_copy = df_copy.drop(columns=['ID'])
        if 'NgayCapNhat' in df_copy.columns:
            df_copy['NgayCapNhat'] = df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_copy.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
        
        # Write VAN_BAN_DEN (Drop ID column if exists)
        try:
            docs_df = read_incoming_docs_db()
            docs_df_copy = docs_df.copy()
            if 'ID' in docs_df_copy.columns:
                docs_df_copy = docs_df_copy.drop(columns=['ID'])
            if 'NgayCapNhat' in docs_df_copy.columns:
                docs_df_copy['NgayCapNhat'] = docs_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
            for col_name in ['NgayBanHanh', 'Deadline']:
                if col_name in docs_df_copy.columns:
                    docs_df_copy[col_name] = docs_df_copy[col_name].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
            docs_df_copy = docs_df_copy.rename(columns={
                'SoKyHieu': 'Sﬂ+Ê / K++ hiﬂ+Áu v-‚n bﬂ¶˙n',
                'NgayBanHanh': 'Ng+·y ban h+·nh',
                'CoQuanGui': 'C¶Ì quan / -…¶Ìn vﬂ+Ô gﬂ+°i',
                'TrichYeu': 'Tr+°ch yﬂ¶+u nﬂ+÷i dung',
                'TenDuAn': 'Dﬂ+¶ +Ìn li+¨n quan',
                'GanttTaskId': 'M+˙ CV Gantt li+¨n kﬂ¶+t',
                'BanChuTri': 'Bﬂ+÷ phﬂ¶°n chﬂ+∫ tr+º xﬂ+° l++',
                'Deadline': 'Hﬂ¶Ìn xﬂ+° l++ / Phﬂ¶˙n hﬂ+Ùi',
                'LinkFile': '-…+°nh k+øm Link / File',
                'TrangThai': 'Trﬂ¶Ìng th+Ìi xﬂ+° l++',
                'NgayCapNhat': 'Thﬂ+•i gian cﬂ¶°p nhﬂ¶°t'
            })
            docs_df_copy.to_excel(writer, sheet_name="VAN_BAN_DEN", index=False)
        except Exception:
            pass
            
        workbook = writer.book
        
        # Helper to style each worksheet
        def style_worksheet(ws):
            navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            white_bold_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            normal_font = Font(name="Calibri", size=11)
            
            center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
            left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
            
            thin_border_side = Side(border_style="thin", color="CCCCCC")
            thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
            
            headers = [str(cell.value or '') for cell in ws[1]]
            
            ws.row_dimensions[1].height = 28
            for col_idx, cell in enumerate(ws[1], 1):
                cell.fill = navy_fill
                cell.font = white_bold_font
                cell.alignment = center_align
                cell.border = thin_border
                
            for row in range(2, ws.max_row + 1):
                ws.row_dimensions[row].height = 22
                for col in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.font = normal_font
                    cell.border = thin_border
                    
                    col_name = headers[col - 1]
                    if col_name in ["ID", "STT", "NgayBatDau", "Deadline", "Deadline", "PhanTramHoanThanh", "TrangThai", "NgayCapNhat"]:
                        cell.alignment = center_align
                    else:
                        cell.alignment = left_align
                        
                    if col_name == "PhanTramHoanThanh":
                        cell.number_format = '0"%"'
                        
            # Autofit columns
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val_str = str(cell.value or '').replace('\n', ' ')
                    if len(val_str) > max_len:
                        max_len = len(val_str)
                ws.column_dimensions[col_letter].width = min(max(max_len + 4, 10), 45)
                
        style_worksheet(workbook["Sheet1"])
        style_worksheet(workbook["GANTT_KHDT"])
        if "VAN_BAN_DEN" in workbook.sheetnames:
            style_worksheet(workbook["VAN_BAN_DEN"])
        
    return output.getvalue()

st.sidebar.markdown("---")
st.sidebar.markdown("### =ÉÙ— XUﬂ¶ÒT Dﬂ+´ LIﬂ+ÂU EXCEL")
try:
    df_for_excel = df
    styled_excel_data = generate_styled_excel(df, df_for_excel)
    st.sidebar.download_button(
        label="Tﬂ¶˙i xuﬂ+Êng tﬂ+Áp Excel",
        data=styled_excel_data,
        file_name="DATA_TIEN_DO_KPI.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_sidebar_excel_dl"
    )
except Exception as e:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.sidebar.download_button(
                label="Tﬂ¶˙i xuﬂ+Êng tﬂ+Áp Excel (Dﬂ+¶ ph+¶ng)",
                data=f.read(),
                file_name="DATA_TIEN_DO_KPI.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_sidebar_excel_dl_fallback"
            )



# Helper function to clean project name whitespace
def clean_proj_name(name):
    return name.strip()

# ----------------- 1. DASHBOARD Tﬂ+ˆNG QUAN -----------------
if menu in ["=É‹« Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác", "=ÉÙÔ Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác"]:
    st.info("=É∆Ì **Gﬂ+˙i ++:** -…ﬂ+‚ xem chi tiﬂ¶+t h¶¶ﬂ+¢ng dﬂ¶Ωn sﬂ+° dﬂ+—ng phﬂ¶∫n mﬂ+¸m, bﬂ¶Ìn h+˙y nhﬂ¶—p v+·o mﬂ+—c **=ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn** ﬂ+É thanh Menu b+¨n tr+Ìi nh+¨!")
    
    st.markdown(f"### =É‹« Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác G«ˆ {selected_company}")

    
    # Calculate stats based on filtered dash_df
    dash_df = display_df.copy()
    total_dash = len(dash_df)
    done_dash = len(dash_df[dash_df['TrangThai'] == 'Ho+·n th+·nh'])
    
    # T+°nh sﬂ+Ê viﬂ+Ác V¶¶ﬂ+¢ng mﬂ¶ªc HOﬂ¶¶C Trﬂ+‡ hﬂ¶Ìn (kh+¶ng -Êﬂ¶+m tr+¶ng)
    is_issue = dash_df['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc'
    is_overdue = (pd.to_datetime(dash_df['Deadline'], errors='coerce') < pd.Timestamp(today)) & (dash_df['TrangThai'] != 'Ho+·n th+·nh')
    issue_and_overdue_count = len(dash_df[is_issue | is_overdue])
    
    doing_dash = total_dash - done_dash - issue_and_overdue_count
    if doing_dash < 0:
        doing_dash = 0
        
    # 4 metrics cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Tﬂ+Úng sﬂ+Ê viﬂ+Ác", total_dash)
    with m_col2:
        st.metric("-…+˙ xong", done_dash)
    with m_col3:
        st.metric("-…ang l+·m", doing_dash)
    with m_col4:
        st.metric("=Éˆ¶ Trﬂ+‡ hﬂ¶Ìn / V¶¶ﬂ+¢ng mﬂ¶ªc", issue_and_overdue_count)

    st.markdown("---")
    
    st.markdown("""
        <style>
        button[data-baseweb="tab"] {
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 1rem !important;
        }
        button[data-baseweb="tab"] span {
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #555555 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] span {
            color: #1976d2 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tab_report, tab_giaoban, tab_data = st.tabs(["=ÉÙË C+ˆNG VIﬂ+ÂC Tﬂ+‹I Hﬂ¶·N", "=ÉÙÛ B+¸O C+¸O GIAO BAN", "=ÉÙÔ Bﬂ¶ÛNG THEO D+ÚI TIﬂ¶+N -…ﬂ+ˇ C+ˆNG VIﬂ+ÂC"])
    
    with tab_report:
        st.markdown(f"### =ÉÙË Dashboard Tﬂ+Úng Quan G«ˆ {selected_company}")
    
        pass
        
        # Overdue and due today/tomorrow alerts scanning (Group 1 & 2)
        def get_badge_and_urgency(deadline_val, today_dt):
            if pd.isna(deadline_val):
                return None, None
            if not isinstance(deadline_val, date):
                if isinstance(deadline_val, datetime):
                    deadline_val = deadline_val.date()
                else:
                    return None, None
            if deadline_val < today_dt:
                days_late = (today_dt - deadline_val).days
                return f"=Éˆ¶ [G‹·n+≈ Trﬂ+‡ {days_late} ng+·y]", 1
            elif deadline_val == today_dt:
                return "G≈¶ [Hﬂ¶Ìn h+¶m nay]", 2
            elif deadline_val == today_dt + timedelta(days=1):
                return "G‹·n+≈ [Hﬂ¶Ìn ng+·y mai]", 3
            return None, None

        alert_list = []
        for _, row in dash_df[dash_df['TrangThai'] != 'Ho+·n th+·nh'].iterrows():
            badge, urgency = get_badge_and_urgency(row['Deadline'], today)
            if badge:
                row_copy = row.copy()
                row_copy['Badge'] = badge
                row_copy['Urgency'] = urgency
                alert_list.append(row_copy)

        if alert_list:
            alert_df_show = pd.DataFrame(alert_list)
            if 'NgayCapNhat' in alert_df_show.columns:
                alert_df_show = alert_df_show.sort_values(by=["Urgency", "NgayCapNhat", "ID"], ascending=[True, False, False])
            else:
                alert_df_show = alert_df_show.sort_values(by=["Urgency", "Deadline"])
            st.error(f"=É‹ø **Cﬂ¶ÛNH B+¸O: Dﬂ+¶ +¸N C+Ù {len(alert_df_show)} Hﬂ¶·NG Mﬂ+ÒC Cﬂ¶™N L¶ªU +• (TRﬂ+‰ Hﬂ¶·N / Sﬂ¶´P -…ﬂ¶+N Hﬂ¶·N)**")        
        st.markdown("---")
    
        # Critical alert panel
        st.markdown("### G‹·n+≈ Hﬂ¶Ìng mﬂ+—c cﬂ¶∫n l¶¶u ++ (Trﬂ+‡ hﬂ¶Ìn hoﬂ¶+c Sﬂ¶ªp -Êﬂ¶+n hﬂ¶Ìn)")
    
        if alert_list:
            alert_df_show = pd.DataFrame(alert_list)
            if 'NgayCapNhat' in alert_df_show.columns:
                alert_df_show = alert_df_show.sort_values(by=["Urgency", "NgayCapNhat", "ID"], ascending=[True, False, False])
            else:
                alert_df_show = alert_df_show.sort_values(by=["Urgency", "Deadline"])
            crit_display = pd.DataFrame()
            crit_display['Ng+·y bﬂ¶ªt -Êﬂ¶∫u'] = alert_df_show['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
            crit_display['Hﬂ¶Ìn ch+¶t'] = alert_df_show['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
            crit_display['Tiﬂ¶+n -Êﬂ+÷'] = alert_df_show['PhanTramHoanThanh'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "0%")
            crit_display['Trﬂ¶Ìng th+Ìi thﬂ+¶c tﬂ¶+'] = alert_df_show['Badge']
            crit_display['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'] = alert_df_show['NguoiChuTri']
            crit_display['Ph+¶ng ban'] = alert_df_show['PhongBan']
            crit_display['Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c'] = alert_df_show['TenDuAn']
            crit_display['T+¨n c+¶ng viﬂ+Ác'] = alert_df_show['TenCongViec']
            crit_display['Ghi ch+¶ / Giﬂ¶˙i tr+ºnh v¶¶ﬂ+¢ng mﬂ¶ªc'] = alert_df_show['GiaiTrinhDeXuat']
        
            st.dataframe(
                crit_display,
                column_config={
                    "Ng+·y bﬂ¶ªt -Êﬂ¶∫u": st.column_config.TextColumn("Ng+·y bﬂ¶ªt -Êﬂ¶∫u", width=90),
                    "Hﬂ¶Ìn ch+¶t": st.column_config.TextColumn("Hﬂ¶Ìn ch+¶t", width=150),
                    "Tiﬂ¶+n -Êﬂ+÷": st.column_config.TextColumn("Tiﬂ¶+n -Êﬂ+÷", width=80),
                    "Trﬂ¶Ìng th+Ìi thﬂ+¶c tﬂ¶+": st.column_config.TextColumn("Trﬂ¶Ìng th+Ìi thﬂ+¶c tﬂ¶+", width=120),
                    "Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án": st.column_config.TextColumn("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án", width=150),
                    "Ph+¶ng ban": st.column_config.TextColumn("Ph+¶ng ban", width=80),
                    "Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c": st.column_config.TextColumn("Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", width=200),
                    "T+¨n c+¶ng viﬂ+Ác": st.column_config.TextColumn("T+¨n c+¶ng viﬂ+Ác", width="large"),
                    "Ghi ch+¶ / Giﬂ¶˙i tr+ºnh v¶¶ﬂ+¢ng mﬂ¶ªc": st.column_config.TextColumn("Ghi ch+¶ / Giﬂ¶˙i tr+ºnh v¶¶ﬂ+¢ng mﬂ¶ªc", width="large")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("=ÉƒÎ -…ﬂ¶˙m bﬂ¶˙o tiﬂ¶+n -Êﬂ+÷: Kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o bﬂ+Ô trﬂ+‡ hﬂ¶Ìn hoﬂ¶+c sﬂ¶ªp -Êﬂ¶+n hﬂ¶Ìn cﬂ¶∫n l¶¶u ++!")
        
        st.markdown("---")
    


    # ----------------- 1.5. B+¸O C+¸O GIAO BAN -----------------
    with tab_giaoban:
        st.markdown(f"### =ÉÙÛ B+Ìo c+Ìo Giao ban G«ˆ {selected_company}")
        
        # Th+¨m filters
        col_f1, col_f2 = st.columns([1, 2.5])
        with col_f1:
            month_opts = ["Tﬂ¶—t cﬂ¶˙ c+Ìc th+Ìng"] + [f"Th+Ìng {i}" for i in range(1, 13)]
            gb_month = st.selectbox("Lﬂ+Ïc theo Th+Ìng", month_opts, index=0)
        with col_f2:
            gb_status = st.radio("Lﬂ+Ïc trﬂ¶Ìng th+Ìi", ["Tﬂ¶—t cﬂ¶˙", "=Éˆ¶ Cﬂ¶∫n ch+¶ ++ gﬂ¶—p", "=ÉÉÌ Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn (GÎÒ3 ng+·y)", "=Éˆ¶ -…ang thﬂ+¶c hiﬂ+Án", "G£‡ Ho+·n th+·nh"], horizontal=True)
            
        # Lﬂ+Ïc c+Ìc c+¶ng viﬂ+Ác c+¶ nguﬂ+Ùn giao viﬂ+Ác l+· "Giao ban"
        gb_df = display_df[display_df['NguonGiaoViec'].astype(str).str.contains("Giao ban", na=False, case=False)].copy()
        
        if not gb_df.empty:
            def _get_deadline_status(row):
                st_val = str(row.get('TrangThai', ''))
                if st_val == 'Ho+·n th+·nh': return "G£‡ Ho+·n th+·nh"
                if st_val == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc': return "=Éˆ— -…ang v¶¶ﬂ+¢ng mﬂ¶ªc"
                
                dl = row.get('Deadline')
                if pd.isna(dl) or dl == "": return "=Éˆ¶ -…ang thﬂ+¶c hiﬂ+Án"
                try:
                    if isinstance(dl, str): dl_date = datetime.strptime(dl, "%Y-%m-%d").date()
                    else: dl_date = dl.date() if isinstance(dl, datetime) else dl
                    diff = (dl_date - today).days
                    if diff < 0: return f"=Éˆ¶ Qu+Ì hﬂ¶Ìn {-diff} ng+·y"
                    if diff <= 3: return f"=ÉÉÌ Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn ({diff} ng+·y)"
                    return "=Éˆ¶ -…ang thﬂ+¶c hiﬂ+Án"
                except:
                    return "=Éˆ¶ -…ang thﬂ+¶c hiﬂ+Án"
            
            gb_df['T+ºnh trﬂ¶Ìng'] = gb_df.apply(_get_deadline_status, axis=1)
            
            if gb_month != "Tﬂ¶—t cﬂ¶˙ c+Ìc th+Ìng":
                m_num = int(gb_month.replace("Th+Ìng ", ""))
                def _match_month(dl):
                    if pd.isna(dl) or dl == "": return False
                    try:
                        if isinstance(dl, str): d = datetime.strptime(dl, "%Y-%m-%d").date()
                        else: d = dl.date() if isinstance(dl, datetime) else dl
                        return d.month == m_num
                    except: return False
                gb_df = gb_df[gb_df['Deadline'].apply(_match_month)]
                
            if gb_status == "=Éˆ¶ Cﬂ¶∫n ch+¶ ++ gﬂ¶—p":
                gb_df = gb_df[gb_df['T+ºnh trﬂ¶Ìng'].str.contains("=Éˆ¶|=Éˆ—", na=False)]
            elif gb_status == "=ÉÉÌ Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn (GÎÒ3 ng+·y)":
                gb_df = gb_df[gb_df['T+ºnh trﬂ¶Ìng'].str.contains("=ÉÉÌ", na=False)]
            elif gb_status == "=Éˆ¶ -…ang thﬂ+¶c hiﬂ+Án":
                gb_df = gb_df[gb_df['T+ºnh trﬂ¶Ìng'].str.contains("=Éˆ¶", na=False)]
            elif gb_status == "G£‡ Ho+·n th+·nh":
                gb_df = gb_df[gb_df['T+ºnh trﬂ¶Ìng'].str.contains("G£‡", na=False)]

            def _get_priority_gb(row):
                st_val = str(row.get('T+ºnh trﬂ¶Ìng', ''))
                if '=Éˆ¶' in st_val or '=Éˆ—' in st_val: return 0
                if '=ÉÉÌ' in st_val: return 1
                if '=Éˆ¶' in st_val: return 2
                return 3
            gb_df['SortPriority'] = gb_df.apply(_get_priority_gb, axis=1)
            if 'NgayCapNhat' in gb_df.columns:
                gb_df = gb_df.sort_values(by=['SortPriority', 'NgayCapNhat', 'ID'], ascending=[True, False, False]).reset_index(drop=True)
            else:
                gb_df = gb_df.sort_values(by=['SortPriority', 'ID'], ascending=[True, False]).reset_index(drop=True)
        
        if gb_df.empty:
            st.info('Ch¶¶a c+¶ c+¶ng viﬂ+Ác n+·o c+¶ "Nguﬂ+Ùn giao viﬂ+Ác" l+· "Giao ban" ph+¶ hﬂ+˙p vﬂ+¢i bﬂ+÷ lﬂ+Ïc.')
            st.write('=É∆Ì Nﬂ¶+u ch¶¶a c+¶ c+¶ng viﬂ+Ác, h+˙y chﬂ+Ïn Nguﬂ+Ùn giao viﬂ+Ác l+· **C+¶ng viﬂ+Ác trong "Giao ban"** khi tﬂ¶Ìo hoﬂ¶+c cﬂ¶°p nhﬂ¶°t c+¶ng viﬂ+Ác.')
        else:
            total_gb = len(gb_df)
            done_gb = len(gb_df[gb_df['TrangThai'] == 'Ho+·n th+·nh'])
            issue_gb = len(gb_df[gb_df['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc'])
            
            gb_col1, gb_col2, gb_col3, gb_col4 = st.columns(4)
            gb_col1.metric("=ÉÙÓ Tﬂ+Úng Sﬂ+Ê Viﬂ+Ác Giao Ban", total_gb)
            gb_col2.metric("G£‡ -…+˙ Ho+·n Th+·nh", done_gb)
            gb_col3.metric("=Éˆ— -…ang V¶¶ﬂ+¢ng Mﬂ¶ªc", issue_gb)
            gb_col4.metric("G≈¶ -…ang Thﬂ+¶c Hiﬂ+Án", total_gb - done_gb - issue_gb)
            
            st.markdown("#### =ÉÙÔ Danh s+Ìch chi tiﬂ¶+t:")
            
            # Formatting the table for Giao ban
            gb_display = gb_df[['Deadline', 'NguoiChuTri', 'TenCongViec', 'PhanTramHoanThanh', 'T+ºnh trﬂ¶Ìng', 'GiaiTrinhDeXuat']]
            
            mobile_mode_gb = st.checkbox("=ÉÙ¶ Chﬂ¶+ -Êﬂ+÷ -…iﬂ+Án thoﬂ¶Ìi", value=False, key="mobile_gb", help="Hiﬂ+‚n thﬂ+Ô dﬂ¶Ìng thﬂ¶+ dﬂ+Ïc -Êﬂ+‚ xem tr+¨n mobile")
            
            if mobile_mode_gb:
                st.markdown("---")
                for idx, row in gb_df.iterrows():
                    prog = int(row['PhanTramHoanThanh']) if pd.notna(row['PhanTramHoanThanh']) else 0
                    try:
                        dl_str = row['Deadline'].strftime('%d/%m/%Y') if pd.notna(row['Deadline']) and hasattr(row['Deadline'], 'strftime') else str(row['Deadline'])
                    except:
                        dl_str = ""
                    
                    with st.container():
                        st.markdown(f"**=ÉÙÓ {row['TenCongViec']}**")
                        st.markdown(f"=ÉÊÒ *{row['NguoiChuTri']}* | T+ºnh trﬂ¶Ìng: **{row['T+ºnh trﬂ¶Ìng']}**")
                        st.markdown(f"G≈¶ **Hﬂ¶Ìn ch+¶t:** {dl_str} | Giﬂ¶˙i tr+ºnh: *{row.get('GiaiTrinhDeXuat', '')}*")
                        st.caption(f"Tiﬂ¶+n -Êﬂ+÷: {prog}%")
                        st.progress(prog)
                        st.markdown("---")
            else:
                st.dataframe(
                    gb_display,
                    column_config={
                        "Deadline": st.column_config.DateColumn("Hﬂ¶Ìn ch+¶t", format="DD/MM/YYYY"),
                        "NguoiChuTri": "Ng¶¶ﬂ+•i phﬂ+— tr+Ìch",
                        "TenCongViec": st.column_config.TextColumn("T+¨n c+¶ng viﬂ+Ác", width="large"),
                        "PhanTramHoanThanh": st.column_config.ProgressColumn("Tiﬂ¶+n -Êﬂ+÷", format="%d%%", min_value=0, max_value=100),
                        "T+ºnh trﬂ¶Ìng": st.column_config.TextColumn("T+ºnh trﬂ¶Ìng"),
                        "GiaiTrinhDeXuat": st.column_config.TextColumn("V¶¶ﬂ+¢ng mﬂ¶ªc / Giﬂ¶˙i tr+ºnh", width="medium")
                    },
                    use_container_width=True,
                    hide_index=True
                )

    # ----------------- 2. Bﬂ¶ÛNG TIﬂ¶+N -…ﬂ+ˇ CHI TIﬂ¶+T -----------------

    with tab_data:
        st.markdown(f"### =ÉÙÔ Bﬂ¶˙ng Tiﬂ¶+n -…ﬂ+÷ C+¶ng Viﬂ+Ác Chi Tiﬂ¶+t G«ˆ {selected_company}")
    
        # Filter tools for Boss
        is_personal = role_mode == "Nh+Ûn vi+¨n" and st.session_state.get("is_personal_authenticated", False)
        
        if is_personal:
            col_filter1, col_filter3 = st.columns(2)
            sel_owner_filter = "Tﬂ¶—t cﬂ¶˙"
        else:
            col_filter1, col_filter2, col_filter3 = st.columns(3)
    
        with col_filter1:
            db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
            merged_projs = get_filtered_projects(selected_company, config, db_projs)
            proj_options = ["Tﬂ¶—t cﬂ¶˙ dﬂ+¶ +Ìn"] + merged_projs
            sel_proj_filter = st.selectbox("Lﬂ+Ïc nhanh theo Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", proj_options)
        
        if not is_personal:
            with col_filter2:
                owners = ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(display_df['NguoiChuTri'].dropna().astype(str).unique())) if not display_df.empty else ["Tﬂ¶—t cﬂ¶˙"]
                sel_owner_filter = st.selectbox("Lﬂ+Ïc theo Ng¶¶ﬂ+•i phﬂ+— tr+Ìch", owners)
            
        with col_filter3:
            months = set()
            if not display_df.empty:
                for _, row in display_df.iterrows():
                    if pd.notna(row.get('NgayBatDau')) and hasattr(row['NgayBatDau'], 'strftime'):
                        months.add(row['NgayBatDau'].strftime('%m/%Y'))
                    if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                        months.add(row['Deadline'].strftime('%m/%Y'))
            month_options = ["Tﬂ¶—t cﬂ¶˙ c+Ìc th+Ìng"] + sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
            sel_month_filter = st.selectbox("Lﬂ+Ïc nhanh theo Th+Ìng", month_options)
        
        # Apply filters
        table_df = display_df.copy()
        if sel_proj_filter != "Tﬂ¶—t cﬂ¶˙ dﬂ+¶ +Ìn":
            clean_proj = clean_proj_name(sel_proj_filter)
            table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
            
        if sel_owner_filter != "Tﬂ¶—t cﬂ¶˙":
            table_df = table_df[table_df['NguoiChuTri'] == sel_owner_filter]
        
        if sel_month_filter != "Tﬂ¶—t cﬂ¶˙ c+Ìc th+Ìng":
            target_month = sel_month_filter
            mask = (
                table_df['NgayBatDau'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
            ) | (
                table_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
            )
            table_df = table_df[mask]
            
        # Sﬂ¶ªp xﬂ¶+p: Ghim Trﬂ+‡ hﬂ¶Ìn/V¶¶ﬂ+¢ng mﬂ¶ªc l+¨n -Êﬂ¶∫u, sau -Ê+¶ mﬂ+¢i -Êﬂ¶+n c+¶ng viﬂ+Ác mﬂ+¢i cﬂ¶°p nhﬂ¶°t
        def _get_priority(row):
            st_val = str(row.get('TrangThai', ''))
            if 'Trﬂ+‡ hﬂ¶Ìn' in st_val or 'V¶¶ﬂ+¢ng mﬂ¶ªc' in st_val or '=Éˆ¶' in st_val or 'G‹·n+≈' in st_val:
                return 0
            return 1
            
        table_df['SortPriority'] = table_df.apply(_get_priority, axis=1)
        if 'NgayCapNhat' in table_df.columns:
            table_df = table_df.sort_values(by=['SortPriority', 'NgayCapNhat', 'ID'], ascending=[True, False, False]).reset_index(drop=True)
        else:
            table_df = table_df.sort_values(by=['SortPriority', 'ID'], ascending=[True, False]).reset_index(drop=True)
        
        if table_df.empty:
            st.info("Kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o ph+¶ hﬂ+˙p vﬂ+¢i bﬂ+÷ lﬂ+Ïc.")
        else:
            df_display = pd.DataFrame()
            df_display['Ph+¶ng ban'] = table_df['PhongBan']
            df_display['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'] = table_df['NguoiChuTri']
            df_display['Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c'] = table_df['TenDuAn']
            df_display['T+¨n c+¶ng viﬂ+Ác'] = table_df['TenCongViec']
            df_display['Ng+·y bﬂ¶ªt -Êﬂ¶∫u'] = table_df['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
            import pandas as pd
            df_display['Tﬂ++ trﬂ+Ïng KPI'] = table_df.apply(lambda row: f"{int(float(str(row.get('TyTrongKPI', 0)).strip() or 0))}%" if pd.to_numeric(row.get('TyTrongKPI', 0), errors='coerce') > 0 else "Tﬂ+¶ chia", axis=1)
        
            # Format Hﬂ¶Ìn ch+¶t
            def format_dl(row):
                if pd.isna(row['Deadline']) or not isinstance(row['Deadline'], (date, datetime)): return ""
                prog = int(row['PhanTramHoanThanh'])
                date_str = row['Deadline'].strftime('%d/%m/%Y')
            
                if prog >= 100:
                    return date_str
            
                # prog < 100
                days_left = (row['Deadline'] - today).days
                if days_left < 0:
                    days_late = abs(days_left)
                    return f"=Éˆ¶ {date_str} (Trﬂ+‡ hﬂ¶Ìn {days_late} ng+·y)"
                elif days_left == 0:
                    return f"G≈¶ {date_str} (Hﬂ¶Ìn h+¶m nay)"
                elif 1 <= days_left <= 3:
                    return f"G‹·n+≈ {date_str} (Sﬂ¶ªp hﬂ¶Ìn - C+¶n {days_left} ng+·y)"
                else:
                    return date_str
            df_display['Hﬂ¶Ìn ch+¶t'] = table_df.apply(format_dl, axis=1)
        
            df_display['Tiﬂ¶+n -Êﬂ+÷'] = table_df['PhanTramHoanThanh']
        
            # Format Trﬂ¶Ìng th+Ìi
            def format_status(row):
                prog = int(row['PhanTramHoanThanh'])
                is_issue = row['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc'
            
                if prog >= 100:
                    return "G£‡ -…+˙ xong"
                
                # prog < 100
                if pd.notna(row['Deadline']) and row['Deadline'] < today:
                    return "G‹·n+≈ Trﬂ+‡ hﬂ¶Ìn"
                
                if is_issue:
                    return "=Éˆ¶ V¶¶ﬂ+¢ng mﬂ¶ªc"
                
                from datetime import date, datetime
                if prog == 0 and pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)) and row['NgayBatDau'] > today:
                    return "G•Ó Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
                
                # Default state based on start date
                if pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)):
                    if today >= row['NgayBatDau']:
                        return "G≈¶ -…ang thﬂ+¶c hiﬂ+Án"
                    else:
                        return "G•Ó Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
                else:
                    return "G≈¶ -…ang thﬂ+¶c hiﬂ+Án"
            df_display['Trﬂ¶Ìng th+Ìi'] = table_df.apply(format_status, axis=1)
        
            # Format Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn
            def format_late_cause(row):
                is_comp = (row['TrangThai'] == 'Ho+·n th+·nh')
                is_late = (pd.notna(row['Deadline']) and row['Deadline'] < today) and not is_comp
                if not is_late:
                    return "--"
            
                val = row.get('PhanLoaiTreHan', '')
                if "chﬂ+∫ quan" in str(val).lower():
                    return "=Éˆ¶ [Do chﬂ+∫ quan]"
                elif "kh+Ìch quan" in str(val).lower():
                    explain = row.get('GiaiTrinhDeXuat', '')
                    if pd.notna(explain) and str(explain).strip():
                        return f"G‹·n+≈ [Do kh+Ìch quan] - {str(explain).strip()}"
                    return "G‹·n+≈ [Do kh+Ìch quan]"
                else:
                    return "--"
            df_display['Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn'] = table_df.apply(format_late_cause, axis=1)
        
            # Format Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm
            def format_notes(row):
                is_comp = (row['TrangThai'] == 'Ho+·n th+·nh')
                if is_comp:
                    val = row['LinkKetQua']
                    if not val or pd.isna(val):
                        return "Ch¶¶a -Ê+°nh k+øm kﬂ¶+t quﬂ¶˙"
                    if isinstance(val, str) and val.startswith("OUTPUT"):
                        display_name = os.path.basename(val)
                        if "_" in display_name:
                            display_name = display_name.split("_", 1)[1]
                        return f"=ÉÙ¸ {display_name}"
                    return str(val)
                else:
                    return row['GiaiTrinhDeXuat'] if (isinstance(row['GiaiTrinhDeXuat'], str) and row['GiaiTrinhDeXuat']) else "--"
            df_display['Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm'] = table_df.apply(format_notes, axis=1)
        
            # Reorder columns
            ordered_cols = [
                'Ng+·y bﬂ¶ªt -Êﬂ¶∫u',
                'Hﬂ¶Ìn ch+¶t',
                'Tiﬂ¶+n -Êﬂ+÷',
                'Trﬂ¶Ìng th+Ìi',
                'Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án',
                'Ph+¶ng ban',
                'Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c',
                'T+¨n c+¶ng viﬂ+Ác',
                'Tﬂ++ trﬂ+Ïng KPI',
                'Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn',
                'Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm'
            ]
            df_display = df_display[ordered_cols]
        
            # Render clean st.dataframe
            st.dataframe(
                df_display,
                column_config={
                    "Ng+·y bﬂ¶ªt -Êﬂ¶∫u": st.column_config.TextColumn("Ng+·y bﬂ¶ªt -Êﬂ¶∫u", width=90),
                    "Hﬂ¶Ìn ch+¶t": st.column_config.TextColumn("Hﬂ¶Ìn ch+¶t", width=150),
                    "Tiﬂ¶+n -Êﬂ+÷": st.column_config.ProgressColumn(
                        "Tiﬂ¶+n -Êﬂ+÷",
                        format="%d%%",
                        min_value=0,
                        max_value=100,
                        width=100
                    ),
                    "Trﬂ¶Ìng th+Ìi": st.column_config.TextColumn("Trﬂ¶Ìng th+Ìi", width=120),
                    "Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án": st.column_config.TextColumn("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án", width=150),
                    "Ph+¶ng ban": st.column_config.TextColumn("Ph+¶ng ban", width=80),
                    "Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c": st.column_config.TextColumn("Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", width=200),
                    "T+¨n c+¶ng viﬂ+Ác": st.column_config.TextColumn("T+¨n c+¶ng viﬂ+Ác", width="large"),
                    "Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn": st.column_config.TextColumn("Nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn", width=150),
                    "Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm": st.column_config.LinkColumn(
                        "Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm",
                        max_chars=300,
                        width="medium"
                    )
                },
                use_container_width=True,
                hide_index=True
            )

elif menu in ["=ÉÊ« Bﬂ¶ÛNG Tﬂ+ˆNG QUAN (View)", "=ÉÙË Bﬂ¶ÛNG Tﬂ+ˆNG QUAN (View)"]:
    # 1. Hide Streamlit UI elements for a clean dashboard view
    st.markdown("""
        <style>
            
            
            
            .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### =ÉÙË Bﬂ¶˙ng Tﬂ+Úng Quan (View) G«ˆ {selected_company}")
    
    col_f1, col_f2, col_f3, col_auto = st.columns([2, 2, 2, 1])
    with col_f1:
        db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
        merged_projs = get_filtered_projects(selected_company, config, db_projs)
        proj_options = ["Tﬂ¶—t cﬂ¶˙ dﬂ+¶ +Ìn"] + merged_projs
        sel_proj = st.selectbox("Lﬂ+Ïc Dﬂ+¶ +Ìn", proj_options, key="tv_proj")
    with col_f2:
        dept_options = ["Tﬂ¶—t cﬂ¶˙ ph+¶ng ban"] + get_departments_for_company(selected_company, config)
        sel_dept = st.selectbox("Lﬂ+Ïc Ph+¶ng ban", dept_options, key="tv_dept")
    with col_f3:
        status_options = ["-…ang thﬂ+¶c hiﬂ+Án", "Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn / Trﬂ+‡ hﬂ¶Ìn", "Ho+·n th+·nh", "V¶¶ﬂ+¢ng mﬂ¶ªc", "Tﬂ¶—t cﬂ¶˙ trﬂ¶Ìng th+Ìi"]
        sel_status = st.selectbox("Lﬂ+Ïc Trﬂ¶Ìng th+Ìi", status_options, key="tv_status", index=1)
    with col_auto:
        auto_refresh = st.checkbox("=Éˆ‰ Auto-refresh (5p)", value=True, help="Tﬂ+¶ -Êﬂ+÷ng tﬂ¶˙i lﬂ¶Ìi trang sau mﬂ+˘i 5 ph+¶t")
        mobile_mode = st.checkbox("=ÉÙ¶ Chﬂ¶+ -Êﬂ+÷ -…iﬂ+Án thoﬂ¶Ìi", value=False, help="Hiﬂ+‚n thﬂ+Ô dﬂ¶Ìng thﬂ¶+ dﬂ+Ïc -Êﬂ+‚ xem tr+¨n mobile")
        if auto_refresh:
            import streamlit.components.v1 as components
            components.html("""
                <script>
                    setTimeout(function(){
                        window.parent.location.reload();
                    }, 300000);
                </script>
            """, height=0, width=0)
            
    # Apply filters
    table_df = display_df.copy()
    if sel_proj != "Tﬂ¶—t cﬂ¶˙ dﬂ+¶ +Ìn":
        clean_proj = clean_proj_name(sel_proj)
        table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
    if sel_dept != "Tﬂ¶—t cﬂ¶˙ ph+¶ng ban":
        table_df = table_df[table_df['PhongBan'] == sel_dept]
        
    def get_days_left(d):
        if pd.notna(d) and hasattr(d, 'strftime'):
            if isinstance(d, datetime):
                d = d.date()
            return (d - today).days
        return 999

    if sel_status == "-…ang thﬂ+¶c hiﬂ+Án":
        table_df = table_df[
            (table_df['TrangThai'] != 'Ho+·n th+·nh') & 
            (table_df['TrangThai'] != 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc') & 
            (table_df['Deadline'].apply(get_days_left) > 3)
        ]
    elif sel_status == "Sﬂ¶ªp tﬂ+¢i hﬂ¶Ìn / Trﬂ+‡ hﬂ¶Ìn":
        table_df = table_df[
            (table_df['TrangThai'] != 'Ho+·n th+·nh') & 
            (table_df['Deadline'].apply(get_days_left) <= 3)
        ]
    elif sel_status == "Ho+·n th+·nh":
        table_df = table_df[table_df['TrangThai'] == 'Ho+·n th+·nh']
    elif sel_status == "V¶¶ﬂ+¢ng mﬂ¶ªc":
        table_df = table_df[table_df['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc']
        
    def _get_priority(row):
        st_val = str(row.get('TrangThai', ''))
        if 'Trﬂ+‡ hﬂ¶Ìn' in st_val or 'V¶¶ﬂ+¢ng mﬂ¶ªc' in st_val or '=Éˆ¶' in st_val or 'G‹·n+≈' in st_val:
            return 0
        return 1
        
    table_df['SortPriority'] = table_df.apply(_get_priority, axis=1)
    if 'NgayCapNhat' in table_df.columns:
        table_df = table_df.sort_values(by=['NgayCapNhat', 'SortPriority', 'ID'], ascending=[False, True, False]).reset_index(drop=True)
    else:
        table_df = table_df.sort_values(by=['SortPriority', 'ID'], ascending=[True, False]).reset_index(drop=True)
        
    if table_df.empty:
        st.info("Kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o ph+¶ hﬂ+˙p vﬂ+¢i bﬂ+÷ lﬂ+Ïc.")
    else:
        df_display = pd.DataFrame()
        df_display['Ph+¶ng ban'] = table_df['PhongBan']
        df_display['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'] = table_df['NguoiChuTri']
        df_display['Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c'] = table_df['TenDuAn']
        df_display['T+¨n c+¶ng viﬂ+Ác'] = table_df['TenCongViec']
        df_display['Ng+·y bﬂ¶ªt -Êﬂ¶∫u'] = table_df['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_display['Tﬂ++ trﬂ+Ïng KPI'] = table_df.apply(lambda row: f"{int(float(str(row.get('TyTrongKPI', 0)).strip() or 0))}%" if pd.to_numeric(row.get('TyTrongKPI', 0), errors='coerce') > 0 else "Tﬂ+¶ chia", axis=1)
        
        def format_dl(row):
            if pd.isna(row['Deadline']) or not isinstance(row['Deadline'], (date, datetime)): return ""
            prog = int(row['PhanTramHoanThanh'])
            date_str = row['Deadline'].strftime('%d/%m/%Y')
            if prog >= 100: return date_str
            days_left = (row['Deadline'] - today).days
            if days_left < 0: return f"=Éˆ¶ {date_str} (Trﬂ+‡ {abs(days_left)} ng+·y)"
            elif days_left == 0: return f"G≈¶ {date_str} (Hﬂ¶Ìn h+¶m nay)"
            elif 1 <= days_left <= 3: return f"G‹·n+≈ {date_str} (C+¶n {days_left} ng+·y)"
            else: return date_str
        df_display['Hﬂ¶Ìn ch+¶t'] = table_df.apply(format_dl, axis=1)
        
        df_display['Tiﬂ¶+n -Êﬂ+÷'] = table_df['PhanTramHoanThanh']
        
        def format_status(row):
            prog = int(row['PhanTramHoanThanh'])
            if prog >= 100: return "G£‡ -…+˙ xong"
            if pd.notna(row['Deadline']) and row['Deadline'] < today: return "G‹·n+≈ Trﬂ+‡ hﬂ¶Ìn"
            if row['TrangThai'] == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc': return "=Éˆ¶ V¶¶ﬂ+¢ng mﬂ¶ªc"
            from datetime import date, datetime
            if prog == 0 and pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)) and row['NgayBatDau'] > today: return "G•Ó Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
            if pd.notna(row['NgayBatDau']) and isinstance(row['NgayBatDau'], (date, datetime)):
                if today >= row['NgayBatDau']: return "G≈¶ -…ang thﬂ+¶c hiﬂ+Án"
            return "G•Ó Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
        df_display['Trﬂ¶Ìng th+Ìi'] = table_df.apply(format_status, axis=1)
        
        ordered_cols = ['Ng+·y bﬂ¶ªt -Êﬂ¶∫u', 'Hﬂ¶Ìn ch+¶t', 'Tiﬂ¶+n -Êﬂ+÷', 'Trﬂ¶Ìng th+Ìi', 'Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án', 'Ph+¶ng ban', 'Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c', 'T+¨n c+¶ng viﬂ+Ác']
        df_display = df_display[ordered_cols]
        
        st.markdown("---")
        if mobile_mode:
            for idx, row in df_display.iterrows():
                prog = int(row['Tiﬂ¶+n -Êﬂ+÷'])
                
                with st.container():
                    st.markdown(f"**=ÉÙÓ {row['T+¨n c+¶ng viﬂ+Ác']}**")
                    st.markdown(f"=ÉÙ¸ *{row['Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c']}* | =ÉÊÒ *{row['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án']}*")
                    st.markdown(f"G≈¶ **Hﬂ¶Ìn ch+¶t:** {row['Hﬂ¶Ìn ch+¶t']} | Trﬂ¶Ìng th+Ìi: **{row['Trﬂ¶Ìng th+Ìi']}**")
                    st.caption(f"Tiﬂ¶+n -Êﬂ+÷: {prog}%")
                    st.progress(prog)
                    st.markdown("---")
        else:
            st.dataframe(
                df_display,
                column_config={
                    "Ng+·y bﬂ¶ªt -Êﬂ¶∫u": st.column_config.TextColumn("Ng+·y bﬂ¶ªt -Êﬂ¶∫u", width=90),
                    "Hﬂ¶Ìn ch+¶t": st.column_config.TextColumn("Hﬂ¶Ìn ch+¶t", width=150),
                    "Tiﬂ¶+n -Êﬂ+÷": st.column_config.ProgressColumn("Tiﬂ¶+n -Êﬂ+÷", format="%d%%", min_value=0, max_value=100, width=100),
                    "Trﬂ¶Ìng th+Ìi": st.column_config.TextColumn("Trﬂ¶Ìng th+Ìi", width=120),
                    "Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án": st.column_config.TextColumn("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án", width=150),
                    "Ph+¶ng ban": st.column_config.TextColumn("Ph+¶ng ban", width=80),
                    "Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c": st.column_config.TextColumn("Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", width=200),
                    "T+¨n c+¶ng viﬂ+Ác": st.column_config.TextColumn("T+¨n c+¶ng viﬂ+Ác", width="large")
                },
                use_container_width=True,
                hide_index=True,
                height=700
            )

# ----------------- 3. TH+ËM / Cﬂ¶ºP NHﬂ¶ºT C+ˆNG VIﬂ+ÂC -----------------


elif menu == "GPÚ Th+¨m / Cﬂ¶°p Nhﬂ¶°t C+¶ng Viﬂ+Ác":
    st.markdown("### G£≈n+≈ Ph+Ûn hﬂ+Á Th+¨m / Cﬂ¶°p Nhﬂ¶°t C+¶ng Viﬂ+Ác")
    
    tab_new, tab_update = st.tabs(["GPÚ Khﬂ+Éi tﬂ¶Ìo c+¶ng viﬂ+Ác mﬂ+¢i", "G£≈n+≈ Cﬂ¶°p nhﬂ¶°t tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác"])
    
    # Form: Add New
    with tab_new:
        st.markdown("#### Th+¨m mﬂ+¢i c+¶ng viﬂ+Ác tﬂ+¶ do")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Company selection
            company_list = list(COMPANIES.keys())
            default_company_idx = 0
            if selected_company in company_list:
                default_company_idx = company_list.index(selected_company)
            entry_company = st.selectbox(
                "-…¶Ìn vﬂ+Ô / C+¶ng ty th+·nh vi+¨n", 
                company_list, 
                index=default_company_idx,
                format_func=lambda x: str(x).replace("CTY CP", "C+ˆNG TY CP")
            )
            
            # 4. Department
            allowed_depts = get_departments_for_company(entry_company, config)
            is_personal = (role_mode == "Nh+Ûn vi+¨n" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
            if is_personal:
                # Deduce their department from their existing tasks or default to first
                user_dept_mode = display_df['PhongBan'].mode()
                user_dept = user_dept_mode[0] if not user_dept_mode.empty else allowed_depts[0]
                task_dept = st.selectbox("Ph+¶ng ban chﬂ+Ôu tr+Ìch nhiﬂ+Ám", [user_dept], index=0, disabled=True)
            else:
                task_dept = st.selectbox("Ph+¶ng ban chﬂ+Ôu tr+Ìch nhiﬂ+Ám", allowed_depts)
            
            # 5. Owner (based on configuration with custom type option)
            dept_personnel = get_personnel_for_company_dept(entry_company, task_dept, config)
            owner_options = list(dept_personnel) + ["G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i kh+Ìc..."]
            
            # Find default lead index if present in department personnel
            dept_lead = DEPT_LEADS.get(entry_company, {}).get(task_dept, "")
            default_lead_idx = 0
            if dept_lead in dept_personnel:
                default_lead_idx = dept_personnel.index(dept_lead)
            
            is_personal = (role_mode == "Nh+Ûn vi+¨n" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
            if is_personal:
                sel_owner_opt = st.selectbox("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án / Phﬂ+— tr+Ìch", [st.session_state.personal_user], index=0, disabled=True)
                task_owner = st.session_state.personal_user
            else:
                sel_owner_opt = st.selectbox("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án / Phﬂ+— tr+Ìch", owner_options, index=default_lead_idx)
                if sel_owner_opt == "G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i kh+Ìc...":
                    task_owner = st.text_input("G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án kh+Ìc...", value="")
                else:
                    task_owner = sel_owner_opt
            
            # 2. Project selection (Categorized dropdown or custom)
            is_marina_co = "CTY CP DMT - MARINA" in entry_company or "Du thuyﬂ+¸n Happy Yacht" in entry_company
            if False:
                proj_options_with_custom = ["GPÚ Tﬂ¶Ìo / Nhﬂ¶°p Dﬂ+¶ +Ìn mﬂ+¢i..."]
            else:
                db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
                merged_projs = get_filtered_projects(entry_company, config, db_projs)
                proj_options_with_custom = merged_projs + ["G£Ïn+≈ Tﬂ+¶ nhﬂ¶°p Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c kh+Ìc..."]
                
            default_proj_opt = st.selectbox("Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", proj_options_with_custom)
            
            if is_marina_co or default_proj_opt in ["G£Ïn+≈ Tﬂ+¶ nhﬂ¶°p Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c kh+Ìc...", "GPÚ Tﬂ¶Ìo / Nhﬂ¶°p Dﬂ+¶ +Ìn mﬂ+¢i..."]:
                project_name = st.text_input("Nhﬂ¶°p t+¨n Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c mﬂ+¢i", value="")
            else:
                project_name = clean_proj_name(default_proj_opt)
            
            # 3. Task details
            task_name = st.text_input("T+¨n c+¶ng viﬂ+Ác (tﬂ+¶ nhﬂ¶°p tﬂ+¶ do)", value="")
            task_nguon = st.selectbox("Nguﬂ+Ùn giao viﬂ+Ác", ["C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º", 'CV giao ban / VB -Êﬂ¶+n'])
            st.caption("=É∆Ì **-…ﬂ+Ônh kﬂ+¶:** -…-‚ng k++ -Êﬂ¶∫u th+Ìng / quﬂ¶˙n l++ giao. **Giao ban:** Ph+Ìt sinh sau khi hﬂ+Ïp giao ban.")
            
        with col2:
            # 6. Dates
            task_start = st.date_input("Ng+·y bﬂ¶ªt -Êﬂ¶∫u thﬂ+¶c hiﬂ+Án", today, format="DD/MM/YYYY")
            task_deadline = st.date_input("Hﬂ¶Ìn ho+·n th+·nh (Deadline)", today, format="DD/MM/YYYY")
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("=Éˆ+ T+¶y chﬂ+Ïn n+Ûng cao: Ghi nhﬂ¶°n trﬂ¶Ìng th+Ìi / Nﬂ+÷p kﬂ¶+t quﬂ¶˙ ngay", expanded=False):
                with st.container():
                    st.markdown("<div style='padding: 15px; border-radius: 8px; border: 1px dashed #ccc; background-color: #f9f9f9; margin-bottom: 20px;'>", unsafe_allow_html=True)
                    # 7 & 8. Status radio
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>=ÉÙÓ Trﬂ¶Ìng th+Ìi c+¶ng viﬂ+Ác</p>", unsafe_allow_html=True)
                    is_late_for_status = (task_deadline < today)
                    if is_late_for_status:
                        status_opts = ["G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác", "G‹·n+≈ C+¶ng viﬂ+Ác CH¶ªA HO+«N TH+«NH, -Êang V¶ªﬂ+‹NG Mﬂ¶´C"]
                    else:
                        status_opts = ["G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác"]
                    task_status_choice = st.radio("Trﬂ¶Ìng th+Ìi c+¶ng viﬂ+Ác", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                    task_is_completed = (task_status_choice == "G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác")
                    task_has_issue = (task_status_choice == "G‹·n+≈ C+¶ng viﬂ+Ác CH¶ªA HO+«N TH+«NH, -Êang V¶ªﬂ+‹NG Mﬂ¶´C")
                    
                    if task_status_choice is not None:
                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                        # 10. Ghi ch+¶ v¶¶ﬂ+¢ng mﬂ¶ªc
                        is_late = (task_deadline < today) and not task_is_completed
                        task_late_cause = "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                        if is_late:
                            st.markdown("**G‹·n+≈ Ph+Ûn loﬂ¶Ìi nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn**")
                            task_late_cause = st.radio(
                                "Ph+Ûn loﬂ¶Ìi nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn",
                                ["=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)", "=ÉÊÒ Do chﬂ+∫ quan"],
                                index=0,
                                label_visibility="collapsed",
                                key="new_task_late_cause"
                            )
                        if is_late or task_has_issue:
                            task_explain = st.text_area("=ÉÙ• Chi tiﬂ¶+t v¶¶ﬂ+¢ng mﬂ¶ªc / Giﬂ¶˙i tr+ºnh nguy+¨n nh+Ûn (Bﬂ¶ªt buﬂ+÷c)", placeholder="M+¶ tﬂ¶˙ chi tiﬂ¶+t nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn hoﬂ¶+c v¶¶ﬂ+¢ng mﬂ¶ªc gﬂ¶+p phﬂ¶˙i...", height=120, key="new_task_explain")
                            if is_late and task_late_cause == "=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)":
                                st.caption("=É∆Ì **L¶¶u ++:** Giﬂ¶˙i tr+ºnh n+·y sﬂ¶+ -Ê¶¶ﬂ+˙c hﬂ+Á thﬂ+Êng gﬂ+°i -Êﬂ¶+n Quﬂ¶˙n l++ -Êﬂ+‚ xem x+¨t mﬂ+¨c -Êﬂ+÷ ghi nhﬂ¶°n KPI.")
                        else:
                            task_explain = ""
                        
                        # 9. Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm
                        if task_has_issue:
                            task_file = None
                            task_link_text = ""
                            result_mode = "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)"
                        else:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if task_is_completed:
                                st.markdown("=É‹ø **<span style='color:red; font-size: 17px;'>-…ﬂ+È X+¸C NHﬂ¶ºN HO+«N TH+«NH, Bﬂ¶´T BUﬂ+ˇC NHﬂ¶ºP B+¸O C+¸O HOﬂ¶¶C Tﬂ¶ÛI FILE D¶ªﬂ+‹I -…+ÈY:</span>**", unsafe_allow_html=True)
                            else:
                                st.markdown("**Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm**")
                            result_mode = st.radio("H+ºnh thﬂ+¨c nﬂ+÷p kﬂ¶+t quﬂ¶˙", ["G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)", "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)"], horizontal=True, key="new_result_mode")
                            if result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)":
                                if task_is_completed:
                                    st.warning("G‹·n+≈ **VUI L+∆NG NHﬂ¶ºP Nﬂ+ˇI DUNG Kﬂ¶+T QUﬂ¶Û / B+¸O C+¸O V+«O +ˆ B+ËN D¶ªﬂ+‹I:**")
                                else:
                                    st.info("=É∆Ì **Ghi ch+¶ nﬂ+÷i dung/tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác v+·o +¶ b+¨n d¶¶ﬂ+¢i:**")
                                task_link_text = st.text_area("Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link", height=100, label_visibility="collapsed", placeholder="V+° dﬂ+—: B+Ìo c+Ìo sﬂ+Ê 01/BC-DMT, -Ê+˙ tr+ºnh sﬂ¶+p, hoﬂ¶+c d+Ìn link Google Drive...", key="new_result_text")
                                task_file = None
                            else:
                                task_file = st.file_uploader("Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)", key="new_result_file")
                                task_link_text = ""
                    else:
                        task_late_cause = "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                        task_explain = ""
                        result_mode = "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)"
                        task_link_text = ""
                        task_file = None
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                

            # 11. Chu kﬂ+¶ theo d+¶i
            task_cycle = "Theo dﬂ+¶ +Ìn / Tﬂ+¶ do"
            
            # 12. Tﬂ++ trﬂ+Ïng KPI
            task_weight = 0
            
            
        submit_new = st.button("=É∆+ L¶¶u", type="primary", key="btn_save_new_task")
        
        if submit_new:
            if not task_name.strip():
                st.error("G‹·n+≈ Vui l+¶ng nhﬂ¶°p T+¨n c+¶ng viﬂ+Ác!")
            elif not task_owner.strip():
                st.error("G‹·n+≈ Vui l+¶ng nhﬂ¶°p Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án!")
            else:
                # Calculate status and progress automatically
                if task_is_completed:
                    calc_status = "Ho+·n th+·nh"
                elif task_has_issue:
                    calc_status = "C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc"
                elif task_deadline < today:
                    calc_status = "Qu+Ì hﬂ¶Ìn"
                elif today >= task_start:
                    calc_status = "-…ang thﬂ+¶c hiﬂ+Án"
                else:
                    calc_status = "Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
                    
                task_progress = calculate_time_progress(task_start, task_deadline, task_is_completed)
                
                is_late = (task_deadline < today and not task_is_completed)
                    
                # Constraints validation
                has_error = False
                if calc_status == "Ho+·n th+·nh":
                    if result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)" and not task_link_text.strip():
                        st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c -Êiﬂ+¸n 'Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm'!")
                        has_error = True
                    elif result_mode == "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)" and task_file is None:
                        st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c tﬂ¶˙i file -Ê+°nh k+øm!")
                        has_error = True
                        
                if is_late:
                    if task_late_cause == "=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)":
                        if not task_explain.strip() or len(task_explain.strip()) < 5:
                            st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c nhﬂ¶°p 'Chi tiﬂ¶+t nguy+¨n nh+Ûn kh+Ìch quan & -…ﬂ+¸ xuﬂ¶—t ph¶¶¶Ìng +Ìn xﬂ+° l++' (tﬂ+Êi thiﬂ+‚u 5 k++ tﬂ+¶)!")
                            has_error = True
                elif calc_status == "C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc":
                    if not task_explain.strip() or len(task_explain.strip()) < 5:
                        st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c nhﬂ¶°p 'Chi tiﬂ¶+t v¶¶ﬂ+¢ng mﬂ¶ªc & -…ﬂ+¸ xuﬂ¶—t hﬂ+˘ trﬂ+˙'!")
                        has_error = True
                        
                if not has_error:
                    with acquire_db_lock():
                        
                        fresh_df = read_db()
                        
                        # Kiﬂ+‚m tra tr+¶ng lﬂ¶+p -Êﬂ+‚ cﬂ¶˙nh b+Ìo ng¶¶ﬂ+•i d+¶ng (tr+Ình click -Ê+¶p)
                        is_duplicate = False
                        if not fresh_df.empty:
                            dup_df = fresh_df[
                                (fresh_df['TenCongViec'].astype(str).str.strip() == task_name.strip()) & 
                                (fresh_df['NguoiChuTri'].astype(str).str.strip() == task_owner.strip()) & 
                                (fresh_df['TenDuAn'].astype(str).str.strip() == project_name) &
                                (fresh_df['Deadline'].astype(str) == str(task_deadline)) &
                                (fresh_df['NgayBatDau'].astype(str) == str(task_start))
                            ]
                            if not dup_df.empty:
                                is_duplicate = True
                                
                        if is_duplicate:
                            st.error("G‹·n+≈ C+¶ng viﬂ+Ác n+·y -Ê+˙ tﬂ+Ùn tﬂ¶Ìi (tr+¶ng T+¨n c+¶ng viﬂ+Ác, Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án, Dﬂ+¶ +Ìn v+· Thﬂ+•i gian)! -…ﬂ+‚ tr+Ình tr+¶ng lﬂ¶+p do bﬂ¶—m nhﬂ¶∫m, hﬂ+Á thﬂ+Êng -Ê+˙ chﬂ¶+n lﬂ¶Ìi. Nﬂ¶+u bﬂ¶Ìn thﬂ+¶c sﬂ+¶ muﬂ+Ên tﬂ¶Ìo 1 c+¶ng viﬂ+Ác giﬂ+Êng hﬂ+Át, vui l+¶ng sﬂ+°a lﬂ¶Ìi T+¨n c+¶ng viﬂ+Ác (v+° dﬂ+—: th+¨m sﬂ+Ê 2 v+·o cuﬂ+Êi).")
                        else:
                            # Auto ID generator
                            next_id = 1
                            if not fresh_df.empty:
                                ids = fresh_df['ID'].tolist()
                                nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                                if nums:
                                    next_id = max(nums) + 1
                            task_id = f"TSK-{next_id:03d}"
                            
                            saved_result = ""
                            
                            if result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)":
                                saved_result = task_link_text.strip()
                            elif result_mode == "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)" and task_file is not None:
                                    upload_dir = os.path.join("OUTPUT", "UPLOADED_FILES")
                                    if not os.path.exists(upload_dir):
                                        os.makedirs(upload_dir, exist_ok=True)
                                    safe_name = re.sub(r'[^\w\-_.]', '_', task_file.name)
                                    file_name = f"{task_id}_{safe_name}"
                                    file_path = os.path.join(upload_dir, file_name)
                                    with open(file_path, "wb") as f:
                                        f.write(task_file.getbuffer())
                                    saved_result = file_path
                                    
                            new_row = {
                                "ID": task_id,
                                "DonVi": entry_company,
                                "PhongBan": task_dept,
                                "NguoiChuTri": task_owner.strip(),
                                "TenDuAn": project_name,
                                "MocTienDo": "Tﬂ+¶ do",
                                "SanPhamBanGiao": "Xem chi tiﬂ¶+t",
                                "TenCongViec": task_name.strip(),
                                "PhanLoaiChiSo": "Chﬂ+Î sﬂ+Ê kﬂ¶+t quﬂ¶˙ (Outcome Metric)",
                                "NgayBatDau": task_start,
                                "Deadline": task_deadline,
                                "DoUuTien": "Trung b+ºnh",
                                "PhanTramHoanThanh": task_progress,
                                "TrangThai": calc_status,
                                "LinkKetQua": saved_result,
                                "GiaiTrinhDeXuat": task_explain.strip(),
                                "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                                "ChuKyTheoDoi": task_cycle,
                                "PhanLoaiTreHan": task_late_cause if is_late else "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷",
                                "TyTrongKPI": task_weight,
                                "NguonGiaoViec": task_nguon,
                                "MucDoGhiNhan": "0% (Kh+¶ng ghi nhﬂ¶°n)"
                            }
                            
                            df_updated = pd.concat([fresh_df, pd.DataFrame([new_row])], ignore_index=True)
                            if save_db(df_updated):
                                st.session_state["success_msg"] = f"=ÉƒÎ -…+˙ khﬂ+Éi tﬂ¶Ìo th+·nh c+¶ng c+¶ng viﬂ+Ác m+˙: {task_id}!"
                                st.rerun()


    # Form: Update Progress
    with tab_update:
        st.markdown("#### Cﬂ¶°p nhﬂ¶°t tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác -Êang chﬂ¶Ìy")
        
        # Display only items matching selected company
        avail_update_df = display_df.copy()
        if 'NgayCapNhat' in avail_update_df.columns:
            avail_update_df = avail_update_df.sort_values(by=['NgayCapNhat', 'ID'], ascending=[False, False]).reset_index(drop=True)
        
        is_personal_update = role_mode == "Nh+Ûn vi+¨n" and st.session_state.get("is_personal_authenticated", False)
        if is_personal_update:
            col_f3, col_f4 = st.columns(2)
            filter_dept = "Tﬂ¶—t cﬂ¶˙"
            filter_owner = "Tﬂ¶—t cﬂ¶˙"
        else:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                departments = ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(avail_update_df['PhongBan'].dropna().astype(str).unique()))
                filter_dept = st.selectbox("Lﬂ+Ïc theo Ph+¶ng ban", departments, key="filter_dept_update")
            with col_f2:
                owners = ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(avail_update_df['NguoiChuTri'].dropna().astype(str).unique()))
                filter_owner = st.selectbox("Lﬂ+Ïc theo Ng¶¶ﬂ+•i phﬂ+— tr+Ìch", owners, key="filter_owner_update")
                
        with col_f3:
            projects = ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(avail_update_df['TenDuAn'].dropna().astype(str).unique()))
            filter_proj = st.selectbox("Lﬂ+Ïc theo Dﬂ+¶ +Ìn", projects, key="filter_proj_update")
        with col_f4:
            months = set()
            if not avail_update_df.empty:
                for _, row in avail_update_df.iterrows():
                    if pd.notna(row.get('NgayBatDau')) and hasattr(row['NgayBatDau'], 'strftime'):
                        months.add(row['NgayBatDau'].strftime('%m/%Y'))
                    if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                        months.add(row['Deadline'].strftime('%m/%Y'))
            month_options = ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
            filter_month = st.selectbox("Lﬂ+Ïc theo Th+Ìng", month_options, key="filter_month_update")
            
        if filter_dept != "Tﬂ¶—t cﬂ¶˙":
            avail_update_df = avail_update_df[avail_update_df['PhongBan'] == filter_dept]
        if filter_owner != "Tﬂ¶—t cﬂ¶˙":
            avail_update_df = avail_update_df[avail_update_df['NguoiChuTri'] == filter_owner]
        if filter_proj != "Tﬂ¶—t cﬂ¶˙":
            avail_update_df = avail_update_df[avail_update_df['TenDuAn'] == filter_proj]
        if filter_month != "Tﬂ¶—t cﬂ¶˙":
            mask = (
                avail_update_df['NgayBatDau'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == filter_month
            ) | (
                avail_update_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == filter_month
            )
            avail_update_df = avail_update_df[mask]

        if avail_update_df.empty:
            st.info("Ch¶¶a c+¶ c+¶ng viﬂ+Ác n+·o khﬂ¶˙ dﬂ+—ng.")
        else:
            def format_task_option(task_id):
                row = df[df['ID'] == task_id].iloc[0]
                pic = row.get('NguoiChuTri', 'Ch¶¶a r+¶')
                return f"{row['TenCongViec']} - Phﬂ+— tr+Ìch: {pic}"
            
            selected_id = st.selectbox("Chﬂ+Ïn c+¶ng viﬂ+Ác cﬂ¶∫n cﬂ¶°p nhﬂ¶°t", avail_update_df['ID'].tolist(), format_func=format_task_option)
            task_data = df[df['ID'] == selected_id].iloc[0]
            
            with st.container():
                col_u1, col_u2 = st.columns(2)
                
                with col_u1:
                    st.markdown(f"**M+˙ Hﬂ¶Ìng mﬂ+—c:** `{task_data['ID']}`")
                    st.markdown(f"**-…¶Ìn vﬂ+Ô:** {task_data['DonVi']}")
                    st.markdown(f"**Ph+¶ng ban phﬂ+— tr+Ìch:** {task_data['PhongBan']}")
                    
                    u_proj = st.text_input("Dﬂ+¶ +Ìn / Hﬂ¶Ìng mﬂ+—c", value=task_data['TenDuAn'], key=f"u_proj_{task_data['ID']}")
                    u_name = st.text_input("T+¨n c+¶ng viﬂ+Ác", value=task_data['TenCongViec'], key=f"u_name_{task_data['ID']}")
                    u_nguon_opts = ["C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º", 'CV giao ban / VB -Êﬂ¶+n']
                    current_nguon = task_data.get('NguonGiaoViec', 'C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º')
                    u_nguon_idx = u_nguon_opts.index(current_nguon) if current_nguon in u_nguon_opts else 0
                    u_nguon = st.selectbox("Nguﬂ+Ùn giao viﬂ+Ác", u_nguon_opts, index=u_nguon_idx, key=f"u_nguon_{task_data['ID']}")
                    st.caption("=É∆Ì **-…ﬂ+Ônh kﬂ+¶:** -…-‚ng k++ -Êﬂ¶∫u th+Ìng. **Giao ban:** Ph+Ìt sinh sau khi hﬂ+Ïp giao ban.")
                    
                    # Owner selection based on configuration
                    u_dept = task_data['PhongBan']
                    u_dept_personnel = get_personnel_for_company_dept(task_data['DonVi'], u_dept, config)
                    u_owner_options = list(u_dept_personnel) + ["G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i kh+Ìc..."]
                    
                    current_owner = task_data['NguoiChuTri']
                    is_personal = (role_mode == "Nh+Ûn vi+¨n" and st.session_state.is_personal_authenticated and st.session_state.personal_user)
                    if is_personal:
                        st.selectbox("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án / Phﬂ+— tr+Ìch", [st.session_state.personal_user], index=0, disabled=True, key=f"u_owner_sel_{task_data['ID']}")
                        u_owner = st.session_state.personal_user
                    else:
                        if current_owner in u_dept_personnel:
                            u_default_index = u_dept_personnel.index(current_owner)
                            u_sel_owner_opt = st.selectbox("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án / Phﬂ+— tr+Ìch", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                            if u_sel_owner_opt == "G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i kh+Ìc...":
                                u_owner = st.text_input("G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án kh+Ìc...", value="", key=f"u_owner_custom_{task_data['ID']}")
                            else:
                                u_owner = u_sel_owner_opt
                        else:
                            u_default_index = len(u_owner_options) - 1
                            u_sel_owner_opt = st.selectbox("Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án / Phﬂ+— tr+Ìch", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                            u_owner = st.text_input("G£Ïn+≈ Nhﬂ¶°p t+¨n ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án kh+Ìc...", value=current_owner, key=f"u_owner_custom_{task_data['ID']}")
                    
                with col_u2:
                    is_emp_locked = (role_mode == "Nh+Ûn vi+¨n")
                    u_start = st.date_input("Ng+·y bﬂ¶ªt -Êﬂ¶∫u thﬂ+¶c hiﬂ+Án", value=pd.to_datetime(task_data['NgayBatDau']).date() if pd.notna(task_data['NgayBatDau']) and str(task_data['NgayBatDau']).strip() else today, format="DD/MM/YYYY", disabled=is_emp_locked, key=f"u_start_{task_data['ID']}")
                    u_deadline = st.date_input("Hﬂ¶Ìn ho+·n th+·nh (Deadline)", value=pd.to_datetime(task_data['Deadline']).date() if pd.notna(task_data['Deadline']) and str(task_data['Deadline']).strip() else today, format="DD/MM/YYYY", disabled=is_emp_locked, key=f"u_deadline_{task_data['ID']}")
                    
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>=ÉÙÓ Trﬂ¶Ìng th+Ìi c+¶ng viﬂ+Ác</p>", unsafe_allow_html=True)
                    u_current_status = task_data.get('TrangThai', '-…ang thﬂ+¶c hiﬂ+Án')
                    u_is_late_for_status = (u_deadline is not None and u_deadline < today)
                    if u_is_late_for_status or u_current_status == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc':
                        u_status_opts = ["G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác", "G‹·n+≈ C+¶ng viﬂ+Ác CH¶ªA HO+«N TH+«NH, -Êang V¶ªﬂ+‹NG Mﬂ¶´C"]
                    else:
                        u_status_opts = ["G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác"]
                    
                    if u_current_status == 'Ho+·n th+·nh':
                        u_status_idx = 0
                    elif u_current_status == 'C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc':
                        u_status_idx = 1
                    else:
                        u_status_idx = None
                        
                    u_status_choice = st.radio("Trﬂ¶Ìng th+Ìi c+¶ng viﬂ+Ác", u_status_opts, index=u_status_idx, label_visibility="collapsed", key=f"u_status_choice_{task_data['ID']}")
                    u_is_completed = (u_status_choice == "G£‡ X+Ìc nhﬂ¶°n -…+‚ HO+«N TH+«NH c+¶ng viﬂ+Ác")
                    u_has_issue = (u_status_choice == "G‹·n+≈ C+¶ng viﬂ+Ác CH¶ªA HO+«N TH+«NH, -Êang V¶ªﬂ+‹NG Mﬂ¶´C")
                    
                    # 11. Chu kﬂ+¶ theo d+¶i
                    current_cycle = task_data.get('ChuKyTheoDoi', 'Theo dﬂ+¶ +Ìn / Tﬂ+¶ do')
                    cycle_list = ["H+·ng tuﬂ¶∫n", "H+·ng th+Ìng", "H+·ng qu++", "Theo dﬂ+¶ +Ìn / Tﬂ+¶ do"]
                    default_cycle_idx = cycle_list.index(current_cycle) if current_cycle in cycle_list else 3
                    u_cycle = current_cycle
                    
                    is_emp_locked = (role_mode == "Nh+Ûn vi+¨n")
                    if is_emp_locked:
                        st.text_input("Tﬂ++ trﬂ+Ïng KPI (%)", value=str(task_data.get('TyTrongKPI', '')), disabled=True, key=f"u_weight_disp_{task_data['ID']}")
                        u_weight = task_data.get('TyTrongKPI', '')
                    else:
                        u_weight = task_data.get('TyTrongKPI', '')
                    
                
                u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
                if u_status_choice is not None:
                    st.markdown("<div style='padding: 15px; border-radius: 8px; border: 1px dashed #ccc; background-color: #f9f9f9; margin-top: 15px;'>", unsafe_allow_html=True)
                    u_late_cause = "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                    if u_is_late:
                        st.markdown("**G‹·n+≈ Ph+Ûn loﬂ¶Ìi nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn**")
                        u_options = ["=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)", "=ÉÊÒ Do chﬂ+∫ quan"]
                        u_current_val = task_data.get('PhanLoaiTreHan', "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷")
                        u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                        u_late_cause = st.radio(
                            "Ph+Ûn loﬂ¶Ìi nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn",
                            u_options,
                            index=u_default_idx,
                            label_visibility="collapsed",
                            key=f"u_late_cause_sel_{task_data['ID']}"
                        )
                    if u_is_late or u_has_issue:
                        u_explain = st.text_area("=ÉÙ• Chi tiﬂ¶+t v¶¶ﬂ+¢ng mﬂ¶ªc / Giﬂ¶˙i tr+ºnh nguy+¨n nh+Ûn (Bﬂ¶ªt buﬂ+÷c)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="M+¶ tﬂ¶˙ chi tiﬂ¶+t nguy+¨n nh+Ûn trﬂ+‡ hﬂ¶Ìn hoﬂ¶+c v¶¶ﬂ+¢ng mﬂ¶ªc gﬂ¶+p phﬂ¶˙i...", height=120, key=f"u_explain_txt_{task_data['ID']}")
                        if u_is_late and u_late_cause == "=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)":
                            if st.session_state.is_admin_authenticated or st.session_state.get('is_manager_authenticated', False):
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Kh+¶ng ghi nhﬂ¶°n)')
                                chamchuoc_opts = ["0% (Kh+¶ng ghi nhﬂ¶°n)", "Miﬂ+‡n trﬂ+Ω (Loﬂ¶Ìi bﬂ+≈ KPI)", "50%", "80%", "90%"]
                                idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                                u_chamchuoc = st.selectbox("Mﬂ+¨c -Êﬂ+÷ ghi nhﬂ¶°n (D+·nh cho Quﬂ¶˙n l++)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                            else:
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Kh+¶ng ghi nhﬂ¶°n)')
                                u_chamchuoc = current_chamchuoc
                                if current_chamchuoc != '0% (Kh+¶ng ghi nhﬂ¶°n)':
                                    st.info(f"-…+˙ -Ê¶¶ﬂ+˙c Quﬂ¶˙n l++ ghi nhﬂ¶°n mﬂ+¨c -Êﬂ+÷ KPI: **{current_chamchuoc}**")
                                else:
                                    st.caption("=É∆Ì **L¶¶u ++:** Giﬂ¶˙i tr+ºnh n+·y sﬂ¶+ -Ê¶¶ﬂ+˙c hﬂ+Á thﬂ+Êng gﬂ+°i -Êﬂ¶+n Quﬂ¶˙n l++ -Êﬂ+‚ xem x+¨t mﬂ+¨c -Êﬂ+÷ ghi nhﬂ¶°n KPI.")
                        else:
                            u_chamchuoc = '0% (Kh+¶ng ghi nhﬂ¶°n)'
                    else:
                        u_explain = ""
                        u_chamchuoc = '0% (Kh+¶ng ghi nhﬂ¶°n)'
                    

                    current_link = task_data['LinkKetQua']
                    u_link_text = ""
                    u_file = None
                    u_result_mode = None
                    if not u_has_issue:
                        if u_is_completed:
                            st.markdown("=É‹ø **<span style='color:red; font-size: 17px;'>-…ﬂ+È X+¸C NHﬂ¶ºN HO+«N TH+«NH, Bﬂ¶´T BUﬂ+ˇC NHﬂ¶ºP B+¸O C+¸O HOﬂ¶¶C Tﬂ¶ÛI FILE D¶ªﬂ+‹I -…+ÈY:</span>**", unsafe_allow_html=True)
                        else:
                            st.markdown("**Cﬂ¶°p nhﬂ¶°t Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm**")
                            
                        u_result_mode = st.radio("H+ºnh thﬂ+¨c nﬂ+÷p kﬂ¶+t quﬂ¶˙", ["G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)", "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                        
                        if u_result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)":
                            if u_is_completed:
                                st.warning("G‹·n+≈ **VUI L+∆NG NHﬂ¶ºP Nﬂ+ˇI DUNG Kﬂ¶+T QUﬂ¶Û / B+¸O C+¸O V+«O +ˆ B+ËN D¶ªﬂ+‹I:**")
                            else:
                                st.info("=É∆Ì **Ghi ch+¶ nﬂ+÷i dung/tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác v+·o +¶ b+¨n d¶¶ﬂ+¢i:**")
                            u_link_text = st.text_area("Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link mﬂ+¢i", height=100, label_visibility="collapsed", placeholder="V+° dﬂ+—: -…+˙ ho+·n th+·nh 50%, tr+ºnh k++ sﬂ¶+p...", key=f"u_result_text_{task_data['ID']}")
                        elif u_result_mode == "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)":
                            u_file = st.file_uploader("Tﬂ¶˙i file -Ê+°nh k+øm mﬂ+¢i", key=f"u_result_file_{task_data['ID']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    u_late_cause = "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                    u_explain = ""
                    u_chamchuoc = '0% (Kh+¶ng ghi nhﬂ¶°n)'
                    u_link_text = ""
                    u_file = None
                    u_result_mode = "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)"

                    

                btn_save, btn_del = st.columns([3, 2])
                
                with btn_save:
                    save_click = st.button("=É∆+ L¶ªU Cﬂ¶ºP NHﬂ¶ºT TIﬂ¶+N -…ﬂ+ˇ", type="primary", key=f"btn_save_update_{task_data['ID']}")
                with btn_del:
                    del_click = False
                    if st.session_state.is_admin_authenticated:
                        confirm_del = st.checkbox("X+Ìc nhﬂ¶°n x+¶a dﬂ+ª liﬂ+Áu n+·y", key=f"confirm_del_{task_data['ID']}")
                        if confirm_del:
                            del_click = st.button("=É˘Ên+≈ X+ÙA C+ˆNG VIﬂ+ÂC CHﬂ+ÓN", type="secondary", key=f"btn_del_update_{task_data['ID']}")


                if save_click:
                    has_error = False
                    
                    # Validate evidence if completed
                    if u_is_completed and not u_link_text.strip() and not u_file:
                        st.error("G•Ó Lﬂ+˘i: Bﬂ¶Ìn phﬂ¶˙i nhﬂ¶°p Link kﬂ¶+t quﬂ¶˙ hoﬂ¶+c Tﬂ¶˙i file -Ê+°nh k+øm -Êﬂ+‚ b+Ìo c+Ìo Ho+·n th+·nh!")
                        has_error = True
                    else:
                        # Calculate status and progress automatically
                        if u_is_completed:
                            u_status = "Chﬂ+• nghiﬂ+Ám thu"
                        elif u_has_issue:
                            u_status = "C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc"
                        elif u_deadline < today:
                            u_status = "Qu+Ì hﬂ¶Ìn"
                        elif today >= u_start:
                            u_status = "-…ang thﬂ+¶c hiﬂ+Án"
                        else:
                            u_status = "Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u"
                            
                        u_progress = calculate_time_progress(u_start, u_deadline, u_is_completed)
                            
                        # Constraints validation
                        if u_status == "Chﬂ+• nghiﬂ+Ám thu":
                            if u_result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)" and not u_link_text.strip() and not current_link:
                                st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c -Êiﬂ+¸n 'Kﬂ¶+t quﬂ¶˙ / File -Ê+°nh k+øm' -Êﬂ+‚ ho+·n th+·nh c+¶ng viﬂ+Ác!")
                                has_error = True
                            elif u_result_mode == "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)" and u_file is None and not current_link:
                                st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c tﬂ¶˙i file -Ê+°nh k+øm -Êﬂ+‚ ho+·n th+·nh c+¶ng viﬂ+Ác!")
                                has_error = True
                            
                        if u_is_late:
                            if u_late_cause == "=ÉÓ∫n+≈ Do kh+Ìch quan (Ph+Ìp l++, -…ﬂ+Êi t+Ìc, Thﬂ+•i tiﬂ¶+t, C¶Ì quan nh+· n¶¶ﬂ+¢c...)":
                                if not u_explain.strip() or len(u_explain.strip()) < 5:
                                    st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c nhﬂ¶°p 'Chi tiﬂ¶+t nguy+¨n nh+Ûn kh+Ìch quan & -…ﬂ+¸ xuﬂ¶—t ph¶¶¶Ìng +Ìn xﬂ+° l++' (tﬂ+Êi thiﬂ+‚u 5 k++ tﬂ+¶)!")
                                    has_error = True
                        elif u_status == "C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc":
                            if not u_explain.strip() or len(u_explain.strip()) < 5:
                                st.error("G‹·n+≈ Bﬂ¶ªt buﬂ+÷c nhﬂ¶°p 'Chi tiﬂ¶+t v¶¶ﬂ+¢ng mﬂ¶ªc & -…ﬂ+¸ xuﬂ¶—t hﬂ+˘ trﬂ+˙'!")
                                has_error = True
                                
                        if not has_error:
                            # Determine final link value
                            final_link = current_link
                            
                            if u_result_mode == "G£Ïn+≈ Nhﬂ¶°p t+¨n B+Ìo c+Ìo / Sﬂ+Ê hiﬂ+Áu V-‚n bﬂ¶˙n / Link (Dﬂ¶Ìng text tﬂ+¶ do)":
                                if u_link_text.strip():
                                    final_link = u_link_text.strip()
                            elif u_result_mode == "=ÉÙ¸ Tﬂ¶˙i file -Ê+°nh k+øm (PDF, Word, Excel, ﬂ¶Ûnh...)" and u_file is not None:
                                upload_dir = os.path.join("OUTPUT", "UPLOADED_FILES")
                                if not os.path.exists(upload_dir):
                                    os.makedirs(upload_dir, exist_ok=True)
                                safe_name = re.sub(r'[^\w\-_.]', '_', u_file.name)
                                file_name = f"{selected_id}_{safe_name}"
                                file_path = os.path.join(upload_dir, file_name)
                                with open(file_path, "wb") as f:
                                    f.write(u_file.getbuffer())
                                final_link = file_path
                                
                            with acquire_db_lock():
                                
                                fresh_df = read_db()
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'TenDuAn'] = u_proj.strip()
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'TenCongViec'] = u_name.strip()
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'NguoiChuTri'] = u_owner.strip()
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'NgayBatDau'] = u_start
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'Deadline'] = u_deadline
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'PhanTramHoanThanh'] = u_progress
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'TrangThai'] = u_status
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'LinkKetQua'] = final_link
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'GiaiTrinhDeXuat'] = u_explain.strip()
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'NgayCapNhat'] = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'ChuKyTheoDoi'] = u_cycle
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'PhanLoaiTreHan'] = u_late_cause if u_is_late else "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'TyTrongKPI'] = str(u_weight)
                                fresh_df.loc[fresh_df['ID'] == selected_id, 'NguonGiaoViec'] = u_nguon
                                if u_is_late:
                                    fresh_df.loc[fresh_df['ID'] == selected_id, 'MucDoGhiNhan'] = u_chamchuoc
                                else:
                                    fresh_df.loc[fresh_df['ID'] == selected_id, 'MucDoGhiNhan'] = '0% (Kh+¶ng ghi nhﬂ¶°n)'

                                if save_db(fresh_df):
                                    st.session_state["success_msg"] = f"=ÉƒÎ -…+˙ l¶¶u cﬂ¶°p nhﬂ¶°t c+¶ng viﬂ+Ác m+˙: {selected_id}!"
                                    st.rerun()
                                
                    if has_error:
                        st.session_state.is_updating_task = False
                            
                if del_click:
                    with acquire_db_lock():
                        
                        fresh_df = read_db()
                        df_after_del = fresh_df[fresh_df['ID'] != selected_id]
                        if save_db(df_after_del):
                            st.session_state["success_msg"] = f"=É˘Ên+≈ -…+˙ x+¶a th+·nh c+¶ng c+¶ng viﬂ+Ác m+˙: {selected_id}!"
                            st.rerun()

                st.markdown("---")
                with st.expander("=Éˆ‰ T+Ìi tﬂ¶Ìo c+¶ng viﬂ+Ác -Êﬂ+Ônh kﬂ+¶ (Nh+Ûn bﬂ¶˙n cho kﬂ+¶ sau)"):
                    st.info("T+°nh n-‚ng n+·y gi+¶p nh+Ûn bﬂ¶˙n c+¶ng viﬂ+Ác hiﬂ+Án tﬂ¶Ìi th+·nh mﬂ+÷t c+¶ng viﬂ+Ác mﬂ+¢i cho kﬂ+¶ tiﬂ¶+p theo (d+·nh cho c+Ìc b+Ìo c+Ìo tuﬂ¶∫n, giao ban th+Ìng...).")
                    
                    rep_name = st.text_input("T+¨n c+¶ng viﬂ+Ác mﬂ+¢i", value=f"{task_data['TenCongViec']} (Kﬂ+¶ tiﬂ¶+p theo)", key=f"rep_name_{task_data['ID']}")
                    
                    try:
                        from dateutil.relativedelta import relativedelta
                        import pandas as pd
                        
                        # Fix for cases where NgayBatDau or Deadline might be NaT or None
                        if pd.notna(task_data.get('NgayBatDau')):
                            default_start = task_data['NgayBatDau'] + relativedelta(months=1)
                        else:
                            default_start = today
                            
                        if pd.notna(task_data.get('Deadline')):
                            default_deadline = task_data['Deadline'] + relativedelta(months=1)
                        else:
                            default_deadline = default_start + timedelta(days=6)
                    except Exception as e:
                        default_start = task_data['Deadline'] + timedelta(days=1) if pd.notna(task_data.get('Deadline')) else today
                        default_deadline = default_start + timedelta(days=6)
                    
                    col_rep1, col_rep2 = st.columns(2)
                    with col_rep1:
                        rep_start = st.date_input("Ng+·y bﬂ¶ªt -Êﬂ¶∫u mﬂ+¢i", value=default_start, format="DD/MM/YYYY", key=f"rep_start_{task_data['ID']}")
                    with col_rep2:
                        rep_deadline = st.date_input("Hﬂ¶Ìn ch+¶t mﬂ+¢i", value=default_deadline, format="DD/MM/YYYY", key=f"rep_deadline_{task_data['ID']}")
                        
                    if st.button("=Éˆ‰ Tﬂ¶·O C+ˆNG VIﬂ+ÂC CHO Kﬂ+¶ SAU", type="primary", key=f"btn_rep_{task_data['ID']}"):
                        with acquire_db_lock():
                            
                            fresh_df = read_db()
                            
                            next_id = 1
                            if not fresh_df.empty:
                                ids = fresh_df['ID'].tolist()
                                import re
                                nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                                if nums:
                                    next_id = max(nums) + 1
                            new_id = f"TSK-{next_id:03d}"
                            
                            new_row = {
                                "ID": new_id,
                                "DonVi": task_data['DonVi'],
                                "PhongBan": task_data['PhongBan'],
                                "NguoiChuTri": task_data['NguoiChuTri'],
                                "TenDuAn": task_data['TenDuAn'],
                                "MocTienDo": "Tﬂ+¶ do",
                                "SanPhamBanGiao": "Xem chi tiﬂ¶+t",
                                "TenCongViec": rep_name.strip(),
                                "PhanLoaiChiSo": "Chﬂ+Î sﬂ+Ê kﬂ¶+t quﬂ¶˙ (Outcome Metric)",
                                "NgayBatDau": rep_start,
                                "Deadline": rep_deadline,
                                "DoUuTien": "Trung b+ºnh",
                                "PhanTramHoanThanh": 0,
                                "TrangThai": "Ch¶¶a bﬂ¶ªt -Êﬂ¶∫u" if today < rep_start else "-…ang thﬂ+¶c hiﬂ+Án",
                                "LinkKetQua": "",
                                "GiaiTrinhDeXuat": "",
                                "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                                "ChuKyTheoDoi": task_data['ChuKyTheoDoi'],
                                "PhanLoaiTreHan": "=ÉÉÛ Kh+¶ng trﬂ+‡ hﬂ¶Ìn / -…+¶ng tiﬂ¶+n -Êﬂ+÷"
                            }
                            
                            df_rep = pd.concat([fresh_df, pd.DataFrame([new_row])], ignore_index=True)
                            if save_db(df_rep):
                                st.session_state["success_msg"] = f"=ÉƒÎ -…+˙ nh+Ûn bﬂ¶˙n th+·nh c+¶ng c+¶ng viﬂ+Ác mﬂ+¢i m+˙: {new_id}!"
                                st.rerun()

# ----------------- 5. -…+¸NH GI+¸ KPI & Xﬂ¶+P LOﬂ¶·I -----------------
elif menu == "=É≈Â -…+Ình gi+Ì KPI & Xﬂ¶+p loﬂ¶Ìi":
    st.markdown(f"### =É≈Â -…+Ình gi+Ì KPI & Xﬂ¶+p loﬂ¶Ìi C+Ì nh+Ûn G«ˆ {selected_company}")
    
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        del st.session_state["success_msg"]
    
    is_hr_view = role_mode == "HR" and st.session_state.get("is_admin_authenticated", False)
    is_manager_view = role_mode == "Quﬂ¶˙n l++" and st.session_state.get('is_manager_authenticated', False)
    
    if is_hr_view:
        kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["=ÉÙ‡ -…+Ình gi+Ì theo Th+Ìng", "=É≈‡ Tﬂ+Úng kﬂ¶+t KPI Cﬂ¶˙ N-‚m (Th+Ìng 13)", "G‹˚n+≈ Th¶¶ﬂ+Éng / Phﬂ¶Ìt -…iﬂ+‚m", "=ÉÙÍ Ph+Ûn t+°ch & Xuﬂ¶—t B+Ìo c+Ìo"])
    elif is_manager_view:
        kpi_tab1, kpi_tab2, kpi_tab3 = st.tabs(["=ÉÙ‡ -…+Ình gi+Ì theo Th+Ìng", "=É≈‡ Tﬂ+Úng kﬂ¶+t KPI Cﬂ¶˙ N-‚m (Th+Ìng 13)", "G‹˚n+≈ Th¶¶ﬂ+Éng / Phﬂ¶Ìt -…iﬂ+‚m"])
    else:
        kpi_tab1, kpi_tab2 = st.tabs(["=ÉÙ‡ -…+Ình gi+Ì theo Th+Ìng", "=É≈‡ Tﬂ+Úng kﬂ¶+t KPI Cﬂ¶˙ N-‚m (Th+Ìng 13)"])
    
    with kpi_tab1:
        st.markdown("#### -…+Ình gi+Ì v+· Xﬂ¶+p loﬂ¶Ìi KPI Th+Ìng")
        
        if is_manager_view:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                selected_month = st.selectbox("Chﬂ+Ïn Th+Ìng", list(range(1, 13)), index=today.month - 1)
            with col_m2:
                selected_year = st.selectbox("Chﬂ+Ïn N-‚m", [today.year - 1, today.year, today.year + 1], index=1)
            selected_dept_m = st.session_state.manager_dept if st.session_state.get('manager_dept') else "Tﬂ¶—t cﬂ¶˙ ph+¶ng ban"
        else:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                selected_month = st.selectbox("Chﬂ+Ïn Th+Ìng", list(range(1, 13)), index=today.month - 1)
            with col_m2:
                selected_year = st.selectbox("Chﬂ+Ïn N-‚m", [today.year - 1, today.year, today.year + 1], index=1)
            with col_m3:
                allowed_depts_m = get_departments_for_company(selected_company, config)
                dept_options_m = ["Tﬂ¶—t cﬂ¶˙ ph+¶ng ban"] + allowed_depts_m
                selected_dept_m = st.selectbox("Lﬂ+Ïc theo Ph+¶ng ban", dept_options_m, key="kpi_m_dept")
            
        kpi_df = display_df.copy()
        if 'NguoiChuTri' not in kpi_df.columns:
            kpi_df['NguoiChuTri'] = ''
        
        def is_in_month(d, m, y):
            import pandas as pd
            from datetime import datetime, date
            if pd.isna(d): return False
            if isinstance(d, str):
                try: d = datetime.strptime(d, "%Y-%m-%d").date()
                except: return False
            if isinstance(d, datetime): d = d.date()
            if isinstance(d, date): return d.month == m and d.year == y
            return False
            
        kpi_df = kpi_df[kpi_df['Deadline'].apply(lambda x: is_in_month(x, selected_month, selected_year))] if not kpi_df.empty else kpi_df
        
        adj_df = read_kpi_adjustments()
        adj_df = adj_df[(adj_df['Thang'] == selected_month) & (adj_df['Nam'] == selected_year)]
        
        if kpi_df.empty and adj_df.empty:
            st.info(f"Kh+¶ng c+¶ dﬂ+ª liﬂ+Áu c+¶ng viﬂ+Ác hoﬂ¶+c -Êiﬂ+‚m th¶¶ﬂ+Éng/phﬂ¶Ìt n+·o trong Th+Ìng {selected_month}/{selected_year}.")
        else:
            import pandas as pd
            from datetime import datetime, date
            personnel_kpi = []
            
            # Find all personnel relevant to THIS company
            company_personnel = set(display_df['NguoiChuTri'].dropna().unique())
            
            all_p = set(kpi_df['NguoiChuTri'].dropna().unique())
            if 'TenNhanVien' in adj_df.columns:
                all_p.update(adj_df['TenNhanVien'].dropna().unique())
            
            # Filter to only keep those who belong to the selected company
            all_p = all_p.intersection(company_personnel)
            
            for person in all_p:
                if not str(person).strip(): continue
                group = kpi_df[kpi_df['NguoiChuTri'] == person]
                total_tasks = len(group)
                done_tasks = len(group[group['TrangThai'] == 'Ho+·n th+·nh'])
                
                group_copy = group.copy()
                group_copy['TyTrongKPI'] = pd.to_numeric(group_copy.get('TyTrongKPI', pd.Series(0, index=group_copy.index)), errors='coerce').fillna(0)
                
                for idx, row in group_copy.iterrows():
                    is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
                    is_late = False
                    dl = row['Deadline']
                    if isinstance(dl, str):
                        try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                        except: pass
                    if isinstance(dl, datetime): dl = dl.date()
                    if isinstance(dl, date): is_late = (dl < today) and not is_comp
                    
                    if is_late and row.get('PhanLoaiTreHan') == "=ÉÓÏ Do kh+Ìch quan":
                        group_copy.at[idx, 'PhanTramHoanThanh'] = 100
                        
                explicit_weight_sum = group_copy[group_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                unweighted_count = len(group_copy[group_copy['TyTrongKPI'] <= 0])
                
                remaining_weight = max(0, 100 - explicit_weight_sum)
                auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
                
                # Calculate score dynamically based on NguonGiaoViec (70/30 rule)
                if 'NguonGiaoViec' not in group_copy.columns:
                    group_copy['NguonGiaoViec'] = 'C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º'
                ke_hoach_tasks = group_copy[~group_copy['NguonGiaoViec'].isin(['C+¶ng viﬂ+Ác trong "Giao ban"', 'CV giao ban / VB -Êﬂ¶+n'])]
                giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'].isin(['C+¶ng viﬂ+Ác trong "Giao ban"', 'CV giao ban / VB -Êﬂ¶+n'])]
                
                def calc_score_for_group(grp):
                    if grp.empty: return 0
                    t_score = 0
                    total_w = 0
                    for idx, row in grp.iterrows():
                        is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        
                        if is_comp:
                            p = 100
                        else:
                            if "kh+Ìch quan" in str(row.get('PhanLoaiTreHan')).lower():
                                cc = row.get('MucDoGhiNhan', '0% (Kh+¶ng ghi nhﬂ¶°n)')
                                if cc == "Miﬂ+‡n trﬂ+Ω (Loﬂ¶Ìi bﬂ+≈ KPI)":
                                    w = 0
                                    p = 0
                                elif cc == "50%": p = 50
                                elif cc == "80%": p = 80
                                elif cc == "90%": p = 90
                                else: p = 0
                            else:
                                p = 0
                        
                        if pd.isna(p): p = 0
                        t_score += (p / 100.0) * w
                        total_w += w
                        
                    if total_w > 0:
                        return (t_score / total_w) * 100
                    return 0

                if len(giao_ban_tasks) > 0:
                    kh_score = calc_score_for_group(ke_hoach_tasks)
                    gb_score = calc_score_for_group(giao_ban_tasks)
                    task_score = kh_score * 0.7 + gb_score * 0.3
                else:
                    task_score = calc_score_for_group(ke_hoach_tasks)

                
                p_adj_df = adj_df[adj_df['TenNhanVien'] == person] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
                adj_score = 0
                if not p_adj_df.empty:
                    for _, r in p_adj_df.iterrows():
                        loai = str(r.get('LoaiHanhVi', '')).lower()
                        diem = int(r.get('DiemDieuChinh', 0))
                        if 'th¶¶ﬂ+Éng' in loai:
                            adj_score += diem
                        elif 'phﬂ¶Ìt' in loai:
                            adj_score -= diem
                        else:
                            adj_score += diem
                
                final_score = min(115, max(0, round(task_score + adj_score, 2)))
                
                # Xﬂ¶+p loﬂ¶Ìi mﬂ+¢i
                if final_score > 100: grade = "A*"
                elif final_score > 91: grade = "A"
                elif final_score > 81: grade = "B"
                elif final_score > 71: grade = "C"
                else:
                    if selected_year == today.year and selected_month == today.month:
                        grade = "-"
                    else:
                        grade = "D"
                
                pb = group['PhongBan'].iloc[0] if not group.empty else ""
                
                personnel_kpi.append({
                    "Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án": person,
                    "Ph+¶ng ban": DEPT_ABBR.get(pb, pb),
                    "Sﬂ+Ê viﬂ+Ác": total_tasks,
                    "-…iﬂ+‚m c+¶ng viﬂ+Ác": round(task_score, 1),
                    "Th¶¶ﬂ+Éng/Phﬂ¶Ìt": adj_score,
                    "Tﬂ+ˆNG -…Iﬂ+ÈM": final_score,
                    "Xﬂ¶+p loﬂ¶Ìi": grade,
                    "_kh_score": round(kh_score, 1) if len(giao_ban_tasks) > 0 else round(task_score, 1),
                    "_gb_score": round(gb_score, 1) if len(giao_ban_tasks) > 0 else 0,
                    "_has_gb": len(giao_ban_tasks) > 0
                })
                
            if personnel_kpi:
                kpi_month_df = pd.DataFrame(personnel_kpi)
                if selected_dept_m != "Tﬂ¶—t cﬂ¶˙ ph+¶ng ban":
                    kpi_month_df = kpi_month_df[kpi_month_df["Ph+¶ng ban"] == DEPT_ABBR.get(selected_dept_m, selected_dept_m)]
                st.dataframe(
                    kpi_month_df[["Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án", "Ph+¶ng ban", "Sﬂ+Ê viﬂ+Ác", "-…iﬂ+‚m c+¶ng viﬂ+Ác", "Th¶¶ﬂ+Éng/Phﬂ¶Ìt", "Tﬂ+ˆNG -…Iﬂ+ÈM", "Xﬂ¶+p loﬂ¶Ìi"]],
                    column_config={
                        "Tﬂ+ˆNG -…Iﬂ+ÈM": st.column_config.ProgressColumn("Tﬂ+ˆNG -…Iﬂ+ÈM", format="%f", min_value=0, max_value=100),
                    },
                    use_container_width=True, hide_index=True
                )

                st.markdown("---")
                with st.expander("=ÉˆÏ Tra cﬂ+¨u chi tiﬂ¶+t -Êiﬂ+‚m KPI cﬂ+∫a tﬂ+Ωng nh+Ûn sﬂ+¶", expanded=False):
                    st.info("=É∆Ì T+°nh n-‚ng n+·y gi+¶p Quﬂ¶˙n l++ -Êﬂ+Êi chiﬂ¶+u c+Ìc -Êﬂ¶∫u viﬂ+Ác v+· mﬂ+¨c -Êﬂ+÷ ho+·n th+·nh cﬂ+∫a nh+Ûn sﬂ+¶ -Êﬂ+‚ x+Ìc minh t+°nh ch+°nh x+Ìc cﬂ+∫a -Êiﬂ+‚m sﬂ+Ê.")
                    valid_people = sorted(list(kpi_month_df['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'].unique()))
                    if valid_people:
                        det_p = st.selectbox("=ÉÊÒ Chﬂ+Ïn nh+Ûn sﬂ+¶ cﬂ¶∫n tra cﬂ+¨u", valid_people, key="detail_person_kpi")
                        if det_p:
                            p_info = kpi_month_df[kpi_month_df['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'] == det_p].iloc[0]
                            st.markdown(f"### =É∫´ Diﬂ+‡n giﬂ¶˙i c+¶ng thﬂ+¨c t+°nh -Êiﬂ+‚m cﬂ+∫a **{det_p}**")
                            
                            kh_val = p_info['_kh_score']
                            gb_val = p_info['_gb_score']
                            has_gb = p_info['_has_gb']
                            task_val = p_info['-…iﬂ+‚m c+¶ng viﬂ+Ác']
                            adj_val = p_info['Th¶¶ﬂ+Éng/Phﬂ¶Ìt']
                            final_val = p_info['Tﬂ+ˆNG -…Iﬂ+ÈM']
                            
                            st.markdown(f"**=ÉÙ• Danh s+Ìch c+¶ng viﬂ+Ác cﬂ+∫a {det_p}:**")
                            p_tasks = kpi_df[kpi_df['NguoiChuTri'] == det_p].copy()
                            if p_tasks.empty:
                                st.warning("Kh+¶ng c+¶ -Êﬂ¶∫u viﬂ+Ác n+·o -Ê¶¶ﬂ+˙c ghi nhﬂ¶°n trong th+Ìng.")
                            else:
                                p_tasks['TyTrongKPI'] = pd.to_numeric(p_tasks.get('TyTrongKPI', pd.Series(0, index=p_tasks.index)), errors='coerce').fillna(0)
                                explicit_w = p_tasks[p_tasks['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                                unweighted = len(p_tasks[p_tasks['TyTrongKPI'] <= 0])
                                auto_w = max(0, 100 - explicit_w) / unweighted if unweighted > 0 else 0
                                
                                quy_dois = []
                                w_thuctes = []
                                kh_parts = []
                                gb_parts = []
                                kh_tw = 0.0
                                gb_tw = 0.0
                                
                                for idx, row in p_tasks.iterrows():
                                    is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
                                    w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                                    if is_comp: 
                                        p = 100
                                        p_tasks.at[idx, 'MucDoGhiNhan'] = "-"
                                    elif "kh+Ìch quan" in str(row.get('PhanLoaiTreHan')).lower():
                                        cc = str(row.get('MucDoGhiNhan', '0%'))
                                        if "Miﬂ+‡n trﬂ+Ω" in cc: w = 0; p = 0
                                        elif "50%" in cc: p = 50
                                        elif "80%" in cc: p = 80
                                        elif "90%" in cc: p = 90
                                        else: p = 0
                                    else: 
                                        p = 0
                                        p_tasks.at[idx, 'MucDoGhiNhan'] = "-"
                                    
                                    quy_dois.append(p)
                                    w_round = round(w, 2)
                                    w_thuctes.append(w_round)
                                    
                                    if row.get('NguonGiaoViec', '') in ['C+¶ng viﬂ+Ác trong "Giao ban"', 'CV giao ban / VB -Êﬂ¶+n']:
                                        if w_round > 0:
                                            gb_parts.append(f"({p} +˘ {w_round}%)")
                                            gb_tw += w_round
                                    else:
                                        if w_round > 0:
                                            kh_parts.append(f"({p} +˘ {w_round}%)")
                                            kh_tw += w_round
                                    
                                p_tasks['Tﬂ++ trﬂ+Ïng (Thﬂ+¶c tﬂ¶+) %'] = w_thuctes
                                p_tasks['-…iﬂ+‚m quy -Êﬂ+Úi'] = quy_dois
                                
                                kh_math = f"[{' + '.join(kh_parts)}] / {round(kh_tw,2)}%" if kh_parts else "0"
                                gb_math = f"[{' + '.join(gb_parts)}] / {round(gb_tw,2)}%" if gb_parts else "0"
                                
                                if has_gb:
                                    st.info(f"**1n+≈G‚˙ -…iﬂ+‚m Kﬂ¶+ hoﬂ¶Ìch / -…ﬂ+Ônh kﬂ+¶ ({kh_val}):** = {kh_math}\n\n"
                                            f"**2n+≈G‚˙ -…iﬂ+‚m Giao ban ({gb_val}):** = {gb_math}\n\n"
                                            f"**3n+≈G‚˙ -…iﬂ+‚m Th¶¶ﬂ+Éng/Phﬂ¶Ìt:** {adj_val}\n\n"
                                            f"=ÉÊÎ **Tﬂ+ˆNG -…Iﬂ+ÈM ({final_val})** = (-…iﬂ+‚m KH +˘ 70% + -…iﬂ+‚m GB +˘ 30%) + Th¶¶ﬂ+Éng/Phﬂ¶Ìt = ({kh_val} +˘ 0.7 + {gb_val} +˘ 0.3) + ({adj_val})")
                                else:
                                    st.info(f"**1n+≈G‚˙ -…iﬂ+‚m Kﬂ¶+ hoﬂ¶Ìch / -…ﬂ+Ônh kﬂ+¶ ({kh_val}):** = {kh_math}\n\n"
                                            f"**2n+≈G‚˙ -…iﬂ+‚m Th¶¶ﬂ+Éng/Phﬂ¶Ìt:** {adj_val}\n\n"
                                            f"=ÉÊÎ **Tﬂ+ˆNG -…Iﬂ+ÈM ({final_val})** = -…iﬂ+‚m KH + Th¶¶ﬂ+Éng/Phﬂ¶Ìt = {kh_val} + ({adj_val})")

                                p_tasks_disp = p_tasks[['NguonGiaoViec', 'TenDuAn', 'TenCongViec', 'Deadline', 'TrangThai', 'PhanLoaiTreHan', 'MucDoGhiNhan', 'TyTrongKPI', 'Tﬂ++ trﬂ+Ïng (Thﬂ+¶c tﬂ¶+) %', '-…iﬂ+‚m quy -Êﬂ+Úi']].copy()
                                p_tasks_disp['Deadline'] = pd.to_datetime(p_tasks_disp['Deadline'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('')
                                st.dataframe(p_tasks_disp, use_container_width=True, hide_index=True)
                                
                            st.markdown(f"**G‹˚n+≈ Lﬂ+Ôch sﬂ+° Th¶¶ﬂ+Éng/Phﬂ¶Ìt cﬂ+∫a {det_p}:**")
                            p_adjs = adj_df[adj_df['TenNhanVien'] == det_p][['LoaiHanhVi', 'LyDo', 'DiemDieuChinh']] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
                            if p_adjs.empty:
                                st.success("Kh+¶ng c+¶ ghi nhﬂ¶°n th¶¶ﬂ+Éng/phﬂ¶Ìt n+·o.")
                            else:
                                st.dataframe(p_adjs, use_container_width=True, hide_index=True)
            else:
                st.info("Kh+¶ng c+¶ dﬂ+ª liﬂ+Áu c+Ì nh+Ûn hﬂ+˙p lﬂ+Á.")
    if 'kpi_tab2' in locals():
        with kpi_tab2:
            st.markdown("#### Tﬂ+Úng kﬂ¶+t KPI Cﬂ¶˙ N-‚m & Xﬂ¶+p loﬂ¶Ìi th¶¶ﬂ+Éng Th+Ìng 13")
            if is_manager_view:
                selected_year_full = st.selectbox("Chﬂ+Ïn N-‚m Tﬂ+Úng Kﬂ¶+t", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
                selected_dept_y = st.session_state.manager_dept if st.session_state.get('manager_dept') else "Tﬂ¶—t cﬂ¶˙ ph+¶ng ban"
            else:
                col_y1, col_y2 = st.columns(2)
                with col_y1:
                    selected_year_full = st.selectbox("Chﬂ+Ïn N-‚m Tﬂ+Úng Kﬂ¶+t", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
                with col_y2:
                    allowed_depts_y = get_departments_for_company(selected_company, config)
                    dept_options_y = ["Tﬂ¶—t cﬂ¶˙ ph+¶ng ban"] + allowed_depts_y
                    selected_dept_y = st.selectbox("Lﬂ+Ïc theo Ph+¶ng ban", dept_options_y, key="kpi_y_dept")
        
            if st.button("=Éˆ‰ Chﬂ¶Ìy / Cﬂ¶°p nhﬂ¶°t B+Ìo c+Ìo Tﬂ+Úng kﬂ¶+t N-‚m", type="primary"):
                with st.spinner("-…ang t+°nh to+Ìn dﬂ+ª liﬂ+Áu 12 th+Ìng..."):
                    import pandas as pd
                    from datetime import datetime, date
                    all_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                    adj_year_df = read_kpi_adjustments()
                    adj_year_df = adj_year_df[adj_year_df['Nam'] == selected_year_full]
                    if 'TenNhanVien' in adj_year_df.columns:
                        all_personnel.update(adj_year_df['TenNhanVien'].dropna().unique())
                
                    # Filter to only keep those who belong to the selected company
                    company_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                    all_personnel = all_personnel.intersection(company_personnel)
                
                    all_personnel = list(all_personnel)
                    all_personnel = [p for p in all_personnel if str(p).strip()]
                    yearly_data = []
                    for person in all_personnel:
                        person_df = display_df[display_df['NguoiChuTri'] == person].copy()
                    
                        months_grades = {}
                        count_a_star = 0
                        count_a = 0
                        count_b = 0
                        count_c = 0
                        count_d = 0
                    
                        for m in range(1, 13):
                            if selected_year_full > today.year or (selected_year_full == today.year and m > today.month):
                                months_grades[f"Th+Ìng {m}"] = "-"
                                continue
                        
                            def is_in_m(d):
                                if pd.isna(d): return False
                                if isinstance(d, str):
                                    try: d = datetime.strptime(d, "%Y-%m-%d").date()
                                    except: return False
                                if isinstance(d, datetime): d = d.date()
                                if isinstance(d, date): return d.month == m and d.year == selected_year_full
                                return False
                            
                            m_df = person_df[person_df['Deadline'].apply(is_in_m)] if not person_df.empty else person_df
                            m_adj_df = adj_year_df[(adj_year_df['TenNhanVien'] == person) & (adj_year_df['Thang'] == m)] if 'TenNhanVien' in adj_year_df.columns else pd.DataFrame()
                        
                            if m_df.empty and m_adj_df.empty:
                                months_grades[f"Th+Ìng {m}"] = "-"
                                continue
                            
                            m_df_copy = m_df.copy()
                            m_df_copy['TyTrongKPI'] = pd.to_numeric(m_df_copy.get('TyTrongKPI', pd.Series(0, index=m_df_copy.index)), errors='coerce').fillna(0)
                        
                            for idx, row in m_df_copy.iterrows():
                                is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
                                is_late = False
                                dl = row['Deadline']
                                if isinstance(dl, str):
                                    try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                                    except: pass
                                if isinstance(dl, datetime): dl = dl.date()
                                if isinstance(dl, date): is_late = (dl < today) and not is_comp
                                if is_late and row.get('PhanLoaiTreHan') == "=ÉÓÏ Do kh+Ìch quan":
                                    m_df_copy.at[idx, 'PhanTramHoanThanh'] = 100
                                
                            explicit_weight = m_df_copy[m_df_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                            uw_count = len(m_df_copy[m_df_copy['TyTrongKPI'] <= 0])
                            auto_w = max(0, 100 - explicit_weight) / uw_count if uw_count > 0 else 0
                        
                            if 'NguonGiaoViec' not in m_df_copy.columns:
                                m_df_copy['NguonGiaoViec'] = 'C+¶ng viﬂ+Ác -Ê¶¶ﬂ+˙c giao / -Êﬂ+Ônh k+º'
                            ke_hoach_tasks_y = m_df_copy[~m_df_copy['NguonGiaoViec'].isin(['C+¶ng viﬂ+Ác trong "Giao ban"', 'CV giao ban / VB -Êﬂ¶+n'])]
                            giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'].isin(['C+¶ng viﬂ+Ác trong "Giao ban"', 'CV giao ban / VB -Êﬂ¶+n'])]
                        
                            def calc_score_for_group_y(grp, auto_w):
                                if grp.empty: return 0
                                score = 0
                                total_w = 0
                                for idx, row in grp.iterrows():
                                    is_comp = (str(row.get('TrangThai')).strip() == 'Ho+·n th+·nh')
                                    w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                                
                                    if is_comp:
                                        p = 100
                                    else:
                                        if "kh+Ìch quan" in str(row.get('PhanLoaiTreHan')).lower():
                                            cc = row.get('MucDoGhiNhan', '0% (Kh+¶ng ghi nhﬂ¶°n)')
                                            if cc == "Miﬂ+‡n trﬂ+Ω (Loﬂ¶Ìi bﬂ+≈ KPI)":
                                                w = 0
                                                p = 0
                                            elif cc == "50%": p = 50
                                            elif cc == "80%": p = 80
                                            elif cc == "90%": p = 90
                                            else: p = 0
                                        else:
                                            p = 0
                                        
                                    if pd.isna(p): p = 0
                                    score += (p / 100.0) * w
                                    total_w += w
                                
                                if total_w > 0:
                                    return (score / total_w) * 100
                                return 0
                            
                            if len(giao_ban_tasks_y) > 0:
                                kh_score_y = calc_score_for_group_y(ke_hoach_tasks_y, auto_w)
                                gb_score_y = calc_score_for_group_y(giao_ban_tasks_y, auto_w)
                                t_score = kh_score_y * 0.7 + gb_score_y * 0.3
                            else:
                                t_score = calc_score_for_group_y(ke_hoach_tasks_y, auto_w)
                        
                            f_score = min(115, max(0, round(t_score + m_adj_df['DiemDieuChinh'].sum(), 2)))
                        
                            if f_score > 100:
                                grade = "A*"
                                count_a_star += 1
                            elif f_score > 91: 
                                grade = "A"
                                count_a += 1
                            elif f_score > 81: 
                                grade = "B"
                                count_b += 1
                            elif f_score > 71:
                                grade = "C"
                                count_c += 1
                            else:
                                if selected_year_full == today.year and m == today.month:
                                    grade = "-"
                                else:
                                    grade = "D"
                                    count_d += 1
                            
                            months_grades[f"Th+Ìng {m}"] = grade
                        
                        # Logic xﬂ¶+p loﬂ¶Ìi n-‚m mﬂ+¢i
                        evaluated = count_a_star + count_a + count_b + count_c + count_d
                        if evaluated == 0:
                            final_grade = "-"
                            bonus = "-"
                        elif evaluated < 12 and selected_year_full >= today.year:
                            final_grade = "-…ang t+°ch l+¨y"
                            bonus = "-"
                        else:
                            if count_c > 0 or count_d > 0:
                                final_grade = "C"
                                bonus = "60%"
                            elif count_b >= 2:
                                final_grade = "B"
                                bonus = "80%"
                            elif (count_a + count_a_star) >= 11:
                                final_grade = "A"
                                bonus = "100%"
                            else:
                                final_grade = "B"
                                bonus = "80%"
                            
                        row_data = {
                            "Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án": person,
                            "Ph+¶ng ban": DEPT_ABBR.get(person_df['PhongBan'].mode()[0], person_df['PhongBan'].mode()[0]) if not person_df.empty else ""
                        }
                        row_data.update(months_grades)
                        row_data["Xﬂ¶+p loﬂ¶Ìi N-‚m"] = final_grade
                        row_data["Mﬂ+¨c h¶¶ﬂ+Éng T13"] = bonus
                        yearly_data.append(row_data)
                    
                    if yearly_data:
                        yearly_df = pd.DataFrame(yearly_data)
                        if selected_dept_y != "Tﬂ¶—t cﬂ¶˙ ph+¶ng ban":
                            yearly_df = yearly_df[yearly_df["Ph+¶ng ban"] == DEPT_ABBR.get(selected_dept_y, selected_dept_y)]
                        st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                    
                        excel_data = kpi_reports.generate_yearly_excel(yearly_df, selected_year_full)
                        st.download_button("=ÉÙ— Xuﬂ¶—t B+Ìo c+Ìo Excel", data=excel_data, file_name=f"TongKet_KPI_{selected_year_full}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.info("Kh+¶ng c+¶ dﬂ+ª liﬂ+Áu.")

    is_hr = role_mode == "HR" and st.session_state.get("is_admin_authenticated", False)
    is_manager = role_mode == "Quﬂ¶˙n l++" and st.session_state.get("is_manager_authenticated", False)
    
    if is_hr or is_manager:
        with kpi_tab3:
            st.markdown("#### G‹˚n+≈ -…iﬂ+¸u chﬂ+Înh -…iﬂ+‚m Th¶¶ﬂ+Éng / Phﬂ¶Ìt")
            all_p_list = []
            
            if is_manager and st.session_state.get('manager_dept'):
                dept = st.session_state.manager_dept
                if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
                    for comp, comp_data in config.get("companies", {}).items():
                        all_p_list.extend(comp_data.get("personnel_by_department", {}).get(dept, []))
                    all_p_list.extend(config.get("personnel_by_department", {}).get(dept, []))
                else:
                    all_p_list.extend(get_personnel_for_company_dept(selected_company, dept, config))
            else:
                if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
                    for comp, comp_data in config.get("companies", {}).items():
                        for dept, persons in comp_data.get("personnel_by_department", {}).items():
                            all_p_list.extend(persons)
                    for dept, persons in config.get("personnel_by_department", {}).items():
                        all_p_list.extend(persons)
                else:
                    valid_depts = get_departments_for_company(selected_company, config)
                    for dept in valid_depts:
                        persons = get_personnel_for_company_dept(selected_company, dept, config)
                        all_p_list.extend(persons)
                        
                    is_marina_co = "CTY CP DMT - MARINA" in selected_company or "Du thuyﬂ+¸n Happy Yacht" in selected_company
                    is_traffic_co = "X+ÈY Dﬂ+¶NG C+ˆNG TR+ÓNH GIAO TH+ˆNG -…N-MT" in selected_company
                    if not is_marina_co and not is_traffic_co:
                        c_personnel = set(display_df['NguoiChuTri'].dropna().unique())
                        leads = DEPT_LEADS.get(selected_company, {}).values()
                        valid_people = c_personnel.union(set(leads))
                        all_p_list = [p for p in all_p_list if p in valid_people]
                        
            all_p_list = sorted(list(set(all_p_list)))
            if not all_p_list:
                all_p_list = ["(Ch¶¶a c+¶ nh+Ûn sﬂ+¶)"]
                
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                adj_person = st.selectbox("T+¨n nh+Ûn vi+¨n", all_p_list)
                adj_month = st.selectbox("Th+Ìng +Ìp dﬂ+—ng", list(range(1, 13)), index=today.month - 1)
                adj_year = st.selectbox("N-‚m +Ìp dﬂ+—ng", [today.year - 1, today.year, today.year + 1], index=1)
            
            with col_f2:
                template_opts = ["-…i trﬂ+‡, vﬂ+¸ sﬂ+¢m", "Qu+¨n chﬂ¶—m c+¶ng", "L++ do kh+Ìc"] if is_hr else ["L++ do kh+Ìc"]
                adj_template = st.selectbox("L++ do mﬂ¶Ωu", template_opts)
                
                if adj_template == "-…i trﬂ+‡, vﬂ+¸ sﬂ+¢m":
                    so_lan = st.number_input("Tﬂ+Úng sﬂ+Ê lﬂ¶∫n trong th+Ìng", min_value=1, value=1)
                    sugg_val = max(0, so_lan - 5) * 2
                    
                    st.info(f"G‰¶n+≈ Bﬂ¶Ìn -Êang nhﬂ¶°p tﬂ+Úng cﬂ+÷ng {so_lan} lﬂ¶∫n vi phﬂ¶Ìm trong th+Ìng {adj_month}.")
                    if so_lan >= 6:
                        st.warning(f"G‹·n+≈ Tﬂ+Ω lﬂ¶∫n 6 trﬂ+É -Êi: -…ﬂ+¸ xuﬂ¶—t trﬂ+Ω tﬂ+Úng cﬂ+÷ng {sugg_val} -Êiﬂ+‚m.")
                    else:
                        st.success("G£‡ D¶¶ﬂ+¢i 6 lﬂ¶∫n: Ch¶¶a bﬂ+Ô trﬂ+Ω -Êiﬂ+‚m.")
                        
                    adj_type = "=É¢Ê Phﬂ¶Ìt -Êiﬂ+‚m"
                    adj_val = st.number_input("Tﬂ+Úng sﬂ+Ê -Êiﬂ+‚m trﬂ+Ω", min_value=0, max_value=100, value=sugg_val)
                    adj_reason = st.text_input("Ghi ch+¶ th+¨m (T+¶y chﬂ+Ïn)")
                    
                elif adj_template == "Qu+¨n chﬂ¶—m c+¶ng":
                    so_lan = st.number_input("Tﬂ+Úng sﬂ+Ê lﬂ¶∫n trong th+Ìng", min_value=1, value=1)
                    sugg_val = max(0, so_lan - 2) * 1
                    
                    st.info(f"G‰¶n+≈ Bﬂ¶Ìn -Êang nhﬂ¶°p tﬂ+Úng cﬂ+÷ng {so_lan} lﬂ¶∫n vi phﬂ¶Ìm trong th+Ìng {adj_month}.")
                    if so_lan >= 3:
                        st.warning(f"G‹·n+≈ Tﬂ+Ω lﬂ¶∫n 3 trﬂ+É -Êi: -…ﬂ+¸ xuﬂ¶—t trﬂ+Ω tﬂ+Úng cﬂ+÷ng {sugg_val} -Êiﬂ+‚m.")
                    else:
                        st.success("G£‡ D¶¶ﬂ+¢i 3 lﬂ¶∫n: Ch¶¶a bﬂ+Ô trﬂ+Ω -Êiﬂ+‚m.")
                        
                    adj_type = "=É¢Ê Phﬂ¶Ìt -Êiﬂ+‚m"
                    adj_val = st.number_input("Tﬂ+Úng sﬂ+Ê -Êiﬂ+‚m trﬂ+Ω", min_value=0, max_value=100, value=sugg_val)
                    adj_reason = st.text_input("Ghi ch+¶ th+¨m (T+¶y chﬂ+Ïn)")
                    
                else:
                    adj_type = st.radio("Ph+Ûn loﬂ¶Ìi h+·nh vi", ["G°… Th¶¶ﬂ+Éng -Êiﬂ+‚m", "=É¢Ê Phﬂ¶Ìt -Êiﬂ+‚m"], horizontal=True)
                    adj_val = st.number_input("Sﬂ+Ê -Êiﬂ+‚m", min_value=0, max_value=15, value=5)
                    adj_reason = st.text_area("L++ do chi tiﬂ¶+t (Bﬂ¶ªt buﬂ+÷c)")
                    
            if st.button("L¶¶u -…iﬂ+‚m -…iﬂ+¸u Chﬂ+Înh", type="primary"):
                if adj_template == "L++ do kh+Ìc" and not adj_reason.strip():
                    st.error("G‹·n+≈ Vui l+¶ng nhﬂ¶°p l++ do chi tiﬂ¶+t!")
                else:
                    actual_val = adj_val if adj_type == "G°… Th¶¶ﬂ+Éng -Êiﬂ+‚m" else -adj_val
                    if adj_template != "L++ do kh+Ìc":
                        final_reason = f"[{adj_template}] ({so_lan} lﬂ¶∫n) {adj_reason.strip()}".strip()
                    else:
                        final_reason = adj_reason.strip()
                    add_kpi_adjustment(adj_person, adj_month, adj_year, adj_type, actual_val, final_reason)
                    st.session_state["success_msg"] = "=ÉƒÎ -…+˙ l¶¶u -Êiﬂ+¸u chﬂ+Înh -Êiﬂ+‚m th+·nh c+¶ng!"
                    st.rerun()

        if 'kpi_tab4' in locals():
            with kpi_tab4:
                st.markdown("### T+¶y chﬂ+Ïn Xuﬂ¶—t B+Ìo C+Ìo & Ph+Ûn t+°ch")
                col_x1, col_x2 = st.columns(2)
            
                with col_x1:
                    st.markdown("#### 1. B+Ìo C+Ìo Ph+¶ng Ban (Excel)")
                    if st.button("Tﬂ¶˙i B+Ìo c+Ìo Ph+¶ng Ban"):
                        data_rows = []
                        for i, person in enumerate(all_p_list):
                            data_rows.append({
                                'HoTen': person, 'ChucVu': 'Nh+Ûn vi+¨n',
                                'SoLanTre': 0, 'SoLanSom': 0, 'SoLanKhongCC': 0,
                                'DiemTruTre': 0, 'DiemTruSom': 0, 'DiemTruKhongCC': 0,
                                'TongTru': 0, 'DiemConLai': 100, 'XepLoai': 'A', 'GhiChu': ''
                            })
                        excel_data = kpi_reports.generate_department_excel(selected_company, selected_month, selected_year, data_rows)
                        st.download_button("=ÉÙ— Tﬂ¶˙i B+Ìo C+Ìo Excel", data=excel_data, file_name=f"KPI_Thang_{selected_month}_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
                with col_x2:
                    st.markdown("#### 2. Phiﬂ¶+u KPI C+Ì Nh+Ûn (Word)")
                    st.info(f"-…ang xuﬂ¶—t dﬂ+ª liﬂ+Áu cﬂ+∫a: **Th+Ìng {selected_month}/{selected_year}** (-…ﬂ+‚ xuﬂ¶—t th+Ìng kh+Ìc, vui l+¶ng quay lﬂ¶Ìi tab '-…+Ình gi+Ì theo Th+Ìng' -Êﬂ+‚ chﬂ+Ïn).")
                    emp_to_export = st.selectbox("Chﬂ+Ïn nh+Ûn vi+¨n", all_p_list, key='emp_export')
                    if st.button("Tﬂ¶Ìo Phiﬂ¶+u -…+Ình Gi+Ì"):
                        # Collect real tasks and penalties
                        emp_tasks = []
                        kpi_score = 100
                        if personnel_kpi:
                            for p in personnel_kpi:
                                if p['Ng¶¶ﬂ+•i thﬂ+¶c hiﬂ+Án'] == emp_to_export:
                                    kpi_score = p['-…iﬂ+‚m c+¶ng viﬂ+Ác']
                                    break
                    
                        e_kpi_df = kpi_df[kpi_df['NguoiChuTri'] == emp_to_export].copy()
                        e_kpi_df['TyTrongKPI'] = pd.to_numeric(e_kpi_df['TyTrongKPI'], errors='coerce').fillna(0)
                        e_kpi_df['PhanTramHoanThanh'] = pd.to_numeric(e_kpi_df['PhanTramHoanThanh'], errors='coerce').fillna(0)
                        # Calc weights again if needed, or just display raw tasks
                        explicit_weight_sum = e_kpi_df[e_kpi_df['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                        unweighted_count = len(e_kpi_df[e_kpi_df['TyTrongKPI'] <= 0])
                        remaining_weight = max(0, 100 - explicit_weight_sum)
                        auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
                    
                        for idx, row in e_kpi_df.iterrows():
                            w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                            pt = row.get('PhanTramHoanThanh', 0)
                            if pd.isna(pt): pt = 0
                        
                            diem_tru = w - (pt / 100.0 * w)
                            emp_tasks.append({
                                'TenCV': row['TenCongViec'],
                                'TgianYC': str(row['Deadline']),
                                'KetQua': f"{pt}% (Tﬂ++ trﬂ+Ïng: {w:.1f}%)",
                                'DiemTru': round(diem_tru, 1)
                            })
                        
                        e_adj_df = adj_df[adj_df['TenNhanVien'] == emp_to_export] if 'TenNhanVien' in adj_df.columns else pd.DataFrame()
                        penalties = e_adj_df.to_dict('records')
                    
                        def _get_pb(name):
                            # Try to find from current company's departments
                            depts = get_departments_for_company(selected_company, config)
                            if depts:
                                for d in depts:
                                    p_list = get_personnel_for_company_dept(selected_company, d, config)
                                    if name in p_list: return d
                            # Fallback to global config
                            for d, p_list in config.get("personnel_by_department", {}).items():
                                if name in p_list: return d
                            return "Kh+Ìc"

                        emp_pb = _get_pb(emp_to_export)
                        word_data = kpi_reports.generate_individual_docx(emp_to_export, selected_month, selected_year, kpi_score, emp_tasks, penalties, "Nh+Ûn vi+¨n", emp_pb)
                        st.download_button("=ÉÙ— Tﬂ¶˙i Phiﬂ¶+u C+Ì Nh+Ûn (Word)", data=word_data, file_name=f"Phieu_KPI_{emp_to_export}_Thang_{selected_month}_{selected_year}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    
                st.divider()
                st.info("-…ﬂ+‚ xem Biﬂ+‚u -Êﬂ+Ù Ph+Ûn t+°ch, vui l+¶ng qua tab 'Tﬂ+Úng kﬂ¶+t KPI Cﬂ¶˙ N-‚m' v+· bﬂ¶—m 'Chﬂ¶Ìy / Cﬂ¶°p nhﬂ¶°t' tr¶¶ﬂ+¢c.")

                        
        with kpi_tab3:
            st.divider()
            st.markdown("##### Lﬂ+Ôch sﬂ+° Th¶¶ﬂ+Éng / Phﬂ¶Ìt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                # Filter out personnel not belonging to the current company
                hist_df = hist_df[hist_df["TenNhanVien"].isin(all_p_list)]
                
                if hist_df.empty:
                    st.info("Ch¶¶a c+¶ lﬂ+Ôch sﬂ+° -Êiﬂ+¸u chﬂ+Înh cho -Ê¶Ìn vﬂ+Ô n+·y.")
                else:
                    def _get_pb(name):
                        # Try to find from current company's departments
                        if selected_company != "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
                            depts = get_departments_for_company(selected_company, config)
                            for d in depts:
                                p_list = get_personnel_for_company_dept(selected_company, d, config)
                                if name in p_list: return d
                        # Fallback to global config
                        for d, p_list in config.get("personnel_by_department", {}).items():
                            if name in p_list: return d
                        return "Kh+Ìc"
                        
                    hist_df["Ph+¶ng ban"] = hist_df["TenNhanVien"].apply(_get_pb)
                    
                    # Reorder columns to put Ph+¶ng ban next to TenNhanVien
                    cols = list(hist_df.columns)
                    if "Ph+¶ng ban" in cols:
                        cols.insert(cols.index("TenNhanVien") + 1, cols.pop(cols.index("Ph+¶ng ban")))
                        hist_df = hist_df[cols]
                    
                    # Lﬂ+Ïc (Filter)
                    if is_manager:
                        f_pb = "Tﬂ¶—t cﬂ¶˙"
                        f_thang = st.selectbox("Lﬂ+Ïc Th+Ìng", ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(set(hist_df["Thang"])), reverse=True), key="flt_adj_thang")
                    else:
                        col_flt1, col_flt2 = st.columns(2)
                        with col_flt1:
                            f_pb = st.selectbox("Lﬂ+Ïc Ph+¶ng Ban", ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(set(hist_df["Ph+¶ng ban"]))), key="flt_adj_pb")
                        with col_flt2:
                            f_thang = st.selectbox("Lﬂ+Ïc Th+Ìng", ["Tﬂ¶—t cﬂ¶˙"] + sorted(list(set(hist_df["Thang"])), reverse=True), key="flt_adj_thang")
                    
                    hist_display_df = hist_df.copy()
                    if f_pb != "Tﬂ¶—t cﬂ¶˙":
                        hist_display_df = hist_display_df[hist_display_df["Ph+¶ng ban"] == f_pb]
                    if f_thang != "Tﬂ¶—t cﬂ¶˙":
                        hist_display_df = hist_display_df[hist_display_df["Thang"] == f_thang]
                    
                    st.dataframe(hist_display_df.sort_values(by=["Ph+¶ng ban", "Thang", "ID"], ascending=[True, False, False]), use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.markdown("##### =É˘Ên+≈ X+¶a -…iﬂ+¸u Chﬂ+Înh KPI")
                    if is_hr:
                        st.info("Nhﬂ¶°p sﬂ+Ê ID t¶¶¶Ìng ﬂ+¨ng trong bﬂ¶˙ng tr+¨n -Êﬂ+‚ x+¶a dﬂ+ª liﬂ+Áu.")
                        col_del1, col_del2 = st.columns([1, 3])
                        with col_del1:
                            del_id = st.number_input("Nhﬂ¶°p ID cﬂ¶∫n x+¶a", min_value=1, value=1)
                        with col_del2:
                            st.write("") # Spacer
                            st.write("")
                            if st.button("G•Ó X+¶a d+¶ng n+·y", type="primary"):
                                success, msg = delete_kpi_adjustment(del_id)
                                if success:
                                    st.success(f"-…+˙ x+¶a th+·nh c+¶ng -Êiﬂ+¸u chﬂ+Înh c+¶ ID: {del_id}")
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.info("G‹·n+≈ Vui l+¶ng li+¨n hﬂ+Á bﬂ+÷ phﬂ¶°n HR nﬂ¶+u bﬂ¶Ìn nhﬂ¶°p sai v+· cﬂ¶∫n x+¶a hoﬂ¶+c sﬂ+°a -Êiﬂ+‚m.")

            else:
                st.info("Ch¶¶a c+¶ lﬂ+Ôch sﬂ+° -Êiﬂ+¸u chﬂ+Înh.")

# ----------------- 6. QUﬂ¶ÛN L+• Cﬂ¶ÒU H+ÓNH -----------------# ----------------- 6. QUﬂ¶ÛN L+• Cﬂ¶ÒU H+ÓNH -----------------
elif menu in ["G£‡ Duyﬂ+Át & Nghiﬂ+Ám thu c+¶ng viﬂ+Ác", "G‹˚n+≈ Duyﬂ+Át viﬂ+Ác Kh+Ìch quan", "G£‡ Duyﬂ+Át viﬂ+Ác Kh+Ìch quan"]:
    st.header("G£‡ Duyﬂ+Át & Nghiﬂ+Ám thu c+¶ng viﬂ+Ác")
    
    if not (st.session_state.is_admin_authenticated or st.session_state.get("is_manager_authenticated", False)):
        st.warning("G‹·n+≈ Vui l+¶ng nhﬂ¶°p **Mﬂ¶°t khﬂ¶¨u Quﬂ¶˙n l++** ﬂ+É thanh b+¨n tr+Ìi (cﬂ+÷t menu) -Êﬂ+‚ truy cﬂ¶°p t+°nh n-‚ng n+·y.")
    else:
        # df is already loaded and mapped with DEPT_ABBR globally
        
        tab_nghiemthu, tab_khachquan = st.tabs(["=ÉÙÊ 1. Nghiﬂ+Ám thu c+¶ng viﬂ+Ác (Checker)", "G‹˚n+≈ 2. Duyﬂ+Át l++ do Kh+Ìch quan"])
        
        with tab_nghiemthu:
            st.markdown("### Nghiﬂ+Ám thu c+¶ng viﬂ+Ác")
            st.info("Danh s+Ìch c+Ìc c+¶ng viﬂ+Ác nh+Ûn vi+¨n -Ê+˙ b+Ìo c+Ìo ho+·n th+·nh. Vui l+¶ng kiﬂ+‚m tra Minh chﬂ+¨ng v+· chﬂ+Ïn Trﬂ¶Ìng th+Ìi duyﬂ+Át.")
            if display_df.empty:
                st.info("Ch¶¶a c+¶ dﬂ+ª liﬂ+Áu c+¶ng viﬂ+Ác.")
            else:
                nghiemthu_df = display_df[display_df['TrangThai'] == 'Chﬂ+• nghiﬂ+Ám thu'].copy()
                if role_mode == "Quﬂ¶˙n l++":
                    manager_dept = st.session_state.get("manager_dept", "Tﬂ¶—t cﬂ¶˙")
                    if manager_dept != "Tﬂ¶—t cﬂ¶˙":
                        nghiemthu_df = nghiemthu_df[nghiemthu_df['PhongBan'] == manager_dept]
                        
                if nghiemthu_df.empty:
                    st.success("=ÉƒÎ Hiﬂ+Án tﬂ¶Ìi kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o chﬂ+• nghiﬂ+Ám thu!")
                else:
                    st.warning(f"C+¶ **{len(nghiemthu_df)}** c+¶ng viﬂ+Ác -Êang chﬂ+• nghiﬂ+Ám thu.")
                    nt_cols = ["ID", "NguoiChuTri", "TenCongViec", "Deadline", "LinkKetQua", "TrangThaiNghiemThu"]
                    if "TrangThaiNghiemThu" not in nghiemthu_df.columns:
                        nghiemthu_df["TrangThaiNghiemThu"] = "Chﬂ+• duyﬂ+Át"
                    disp_nt = nghiemthu_df[nt_cols].copy()
                    
                    nt_col_config = {
                        "ID": st.column_config.TextColumn("M+˙ CV", disabled=True),
                        "NguoiChuTri": st.column_config.TextColumn("Ng¶¶ﬂ+•i Phﬂ+— Tr+Ìch", disabled=True),
                        "TenCongViec": st.column_config.TextColumn("T+¨n C+¶ng Viﬂ+Ác", disabled=True),
                        "Deadline": st.column_config.DateColumn("Hﬂ¶Ìn Ch+¶t", disabled=True, format="DD/MM/YYYY"),
                        "LinkKetQua": st.column_config.LinkColumn("Minh Chﬂ+¨ng", disabled=True),
                        "TrangThaiNghiemThu": st.column_config.SelectboxColumn(
                            "Trﬂ¶Ìng th+Ìi Duyﬂ+Át",
                            options=["Chﬂ+• duyﬂ+Át", "G£‡ Duyﬂ+Át (Ho+·n th+·nh)", "G•Ó Tﬂ+Ω chﬂ+Êi (L+·m lﬂ¶Ìi)"],
                            required=True
                        )
                    }
                    edited_nt = st.data_editor(
                        disp_nt,
                        column_config=nt_col_config,
                        hide_index=True,
                        use_container_width=True,
                        num_rows="fixed",
                        key="editor_nghiemthu"
                    )
                    
                    if st.button("=É∆+ L¶¶u kﬂ¶+t quﬂ¶˙ Nghiﬂ+Ám thu", type="primary"):
                        with acquire_db_lock():
                            fresh_df = read_db()
                            changed = False
                            for idx, row in edited_nt.iterrows():
                                task_id = row['ID']
                                new_val = row['TrangThaiNghiemThu']
                                if new_val == "G£‡ Duyﬂ+Át (Ho+·n th+·nh)":
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThai'] = 'Ho+·n th+·nh'
                                    if 'TrangThaiNghiemThu' in fresh_df.columns:
                                        fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThaiNghiemThu'] = '-…+˙ duyﬂ+Át'
                                    changed = True
                                elif new_val == "G•Ó Tﬂ+Ω chﬂ+Êi (L+·m lﬂ¶Ìi)":
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThai'] = '-…ang thﬂ+¶c hiﬂ+Án'
                                    fresh_df.loc[fresh_df['ID'] == task_id, 'PhanTramHoanThanh'] = 0
                                    if 'TrangThaiNghiemThu' in fresh_df.columns:
                                        fresh_df.loc[fresh_df['ID'] == task_id, 'TrangThaiNghiemThu'] = 'Tﬂ+Ω chﬂ+Êi'
                                    changed = True
                            
                            if changed:
                                if save_db(fresh_df):
                                    st.success("G£‡ -…+˙ l¶¶u kﬂ¶+t quﬂ¶˙ nghiﬂ+Ám thu th+·nh c+¶ng!")
                                    st.rerun()
                                    
        with tab_khachquan:
            if display_df.empty:
                st.info("Ch¶¶a c+¶ dﬂ+ª liﬂ+Áu c+¶ng viﬂ+Ác.")
            else:
                if role_mode == "Quﬂ¶˙n l++":
                    col_thang, col_nam = st.columns(2)
                    with col_thang:
                        thang_opts = list(range(1, 13))
                        sel_thang = st.selectbox("Chﬂ+Ïn Th+Ìng", thang_opts, index=today.month - 1)
                    with col_nam:
                        nam_opts = [today.year - 1, today.year, today.year + 1]
                        sel_nam = st.selectbox("Chﬂ+Ïn N-‚m", nam_opts, index=1)
                    sel_phong = "Tﬂ¶—t cﬂ¶˙"
                else:
                    col_thang, col_nam, col_phong = st.columns(3)
                    with col_thang:
                        thang_opts = list(range(1, 13))
                        sel_thang = st.selectbox("Chﬂ+Ïn Th+Ìng", thang_opts, index=today.month - 1)
                    with col_nam:
                        nam_opts = [today.year - 1, today.year, today.year + 1]
                        sel_nam = st.selectbox("Chﬂ+Ïn N-‚m", nam_opts, index=1)
                    with col_phong:
                        valid_depts = sorted([d for d in display_df['PhongBan'].dropna().unique() if str(d).strip() != ""])
                        phong_opts = ["Tﬂ¶—t cﬂ¶˙"] + valid_depts
                        sel_phong = st.selectbox("Lﬂ+Ïc theo Ph+¶ng/Ban", phong_opts)
                    
                st.markdown("---")
                
                # Filter logic
                def is_in_selected_month(d_str):
                    if not d_str: return False
                    try:
                        d = pd.to_datetime(d_str)
                        return d.month == sel_thang and d.year == sel_nam
                    except:
                        return False
                
                local_df = display_df.copy()        
                local_df['is_in_month'] = local_df['Deadline'].apply(is_in_selected_month)
                
                # Condition: Deadline in month, objective reason
                mask = local_df['is_in_month'] & local_df['PhanLoaiTreHan'].astype(str).str.lower().str.contains("kh+Ìch quan")
                if sel_phong != "Tﬂ¶—t cﬂ¶˙":
                    mask = mask & (local_df['PhongBan'] == sel_phong)
                    
                filtered_df = local_df[mask].copy()
                
                if filtered_df.empty:
                    st.success(f"=ÉƒÎ Kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o b+Ìo c+Ìo Kh+Ìch quan trong th+Ìng {sel_thang}/{sel_nam}!")
                else:
                    st.info(f"-…ang hiﬂ+‚n thﬂ+Ô **{len(filtered_df)}** c+¶ng viﬂ+Ác b+Ìo c+Ìo l++ do Kh+Ìch quan.")
                    
                    # Setup Editor
                    # Compute dynamic state for UI
                    filtered_df["TrangThaiDuyetKQ"] = filtered_df["MucDoGhiNhan"].apply(lambda x: "=Éˆ¶ Ch¶¶a duyﬂ+Át" if str(x).strip() == "Ch¶¶a -Ê+Ình gi+Ì" else "=ÉÉÛ -…+˙ duyﬂ+Át")

                    edit_cols = ["ID", "PhongBan", "NguoiChuTri", "TenCongViec", "Deadline", "TrangThai", "GiaiTrinhDeXuat", "TrangThaiDuyetKQ", "MucDoGhiNhan"]
                    disp_df = filtered_df[edit_cols].copy()
                    
                    # We need to make all columns disabled EXCEPT MucDoGhiNhan
                    col_config = {
                        "ID": st.column_config.TextColumn("M+˙ CV", disabled=True),
                        "PhongBan": st.column_config.TextColumn("Ph+¶ng/Ban", disabled=True),
                        "NguoiChuTri": st.column_config.TextColumn("Ng¶¶ﬂ+•i Phﬂ+— Tr+Ìch", disabled=True),
                        "TenCongViec": st.column_config.TextColumn("T+¨n C+¶ng Viﬂ+Ác", disabled=True),
                        "Deadline": st.column_config.DateColumn("Hﬂ¶Ìn Ch+¶t", disabled=True, format="DD/MM/YYYY"),
                        "TrangThai": st.column_config.TextColumn("Trﬂ¶Ìng Th+Ìi", disabled=True),
                        "GiaiTrinhDeXuat": st.column_config.TextColumn("Giﬂ¶˙i Tr+ºnh Kh+Ìch Quan", disabled=True),
                        "TrangThaiDuyetKQ": st.column_config.TextColumn("Trﬂ¶Ìng th+Ìi", disabled=True),
                        "MucDoGhiNhan": st.column_config.SelectboxColumn(
                            "Mﬂ+¨c -Êﬂ+÷ Ghi nhﬂ¶°n KPI",
                            help="Chﬂ+Ïn mﬂ+¨c -Êiﬂ+‚m -Ê+Ình gi+Ì theo l++ do kh+Ìch quan (Chﬂ+Î d+·nh cho Quﬂ¶˙n l++)",
                            options=["Ch¶¶a -Ê+Ình gi+Ì", "0% (Kh+¶ng ghi nhﬂ¶°n)", "Miﬂ+‡n trﬂ+Ω (Loﬂ¶Ìi bﬂ+≈ KPI)", "50%", "80%", "90%"],
                            required=True
                        )
                    }
                    
                    edited_df = st.data_editor(
                        disp_df,
                        column_config=col_config,
                        hide_index=True,
                        use_container_width=True,
                        num_rows="fixed",
                        key=f"editor_approve_{sel_thang}_{sel_nam}"
                    )
                    
                    if st.button("=É∆+ L¶¶u tﬂ¶—t cﬂ¶˙ thay -Êﬂ+Úi", type="primary"):
                        with acquire_db_lock():
                            
                            fresh_df = read_db()
                            changed = False
                            for idx, row in edited_df.iterrows():
                                task_id = row['ID']
                                new_val = row['MucDoGhiNhan']
                                # Some tasks might not exist if deleted concurrently, but for robustness:
                                if task_id in fresh_df['ID'].values:
                                    old_val = fresh_df.loc[fresh_df['ID'] == task_id, 'MucDoGhiNhan'].values[0]
                                    if new_val != old_val:
                                        fresh_df.loc[fresh_df['ID'] == task_id, 'MucDoGhiNhan'] = new_val
                                        changed = True
                                    
                            if changed:
                                fresh_df = fresh_df.drop(columns=['is_in_month', 'TrangThaiDuyetKQ_disp'], errors='ignore')
                                if save_db(fresh_df):
                                    st.success("G£‡ -…+˙ l¶¶u to+·n bﬂ+÷ ph+¨ duyﬂ+Át th+·nh c+¶ng!")
                                    st.rerun()
                            else:
                                st.info("Ch¶¶a c+¶ thay -Êﬂ+Úi n+·o cﬂ¶∫n l¶¶u.")


elif menu == "=ÉˆÏ Quﬂ¶˙n l++ & -…ﬂ+Êi chiﬂ¶+u JD":
    st.markdown("### =ÉˆÏ Quﬂ¶˙n l++ & -…ﬂ+Êi chiﬂ¶+u JD (Tr+° tuﬂ+Á nh+Ûn tﬂ¶Ìo)")
    st.info("=É∆Ì Hﬂ+Á thﬂ+Êng sﬂ+° dﬂ+—ng **Tr+° tuﬂ+Á nh+Ûn tﬂ¶Ìo (Google Gemini)** -Êﬂ+‚ ph+Ûn t+°ch tﬂ+¶ -Êﬂ+÷ng viﬂ+Ác nh+Ûn sﬂ+¶ l+·m c+¶ -Ê+¶ng chuy+¨n m+¶n trong Bﬂ¶˙n M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác (JD) hay kh+¶ng.")
    
    tab_hr, tab_ai = st.tabs(["=ÉÙ• 1. Cﬂ¶°p nhﬂ¶°t M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác (D+·nh cho HR)", "=ÉˆÏ 2. AI -…ﬂ+Êi chiﬂ¶+u & B+Ìo c+Ìo (D+·nh cho Sﬂ¶+p)"])
    
    with tab_hr:
        st.markdown("#### Khai b+Ìo JD nguy+¨n bﬂ¶˙n cho Nh+Ûn sﬂ+¶")
        st.write("Vui l+¶ng mﬂ+É file Word M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác cﬂ+∫a nh+Ûn sﬂ+¶, copy phﬂ¶∫n **TR+¸CH NHIﬂ+ÂM C+ˆNG VIﬂ+ÂC** v+· d+Ìn v+·o -Ê+Ûy.")
        
        # Select personnel
        if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
            st.warning("G‹·n+≈ Vui l+¶ng chﬂ+Ïn cﬂ+— thﬂ+‚ C+¶ng ty ﬂ+É cﬂ+÷t tr+Ìi.")
        else:
            comp_data = config.get("companies", {}).get(selected_company, {})
            all_depts = comp_data.get("departments", [])
            sel_dept = st.selectbox("Chﬂ+Ïn Ph+¶ng ban", all_depts, key="jd_dept")
            
            personnel = comp_data.get("personnel_by_department", {}).get(sel_dept, [])
            if personnel:
                sel_person = st.selectbox("Chﬂ+Ïn Nh+Ûn sﬂ+¶", personnel, key="jd_person")
                
                if "job_descriptions" not in config:
                    config["job_descriptions"] = {}
                if selected_company not in config["job_descriptions"]:
                    config["job_descriptions"][selected_company] = {}
                    
                existing_jd_data = config["job_descriptions"][selected_company].get(sel_person, "")
                if isinstance(existing_jd_data, str):
                    existing_jd_text = existing_jd_data
                else:
                    existing_jd_text = existing_jd_data.get("jd_text", "")
                    
                st.write("---")
                st.markdown("**C+Ìch 1: Nhﬂ¶°p v-‚n bﬂ¶˙n hoﬂ¶+c d+Ìn (Copy/Paste)**")
                jd_text = st.text_area("Nﬂ+÷i dung M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác:", value=existing_jd_text, height=200, key=f"jd_text_{sel_person}")
                
                st.markdown("**C+Ìch 2: Tﬂ¶˙i l+¨n file Word/PDF (Tﬂ+¶ -Êﬂ+÷ng -Êﬂ+Ïc nﬂ+÷i dung)**")
                uploaded_file = st.file_uploader("K+¨o thﬂ¶˙ file JD v+·o -Ê+Ûy", type=['docx', 'pdf'], key=f"jd_upload_{sel_person}")
                
                if uploaded_file is not None:
                    if st.button("Tr+°ch xuﬂ¶—t nﬂ+÷i dung tﬂ+Ω File"):
                        with st.spinner("-…ang -Êﬂ+Ïc file..."):
                            try:
                                text = ""
                                if uploaded_file.name.endswith(".docx"):
                                    import docx
                                    doc = docx.Document(uploaded_file)
                                    text = "\n".join([p.text for p in doc.paragraphs])
                                elif uploaded_file.name.endswith(".pdf"):
                                    import pypdf
                                    pdf = pypdf.PdfReader(uploaded_file)
                                    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                                
                                if not text.strip():
                                    st.warning("G‹·n+≈ Kh+¶ng thﬂ+‚ -Êﬂ+Ïc -Ê¶¶ﬂ+˙c chﬂ+ª tﬂ+Ω file n+·y (c+¶ thﬂ+‚ -Ê+Ûy l+· file scan/ﬂ¶˙nh). Vui l+¶ng copy v+· d+Ìn v-‚n bﬂ¶˙n thﬂ+∫ c+¶ng v+·o +¶ ph+°a tr+¨n.")
                                else:
                                    st.session_state[f"extracted_text_{sel_person}"] = text
                            except Exception as e:
                                st.error(f"Lﬂ+˘i -Êﬂ+Ïc file: {e}")
                
                if st.session_state.get(f"extracted_text_{sel_person}"):
                    st.success("-…+˙ tr+°ch xuﬂ¶—t th+·nh c+¶ng! Bﬂ¶Ìn c+¶ thﬂ+‚ xem v+· chﬂ+Înh sﬂ+°a tr¶¶ﬂ+¢c khi l¶¶u:")
                    jd_text = st.text_area("Nﬂ+÷i dung tr+°ch xuﬂ¶—t", value=st.session_state[f"extracted_text_{sel_person}"], height=200, key=f"jd_text_ext_{sel_person}")
                
                if st.button("=É∆+ L¶¶u M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác", type="primary"):
                    if not jd_text.strip():
                        st.error("G‹·n+≈ Nﬂ+÷i dung M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác -Êang trﬂ+Êng! Vui l+¶ng nhﬂ¶°p nﬂ+÷i dung hoﬂ¶+c tr+°ch xuﬂ¶—t tﬂ+Ω file tr¶¶ﬂ+¢c khi l¶¶u.")
                    else:
                        if isinstance(existing_jd_data, dict):
                            new_data = existing_jd_data.copy()
                            new_data["jd_text"] = jd_text
                        else:
                            new_data = {"jd_text": jd_text}
                            
                        config["job_descriptions"][selected_company][sel_person] = new_data
                        if save_config(config):
                            st.success(f"G£‡ -…+˙ l¶¶u Bﬂ¶˙n m+¶ tﬂ¶˙ c+¶ng viﬂ+Ác (JD) th+·nh c+¶ng cho nh+Ûn sﬂ+¶ **{sel_person}**!")
                            import time
                            time.sleep(1)
                            st.rerun()
            else:
                st.warning("Ph+¶ng ban n+·y ch¶¶a c+¶ nh+Ûn sﬂ+¶.")

    with tab_ai:
        st.markdown("#### =ÉˆÏ Ph+Ûn t+°ch -Êﬂ+÷ phﬂ+∫ c+¶ng viﬂ+Ác thﬂ+¶c tﬂ¶+ vﬂ+¢i JD")
        if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
            st.warning("G‹·n+≈ Vui l+¶ng chﬂ+Ïn cﬂ+— thﬂ+‚ C+¶ng ty ﬂ+É cﬂ+÷t tr+Ìi.")
        else:
            comp_data = config.get("companies", {}).get(selected_company, {})
            
            months = set()
            if not display_df.empty:
                for _, row in display_df.iterrows():
                    if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                        months.add(row['Deadline'].strftime('%m/%Y'))
            month_options = sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
            if not month_options: month_options = [today.strftime('%m/%Y')]
            
            c1, c2, c3 = st.columns(3)
            with c1: ai_month = st.selectbox("Th+Ìng -Ê+Ình gi+Ì", month_options, key="ai_month_select")
            with c2: ai_dept = st.selectbox("Ph+¶ng ban", comp_data.get("departments", []), key="ai_dept_select")
            
            ai_personnel = comp_data.get("personnel_by_department", {}).get(ai_dept, [])
            with c3:
                if ai_personnel:
                    ai_person = st.selectbox("Nh+Ûn sﬂ+¶", ai_personnel, key="ai_person_select")
                else:
                    ai_person = None
                    st.warning("Trﬂ+Êng")
            

            # --- BATCH AI SCAN ---
            st.markdown("---")
            with st.expander("G‹Ì Qu+¨t nhanh to+·n bﬂ+÷ Ph+¶ng ban (Batch AI Scan)", expanded=False):
                st.info("T+°nh n-‚ng n+·y sﬂ¶+ tﬂ+¶ -Êﬂ+÷ng kiﬂ+‚m tra JD cﬂ+∫a tﬂ¶—t cﬂ¶˙ nh+Ûn sﬂ+¶ trong ph+¶ng ban. Nhﬂ+ªng ai ch¶¶a c+¶ kﬂ¶+t quﬂ¶˙ sﬂ¶+ tﬂ+¶ -Êﬂ+÷ng gﬂ+Ïi AI -Êﬂ+‚ ph+Ûn t+°ch. Khuy+¨n d+¶ng khi bﬂ¶Ìn muﬂ+Ên kiﬂ+‚m tra tﬂ+Úng thﬂ+‚ cﬂ¶˙ ph+¶ng.")
                
                batch_api_key = ""
                try:
                    if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
                        batch_api_key = st.secrets["gemini"]["api_key"]
                except:
                    pass
                if not batch_api_key:
                    import os
                    batch_api_key = os.environ.get("GEMINI_API_KEY", "")
                    
                if not batch_api_key:
                    batch_api_key = st.text_input("=ÉˆÊ Nhﬂ¶°p kh+¶a API Gemini -Êﬂ+‚ qu+¨t h+·ng loﬂ¶Ìt:", type="password", key="batch_api_key_input")
                
                if st.button("=É‹« Bﬂ¶ªt -Êﬂ¶∫u Qu+¨t to+·n bﬂ+÷", type="primary"):
                    if not batch_api_key:
                        st.error("Vui l+¶ng nhﬂ¶°p API Key!")
                    elif not ai_personnel:
                        st.warning("Ph+¶ng ban kh+¶ng c+¶ nh+Ûn sﬂ+¶.")
                    else:
                        import google.generativeai as genai
                        import hashlib
                        import json
                        import time
                        
                        genai.configure(api_key=batch_api_key, transport='rest')
                        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        model_name = 'gemini-3.6-flash' if 'models/gemini-3.6-flash' in valid_models else ('gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else 'gemini-pro')
                        model = genai.GenerativeModel(model_name)
                        
                        results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def is_same_person_batch(db_name, target_name):
                            db_str = str(db_name).strip().lower()
                            tgt_str = str(target_name).strip().lower()
                            if db_str == tgt_str: return True
                            tgt_parts = tgt_str.split()
                            if len(tgt_parts) >= 2:
                                return tgt_parts[0] in db_str and tgt_parts[-1] in db_str
                            return False
                        
                        total_people = len(ai_personnel)
                        
                        for idx, p in enumerate(ai_personnel):
                            status_text.text(f"-…ang ph+Ûn t+°ch ({idx+1}/{total_people}): {p}...")
                            
                            # Lﬂ+Ïc c+¶ng viﬂ+Ác
                            p_tasks = display_df[
                                (display_df['NguoiChuTri'].apply(lambda x: is_same_person_batch(x, p))) & 
                                (display_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == ai_month)
                            ]
                            
                            if p_tasks.empty:
                                results.append({"Nh+Ûn sﬂ+¶": p, "Kﬂ¶+t quﬂ¶˙": "Trﬂ+Êng", "Tﬂ++ lﬂ+Á khﬂ+¢p": None, "Chi tiﬂ¶+t": "Kh+¶ng c+¶ c+¶ng viﬂ+Ác trong th+Ìng n+·y"})
                            else:
                                jd_data = config.get("job_descriptions", {}).get(selected_company, {}).get(p, "")
                                jd_str = jd_data if isinstance(jd_data, str) else jd_data.get("jd_text", "")
                                
                                if not jd_str.strip():
                                    results.append({"Nh+Ûn sﬂ+¶": p, "Kﬂ¶+t quﬂ¶˙": "Thiﬂ¶+u JD", "Tﬂ++ lﬂ+Á khﬂ+¢p": None, "Chi tiﬂ¶+t": "Ch¶¶a khai b+Ìo M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác"})
                                else:
                                    tasks_list = "\n".join([f"- {row['TenCongViec']}" for _, row in p_tasks.iterrows()])
                                    prompt = f"""
                                    -…+¶ng vai mﬂ+÷t Gi+Ìm -Êﬂ+Êc nh+Ûn sﬂ+¶ cﬂ+¶c kﬂ+¶ tinh tﬂ¶+. 
                                    D¶¶ﬂ+¢i -Ê+Ûy l+· Bﬂ¶˙n M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác (JD) cﬂ+∫a nh+Ûn vi+¨n {p}:
                                
                                    [Bﬂ¶ÛN M+ˆ Tﬂ¶Û C+ˆNG VIﬂ+ÂC]
                                    {jd_str}
                                    [Kﬂ¶+T TH+‹C JD]
                                
                                    V+· -Ê+Ûy l+· danh s+Ìch c+¶ng viﬂ+Ác hﬂ+Ï thﬂ+¶c hiﬂ+Án trong th+Ìng:
                                    {tasks_list}
                                
                                    NHIﬂ+ÂM Vﬂ+Ò Cﬂ+™A Bﬂ¶·N:
                                    1. -…ﬂ+Êi chiﬂ¶+u Tﬂ+¨NG c+¶ng viﬂ+Ác xem n+¶ c+¶ KHﬂ+‹P vﬂ+¢i chuy+¨n m+¶n quy -Êﬂ+Ônh trong JD kh+¶ng. 
                                    (L¶¶u ++: T+¨n c+¶ng viﬂ+Ác thﬂ+¶c tﬂ¶+ c+¶ thﬂ+‚ chi tiﬂ¶+t v+· tﬂ+Ω ngﬂ+ª kh+Ìc biﬂ+Át so vﬂ+¢i JD v-‚n xu+¶i. H+˙y d+¶ng t¶¶ duy suy luﬂ¶°n vﬂ+¸ bﬂ¶˙n chﬂ¶—t v+· mﬂ+—c -Ê+°ch -Êﬂ+‚ ph+Ìn -Êo+Ìn).
                                    2. Nﬂ¶+u khﬂ+¢p, giﬂ¶˙i th+°ch v+º n+¶ phﬂ+—c vﬂ+— cho mﬂ+—c n+·o trong JD. Nﬂ¶+u ngo+·i JD, ghi r+¶ l+· c+¶ng viﬂ+Ác ph+Ìt sinh.
                                    3. Format kﬂ¶+t quﬂ¶˙ -Êﬂ¶∫u ra th+·nh -Ê+¶ng -Êﬂ+Ônh dﬂ¶Ìng chuﬂ+˘i JSON th+¶ nh¶¶ sau (chﬂ+Î trﬂ¶˙ vﬂ+¸ JSON, kh+¶ng chﬂ+¨a dﬂ¶—u tick markdown ```json):
                                    {{
                                        "ty_le_khop": <sﬂ+Ê nguy+¨n tﬂ+Ω 0-100, v+° dﬂ+— 80>,
                                        "chi_tiet": [
                                            {{
                                                "ten_cong_viec": "<T+¨n c+¶ng viﬂ+Ác y nguy+¨n trong danh s+Ìch>",
                                                "phan_loai": "<Chﬂ+Î -Êiﬂ+¸n 'Khﬂ+¢p JD' hoﬂ¶+c 'Ngo+·i JD'>",
                                                "nhan_xet": "<Ph+Ûn t+°ch ngﬂ¶ªn gﬂ+Ïn 1-2 c+Ûu>"
                                            }}
                                        ]
                                    }}
                                    """
                                    
                                    prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
                                    cache_file = f".ai_cache_{prompt_hash}.txt"
                                    
                                    try:
                                        if os.path.exists(cache_file):
                                            with open(cache_file, "r", encoding="utf-8") as f:
                                                raw_text = f.read()
                                        else:
                                            max_retries = 3
                                            for attempt in range(max_retries):
                                                try:
                                                    response = model.generate_content(
                                                        prompt, 
                                                        generation_config={"temperature": 0.0},
                                                        request_options={"timeout": 60.0}
                                                    )
                                                    raw_text = response.text
                                                    break
                                                except Exception as api_err:
                                                    if attempt == max_retries - 1:
                                                        raise api_err
                                                    time.sleep(3 * (attempt + 1))
                                                    
                                            if raw_text:
                                                with open(cache_file, "w", encoding="utf-8") as f:
                                                    f.write(raw_text)
                                            time.sleep(3) # Tr+Ình rate limit

                                            
                                        cleaned = raw_text.strip()
                                        if cleaned.startswith("```json"):
                                            cleaned = cleaned[7:]
                                        if cleaned.endswith("```"):
                                            cleaned = cleaned[:-3]
                                        
                                        data = json.loads(cleaned)
                                        ty_le = data.get("ty_le_khop", 0)
                                        ngoai_jd_count = sum(1 for c in data.get("chi_tiet", []) if "Ngo+·i JD" in c.get("phan_loai", ""))
                                        
                                        if ty_le == 100:
                                            res_text = "=ÉÉÛ Tﬂ+Êt (100% khﬂ+¢p)"
                                        elif ty_le >= 50:
                                            res_text = f"=ÉÉÌ Cﬂ¶˙nh b+Ìo ({ty_le}% khﬂ+¢p)"
                                        else:
                                            res_text = f"=Éˆ¶ Lﬂ+Ách JD ({ty_le}% khﬂ+¢p)"
                                            
                                        chi_tiet_text = f"{ngoai_jd_count} viﬂ+Ác ngo+·i JD" if ngoai_jd_count > 0 else "Ho+·n to+·n khﬂ+¢p"
                                        
                                        results.append({"Nh+Ûn sﬂ+¶": p, "Kﬂ¶+t quﬂ¶˙": res_text, "Tﬂ++ lﬂ+Á khﬂ+¢p": ty_le, "Chi tiﬂ¶+t": chi_tiet_text})
                                    except Exception as e:
                                        results.append({"Nh+Ûn sﬂ+¶": p, "Kﬂ¶+t quﬂ¶˙": "Lﬂ+˘i AI", "Tﬂ++ lﬂ+Á khﬂ+¢p": None, "Chi tiﬂ¶+t": str(e)})
                            
                            progress_bar.progress((idx + 1) / total_people)
                            
                        status_text.success("G£‡ -…+˙ ho+·n th+·nh ph+Ûn t+°ch to+·n bﬂ+÷ ph+¶ng ban!")
                        
                        if results:
                            df_res = pd.DataFrame(results)
                            st.dataframe(df_res, use_container_width=True, hide_index=True)
                            
            st.markdown("---")

            if ai_person:
                jd_source_data = config.get("job_descriptions", {}).get(selected_company, {}).get(ai_person, "")
                if isinstance(jd_source_data, str):
                    jd_source = jd_source_data
                else:
                    jd_source = jd_source_data.get("jd_text", "")
                    
                if not jd_source.strip():
                    st.error(f"G‹·n+≈ Nh+Ûn sﬂ+¶ **{ai_person}** ch¶¶a -Ê¶¶ﬂ+˙c khai b+Ìo M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác. Vui l+¶ng sang tab b+¨n cﬂ¶Ình -Êﬂ+‚ cﬂ¶°p nhﬂ¶°t JD tr¶¶ﬂ+¢c khi AI c+¶ thﬂ+‚ qu+¨t.")
                else:
                    with st.expander("Xem tr¶¶ﬂ+¢c JD gﬂ+Êc (L+·m c¶Ì sﬂ+É chﬂ¶—m) =ÉÊ«", expanded=False):
                        st.text(jd_source)
                        
                    # Filter tasks for this person in this month flexibly to handle name changes (e.g. L+¨ Ngﬂ+Ïc T+¶ Uy+¨n vs L+¨ Thﬂ+Ô T+¶ Uy+¨n)
                    def is_same_person(db_name, target_name):
                        db_str = str(db_name).strip().lower()
                        tgt_str = str(target_name).strip().lower()
                        if db_str == tgt_str: return True
                        
                        # Match first and last name if exact match fails
                        tgt_parts = tgt_str.split()
                        if len(tgt_parts) >= 2:
                            return tgt_parts[0] in db_str and tgt_parts[-1] in db_str
                        return False
                        
                    ai_tasks = display_df[
                        (display_df['NguoiChuTri'].apply(lambda x: is_same_person(x, ai_person))) & 
                        (display_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == ai_month)
                    ]
                    
                    if ai_tasks.empty:
                        st.info(f"Kh+¶ng c+¶ c+¶ng viﬂ+Ác n+·o -Ê¶¶ﬂ+˙c -Ê-‚ng k++ trong th+Ìng {ai_month}.")
                    else:
                        st.write(f"T+ºm thﬂ¶—y **{len(ai_tasks)}** -Êﬂ¶∫u c+¶ng viﬂ+Ác do nh+Ûn sﬂ+¶ -Ê-‚ng k++ trong th+Ìng.")
                        
                        import os
                        api_key = ""
                        try:
                            if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
                                api_key = st.secrets["gemini"]["api_key"]
                        except:
                            pass
                            
                        if not api_key:
                            api_key = os.environ.get("GEMINI_API_KEY", "")
                            
                        if not api_key:
                            api_key = st.text_input("=ÉˆÊ Nhﬂ¶°p kh+¶a API Gemini (API Key) cﬂ+∫a bﬂ¶Ìn -Êﬂ+‚ tiﬂ¶+p tﬂ+—c:", type="password")
                            
                        if not api_key:
                            st.warning("G‹·n+≈ Vui l+¶ng cﬂ¶—u h+ºnh API Key hoﬂ¶+c nhﬂ¶°p v+·o +¶ trﬂ+Êng b+¨n tr+¨n -Êﬂ+‚ sﬂ+° dﬂ+—ng AI.")
                        else:
                            if st.button("=ÉˆÏ CHﬂ¶·Y AI QU+ÎT -…ﬂ+ˇ PHﬂ+™ (GEMINI)", type="primary"):
                                with st.spinner("=É∫· AI -Êang -Êﬂ+Ïc JD v+· suy luﬂ¶°n c+¶ng viﬂ+Ác... (C+¶ thﬂ+‚ mﬂ¶—t 5-10 gi+Ûy)"):
                                    try:
                                        import google.generativeai as genai
                                        genai.configure(api_key=api_key, transport='rest')
                                        
                                        # Tﬂ+¶ -Êﬂ+÷ng d+¶ model khﬂ¶˙ dﬂ+—ng cho API Key n+·y
                                        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                                        model_name = 'gemini-3.6-flash'
                                        if 'models/gemini-3.6-flash' in valid_models:
                                            model_name = 'gemini-3.6-flash'
                                        elif 'models/gemini-1.5-flash' in valid_models:
                                            model_name = 'gemini-1.5-flash'
                                        elif 'models/gemini-pro' in valid_models:
                                            model_name = 'gemini-pro'
                                        elif valid_models:
                                            # Tr+Ình chﬂ+Ïn c+Ìc model c+¨ hoﬂ¶+c bﬂ+Ô deprecate nﬂ¶¶m ﬂ+É -Êﬂ¶∫u danh s+Ìch
                                            model_name = valid_models[-1].replace('models/', '')
                                            
                                        model = genai.GenerativeModel(model_name)
                                        
                                        # R+¶t gﬂ+Ïn danh s+Ìch c+¶ng viﬂ+Ác
                                        tasks_list = "\n".join([f"- {row['TenCongViec']}" for _, row in ai_tasks.iterrows()])
                                    
                                        prompt = f"""
                                        -…+¶ng vai mﬂ+÷t Gi+Ìm -Êﬂ+Êc nh+Ûn sﬂ+¶ cﬂ+¶c kﬂ+¶ tinh tﬂ¶+. 
                                        D¶¶ﬂ+¢i -Ê+Ûy l+· Bﬂ¶˙n M+¶ tﬂ¶˙ c+¶ng viﬂ+Ác (JD) cﬂ+∫a nh+Ûn vi+¨n {ai_person}:
                                    
                                        [Bﬂ¶ÛN M+ˆ Tﬂ¶Û C+ˆNG VIﬂ+ÂC]
                                        {jd_source}
                                        [Kﬂ¶+T TH+‹C JD]
                                    
                                        V+· -Ê+Ûy l+· danh s+Ìch c+¶ng viﬂ+Ác hﬂ+Ï thﬂ+¶c hiﬂ+Án trong th+Ìng:
                                        {tasks_list}
                                    
                                        NHIﬂ+ÂM Vﬂ+Ò Cﬂ+™A Bﬂ¶·N:
                                        1. -…ﬂ+Êi chiﬂ¶+u Tﬂ+¨NG c+¶ng viﬂ+Ác xem n+¶ c+¶ KHﬂ+‹P vﬂ+¢i chuy+¨n m+¶n quy -Êﬂ+Ônh trong JD kh+¶ng. 
                                        (L¶¶u ++: T+¨n c+¶ng viﬂ+Ác thﬂ+¶c tﬂ¶+ c+¶ thﬂ+‚ chi tiﬂ¶+t v+· tﬂ+Ω ngﬂ+ª kh+Ìc biﬂ+Át so vﬂ+¢i JD v-‚n xu+¶i. H+˙y d+¶ng t¶¶ duy suy luﬂ¶°n vﬂ+¸ bﬂ¶˙n chﬂ¶—t v+· mﬂ+—c -Ê+°ch -Êﬂ+‚ ph+Ìn -Êo+Ìn).
                                        2. Nﬂ¶+u khﬂ+¢p, giﬂ¶˙i th+°ch v+º n+¶ phﬂ+—c vﬂ+— cho mﬂ+—c n+·o trong JD. Nﬂ¶+u ngo+·i JD, ghi r+¶ l+· c+¶ng viﬂ+Ác ph+Ìt sinh.
                                        3. Format kﬂ¶+t quﬂ¶˙ -Êﬂ¶∫u ra th+·nh -Ê+¶ng -Êﬂ+Ônh dﬂ¶Ìng chuﬂ+˘i JSON th+¶ nh¶¶ sau (chﬂ+Î trﬂ¶˙ vﬂ+¸ JSON, kh+¶ng chﬂ+¨a dﬂ¶—u tick markdown ```json):
                                        {{
                                            "ty_le_khop": <sﬂ+Ê nguy+¨n tﬂ+Ω 0-100, v+° dﬂ+— 80>,
                                            "chi_tiet": [
                                                {{
                                                    "ten_cong_viec": "<T+¨n c+¶ng viﬂ+Ác y nguy+¨n trong danh s+Ìch>",
                                                    "phan_loai": "<Chﬂ+Î -Êiﬂ+¸n 'Khﬂ+¢p JD' hoﬂ¶+c 'Ngo+·i JD'>",
                                                    "nhan_xet": "<Ph+Ûn t+°ch ngﬂ¶ªn gﬂ+Ïn 1-2 c+Ûu>"
                                                }}, ...
                                            ]
                                        }}
                                        """
                                    
                                        import hashlib
                                        import os
                                        
                                        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
                                        cache_file = f".ai_cache_{prompt_hash}.txt"
                                        
                                        if os.path.exists(cache_file):
                                            with open(cache_file, "r", encoding="utf-8") as f:
                                                raw_text = f.read()
                                        else:
                                            max_retries = 3
                                            for attempt in range(max_retries):
                                                try:
                                                    response = model.generate_content(
                                                        prompt, 
                                                        generation_config={"temperature": 0.0},
                                                        request_options={"timeout": 60.0}
                                                    )
                                                    raw_text = response.text
                                                    break
                                                except Exception as api_err:
                                                    if attempt == max_retries - 1:
                                                        raise api_err
                                                    import time
                                                    time.sleep(4 * (attempt + 1))
                                                    
                                            if raw_text:
                                                with open(cache_file, "w", encoding="utf-8") as f:
                                                    f.write(raw_text)
                                    
                                        import re
                                        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                                        if json_match:
                                            res_json = json.loads(json_match.group())
                                        
                                            st.markdown("### =ÉÙË Kﬂ¶+T QUﬂ¶Û -…ﬂ+…I CHIﬂ¶+U JD V+« C+ˆNG VIﬂ+ÂC -…-ÈNG K+•")
                                        
                                            # Pie chart
                                            match_rate = res_json.get("ty_le_khop", 0)
                                            m_data = pd.DataFrame({
                                                "Ph+Ûn loﬂ¶Ìi": ["Khﬂ+¢p chuy+¨n m+¶n (JD)", "C+¶ng viﬂ+Ác ngo+·i JD"],
                                                "Tﬂ++ lﬂ+Á": [match_rate, 100 - match_rate]
                                            })
                                            fig = px.pie(m_data, values='Tﬂ++ lﬂ+Á', names='Ph+Ûn loﬂ¶Ìi', color='Ph+Ûn loﬂ¶Ìi',
                                                         color_discrete_map={"Khﬂ+¢p chuy+¨n m+¶n (JD)": "#22c55e", "C+¶ng viﬂ+Ác ngo+·i JD": "#f97316"},
                                                         title=f"-…ﬂ+÷ phﬂ+∫ JD Th+Ìng {ai_month}", hole=0.4)
                                            st.plotly_chart(fig, use_container_width=True)
                                        
                                            # Table
                                            res_df = pd.DataFrame(res_json.get("chi_tiet", []))
                                            if not res_df.empty:
                                                # Format columns for display
                                                res_df = res_df.rename(columns={
                                                    "ten_cong_viec": "C+¶ng viﬂ+Ác",
                                                    "phan_loai": "-…+Ình gi+Ì cﬂ+∫a AI",
                                                    "nhan_xet": "Nhﬂ¶°n x+¨t chi tiﬂ¶+t"
                                                })
                                                res_df.insert(0, 'STT', range(1, len(res_df) + 1))
                                            
                                                def color_ph(val):
                                                    if "Khﬂ+¢p" in str(val):
                                                        return 'color: #166534; background-color: #dcfce7; font-weight: bold; border-radius: 4px;'
                                                    else:
                                                        return 'color: #9a3412; background-color: #ffedd5; font-weight: bold; border-radius: 4px;'
                                                    
                                                st.dataframe(res_df.style.map(color_ph, subset=['-…+Ình gi+Ì cﬂ+∫a AI']), use_container_width=True, hide_index=True)
                                        else:
                                            st.error("Lﬂ+˘i: AI trﬂ¶˙ vﬂ+¸ kﬂ¶+t quﬂ¶˙ kh+¶ng mong muﬂ+Ên. Vui l+¶ng thﬂ+° lﬂ¶Ìi.")
                                            with st.expander("Dﬂ+ª liﬂ+Áu th+¶ AI trﬂ¶˙ vﬂ+¸"):
                                                st.write(raw_text)
                                        
                                    except ImportError:
                                        st.error("Ch¶¶a c+·i -Êﬂ¶+t th¶¶ viﬂ+Án `google-generativeai`. Vui l+¶ng chﬂ¶Ìy `pip install google-generativeai`.")
                                    except Exception as e:
                                        st.error(f"Lﬂ+˘i hﬂ+Á thﬂ+Êng khi gﬂ+Ïi AI: {e}")

elif menu == "G‹÷n+≈ Quﬂ¶˙n L++ Cﬂ¶—u H+ºnh":
    st.markdown("### G‹÷n+≈ Quﬂ¶˙n L++ Cﬂ¶—u H+ºnh Hﬂ+Á Thﬂ+Êng")
    
    tab_proj, tab_dept, tab_gsheets = st.tabs(["=ÉÙ¸ Quﬂ¶˙n l++ Dﬂ+¶ +Ìn", "=É≈Û Quﬂ¶˙n l++ Ph+¶ng ban", "=ÉÙË -…ﬂ+Ùng bﬂ+÷ Google Sheets"])
    
    with tab_proj:
        if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
            st.warning("G‹·n+≈ Vui l+¶ng chﬂ+Ïn cﬂ+— thﬂ+‚ mﬂ+÷t **C+¶ng ty / -…¶Ìn vﬂ+Ô** ﬂ+É menu b+¨n tr+Ìi -Êﬂ+‚ tiﬂ¶+n h+·nh cﬂ¶—u h+ºnh (Kh+¶ng +Ìp dﬂ+—ng cho 'Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô').")
        else:
            st.info(f"-…ang cﬂ¶—u h+ºnh dﬂ+ª liﬂ+Áu cho: **{selected_company}**")
            # Load current company's config
            comp_config = config.get("companies", {}).get(selected_company, {})
            comp_projects_by_cat = comp_config.get("projects_by_category", {})
            
            st.markdown(f"#### Quﬂ¶˙n l++ Danh mﬂ+—c Dﬂ+¶ +Ìn - {selected_company}")
            
            cats = list(comp_projects_by_cat.keys())
            if not cats:
                st.info("Ch¶¶a c+¶ l-¨nh vﬂ+¶c dﬂ+¶ +Ìn n+·o. Vui l+¶ng cﬂ¶°p nhﬂ¶°t cﬂ¶—u tr+¶c JSON hoﬂ¶+c th+¨m mﬂ+¢i.")
            else:
                sel_cat = st.selectbox("Chﬂ+Ïn L-¨nh vﬂ+¶c dﬂ+¶ +Ìn", cats)
                projs_in_cat = comp_projects_by_cat.get(sel_cat, [])
                
                st.markdown(f"**Danh s+Ìch dﬂ+¶ +Ìn hiﬂ+Án tﬂ¶Ìi trong [{sel_cat}]:**")
                st.write(", ".join(projs_in_cat) if projs_in_cat else "Ch¶¶a c+¶ dﬂ+¶ +Ìn n+·o")
                
                st.markdown("---")
                
                col_add, col_edit, col_del = st.columns(3)
                
                with col_add:
                    st.markdown("**GPÚ Th+¨m dﬂ+¶ +Ìn mﬂ+¢i**")
                    new_proj_name = st.text_input("T+¨n dﬂ+¶ +Ìn mﬂ+¢i", key="admin_add_proj")
                    if st.button("Th+¨m dﬂ+¶ +Ìn", type="primary"):
                        if new_proj_name.strip():
                            if new_proj_name.strip() not in projs_in_cat:
                                config["companies"][selected_company]["projects_by_category"][sel_cat].append(new_proj_name.strip())
                                if save_config(config):
                                    st.success(f"-…+˙ th+¨m dﬂ+¶ +Ìn: {new_proj_name}")
                                    
                                    st.rerun()
                            else:
                                st.error("Dﬂ+¶ +Ìn -Ê+˙ tﬂ+Ùn tﬂ¶Ìi!")
                        else:
                            st.error("T+¨n dﬂ+¶ +Ìn kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                            
                with col_edit:
                    st.markdown("**G£≈n+≈ -…ﬂ+Úi t+¨n dﬂ+¶ +Ìn**")
                    if projs_in_cat:
                        proj_to_edit = st.selectbox("Chﬂ+Ïn dﬂ+¶ +Ìn cﬂ¶∫n sﬂ+°a", projs_in_cat, key="admin_edit_proj_sel")
                        edited_proj_name = st.text_input("T+¨n dﬂ+¶ +Ìn mﬂ+¢i", value=proj_to_edit, key="admin_edit_proj_val")
                        if st.button("L¶¶u -Êﬂ+Úi t+¨n"):
                            if edited_proj_name.strip():
                                idx = config["companies"][selected_company]["projects_by_category"][sel_cat].index(proj_to_edit)
                                config["companies"][selected_company]["projects_by_category"][sel_cat][idx] = edited_proj_name.strip()
                                if save_config(config):
                                    st.success(f"-…+˙ -Êﬂ+Úi t+¨n th+·nh: {edited_proj_name}")
                                    
                                    st.rerun()
                            else:
                                st.error("T+¨n mﬂ+¢i kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                    else:
                        st.write("Kh+¶ng c+¶ dﬂ+¶ +Ìn -Êﬂ+‚ sﬂ+°a.")
                        
                with col_del:
                    st.markdown("**=É˘Ên+≈ X+¶a dﬂ+¶ +Ìn**")
                    if projs_in_cat:
                        proj_to_del = st.selectbox("Chﬂ+Ïn dﬂ+¶ +Ìn cﬂ¶∫n x+¶a", projs_in_cat, key="admin_del_proj_sel")
                        if st.button("X+Ìc nhﬂ¶°n x+¶a dﬂ+¶ +Ìn", type="secondary"):
                            config["companies"][selected_company]["projects_by_category"][sel_cat].remove(proj_to_del)
                            if save_config(config):
                                st.success(f"-…+˙ x+¶a dﬂ+¶ +Ìn: {proj_to_del}")
                                
                                st.rerun()
                    else:
                        st.write("Kh+¶ng c+¶ dﬂ+¶ +Ìn -Êﬂ+‚ x+¶a.")
    
    with tab_dept:
        if selected_company == "Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô":
            st.warning("G‹·n+≈ Vui l+¶ng chﬂ+Ïn cﬂ+— thﬂ+‚ mﬂ+÷t **C+¶ng ty / -…¶Ìn vﬂ+Ô** ﬂ+É menu b+¨n tr+Ìi -Êﬂ+‚ tiﬂ¶+n h+·nh cﬂ¶—u h+ºnh (Kh+¶ng +Ìp dﬂ+—ng cho 'Tﬂ¶—t cﬂ¶˙ -Ê¶Ìn vﬂ+Ô').")
        else:
            comp_config = config.get("companies", {}).get(selected_company, {})
            comp_depts = comp_config.get("departments", [])
            comp_personnel = comp_config.get("personnel_by_department", {})
            
            st.markdown(f"#### Quﬂ¶˙n l++ Danh s+Ìch Ph+¶ng ban - {selected_company}")
            st.markdown(f"**Danh s+Ìch ph+¶ng ban hiﬂ+Án tﬂ¶Ìi ({len(comp_depts)} ph+¶ng ban):**")
            st.write(", ".join(comp_depts) if comp_depts else "Ch¶¶a c+¶ ph+¶ng ban n+·o")
            
            st.markdown("---")
            
            col_d_add, col_d_edit, col_d_del = st.columns(3)
            
            with col_d_add:
                st.markdown("**GPÚ Th+¨m ph+¶ng ban mﬂ+¢i**")
                new_dept_name = st.text_input("T+¨n ph+¶ng ban mﬂ+¢i", key="admin_add_dept")
                if st.button("Th+¨m ph+¶ng ban", type="primary"):
                    if new_dept_name.strip():
                        if new_dept_name.strip() not in comp_depts:
                            config["companies"][selected_company]["departments"].append(new_dept_name.strip())
                            if save_config(config):
                                st.success(f"-…+˙ th+¨m ph+¶ng ban: {new_dept_name}")
                                
                                st.rerun()
                        else:
                            st.error("Ph+¶ng ban -Ê+˙ tﬂ+Ùn tﬂ¶Ìi!")
                    else:
                        st.error("T+¨n kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                        
            with col_d_edit:
                st.markdown("**G£≈n+≈ -…ﬂ+Úi t+¨n ph+¶ng ban**")
                if comp_depts:
                    dept_to_edit = st.selectbox("Chﬂ+Ïn ph+¶ng ban cﬂ¶∫n sﬂ+°a", comp_depts, key="admin_edit_dept_sel")
                    edited_dept_name = st.text_input("T+¨n ph+¶ng ban mﬂ+¢i", value=dept_to_edit, key="admin_edit_dept_val")
                    if st.button("L¶¶u -Êﬂ+Úi t+¨n ph+¶ng"):
                        if edited_dept_name.strip():
                            idx = config["companies"][selected_company]["departments"].index(dept_to_edit)
                            config["companies"][selected_company]["departments"][idx] = edited_dept_name.strip()
                            # Update personnel keys as well
                            if dept_to_edit in config["companies"][selected_company]["personnel_by_department"]:
                                config["companies"][selected_company]["personnel_by_department"][edited_dept_name.strip()] = config["companies"][selected_company]["personnel_by_department"].pop(dept_to_edit, [])
                            if save_config(config):
                                st.success(f"-…+˙ -Êﬂ+Úi t+¨n th+·nh: {edited_dept_name}")
                                
                                st.rerun()
                        else:
                            st.error("T+¨n mﬂ+¢i kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                else:
                    st.write("Kh+¶ng c+¶ ph+¶ng ban -Êﬂ+‚ sﬂ+°a.")
                    
            with col_d_del:
                st.markdown("**=É˘Ên+≈ X+¶a ph+¶ng ban**")
                if comp_depts:
                    dept_to_del = st.selectbox("Chﬂ+Ïn ph+¶ng ban cﬂ¶∫n x+¶a", comp_depts, key="admin_del_dept_sel")
                    if st.button("X+Ìc nhﬂ¶°n x+¶a ph+¶ng", type="secondary"):
                        config["companies"][selected_company]["departments"].remove(dept_to_del)
                        # Remove personnel mapping too
                        config["companies"][selected_company]["personnel_by_department"].pop(dept_to_del, None)
                        if save_config(config):
                            st.success(f"-…+˙ x+¶a ph+¶ng ban: {dept_to_del}")
                            
                            st.rerun()
                else:
                    st.write("Kh+¶ng c+¶ ph+¶ng ban -Êﬂ+‚ x+¶a.")
    
            st.markdown("---")
            st.markdown(f"#### =ÉÊ— Quﬂ¶˙n l++ Nh+Ûn sﬂ+¶ theo Ph+¶ng ban - {selected_company}")
            
            if comp_depts:
                sel_dept_p = st.selectbox("Chﬂ+Ïn ph+¶ng ban -Êﬂ+‚ quﬂ¶˙n l++ nh+Ûn sﬂ+¶", comp_depts, key="admin_sel_dept_p")
                    
                # Load personnel list
                current_p_list = comp_personnel.get(sel_dept_p, [])
                
                st.markdown(f"**Danh s+Ìch nh+Ûn sﬂ+¶ thuﬂ+÷c [{sel_dept_p}] ({len(current_p_list)} ng¶¶ﬂ+•i):**")
                st.write(", ".join(current_p_list) if current_p_list else "Ch¶¶a c+¶ nh+Ûn sﬂ+¶ n+·o")
                
                st.markdown("---")
                
                col_p_add, col_p_edit, col_p_del = st.columns(3)
                
                with col_p_add:
                    st.markdown("**GPÚ Th+¨m nh+Ûn sﬂ+¶ mﬂ+¢i**")
                    new_p_name = st.text_input("T+¨n nh+Ûn sﬂ+¶ mﬂ+¢i", key="admin_add_p_name")
                    if st.button("Th+¨m nh+Ûn sﬂ+¶", type="primary", key="btn_admin_add_p"):
                        if new_p_name.strip():
                            if new_p_name.strip() not in current_p_list:
                                if sel_dept_p not in config["companies"][selected_company]["personnel_by_department"]:
                                    config["companies"][selected_company]["personnel_by_department"][sel_dept_p] = []
                                config["companies"][selected_company]["personnel_by_department"][sel_dept_p].append(new_p_name.strip())
                                if save_config(config):
                                    st.success(f"-…+˙ th+¨m nh+Ûn sﬂ+¶: {new_p_name.strip()}")
                                    
                                    st.rerun()
                            else:
                                st.error("Nh+Ûn sﬂ+¶ -Ê+˙ tﬂ+Ùn tﬂ¶Ìi trong ph+¶ng ban n+·y!")
                        else:
                            st.error("T+¨n nh+Ûn sﬂ+¶ kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                            
                with col_p_edit:
                    st.markdown("**G£≈n+≈ Sﬂ+°a t+¨n nh+Ûn sﬂ+¶**")
                    if current_p_list:
                        p_to_edit = st.selectbox("Chﬂ+Ïn nh+Ûn sﬂ+¶ cﬂ¶∫n sﬂ+°a", current_p_list, key="admin_edit_p_sel")
                        edited_p_name = st.text_input("T+¨n nh+Ûn sﬂ+¶ mﬂ+¢i", value=p_to_edit, key="admin_edit_p_val")
                        if st.button("L¶¶u thay -Êﬂ+Úi", key="btn_admin_edit_p"):
                            if edited_p_name.strip():
                                if edited_p_name.strip() not in current_p_list or edited_p_name.strip() == p_to_edit:
                                    idx = current_p_list.index(p_to_edit)
                                    config["companies"][selected_company]["personnel_by_department"][sel_dept_p][idx] = edited_p_name.strip()
                                    if save_config(config):
                                        st.success(f"-…+˙ cﬂ¶°p nhﬂ¶°t t+¨n nh+Ûn sﬂ+¶ th+·nh: {edited_p_name.strip()}")
                                        
                                        st.rerun()
                                else:
                                    st.error("T+¨n mﬂ+¢i -Ê+˙ tﬂ+Ùn tﬂ¶Ìi trong ph+¶ng ban n+·y!")
                            else:
                                st.error("T+¨n mﬂ+¢i kh+¶ng -Ê¶¶ﬂ+˙c -Êﬂ+‚ trﬂ+Êng!")
                    else:
                        st.write("Kh+¶ng c+¶ nh+Ûn sﬂ+¶ -Êﬂ+‚ sﬂ+°a.")
                        
                with col_p_del:
                    st.markdown("**=É˘Ên+≈ X+¶a nh+Ûn sﬂ+¶**")
                    if current_p_list:
                        p_to_del = st.selectbox("Chﬂ+Ïn nh+Ûn sﬂ+¶ cﬂ¶∫n x+¶a", current_p_list, key="admin_del_p_sel")
                        if st.button("X+Ìc nhﬂ¶°n x+¶a", type="secondary", key="btn_admin_del_p"):
                            config["companies"][selected_company]["personnel_by_department"][sel_dept_p].remove(p_to_del)
                            if save_config(config):
                                st.success(f"-…+˙ x+¶a nh+Ûn sﬂ+¶: {p_to_del}")
                                
                                st.rerun()
                    else:
                        st.write("Kh+¶ng c+¶ nh+Ûn sﬂ+¶ -Êﬂ+‚ x+¶a.")
            else:
                st.warning("Vui l+¶ng tﬂ¶Ìo +°t nhﬂ¶—t mﬂ+÷t ph+¶ng ban tr¶¶ﬂ+¢c khi cﬂ¶—u h+ºnh nh+Ûn sﬂ+¶.")

    with tab_gsheets:
        st.markdown("#### =ÉÙË Cﬂ¶—u h+ºnh kﬂ¶+t nﬂ+Êi Google Sheets")
        if is_gsheets_configured():
            st.success("=ÉƒÎ Hﬂ+Á thﬂ+Êng -Ê+˙ kﬂ¶+t nﬂ+Êi th+·nh c+¶ng vﬂ+¢i Google Sheets! Mﬂ+Ïi thay -Êﬂ+Úi dﬂ+ª liﬂ+Áu sﬂ¶+ -Ê¶¶ﬂ+˙c tﬂ+¶ -Êﬂ+÷ng -Êﬂ+Ùng bﬂ+÷ thﬂ+•i gian thﬂ+¶c.")
            try:
                st.info(f"**Spreadsheet URL:** `{st.secrets['connections']['gsheets']['spreadsheet']}`")
            except Exception:
                pass
        else:
            st.warning("G‹·n+≈ Hiﬂ+Án tﬂ¶Ìi hﬂ+Á thﬂ+Êng -Êang hoﬂ¶Ìt -Êﬂ+÷ng ﬂ+É chﬂ¶+ -Êﬂ+÷ ngoﬂ¶Ìi tuyﬂ¶+n (Offline) bﬂ¶¶ng file Excel cﬂ+—c bﬂ+÷.")
            
        st.markdown("""
        ### =ÉÙ• H¶¶ﬂ+¢ng dﬂ¶Ωn kﬂ¶+t nﬂ+Êi Google Sheets tr+¨n Streamlit Cloud
        -…ﬂ+‚ -Êﬂ+Ùng bﬂ+÷ dﬂ+ª liﬂ+Áu trﬂ+¶c tuyﬂ¶+n, vui l+¶ng thﬂ+¶c hiﬂ+Án c+Ìc b¶¶ﬂ+¢c sau:
        
        1. **Tﬂ¶Ìo Google Sheet**: Tﬂ¶Ìo mﬂ+÷t bﬂ¶˙ng t+°nh Google Sheets mﬂ+¢i. -…ﬂ¶˙m bﬂ¶˙o sheet -Êﬂ¶∫u ti+¨n c+¶ t+¨n l+· `Sheet1`.
        2. **-…ﬂ+Ônh cﬂ¶—u h+ºnh cﬂ+÷t mﬂ¶Ωu**: Bﬂ¶Ìn c+¶ thﬂ+‚ tﬂ¶˙i file Excel hiﬂ+Án tﬂ¶Ìi tﬂ+Ω sidebar xuﬂ+Êng v+· copy cﬂ¶—u tr+¶c cﬂ+÷t sang Google Sheets. C+Ìc cﬂ+÷t gﬂ+Ùm:
           `ID`, `DonVi`, `PhongBan`, `NguoiChuTri`, `TenDuAn`, `MocTienDo`, `SanPhamBanGiao`, `TenCongViec`, `PhanLoaiChiSo`, `NgayBatDau`, `Deadline`, `DoUuTien`, `PhanTramHoanThanh`, `TrangThai`, `LinkKetQua`, `GiaiTrinhDeXuat`, `NgayCapNhat`
        3. **Chia sﬂ¶+ quyﬂ+¸n chﬂ+Înh sﬂ+°a**: Chia sﬂ¶+ Google Sheet -Ê+¶ vﬂ+¢i t+·i khoﬂ¶˙n **Google Service Account** cﬂ+∫a bﬂ¶Ìn (cﬂ¶—p quyﬂ+¸n **Editor**).
        4. **Cﬂ¶—u h+ºnh Secrets tr+¨n Streamlit Cloud**:
           - Truy cﬂ¶°p Dashboard cﬂ+∫a Streamlit Cloud -> V+·o ﬂ+¨ng dﬂ+—ng -> Chﬂ+Ïn **Settings** -> **Secrets**.
           - Nhﬂ¶°p th+¶ng tin cﬂ¶—u h+ºnh Service Account theo -Êﬂ+Ônh dﬂ¶Ìng sau:
           ```toml
           [connections.gsheets]
           spreadsheet = "https://docs.google.com/spreadsheets/d/your-spreadsheet-id"
           type = "service_account"
           project_id = "your-project-id"
           private_key_id = "your-private-key-id"
           private_key = "-----BEGIN PRIVATE KEY-----\\nyour-private-key-details\\n-----END PRIVATE KEY-----\\n"
           client_email = "your-service-account-email@your-project.iam.gserviceaccount.com"
           client_id = "your-client-id"
           auth_uri = "https://accounts.google.com/o/oauth2/auth"
           token_uri = "https://oauth2.googleapis.com/token"
           auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
           client_x509_cert_url = "https://www.googleapis.com/workspace/3pid/cert"
           ```
        5. **Khﬂ+Éi -Êﬂ+÷ng lﬂ¶Ìi (Reboot) app**: L¶¶u lﬂ¶Ìi Secrets, Streamlit sﬂ¶+ tﬂ+¶ -Êﬂ+÷ng -Êﬂ+Ùng bﬂ+÷ v+· nﬂ¶Ìp dﬂ+ª liﬂ+Áu tﬂ+Ω Google Sheets.
        """)

# ----------------- 6. Sﬂ+ˆ TAY H¶ªﬂ+‹NG Dﬂ¶¨N -----------------
elif menu == "=ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn":
    st.markdown("## =ÉÙ˚ Sﬂ+Ú tay H¶¶ﬂ+¢ng dﬂ¶Ωn sﬂ+° dﬂ+—ng phﬂ¶∫n mﬂ+¸m KPI")
    st.markdown("Chﬂ+Ïn vai tr+¶ cﬂ+∫a bﬂ¶Ìn -Êﬂ+‚ xem h¶¶ﬂ+¢ng dﬂ¶Ωn chi tiﬂ¶+t:")
    
    tab_nv, tab_ql, tab_tc = st.tabs(["=ÉÊøG«Ï=É∆+ H¶¶ﬂ+¢ng dﬂ¶Ωn Nh+Ûn vi+¨n", "=ÉÊˆ H¶¶ﬂ+¢ng dﬂ¶Ωn Quﬂ¶˙n l++", "=ÉÓÉ Ti+¨u ch+° -…+Ình gi+Ì & Xﬂ¶+p loﬂ¶Ìi"])
    
    with tab_nv:
        st.info("""
        **1n+≈G‚˙ -…-‚ng k++ c+¶ng viﬂ+Ác (-…ﬂ¶∫u th+Ìng)**
        - =ÉÚ∆ **Thﬂ+•i gian:** Tﬂ+Ω ng+·y 30 th+Ìng tr¶¶ﬂ+¢c -Êﬂ¶+n ng+·y 3 th+Ìng n+·y.
        - =É˚¶n+≈ **Thao t+Ìc:** V+·o mﬂ+—c **Th+¨m / Cﬂ¶°p nhﬂ¶°t c+¶ng viﬂ+Ác**.
        - =ÉÙ• **Nﬂ+÷i dung:** Tﬂ+¶ khai b+Ìo c+Ìc -Êﬂ¶∫u viﬂ+Ác ch+°nh trong th+Ìng. Hﬂ+Á thﬂ+Êng sﬂ¶+ tﬂ+¶ -Êﬂ+÷ng t+°nh to+Ìn v+· chia -Êﬂ+¸u tﬂ++ trﬂ+Ïng KPI cho tﬂ¶—t cﬂ¶˙ c+Ìc c+¶ng viﬂ+Ác cﬂ+∫a bﬂ¶Ìn.
        """)
        
        st.success("""
        **2n+≈G‚˙ B+Ìo c+Ìo tiﬂ¶+n -Êﬂ+÷ v+· Ho+·n th+·nh**
        - =É˚¶n+≈ Khi thﬂ+¶c hiﬂ+Án xong c+¶ng viﬂ+Ác, v+·o mﬂ+—c **Th+¨m / Cﬂ¶°p nhﬂ¶°t c+¶ng viﬂ+Ác**, -Ê+Ình dﬂ¶—u tick v+·o +¶ **GˇÊn+≈ C+¶ng viﬂ+Ác -Ê+˙ ho+·n th+·nh**.
        - =ÉÙÓ **L¶¶u ++ quan trﬂ+Ïng:** Bﬂ¶Ìn cﬂ¶∫n d+Ìn k+øm Link minh chﬂ+¨ng kﬂ¶+t quﬂ¶˙ (tﬂ+Ω Google Drive, OneDrive...) hoﬂ¶+c ghi t+¨n/sﬂ+Ê hiﬂ+Áu v-‚n bﬂ¶˙n v+·o +¶ khai b+Ìo kﬂ¶+t quﬂ¶˙.
        """)
        
        st.warning("""
        **3n+≈G‚˙ Xﬂ+° l++ Trﬂ+‡ hﬂ¶Ìn / C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc**
        - Nﬂ¶+u rﬂ+∫i ro trﬂ+‡ hﬂ¶Ìn, -Êﬂ+Úi trﬂ¶Ìng th+Ìi th+·nh **C+¶ v¶¶ﬂ+¢ng mﬂ¶ªc** v+· ghi r+¶ l++ do tﬂ¶Ìi +¶ *Giﬂ¶˙i tr+ºnh / -…ﬂ+¸ xuﬂ¶—t*.
        - =ÉÓÏ **Do kh+Ìch quan**: Hﬂ+Á thﬂ+Êng gﬂ+°i y+¨u cﬂ¶∫u -Êﬂ+‚ Quﬂ¶˙n l++ xem x+¨t l++ do v+· -Ê+Ình gi+Ì lﬂ¶Ìi mﬂ+¨c -Êiﬂ+‚m (50%, 80%, 90%...).
        - =ÉÓ∫n+≈ **Do chﬂ+∫ quan**: C+¶ng viﬂ+Ác bﬂ+Ô t+°nh l+· ch¶¶a ho+·n th+·nh v+· nhﬂ¶°n 0 -Êiﬂ+‚m KPI.
        """)
        
        st.error("""
        **4n+≈G‚˙ Theo d+¶i c+¶ng viﬂ+Ác h+·ng ng+·y**
        - =É˚¶n+≈ V+·o mﬂ+—c **Bﬂ¶˙ng theo d+¶i tiﬂ¶+n -Êﬂ+÷ c+¶ng viﬂ+Ác**.
        - Xem thﬂ¶+ **C+ˆNG VIﬂ+ÂC Tﬂ+‹I Hﬂ¶·N** -Êﬂ+‚ biﬂ¶+t viﬂ+Ác n+·o sﬂ¶ªp -Êﬂ¶+n hﬂ¶Ìn (m+·u v+·ng) hoﬂ¶+c -Ê+˙ trﬂ+‡ hﬂ¶Ìn (m+·u -Êﬂ+≈) -Êﬂ+‚ ¶¶u ti+¨n xﬂ+° l++.
        """)
        
    with tab_ql:
        st.success("""
        **1n+≈G‚˙ Xem x+¨t v+· -…+Ình gi+Ì l++ do Kh+Ìch quan**
        - =É˚¶n+≈ V+·o mﬂ+—c **G£‡ Duyﬂ+Át viﬂ+Ác Kh+Ìch quan**.
        - Hﬂ+Á thﬂ+Êng liﬂ+Át k+¨ c+Ìc c+¶ng viﬂ+Ác nh+Ûn vi+¨n b+Ìo c+Ìo trﬂ+‡ hﬂ¶Ìn vﬂ+¢i l++ do **Kh+Ìch quan**.
        - Bﬂ¶Ìn xem x+¨t giﬂ¶˙i tr+ºnh, click trﬂ+¶c tiﬂ¶+p v+·o +¶ *Mﬂ+¨c -Êﬂ+÷ KPI ghi nhﬂ¶°n* -Êﬂ+‚ chﬂ+Ïn -Êiﬂ+‚m ph+¶ hﬂ+˙p (Miﬂ+‡n trﬂ+Ω, 50%, 80%, 90%...).
        - Nhﬂ¶—n **=É∆+ L¶¶u to+·n bﬂ+÷ ph+¨ duyﬂ+Át** ﬂ+É cuﬂ+Êi danh s+Ìch.
        """)
        
        st.info("""
        **2n+≈G‚˙ Xem B+Ìo c+Ìo Xﬂ¶+p loﬂ¶Ìi KPI (Ng+·y 1-3 -Êﬂ¶∫u th+Ìng)**
        - =ÉÚ∆ **Thﬂ+•i gian:** Tﬂ+Ω ng+·y 1 -Êﬂ¶+n ng+·y 3 h+·ng th+Ìng.
        - =Éƒª **Mﬂ+—c -Ê+°ch:** X+Ìc nhﬂ¶°n -Êiﬂ+‚m sﬂ+Ê KPI cﬂ+∫a th+Ìng tr¶¶ﬂ+¢c -Êﬂ+‚ Ph+¶ng HCNS l¶¶u kﬂ¶+t quﬂ¶˙.
        - Xem biﬂ+‚u -Êﬂ+Ù tﬂ+Úng quan v+· Bﬂ¶˙ng dﬂ+ª liﬂ+Áu tﬂ+¶ -Êﬂ+÷ng Xﬂ¶+p loﬂ¶Ìi cho tﬂ+Ωng nh+Ûn sﬂ+¶.
        """)

    with tab_tc:
        st.info("""
        **=ÉÓÉ TI+ËU CH+Ï -…+¸NH GI+¸ V+« Xﬂ¶+P LOﬂ¶·I KPI**
        
        =É∫´ **1. C+¶ng thﬂ+¨c t+°nh -Êiﬂ+‚m KPI Tﬂ+Úng:**
        > :blue[**-…iﬂ+‚m KPI**] = (:green[**-…iﬂ+‚m trung b+ºnh c+¶ng viﬂ+Ác -…ﬂ+Ônh kﬂ+¶**] +˘ **70%**) + (:orange[**-…iﬂ+‚m trung b+ºnh c+¶ng viﬂ+Ác Giao ban**] +˘ **30%**) + :red[**-…iﬂ+‚m th¶¶ﬂ+Éng/phﬂ¶Ìt**]
        
        *(L¶¶u ++: Nﬂ¶+u kh+¶ng c+¶ c+¶ng viﬂ+Ác Giao ban, hﬂ+Á thﬂ+Êng sﬂ¶+ tﬂ+¶ -Êﬂ+÷ng -Êiﬂ+¸u chﬂ+Înh 100% trﬂ+Ïng sﬂ+Ê cho c+¶ng viﬂ+Ác -…ﬂ+Ônh kﬂ+¶).*
        
        =ÉÙË **2. Ph+Ûn loﬂ¶Ìi v+· Quy -Êﬂ+Úi -…iﬂ+‚m Xﬂ¶+p loﬂ¶Ìi:**
        - Tﬂ+Úng -Êiﬂ+‚m **> 100**: Xﬂ¶+p loﬂ¶Ìi **A\*** (Xuﬂ¶—t sﬂ¶ªc - > 100 -Êiﬂ+‚m): -…ﬂ¶Ìt mﬂ+¨c 110G«Ù120% l¶¶¶Ìng, nhﬂ¶¶m kh+°ch lﬂ+Á tinh thﬂ¶∫n l+·m viﬂ+Ác v¶¶ﬂ+˙t trﬂ+÷i.
        - Tﬂ+Úng -Êiﬂ+‚m **> 91**: Xﬂ¶+p loﬂ¶Ìi **A** (Xuﬂ¶—t sﬂ¶ªc)
        - Tﬂ+Úng -Êiﬂ+‚m **> 81**: Xﬂ¶+p loﬂ¶Ìi **B** (Tﬂ+Êt)
        - Tﬂ+Úng -Êiﬂ+‚m **> 71**: Xﬂ¶+p loﬂ¶Ìi **C** (Kh+Ì)
        - Tﬂ+Úng -Êiﬂ+‚m **<= 71**: Xﬂ¶+p loﬂ¶Ìi **D** (K+¨m)
        
        G‹˚n+≈ **3. Vﬂ+¸ -…iﬂ+‚m Th¶¶ﬂ+Éng / Phﬂ¶Ìt:**
        - **Cﬂ+÷ng -Êiﬂ+‚m (+):** +¸p dﬂ+—ng cho c+Ìc c+¶ng viﬂ+Ác ho+·n th+·nh xuﬂ¶—t sﬂ¶ªc v¶¶ﬂ+˙t tiﬂ¶+n -Êﬂ+÷, hoﬂ¶+c c+¶ s+Ìng kiﬂ¶+n mang lﬂ¶Ìi hiﬂ+Áu quﬂ¶˙ cao.
        - **Trﬂ+Ω -Êiﬂ+‚m (-):** +¸p dﬂ+—ng khi vi phﬂ¶Ìm nﬂ+÷i quy, chﬂ¶°m trﬂ+‡ b+Ìo c+Ìo, hoﬂ¶+c c+¶ sai s+¶t nghiﬂ+Áp vﬂ+— g+Ûy ﬂ¶˙nh h¶¶ﬂ+Éng.
        - *Quﬂ¶˙n l++ trﬂ+¶c tiﬂ¶+p hoﬂ¶+c HCNS sﬂ¶+ r+· so+Ìt v+· cﬂ¶°p nhﬂ¶°t quﬂ+¶ -Êiﬂ+‚m Th¶¶ﬂ+Éng/Phﬂ¶Ìt n+·y tr¶¶ﬂ+¢c thﬂ+•i -Êiﬂ+‚m chﬂ+Êt sﬂ+Ú cuﬂ+Êi th+Ìng.*
        """)

