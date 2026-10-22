import streamlit as st

# Force calendar header visible to fix caching issues


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
    st.error("Thư viện google-generativeai chưa được cài đặt. Vui lòng kiểm tra file requirements.txt.")

from datetime import datetime, date, timedelta

def calculate_time_progress(start_date, deadline_date, is_completed=False):
    """Tính % sức khỏe thời gian: Đang tốt (99), Sắp tới hạn (50), Trễ hạn (0)"""
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
            return 0.0  # Trễ hạn
        elif 0 <= days_left <= 3:
            return 50.0  # Sắp tới hạn
        else:
            return 99.0  # Còn nhiều hạn
    except Exception:
        return 0.0

from contextlib import contextmanager
import time

@contextmanager
def acquire_db_lock(timeout=10):
    # Supabase uses Postgres which has atomic upserts, no need for local locks that break in Cloud
    yield

def is_user_authenticated():
    return bool(
        st.session_state.get('is_admin_authenticated', False) or 
        st.session_state.get('is_manager_authenticated', False) or 
        st.session_state.get('is_personal_authenticated', False)
    )

def require_authentication():
    if not is_user_authenticated():
        st.markdown("""
            <div style="background-color: #ffffff; padding: 40px 30px; border-radius: 12px; border: 2px solid #e2e8f0; border-top: 5px solid #f97316; text-align: center; margin: 25px auto; max-width: 820px; box-shadow: 0 10px 25px rgba(30, 58, 138, 0.08);">
                <div style="width: 72px; height: 72px; background: #fff7ed; border: 2px solid #ffedd5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 34px;">
                    🔒
                </div>
                <h2 style="color: #1e3a8a !important; font-size: 26px !important; font-weight: 800 !important; margin-bottom: 12px !important; letter-spacing: -0.5px;">
                    YÊU CẦU ĐĂNG NHẬP HỆ THỐNG
                </h2>
                <p style="font-size: 16px; color: #334155 !important; max-width: 680px; margin: 0 auto 24px auto; line-height: 1.6;">
                    Để bảo mật dữ liệu <strong style="color: #1e3a8a;">Kế hoạch (KH)</strong>, <strong style="color: #1e3a8a;">Chỉ tiêu Dự án</strong> và <strong style="color: #1e3a8a;">Tiến độ công việc nội bộ</strong> của DMT Group, các thông tin chỉ được hiển thị sau khi bạn xác thực danh tính.
                </p>
                <div style="background-color: #f8fafc; border: 1.5px solid #cbd5e1; border-left: 5px solid #f97316; border-radius: 8px; padding: 20px 24px; text-align: left; max-width: 650px; margin: 0 auto;">
                    <p style="color: #c2410c !important; font-weight: 800 !important; margin-bottom: 12px !important; font-size: 16px;">
                        👉 Vui lòng đăng nhập tại thanh Menu bên trái (Sidebar):
                    </p>
                    <ul style="color: #0f172a !important; font-size: 15px !important; margin: 0; padding-left: 22px; line-height: 2;">
                        <li><strong style="color: #1e3a8a;">Nhân viên:</strong> Chọn <em>QUYỀN TRUY CẬP: Nhân viên</em> ➔ Chọn Phòng ban ➔ Chọn Tên của bạn ➔ Bấm <b style="color: #f97316;">Xác nhận Đăng nhập</b>.</li>
                        <li><strong style="color: #1e3a8a;">Quản lý:</strong> Chọn <i>QUYỀN TRUY CẬP: Quản lý</i> ➔ Chọn Phòng ban ➔ Chọn Tên Quản lý ➔ Nhập mật khẩu.</li>
                        <li><strong style="color: #1e3a8a;">HR / Toàn quyền:</strong> Chọn <i>QUYỀN TRUY CẬP: HR</i> ➔ Nhập mật khẩu quản trị HR.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.stop()

# Page config - Light Theme is handled natively by Streamlit's default settings


# Chống dịch tự động của Google (gây lỗi chính tả) và chuẩn hóa Font chữ tiếng Việt




# Standardized companies based on CIENCO, DMT Group, and DMT Marina documents
COMPANIES = {
    "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG": {},
    "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {},
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {}
}

# Department abbreviations mapping
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

DEFAULT_PERSONNEL = {
    "Hội đồng quản trị": ["Đặng Thanh Bình"],
    "HĐQT": ["Đặng Thanh Bình"],
    "Ban Lãnh đạo": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
    "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
    "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"],
    "HCNS": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"],
    "Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Lê Thị Hải"],
    "TCKT": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Lê Thị Hải"],
    "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Phan Thị Kim Cúc", "Trần Tin"],
    "KHĐT": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Phan Thị Kim Cúc", "Trần Tin"],
    "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],
    "CBĐT": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],
    "Ban Kỹ thuật": ["Nguyễn Văn Bồn"],
    "KT": ["Nguyễn Văn Bồn"],
    "Ban Đền bù Giải tỏa": ["Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "ĐBGT": ["Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Ban Dự án": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
    "DA": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
    "Xí nghiệp DTBD": ["Mai Văn Châu"],
    "XN DTBD": ["Mai Văn Châu"],
    "Sàn GDBĐS": ["Ngô Thị Tâm"],
}

def is_gsheets_configured():
    try:
        # Check if connections.gsheets exists in secrets
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return True
    except Exception:
        pass
    return False

import threading
import time

_SUPABASE_CLIENT_INSTANCE = None
_CLIENT_LOCK = threading.Lock()
_INSERT_TASK_LOCK = threading.RLock()

def execute_with_retry(query_func, max_retries=3, initial_delay=0.25):
    """Thực thi thao tác Supabase với cơ chế retry tự động theo cấp số nhân khi mạng lag / nghẽn kết nối"""
    last_err = None
    for attempt in range(max_retries):
        try:
            return query_func()
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(initial_delay * (2 ** attempt))
            else:
                raise e

def get_gsheets_conn():
    global _SUPABASE_CLIENT_INSTANCE
    if _SUPABASE_CLIENT_INSTANCE is not None:
        return _SUPABASE_CLIENT_INSTANCE
    with _CLIENT_LOCK:
        if _SUPABASE_CLIENT_INSTANCE is not None:
            return _SUPABASE_CLIENT_INSTANCE
        from supabase import create_client, ClientOptions
        SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
        SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
        try:
            options = ClientOptions(postgrest_client_timeout=15)
            _SUPABASE_CLIENT_INSTANCE = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)
            return _SUPABASE_CLIENT_INSTANCE
        except Exception as e:
            try:
                _SUPABASE_CLIENT_INSTANCE = create_client(SUPABASE_URL, SUPABASE_KEY)
                return _SUPABASE_CLIENT_INSTANCE
            except Exception as e2:
                import streamlit as st
                st.warning(f"Chưa cấu hình Supabase Connection: {e2}")
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

import json
import pandas as pd
import numpy as np

@st.cache_data(ttl=5, show_spinner=False)
def _cached_fetch_table_data(worksheet, filters_str):
    conn = get_gsheets_conn()
    if not conn: return None
    table_name = _get_table_name(worksheet)
    query = conn.table(table_name).select('*')
    if filters_str:
        filters = json.loads(filters_str)
        if filters.get('DonVi') == "Tất cả đơn vị":
            del filters['DonVi']
        elif filters.get('DonVi') in ["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]:
            filters['DonVi'] = ["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]
            
        for k, v in filters.items():
            if isinstance(v, list):
                query = query.in_(k, v)
            else:
                query = query.eq(k, v)
    res = execute_with_retry(lambda: query.execute())
    return res.data

def safe_gsheets_read(conn, worksheet, ttl=15, fallback_df=None, filters=None):
    # Invalidate cache trick 1
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    
    import streamlit as st
    import pandas as pd
    import numpy as np
            
    try:
        filters_str = json.dumps(filters) if filters else ""
        data = _cached_fetch_table_data(worksheet, filters_str)
        if not data:
            return fallback_df
            
        df = pd.DataFrame(data)
        df = df.replace("", np.nan).dropna(how='all')
        
        if worksheet == "Sheet1":
            col_mapping = {
                'ID': 'Mã CV',
                'TenCongViec': 'Tên công việc',
                'PhanTramHoanThanh': 'Tiến độ %',
                'TrangThai': 'Trạng thái',
                'Deadline': 'Hạn chót'
            }
            df.rename(columns=col_mapping, inplace=True)
            if "NgayBatDau" in df.columns:
                df["NgayBatDau"] = pd.to_datetime(df["NgayBatDau"], errors="coerce").dt.strftime('%d/%m/%Y')
            if "Hạn chót" in df.columns:
                df["Hạn chót"] = pd.to_datetime(df["Hạn chót"], errors="coerce").dt.strftime('%d/%m/%Y')
                
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
        st.warning(f"Lỗi đọc Supabase ({worksheet}): {e}")
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
                'Mã CV': 'ID', 'MaCV': 'ID',
                'Tên công việc': 'TenCongViec', 'Nội dung': 'TenCongViec', 'Công việc': 'TenCongViec',
                'Tiến độ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiến độ': 'PhanTramHoanThanh',
                'Trạng thái': 'TrangThai', 'Status': 'TrangThai',
                'Hạn chót': 'Deadline', 'Ngày hoàn thành': 'Deadline'
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
            _cached_fetch_table_data.clear()
            
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
            
        _cached_fetch_table_data.clear()
        return True
    except Exception as e:
        err_msg = str(e)
        import streamlit as st


        st.error(f"Lỗi khi lưu vào Supabase ({worksheet}): {err_msg}")
        return False


def save_config(config_data):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa cấu hình Google Sheets (secrets.toml).")
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
            st.error("⚠️ Lỗi: Không tìm thấy trang tính 'CONFIG' trên Google Sheets! Vui lòng mở Google Sheets, tạo một Sheet mới đặt tên là 'CONFIG', sau đó lưu lại.")
            return False
            
        st.cache_data.clear()
        config_data["job_descriptions"] = job_descriptions
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False

def load_config():
    default_config = {
        "companies": {
            "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG": {
                "projects_by_category": {
                    "BĐS & KDC": ["KDC Bàu Mạc", "KDC Nam Bàu Mạc", "KĐT Phước Lý & Phước Lý MR", "TĐC Phước Lý 2 & Hoà Liên 5", "Dự án Phong Nam", "Khu BT ST Hoà Ninh"],
                    "HẠ TẦNG & GIAO THÔNG": ["Tuyến đường Lê Trọng Tấn", "Tuyến đường Lê Trọng Tấn - Hoà Nhơn", "Tuyến đường Trần Hưng Đạo (BT)", "Trục I Tây Bắc", "Khu TĐC Hoà Vang"],
                    "THƯƠNG MẠI & KHÁCH SẠN": ["Khách sạn DMT-Group"]
                },
                "departments": ["HĐQT", "BLĐ", "HCNS", "TCKT", "KHĐT", "CBĐT", "KT", "ĐBGT", "DA", "XN DTBD", "Sàn GDBĐS"],
                "personnel_by_department": {
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
            },
            "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {
                "projects_by_category": {
                    "THƯƠNG MẠI & KHÁCH SẠN": ["Du thuyền Happy Yacht (DMT Marina)", "Du thuyền Happy Yacht"]
                },
                "departments": ["BLĐ"],
                "personnel_by_department": {
                    "BLĐ": ["Trần Cường"]
                }
            },
            "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
                "projects_by_category": {},
                "departments": ["HĐQT", "BLĐ", "KT", "BCH CT", "XN XMTB", "HCNS", "TCKT", "Mỏ"],
                "personnel_by_department": {
                    "HĐQT": ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"],
                    "BLĐ": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
                    "KT": ["Phạm Quang Nghĩa", "Lê Văn Thành", "Ngô Văn Hoàng"],
                    "BCH CT": ["Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long"],
                    "XN XMTB": ["Đặng Hiền"],
                    "TCKT": ["Nguyễn Thị Ngọc Hà", "Nguyễn Thị Như Can"],
                    "HCNS": ["Nguyễn Thị Mỹ Phương"],
                    "Mỏ": ["Lê Nho Tân"]
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
            
        # Migrate old company names to new standardized names
        companies_data = data.get("companies", {})
        if "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG" in companies_data:
            companies_data["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"] = companies_data.pop("CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG")
        if "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT" in companies_data:
            companies_data["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"] = companies_data.pop("CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT")

        # Map departments to abbreviations to ensure consistency across the app
        abbr_map = {
            "Ban Lãnh đạo": "BLĐ",
            "Lãnh đạo": "BLĐ",
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
            "Xí nghiệp xe thiết bị": "XN XMTB"
        }
        
        for comp_name, comp_data in data.get("companies", {}).items():
            if "departments" in comp_data:
                comp_data["departments"] = [abbr_map.get(d, d) for d in comp_data["departments"]]
            if "personnel_by_department" in comp_data:
                new_personnel = {}
                for d, p in comp_data["personnel_by_department"].items():
                    new_personnel[abbr_map.get(d, d)] = p
                
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
                
        return data
    except Exception as e:
        print("Error parsing DB config:", e)
        return default_config


# Load current config dynamically


def save_bsc_config(bsc_data):
    conn = get_gsheets_conn()
    if conn is None:
        return False
    try:
        import json
        import pandas as pd
        df_save = pd.DataFrame([{
            "NhanSu": "APP_BSC_CONFIG",
            "PhongBan": "SYSTEM",
            "Role": "SYSTEM",
            "config_json": json.dumps(bsc_data, ensure_ascii=False)
        }])
        success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        import streamlit as st
        st.cache_data.clear()
        return success
    except Exception as e:
        print("Error saving BSC config:", e)
        return False

def load_bsc_config():
    default_config = {"years": {}, "quarters": {}, "months": {}}
    conn = get_gsheets_conn()
    if conn is None:
        return default_config
    try:
        import json
        df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=30)
        if df is None or df.empty:
            return default_config

        if "NhanSu" in df.columns and "config_json" in df.columns:
            rows = df[df["NhanSu"] == "APP_BSC_CONFIG"]
            if not rows.empty:
                json_str = rows.iloc[0]["config_json"]
                data = json.loads(json_str)
                for key in ["years", "quarters", "months"]:
                    if key not in data:
                        data[key] = {}
                        
                # Inject DEMO data if HCNS has no data
                demo_year_key = "Ban Hành chính Nhân sự_2026"
                demo_month_key = "Ban Hành chính Nhân sự_2026_10"
                if demo_year_key not in data["years"]:
                    data["years"][demo_year_key] = [
                        {"name": "Kiện toàn bộ hồ sơ PCCC, diễn tập, thẩm định định kỳ", "quarter": "Cả năm"},
                        {"name": "Xây dựng hệ thống cấp bậc chức danh, KPI toàn hệ thống (BCS)", "quarter": "Q4"},
                        {"name": "Rà soát toàn bộ hồ sơ Pháp lý - Cty CP Đầu tư ĐNMT", "quarter": "Q1"}
                    ]
                if demo_month_key not in data["months"]:
                    data["months"][demo_month_key] = [
                        {"name": "Hoàn thành quy trình tự kiểm tra PCCC cơ sở", "weight": 20},
                        {"name": "Thành lập đội KPIs Công ty và lập kế hoạch khung năng lực", "weight": 40},
                        {"name": "Rà soát đánh số danh mục Hồ sơ pháp lý Công ty BT1-BT5", "weight": 30}
                    ]
                return data

        return default_config
    except Exception as e:
        print("Error loading BSC config:", e)
        return default_config


config = load_config() # force reload 2

DEPT_ABBR = {
    "Hội đồng quản trị": "HĐQT",
    "HĐQT": "HĐQT",
    "Ban Lãnh đạo": "BLĐ",
    "Lãnh đạo": "BLĐ",
    "BLĐ": "BLĐ",
    "Ban Hành chính Nhân sự": "HCNS",
    "HCNS": "HCNS",
    "Ban Tài chính Kế toán": "TCKT",
    "TCKT": "TCKT",
    "Ban Kế hoạch Đầu tư": "KHĐT",
    "KHĐT": "KHĐT",
    "Ban Chuẩn bị Đầu tư": "CBĐT",
    "CBĐT": "CBĐT",
    "Ban Kỹ thuật": "KT",
    "KT": "KT",
    "Ban Đền bù Giải tỏa": "ĐBGT",
    "ĐBGT": "ĐBGT",
    "Ban Dự án": "DA",
    "DA": "DA",
    "Xí nghiệp DTBD": "XN DTBD",
    "XN DTBD": "XN DTBD",
    "Sàn GDBĐS": "Sàn GDBĐS",
    "Ban chỉ huy Công trường": "BCH CT",
    "BCH CT": "BCH CT",
    "Xí nghiệp xe máy thiết bị": "XN XMTB",
    "Xí nghiệp xe thiết bị": "XN XMTB",
    "XN XMTB": "XN XMTB",
    "Ban TCKT": "TCKT",
    "Ban HCNS": "HCNS",
    "Ban KHĐT": "KHĐT",
    "Ban CBĐT": "CBĐT",
    "Ban KT": "KT",
    "Ban ĐBGT": "ĐBGT",
    "Ban DA": "DA",
    "BCH Công trường": "BCH CT",
    "XN Xe máy thiết bị": "XN XMTB"
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

DEPT_LEADS = {
    "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG": {
        "HĐQT": ["Đặng Thanh Bình"],
        "Hội đồng quản trị": ["Đặng Thanh Bình"],
        "BLĐ": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
        "Ban Lãnh đạo": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn"],
        "HCNS": ["Nguyễn Thị Hạnh Tiên"],
        "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên"],
        "TCKT": ["Đồng Thị Nguyệt Nga"],
        "Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga"],
        "KHĐT": ["Nguyễn Trần Thức"],
        "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức"],
        "CBĐT": ["Hồ Văn Khoa"],
        "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa"],
        "KT": [],
        "Ban Kỹ thuật": [],
        "ĐBGT": [],
        "Ban Đền bù Giải tỏa": [],
        "DA": [],
        "Ban Dự án": [],
        "XN DTBD": [],
        "Xí nghiệp DTBD": [],
        "SÀN": [],
        "Sàn GDBĐS": []
    },
    "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "HĐQT": ["Đặng Thị Lan Ngọc", "Đặng Thanh Bình"],
        "Hội đồng quản trị": ["Đặng Thị Lan Ngọc", "Đặng Thanh Bình"],
        "BLĐ": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
        "Ban Lãnh đạo": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
        "HCNS": ["Nguyễn Thị Mỹ Phương"],
        "Ban Hành chính Nhân sự": ["Nguyễn Thị Mỹ Phương"],
        "TCKT": ["Nguyễn Thị Ngọc Hà"],
        "Ban Tài chính Kế toán": ["Nguyễn Thị Ngọc Hà"],
        "KT": [],
        "Ban Kỹ thuật": [],
        "BCH CT": [],
        "Ban chỉ huy Công trường": [],
        "XN XMTB": [],
        "Xí nghiệp xe máy thiết bị": [],
        "Mỏ": [],
        "Ban Quản lý Mỏ": []
    },
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "HĐQT": ["Đặng Thị Lan Ngọc", "Đặng Thanh Bình"],
        "Hội đồng quản trị": ["Đặng Thị Lan Ngọc", "Đặng Thanh Bình"],
        "BLĐ": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
        "Ban Lãnh đạo": ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"],
        "HCNS": ["Nguyễn Thị Mỹ Phương"],
        "Ban Hành chính Nhân sự": ["Nguyễn Thị Mỹ Phương"],
        "TCKT": ["Nguyễn Thị Ngọc Hà"],
        "Ban Tài chính Kế toán": ["Nguyễn Thị Ngọc Hà"],
        "KT": [],
        "Ban Kỹ thuật": [],
        "BCH CT": [],
        "Ban chỉ huy Công trường": [],
        "XN XMTB": [],
        "Xí nghiệp xe máy thiết bị": [],
        "Mỏ": [],
        "Ban Quản lý Mỏ": []
    },
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {
        "BLĐ": ["Trần Cường"],
        "Ban Lãnh đạo": ["Trần Cường"]
    },
    "CÔNG TY CỔ PHẦN DMT-MARINA": {
        "BLĐ": ["Trần Cường"],
        "Ban Lãnh đạo": ["Trần Cường"]
    }
}
DEPT_LEADS["CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"] = DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]
DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"] = DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]
DEPT_LEADS["CÔNG TY CỔ PHẦN ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"] = DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]
DEPT_LEADS["CÔNG TY CỔ PHẦN ĐẦU TƯ ĐÀ NẴNG MIỀN TRUNG"] = DEPT_LEADS["CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG"]
DEPT_LEADS["CÔNG TY CỔ PHẦN XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐÀ NẴNG - MIỀN TRUNG"] = DEPT_LEADS["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]

# ==============================================================================
# HIERARCHY CHUẨN XÁC THEO SHEET 'MARINA (3)' TRONG FILE 'Phân quyền.xls'
# ĐÂY LÀ SINGLE SOURCE OF TRUTH CHO TOÀN BỘ HỆ THỐNG
# ==============================================================================
HIERARCHY_MARINA_3 = {
    # 1. HĐQT & Ban Lãnh đạo cấp cao (Thể, Nữ, Tôn hiện tại chưa ai quản lý)
    "Đặng Thanh Bình": None,   # CT HĐQT Đầu Tư -> Toàn quyền xem và duyệt toàn hệ thống
    "Đặng Thị Lan Ngọc": None,  # CT HĐQT Cienco -> Toàn quyền xem và duyệt toàn hệ thống
    "Đặng Ngọc Hoàng": ["Trần Cường", "Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm"], # PCT HĐQT Đầu Tư, CT HĐQT Marina (quản lý Trần Cường, Hạnh Tiên, Ngô Thị Tâm)
    "Trần Quốc Thể": ["Nguyễn Văn Bồn", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"], # TGĐ Đầu Tư (quản lý Bồn, Khoa, Thức, Châu, Thắng, Hiếu)
    "Đoàn Thị Ngọc Nữ": ["Đồng Thị Nguyệt Nga"], # PTGĐ Đầu Tư phụ trách TCKT (chị Ngọc Hà ở Cienco do anh Thái Văn Thành duyệt)
    "Nguyễn Ngọc Tôn": ["Đặng Công Nhựt", "Đặng Công Nhật", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"], # PTGĐ Đầu Tư phụ trách ĐBGT (hiện tại chưa ai quản lý)
    "Thái Văn Thành": [ # TGĐ Cienco (Nguyễn Văn Bồn do anh Thể duyệt; Đặng Hiền do anh Trọng duyệt)
        "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Nguyễn Thị Mỹ Phụng",
        "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", 
        "Lê Văn Thành", "Ngô Văn Hoàng"
    ],
    "Trần Văn Trọng": [ # PTGĐ Cienco
        "Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", 
        "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Đặng Hiển"
    ],
    "Trần Cường": [], # Giám đốc Marina (nhân sự duy nhất tại Marina, do anh Đặng Ngọc Hoàng quản lý)

    # 2. Lãnh đạo Phòng/Ban & Đơn vị theo sheet MARINA (3)
    "Nguyễn Thị Hạnh Tiên": ["Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"], # Trưởng Ban HCNS (Đầu Tư) / Trưởng Ban HCTH (Marina)
    "Đồng Thị Nguyệt Nga": ["Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Lê Thị Hải"], # GĐ Ban TCKT Đầu Tư (chỉ có chị Nga duyệt Hoàng Hà, Nhật Sang, Lê Thị Hải)
    "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Như Can"], # PGĐ Ban TCKT Cienco (duyệt Như Can; Lê Thị Hải do Đồng Thị Nguyệt Nga duyệt)
    "Hồ Văn Khoa": ["Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"], # GĐ Ban CBĐT
    "Nguyễn Trần Thức": ["Nguyễn Đức Lợi", "Phan Thị Kim Cúc", "Trần Tin"], # GĐ Ban KHĐT
    "Nguyễn Thị Mỹ Phương": [] # PGĐ Ban HCNS Cienco (chế độ Quản lý, không duyệt công việc)
}

# ==============================================================================
# PHÂN CÔNG PHÒNG BAN PHỤ TRÁCH CHO THÀNH VIÊN BAN LÃNH ĐẠO (BLĐ)
# ==============================================================================
BLD_MANAGED_DEPTS = {
    "Trần Quốc Thể": ["CBĐT", "KHĐT"],
    "Nguyễn Ngọc Tôn": ["ĐBGT"],
    "Đoàn Thị Ngọc Nữ": ["TCKT"],
    "Đặng Ngọc Hoàng": ["Sàn GDBĐS", "HCNS", "BLĐ"],
    "Thái Văn Thành": ["KT", "BCH CT", "XN XMTB", "Mỏ", "TCKT", "HCNS"],
    "Trần Văn Trọng": ["KT", "BCH CT", "XN XMTB", "Mỏ"]
}

def get_bld_managed_departments(user_name):
    """
    Trả về danh sách phòng ban mà thành viên BLĐ phụ trách.
    - Trả về None nếu là HĐQT (toàn quyền xem mọi ban).
    - Trả về list tên viết tắt các ban nếu là BLĐ.
    - Trả về None nếu không thuộc BLĐ.
    """
    if not user_name:
        return None
    if user_name in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
        return None
    return BLD_MANAGED_DEPTS.get(user_name)

def get_subordinates_for_manager(manager_user):
    """
    Trả về danh sách cấp dưới trực tiếp cần duyệt/nghiệm thu theo sheet MARINA (3).
    - Trả về None nếu là HĐQT (toàn quyền, duyệt mọi công việc).
    - Trả về list tên cấp dưới nếu có.
    - Trả về [] nếu không quản lý ai.
    """
    if not manager_user:
        return []
    if manager_user in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
        return None
    subs = HIERARCHY_MARINA_3.get(manager_user)
    if subs is None and manager_user in HIERARCHY_MARINA_3:
        return None
    return list(dict.fromkeys(subs)) if subs else []

def get_allowed_personnel_for_manager(manager_user, include_self=True):
    """
    Trả về danh sách nhân sự mà Quản lý được xem tiến độ / KPI:
    Bao gồm chính mình + toàn bộ cấp dưới thuộc quyền theo sheet MARINA (3).
    - Trả về None nếu là HĐQT (toàn quyền, xem mọi nhân sự).
    """
    if not manager_user:
        return []
    if manager_user in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
        return None
    subs = HIERARCHY_MARINA_3.get(manager_user)
    if subs is None and manager_user in HIERARCHY_MARINA_3:
        return None
    res = list(subs) if subs else []
    if include_self and manager_user not in res:
        res.insert(0, manager_user)
    return list(dict.fromkeys(res))

def setup_manager_db_filters(db_filters, manager_user, manager_dept, selected_company):
    """
    Cấu hình bộ lọc db_filters chuẩn hóa cho Quản lý theo sheet MARINA (3):
    1. Nếu là HĐQT: Xem toàn bộ mọi công ty, phòng ban.
    2. Nếu là BLĐ: Chỉ thấy công việc của các phòng ban mình phụ trách + công việc của chính mình.
    3. Nếu là Quản lý các phòng ban khác: Lọc theo danh sách cấp dưới + chính mình.
    """
    if not manager_user:
        return db_filters
        
    if manager_dept in ["HĐQT", "Hội đồng quản trị"] or manager_user in ["Đặng Thanh Bình", "Đặng Thị Lan Ngọc"]:
        if 'DonVi' in db_filters: del db_filters['DonVi']
        if 'PhongBan' in db_filters: del db_filters['PhongBan']
        if 'NguoiChuTri' in db_filters: del db_filters['NguoiChuTri']
        return db_filters

    # 1. Kiểm tra nếu là thành viên BLĐ
    bld_depts = get_bld_managed_departments(manager_user)
    if bld_depts is not None:
        if 'DonVi' in db_filters: del db_filters['DonVi']
        expanded_depts = []
        for d in bld_depts + ["BLĐ"]:
            short_name = DEPT_ABBR.get(d, d)
            expanded_depts.extend([k for k, v in DEPT_ABBR.items() if v == short_name or k == d] + [d, short_name])
        db_filters['PhongBan'] = list(set(expanded_depts))
        if 'NguoiChuTri' in db_filters: del db_filters['NguoiChuTri']
        return db_filters
        
    # 2. Quản lý phòng ban bình thường
    allowed = get_allowed_personnel_for_manager(manager_user, include_self=True)
    if allowed is not None and len(allowed) > 0:
        if 'DonVi' in db_filters: del db_filters['DonVi']
        if 'PhongBan' in db_filters: del db_filters['PhongBan']
        db_filters['NguoiChuTri'] = allowed
    else:
        if manager_dept and manager_dept != "Tất cả":
            db_filters['PhongBan'] = manager_dept
            
    return db_filters



def get_personnel_for_company_dept(company, dept, config):
    companies = config.get("companies", {})
    personnel_list = []
    
    abbr_dept = DEPT_ABBR.get(dept, dept)
    
    comp_data = companies.get(company, {})
    p_by_dept = comp_data.get("personnel_by_department", {})
    
    personnel_list = p_by_dept.get(dept, [])
    if not personnel_list:
        personnel_list = p_by_dept.get(abbr_dept, [])
    if not personnel_list:
        for k, v in DEPT_ABBR.items():
            if v == dept or v == abbr_dept or k == dept or k == abbr_dept:
                if k in p_by_dept and p_by_dept[k]:
                    personnel_list = p_by_dept[k]
                    break
                    
    if not personnel_list:
        g_p_by_dept = config.get("personnel_by_department", {})
        personnel_list = (
            g_p_by_dept.get(dept, []) or 
            g_p_by_dept.get(abbr_dept, []) or 
            DEFAULT_PERSONNEL.get(dept, []) or 
            DEFAULT_PERSONNEL.get(abbr_dept, [])
        )
        
    return list(dict.fromkeys(personnel_list)) if personnel_list else []

def get_departments_for_company(company, config):
    companies = config.get("companies", {})
    depts = []
    if company in companies:
        depts = companies[company].get("departments", [])
    if not depts:
        all_depts = set()
        for comp_data in companies.values():
            all_depts.update(comp_data.get("departments", []))
        global_depts = config.get("departments", [])
        all_depts.update(global_depts)
        depts = sorted(list(all_depts))
        
    depts = list(depts)
    if "MARINA" in str(company).upper() and "HCTH" not in depts:
        depts.append("HCTH")
    if "GIAO THÔNG" in str(company).upper() and "Mỏ" not in depts:
        depts.append("Mỏ")
    return depts


def get_filtered_projects(company_name, config, db_projs, department=None, manager_user=None):
    dept_projs = set()
    is_leader = department in ["BLĐ", "HĐQT"]
    bld_depts = get_bld_managed_departments(manager_user) if (manager_user and is_leader) else None
    
    try:
        import json
        import os
        if os.path.exists('project_targets.json'):
            with open('project_targets.json', 'r', encoding='utf-8') as f:
                targets = json.load(f)
                for t in targets:
                    t_comp = t.get("company", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG")
                    t_dept = DEPT_ABBR.get(t.get("department"), t.get("department"))
                    
                    if is_leader:
                        if bld_depts is not None:
                            # Thành viên BLĐ chỉ thấy dự án thuộc ban mình phụ trách
                            if t_dept in bld_depts or t_dept == "BLĐ":
                                if not company_name or company_name == "Tất cả đơn vị" or t_comp == company_name:
                                    dept_projs.add(t.get("project_name"))
                        else:
                            # HĐQT xem toàn bộ dự án của công ty
                            if not company_name or company_name == "Tất cả đơn vị" or t_comp == company_name:
                                dept_projs.add(t.get("project_name"))
                    elif department:
                        if t_dept == department:
                            dept_projs.add(t.get("project_name"))
                    else:
                        if not company_name or company_name == "Tất cả đơn vị" or t_comp == company_name:
                            dept_projs.add(t.get("project_name"))
    except:
        pass
        
    if department and not (is_leader and bld_depts is None) and len(dept_projs) > 0:
        merged = list(set(list(dept_projs) + db_projs))
        return sorted(merged)
        
    # Fallback to config.json (and for HĐQT)
    companies = config.get("companies", {})
    projs_by_cat = {}
    if company_name in companies:
        projs_by_cat = companies[company_name].get("projects_by_category", {})
    else:
        projs_by_cat = config.get("projects_by_category", {})
        
    all_projs = []
    for cat, projs in projs_by_cat.items():
        all_projs.extend(projs)
        
    merged = list(set(all_projs + list(dept_projs) + db_projs))
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
            
            # 1. Tự động chuẩn hóa và ánh xạ tên cột
            col_mapping = {
                'Mã CV': 'ID', 'MaCV': 'ID',
                'Tên công việc': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nội dung': 'TenCongViec', 'Công việc': 'TenCongViec',
                'Tiến độ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiến độ': 'PhanTramHoanThanh',
                'Trạng thái': 'TrangThai', 'Status': 'TrangThai',
                'Hạn chót': 'Deadline', 'Ngày hoàn thành': 'Deadline'
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
            
            # 3. Xử lý dữ liệu rỗng / NaN an toàn
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('Đang thực hiện')
                df['TrangThai'] = df['TrangThai'].replace('', 'Đang thực hiện')

    except Exception as e:
        import streamlit as st


        st.error(f"Lỗi khi đọc dữ liệu GANTT_KHDT: {e}")
        raise e
        
    # Khởi tạo các cột thiếu
    for col in ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]:
        if col not in df.columns:
            df[col] = ""

            
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['NgayCapNhat'] = df['NgayCapNhat'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))
    df['ID'] = df['ID'].astype(str)
    df['TenDuAn'] = df['TenDuAn'].fillna('Dự án mặc định')
    df['TenCongViec'] = df['TenCongViec'].fillna('')
    df['GiaiDoan'] = df['GiaiDoan'].fillna('Khác')
    df['Milestone'] = df['Milestone'].fillna('')
    df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0).astype(int)
    
    phase_mapping = {
        "Concept Dev": "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
        "1. Phát triển Ý tưởng & Khảo sát": "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
        "System Design": "2. Pháp lý Dự án & Quy hoạch 1/500",
        "2. Thiết kế Cơ sở & Quy hoạch": "2. Pháp lý Dự án & Quy hoạch 1/500",
        "Detail Design": "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
        "3. Thiết kế Chi tiết & Lập Báo cáo": "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
        "Legal / Regulatory": "4. Thiết kế Bản vẽ Thi công & Thẩm định",
        "4. Phê duyệt Pháp lý & Thẩm định": "4. Thiết kế Bản vẽ Thi công & Thẩm định",
        "Test & Refine": "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
        "5. Thử nghiệm & Chỉnh sửa": "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
        "Produce": "6. Thi công Xây lắp & Lắp đặt Thiết bị",
        "Produce / Execute": "6. Thi công Xây lắp & Lắp đặt Thiết bị",
        "6. Triển khai & Thực thi": "6. Thi công Xây lắp & Lắp đặt Thiết bị"
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


        st.error(f"Lỗi khi đọc trang tính KPI_ADJUSTMENTS: {e}")
        raise e

import uuid
def add_kpi_adjustment(ten, thang, nam, loai, diem, lydo):
    if hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
    import pandas as pd
    df = read_kpi_adjustments()
    if not df.empty:
        dup = df[(df['TenNhanVien'] == ten) & (df['Thang'] == thang) & (df['Nam'] == nam) & (df['LoaiHanhVi'] == loai) & (df['DiemDieuChinh'] == diem) & (df['LyDo'] == lydo)]
        if not dup.empty:
            return True, ""
    
    new_id = uuid.uuid4().hex[:8]
    new_row = {
        "ID": new_id,
        "NhanSu": ten,
        "Thang": thang,
        "Nam": nam,
        "LoaiDieuChinh": loai,
        "SoDiem": diem,
        "LyDo": lydo
    }
    
    if insert_db_record("KPI_ADJUSTMENTS", new_row):
        return True, ""
    return False, "Không thể thêm KPI Adjustment"

def edit_kpi_adjustment(adj_id, ten, thang, nam, loai, diem, lydo):
    update_dict = {
        "NhanSu": ten,
        "Thang": thang,
        "Nam": nam,
        "LoaiDieuChinh": loai,
        "SoDiem": diem,
        "LyDo": lydo
    }
    if update_db_record("KPI_ADJUSTMENTS", "ID", adj_id, update_dict):
        return True, ""
    return False, "Lỗi cập nhật KPI Adjustment"

def delete_kpi_adjustment(adj_id):
    if delete_db_record("KPI_ADJUSTMENTS", "ID", adj_id):
        return True, ""
    return False, "Lỗi xóa KPI Adjustment" 

def save_gantt_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        
        safe_gsheets_update(conn, worksheet="GANTT_KHDT", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False

def read_kpi_plans():
    df = read_sqlite_table("kpi_plans")
    if df is None or df.empty:
        import pandas as pd
        return pd.DataFrame(columns=["User", "Month", "Year", "Status"])
    return df

def save_kpi_plans(df):
    save_sqlite_table(df, "kpi_plans")

def read_kpi_tasks():
    df = read_sqlite_table("kpi_tasks")
    if df is None or df.empty:
        import pandas as pd
        return pd.DataFrame(columns=["id", "User", "Month", "Year", "Name", "BSC", "Type", "Weight", "Target", "Status", "Progress", "Score", "Note"])
    return df

def save_kpi_tasks(df):
    save_sqlite_table(df, "kpi_tasks")

def auto_scale_tasks(tasks_df, user, month, year):
    # Auto scale existing tasks if a new task pushes total weight over 100
    if tasks_df is None or tasks_df.empty:
        return tasks_df
    tasks_df['Weight'] = pd.to_numeric(tasks_df['Weight'], errors='coerce').fillna(0.0).astype(float)
    user_tasks = tasks_df[(tasks_df['User']==user) & (tasks_df['Month']==month) & (tasks_df['Year']==year)]
    total_w = user_tasks['Weight'].sum()
    if total_w > 100:
        # Scale down proportionally
        ratio = 100.0 / total_w
        for idx in user_tasks.index:
            tasks_df.at[idx, 'Weight'] = round(float(tasks_df.at[idx, 'Weight']) * ratio, 2)
    return tasks_df

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
        "NGÀY": ["NGÀY", "Ngày", "Ngay"],
        "ĐƠN VỊ": ["ĐƠN VỊ", "Đơn vị", "Don vi", "Co quan gui", "Cơ quan gửi"],
        "NỘI DUNG": ["NỘI DUNG", "Nội dung", "Noi dung", "Trich yeu", "Trích yếu"],
        "Số ký hiệu": ["Số ký hiệu", "Số / Ký hiệu", "So ky hieu", "SỐ KÝ HIỆU", "SoKyHieu"],
        "Thời hạn hoàn thành": ["Thời hạn hoàn thành", "THỜI HẠN HOÀN THÀNH", "Ngày hoàn thành", "NGÀY HOÀN THÀNH", "Deadline"],
        "Trạng thái": ["Trạng thái", "Trang thai", "TRẠNG THÁI", "TrangThai"],
        "Người/ Ban thực hiện": ["Người/ Ban thực hiện", "Nguoi/ Ban thuc hien", "NGƯỜI/ BAN THỰC HIỆN", "Bộ phận chủ trì", "Ban chủ trì", "BanChuTri"],
        "Ghi chú": ["Ghi chú", "Ghi chu", "GhiChu", "Note", "Ghi chú khác"]
    }
    
    for key, possibilities in fields.items():
        found_col = None
        for col in import_df.columns:
            if col.lower() in [p.lower() for p in possibilities]:
                found_col = col
                break
        mapping[key] = found_col
        
    # Check if critical columns exist
    critical_fields = ["NỘI DUNG", "Số ký hiệu", "Thời hạn hoàn thành"]
    missing_critical = [f for f in critical_fields if mapping[f] is None]
    if missing_critical:
        return False, f"Thiếu các cột bắt buộc trong bảng dữ liệu: {', '.join(missing_critical)}"
        
    # Keep rows where "Thời hạn hoàn thành" and "NỘI DUNG" are not null / empty
    deadline_col = mapping["Thời hạn hoàn thành"]
    content_col = mapping["NỘI DUNG"]
    so_ky_hieu_col = mapping["Số ký hiệu"]
    ghi_chu_col = mapping["Ghi chú"]
    
    # Drop rows that are completely empty or have null deadline/content
    valid_df = import_df.dropna(subset=[deadline_col])
    valid_df = valid_df[valid_df[deadline_col].astype(str).str.strip() != ""]
    valid_df = valid_df[valid_df[content_col].notna() & (valid_df[content_col].astype(str).str.strip() != "")]
    
    if valid_df.empty:
        return False, "Không tìm thấy dòng hợp lệ nào chứa đầy đủ thông tin 'Thời hạn hoàn thành' và 'Nội dung'."
        
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
            date_col = mapping["NGÀY"]
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
            co_quan_gui = str(row[mapping["ĐƠN VỊ"]]).strip() if mapping["ĐƠN VỊ"] and not pd.isna(row[mapping["ĐƠN VỊ"]]) else ""
            trich_yeu = str(row[content_col]).strip()
            
            ban_chu_tri_raw = str(row[mapping["Người/ Ban thực hiện"]]).strip() if mapping["Người/ Ban thực hiện"] and not pd.isna(row[mapping["Người/ Ban thực hiện"]]) else ""
            config = load_settings()
            all_depts = set(config.get("departments", []))
            for comp_data in config.get("companies", {}).values():
                all_depts.update(comp_data.get("departments", []))
                
            if ban_chu_tri_raw in all_depts:
                ban_chu_tri = ban_chu_tri_raw
            else:
                ban_chu_tri = "Ban Lãnh đạo"
                
            trang_thai_raw = str(row[mapping["Trạng thái"]]).strip() if mapping["Trạng thái"] and not pd.isna(row[mapping["Trạng thái"]]) else "⏳ Đang xử lý"
            ghi_chu = str(row[ghi_chu_col]).strip() if ghi_chu_col and not pd.isna(row[ghi_chu_col]) else ""
            
            is_completed = trang_thai_raw in ["Đã xong", "Hoàn thành", "Đã hoàn thành", "✅ Đã xong"]
            
            trang_thai = "⏳ Đang xử lý"
            if is_completed:
                trang_thai = "✅ Đã xong"
            else:
                if pd.notna(deadline_val) and deadline_val < today:
                    days_late = (today - deadline_val).days
                    trang_thai = f"⚠️ Trễ hạn xử lý CV (Trễ {days_late} ngày)"
                else:
                    trang_thai = "⏳ Đang xử lý"
                    
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
                    "DonVi": selected_company if selected_company != "Tất cả đơn vị" else "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
                    "SoKyHieu": so_ky_hieu,
                    "NgayBanHanh": ngay_ban_hanh,
                    "CoQuanGui": co_quan_gui,
                    "TrichYeu": trich_yeu,
                    "TenDuAn": "Quản lý Công văn đến",
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
                docs_df.at[idx, "DonVi"] = selected_company if selected_company != "Tất cả đơn vị" else docs_df.at[idx, "DonVi"]
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
            task_name = f"📩 [Công văn đến] {trich_yeu} (Số: {so_ky_hieu})"
            duplicate_task = tasks_df[tasks_df['TenCongViec'].str.contains(so_ky_hieu, na=False)]
            
            task_status = "Đang thực hiện"
            if trang_thai == "✅ Đã xong":
                task_status = "Hoàn thành"
            elif pd.notna(deadline_val) and deadline_val < today:
                task_status = "Quá hạn"
                
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
                    "DonVi": selected_company if selected_company != "Tất cả đơn vị" else "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG",
                    "PhongBan": ban_chu_tri,
                    "NguoiChuTri": "Ban Lãnh đạo",
                    "TenDuAn": "Quản lý Công văn đến",
                    "MocTienDo": "Tự do",
                    "SanPhamBanGiao": "Xem chi tiết văn bản",
                    "TenCongViec": task_name,
                    "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
                    "NgayBatDau": ngay_ban_hanh,
                    "Deadline": deadline_val,
                    "DoUuTien": "Trung bình",
                    "PhanTramHoanThanh": 100 if task_status == "Hoàn thành" else 99,
                    "TrangThai": task_status,
                    "LinkKetQua": "",
                    "GiaiTrinhDeXuat": "",
                    "NgayCapNhat": (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    "ChuKyTheoDoi": "Theo dự án / Tự do",
                    "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ" if task_status != "Quá hạn" else "👤 Do chủ quan"
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
                tasks_df.at[t_idx, "PhanTramHoanThanh"] = 100 if task_status == "Hoàn thành" else 99
            tasks_df.at[t_idx, "NgayCapNhat"] = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            
        if save_incoming_docs_db(docs_df) and save_db(tasks_df):
            return True, f"Đồng bộ thành công! Đã thêm mới {success_count} văn bản và cập nhật {update_count} văn bản."
        else:
            return False, "Không thể lưu dữ liệu vào cơ sở dữ liệu."

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
            
            # 1. Tự động chuẩn hóa và ánh xạ tên cột
            col_mapping = {
                'Mã CV': 'ID', 'MaCV': 'ID',
                'Tên công việc': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nội dung': 'TenCongViec', 'Công việc': 'TenCongViec',
                'Tiến độ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiến độ': 'PhanTramHoanThanh',
                'Trạng thái': 'TrangThai', 'Status': 'TrangThai',
                'Hạn chót': 'Deadline', 'Ngày hoàn thành': 'Deadline'
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
            
            # 3. Xử lý dữ liệu rỗng / NaN an toàn
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('Đang thực hiện')
                df['TrangThai'] = df['TrangThai'].replace('', 'Đang thực hiện')

    except Exception as e:
        pass
        df = pd.DataFrame(columns=required_cols)

    # Khởi tạo các cột thiếu để tránh KeyError
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
            if deadline_val < today_dt and "✅ Đã xong" not in status_val and "Đã xong" not in status_val:
                days_late = (today_dt - deadline_val).days
                df.at[idx, 'TrangThai'] = f"⚠️ Trễ hạn xử lý CV (Trễ {days_late} ngày)"
                
    return df

def save_incoming_docs_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBanHanh'] = df_save['NgayBanHanh'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        
        safe_gsheets_update(conn, worksheet="VAN_BAN_DEN", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False


def load_project_targets():
    import json
    import os
    target_file = 'project_targets.json'
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def normalize_proj_key(s):
    if not s:
        return ""
    import unicodedata, re
    s = unicodedata.normalize('NFC', str(s).lower())
    s = s.replace('oà', 'òa').replace('oá', 'óa').replace('oả', 'ỏa').replace('oã', 'õa').replace('oạ', 'ọa')
    s = s.replace('uỳ', 'ùy').replace('uý', 'úy').replace('uỷ', 'ủy').replace('uỹ', 'ũy').replace('uỵ', 'ụy')
    for token in ['[dự án]', '[hạng mục]', 'dự án', 'kđt', 'khu đô thị', 'kdc', 'khu dân cư', 'htkt', 'tđc', 'khu tđc', 'tái định cư', 'kbt', 'sinh thái', 'st', 'tuyến đường', 'đường']:
        s = s.replace(token, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def is_bld_user(user=None, dept=None, is_admin=False):
    """
    Kiểm tra xem người dùng có thuộc Ban Lãnh đạo cấp cao (BLĐ / HĐQT / HR) hay không:
    - Admin / HR toàn quyền: True
    - Thuộc phòng ban BLĐ / HĐQT: True
    - Tên thuộc danh sách Lãnh đạo cấp cao (HĐQT & Ban TGĐ): True
    """
    if is_admin:
        return True
    if dept in ["BLĐ", "HĐQT", "Ban Lãnh đạo", "Hội đồng quản trị"]:
        return True
    bld_names = [
        "Đặng Thanh Bình", "Đặng Thị Lan Ngọc", 
        "Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng", "Nguyễn Ngọc Tôn",
        "Thái Văn Thành", "Trần Văn Trọng"
    ]
    if user in bld_names:
        return True
    return False


def match_project_targets(project_name, task_dept=None, company=None, is_bld=False):
    """
    Tìm kiếm và ánh xạ các Chỉ tiêu (targets) từ project_targets.json tương ứng với dự án được chọn.
    - Nếu không phải BLĐ và có task_dept: CHỈ TRẢ VỀ các chỉ tiêu thuộc phòng ban task_dept. Tuyệt đối không hiển thị chỉ tiêu của ban khác!
    - Nếu là BLĐ: Trả về đầy đủ (ưu tiên task_dept lên đầu).
    """
    all_targets = load_project_targets()
    if not all_targets:
        return []
    
    # 1. Lọc theo Công ty nếu có (trừ "Tất cả đơn vị")
    if company and company != "Tất cả đơn vị":
        comp_targets = [t for t in all_targets if t.get("company", "CÔNG TY CP ĐẦU TƯ ĐÀ NẴNG") == company]
        if comp_targets:
            all_targets = comp_targets

    # Chuẩn hóa task_dept
    abbr_task_dept = DEPT_ABBR.get(task_dept, task_dept) if task_dept else None

    # Nếu không phải BLĐ, chỉ được phép xem chỉ tiêu thuộc ban của mình
    if not is_bld and abbr_task_dept:
        all_targets = [t for t in all_targets if DEPT_ABBR.get(t.get("department"), t.get("department")) == abbr_task_dept]

    if not project_name:
        return all_targets

    clean_p = project_name.replace("[Dự án] ", "").replace("[Hạng mục] ", "").strip()
    norm_p = normalize_proj_key(clean_p)
    keywords = [w.strip() for w in norm_p.split('&') if len(w.strip()) >= 3]
    if not keywords and norm_p:
        keywords = [norm_p]

    is_adhoc = any(k in clean_p.lower() for k in ["nhiệm vụ khác", "phát sinh", "ngoài kế hoạch", "đột xuất"])

    matched = []
    for t in all_targets:
        t_proj = t.get("project_name", "")
        if t_proj == clean_p:
            matched.append(t)
            continue
        if is_adhoc and ("nhiệm vụ khác" in t_proj.lower() or "phát sinh" in t_proj.lower()):
            matched.append(t)
            continue
        norm_t = normalize_proj_key(t_proj)
        if norm_p and (norm_p in norm_t or norm_t in norm_p):
            matched.append(t)
            continue
        if any(kw in norm_t for kw in keywords):
            matched.append(t)
            continue

    # Khử trùng lặp
    seen = set()
    unique_matched = []
    for t in matched:
        tid = t.get("target_id") or t.get("target_name")
        if tid not in seen:
            seen.add(tid)
            unique_matched.append(t)

    if not is_bld:
        # Cách ly tuyệt đối: Chỉ trả về chỉ tiêu thuộc phòng ban người dùng
        if abbr_task_dept:
            return [t for t in unique_matched if DEPT_ABBR.get(t.get("department"), t.get("department")) == abbr_task_dept]
        return []

    # Sắp xếp: Ưu tiên phòng ban của người dùng lên trước (dành riêng cho BLĐ)
    if abbr_task_dept:
        same_dept = [t for t in unique_matched if DEPT_ABBR.get(t.get("department"), t.get("department")) == abbr_task_dept]
        other_dept = [t for t in unique_matched if DEPT_ABBR.get(t.get("department"), t.get("department")) != abbr_task_dept]
        return same_dept + other_dept

    return unique_matched


def read_db(filters=None):
    # Force cache clear for new progress calculation rules
    required_cols = [
        "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
        "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI", "NguonGiaoViec", "MucDoGhiNhan"
    ]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    if filters:
        if filters.get('DonVi') == "Tất cả đơn vị":
            del filters['DonVi']
        elif filters.get('DonVi') in ["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]:
            filters['DonVi'] = ["CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT", "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT"]
            
        if 'PhongBan' in filters:
            pb_filter = filters['PhongBan']
            if isinstance(pb_filter, str):
                short_name = DEPT_ABBR.get(pb_filter, pb_filter)
                long_names = [k for k, v in DEPT_ABBR.items() if v == short_name or k == pb_filter]
                filters['PhongBan'] = list(set([pb_filter, short_name] + long_names))
            elif isinstance(pb_filter, list):
                expanded_pb = []
                for p in pb_filter:
                    short_name = DEPT_ABBR.get(p, p)
                    long_names = [k for k, v in DEPT_ABBR.items() if v == short_name or k == p]
                    expanded_pb.extend([p, short_name] + long_names)
                filters['PhongBan'] = list(set(expanded_pb))
            
    try:
        df = safe_gsheets_read(conn, worksheet="Sheet1", ttl=15, filters=filters)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
        else:
            
            df.columns = [str(c).strip() for c in df.columns]
            
            # 1. Tự động chuẩn hóa và ánh xạ tên cột
            col_mapping = {
                'Mã CV': 'ID', 'MaCV': 'ID',
                'Tên công việc': 'TenCongViec', 'TenCongViec': 'TenCongViec', 'Nội dung': 'TenCongViec', 'Công việc': 'TenCongViec',
                'Tiến độ %': 'PhanTramHoanThanh', 'Progress': 'PhanTramHoanThanh', 'Tiến độ': 'PhanTramHoanThanh',
                'Trạng thái': 'TrangThai', 'Status': 'TrangThai',
                'Hạn chót': 'Deadline', 'Ngày hoàn thành': 'Deadline'
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
            
            # 3. Xử lý dữ liệu rỗng / NaN an toàn
            if 'PhanTramHoanThanh' in df.columns:
                df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0)
            if 'TrangThai' in df.columns:
                df['TrangThai'] = df['TrangThai'].fillna('Đang thực hiện')
                df['TrangThai'] = df['TrangThai'].replace('', 'Đang thực hiện')
            
            if 'PhongBan' in df.columns:
                df['PhongBan'] = df['PhongBan'].apply(lambda x: DEPT_ABBR.get(str(x).strip(), str(x).strip()))

    except Exception as e:
        import streamlit as st


        st.error(f"Lỗi khi đọc dữ liệu Sheet1: {e}")
        raise e

    # Khởi tạo các cột thiếu để tránh KeyError
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""


    # Check and initialize missing columns dynamically
    if "ChuKyTheoDoi" not in df.columns:
        df["ChuKyTheoDoi"] = "Theo dự án / Tự do"
    if "PhanLoaiTreHan" not in df.columns:
        df["PhanLoaiTreHan"] = "🟢 Không trễ hạn / Đúng tiến độ"
    if "NguonGiaoViec" not in df.columns:
        df["NguonGiaoViec"] = "Công việc được giao / định kì"
    if "MucDoGhiNhan" not in df.columns:
        df["MucDoGhiNhan"] = ""
    else:
        def clean_mucdo(val):
            val_str = str(val).strip()
            if val_str in ['nan', 'None', '']: return ""
            if val_str == "0.5" or "50" in val_str: return "50%"
            if val_str == "0.8" or "80" in val_str: return "80%"
            if val_str == "0.9" or "90" in val_str: return "90%"
            if "0%" in val_str or "0" == val_str: return "0% (Không ghi nhận)"
            return val_str
        df["MucDoGhiNhan"] = df["MucDoGhiNhan"].apply(clean_mucdo)

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Clean data formats
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))).dt.date
    df['NgayCapNhat'] = df['NgayCapNhat'].astype(str).str.replace('T', ' ', regex=False).str.slice(0, 19).apply(lambda x: pd.to_datetime(x, dayfirst=True, errors='coerce'))
    df['DonVi'] = df['DonVi'].fillna('CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
    df['TenDuAn'] = df['TenDuAn'].fillna('')
    df['MocTienDo'] = df['MocTienDo'].fillna('Tự do')
    df['SanPhamBanGiao'] = df['SanPhamBanGiao'].fillna('Xem chi tiết')
    df['LinkKetQua'] = df['LinkKetQua'].fillna('')
    df['GiaiTrinhDeXuat'] = df['GiaiTrinhDeXuat'].fillna('')
    df['ChuKyTheoDoi'] = df['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
    df['PhanLoaiTreHan'] = df['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
    df['ID'] = df['ID'].astype(str)
    
    # 🧹 Auto-healing: Dọn dẹp hoàn toàn các công việc trùng lặp do lỗi mạng / click đúp (nếu có)
    if 'ID' in df.columns:
        df['ID'] = df['ID'].astype(str).str.strip()
        df = df.drop_duplicates(subset=['ID'], keep='last').reset_index(drop=True)
    
    # Tự động loại bỏ các bản ghi trùng lặp nội dung do click đúp nhanh (cùng người, tên việc, dự án, hạn chót)
    core_cols = ['DonVi', 'PhongBan', 'NguoiChuTri', 'TenDuAn', 'TenCongViec', 'NgayBatDau', 'Deadline']
    if all(c in df.columns for c in core_cols):
        df = df.drop_duplicates(subset=core_cols, keep='first').reset_index(drop=True)
    
    for idx, row in df.iterrows():
        is_comp = str(row['TrangThai']).strip() == "Hoàn thành"
        start_d = row['NgayBatDau']
        end_d = row['Deadline']
        df.at[idx, 'PhanTramHoanThanh'] = calculate_time_progress(start_d, end_d, is_comp)
        
    if 'NgayCapNhat' in df.columns:
        df['NgayCapNhat_dt'] = pd.to_datetime(df['NgayCapNhat'], errors='coerce')
        df = df.sort_values(by='NgayCapNhat_dt', ascending=False).drop(columns=['NgayCapNhat_dt']).reset_index(drop=True)
        
    return df


def insert_db_record(worksheet, new_row_dict):
    conn = get_gsheets_conn()
    if conn is None: return False
    try:
        table_name = _get_table_name(worksheet)
        import math
        from datetime import date, datetime
        import pandas as pd
        for k, v in list(new_row_dict.items()):
            if isinstance(v, (date, datetime)):
                new_row_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, float):
                if math.isnan(v): new_row_dict[k] = None
                elif v.is_integer(): new_row_dict[k] = int(v)
            elif pd.isna(v):
                new_row_dict[k] = None
        conn.table(table_name).insert(new_row_dict).execute()
        _cached_fetch_table_data.clear()
        if worksheet == "KPI_ADJUSTMENTS" and hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi insert Supabase ({worksheet}): {e}")
        return False

def update_db_record(worksheet, id_col, id_val, update_dict):
    conn = get_gsheets_conn()
    if conn is None: return False
    try:
        table_name = _get_table_name(worksheet)
        import math
        from datetime import date, datetime
        import pandas as pd
        for k, v in list(update_dict.items()):
            if isinstance(v, (date, datetime)):
                update_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, float):
                if math.isnan(v): update_dict[k] = None
                elif v.is_integer(): update_dict[k] = int(v)
            elif pd.isna(v):
                update_dict[k] = None
        conn.table(table_name).update(update_dict).eq(id_col, id_val).execute()
        _cached_fetch_table_data.clear()
        if worksheet == "KPI_ADJUSTMENTS" and hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi update Supabase ({worksheet}): {e}")
        return False

def delete_db_record(worksheet, id_col, id_val):
    conn = get_gsheets_conn()
    if conn is None: return False
    try:
        table_name = _get_table_name(worksheet)
        conn.table(table_name).delete().eq(id_col, id_val).execute()
        _cached_fetch_table_data.clear()
        if worksheet == "KPI_ADJUSTMENTS" and hasattr(read_kpi_adjustments, "clear"): read_kpi_adjustments.clear()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi delete Supabase ({worksheet}): {e}")
        return False

def insert_task(new_row_dict):
    conn = get_gsheets_conn()
    if conn is None: return False
    
    with _INSERT_TASK_LOCK:
        try:
            table_name = _get_table_name("Sheet1")
            import uuid
            import math
            from datetime import date, datetime, timedelta
            import pandas as pd
            
            # --- ATOMIC DEDUPLICATION SHIELD ---
            # Kiểm tra trực tiếp trong Supabase để chặn hoàn toàn click đúp / gửi lặp
            p_owner = str(new_row_dict.get('NguoiChuTri', '')).strip()
            p_name = str(new_row_dict.get('TenCongViec', '')).strip()
            p_proj = str(new_row_dict.get('TenDuAn', '')).strip()
            p_dl = str(new_row_dict.get('Deadline', ''))[:10]
            
            if p_owner and p_name:
                try:
                    recent_res = execute_with_retry(lambda: conn.table(table_name).select('ID, TenCongViec, NguoiChuTri, TenDuAn, Deadline, NgayCapNhat')\
                        .eq('NguoiChuTri', p_owner)\
                        .eq('TenCongViec', p_name)\
                        .execute())
                    if recent_res and recent_res.data:
                        for existing in recent_res.data:
                            ex_dl = str(existing.get('Deadline', ''))[:10]
                            ex_proj = str(existing.get('TenDuAn', '')).strip()
                            if ex_dl == p_dl and ex_proj == p_proj:
                                ex_time_str = str(existing.get('NgayCapNhat', ''))
                                try:
                                    ex_time = datetime.strptime(ex_time_str[:19], '%Y-%m-%d %H:%M:%S')
                                    if (datetime.now() - ex_time).total_seconds() < 25:
                                        return existing['ID']
                                except:
                                    return existing['ID']
                except:
                    pass
            
            # generate ID automatically to avoid collision
            new_row_dict['ID'] = f"TSK-{uuid.uuid4().hex[:8].upper()}"
            
            # clean datetimes
            for k, v in list(new_row_dict.items()):
                if isinstance(v, (date, datetime)):
                    new_row_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, float):
                    if math.isnan(v): new_row_dict[k] = None
                    elif v.is_integer(): new_row_dict[k] = int(v)
                elif pd.isna(v):
                    new_row_dict[k] = None
                    
            execute_with_retry(lambda: conn.table(table_name).insert(new_row_dict).execute())
            
            if hasattr(read_db, "clear"): read_db.clear()
            _cached_fetch_table_data.clear()
            return new_row_dict['ID']
        except Exception as e:
            import streamlit as st
            st.error(f"Lỗi insert Supabase: {e}")
            return False

def update_task(task_id, update_dict):
    conn = get_gsheets_conn()
    if conn is None: return False
    try:
        table_name = _get_table_name("Sheet1")
        import math
        from datetime import date, datetime
        import pandas as pd
        
        for k, v in list(update_dict.items()):
            if isinstance(v, (date, datetime)):
                update_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, float):
                if math.isnan(v): update_dict[k] = None
                elif v.is_integer(): update_dict[k] = int(v)
            elif pd.isna(v):
                update_dict[k] = None
                
        execute_with_retry(lambda: conn.table(table_name).update(update_dict).eq('ID', task_id).execute())
        
        if hasattr(read_db, "clear"): read_db.clear()
        _cached_fetch_table_data.clear()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi update Supabase: {e}")
        return False


def delete_task(task_id):
    conn = get_gsheets_conn()
    if conn is None: return False
    try:
        table_name = _get_table_name("Sheet1")
        execute_with_retry(lambda: conn.table(table_name).delete().eq('ID', task_id).execute())
        
        if hasattr(read_db, "clear"): read_db.clear()
        _cached_fetch_table_data.clear()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi delete Supabase: {e}")
        return False

def save_db(df):


    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) and isinstance(x, (date, datetime)) else (str(x) if pd.notna(x) else None))
        df_save['ChuKyTheoDoi'] = df_save['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
        if 'NguonGiaoViec' not in df_save.columns: df_save['NguonGiaoViec'] = 'Công việc được giao / định kì'
        df_save['NguonGiaoViec'] = df_save['NguonGiaoViec'].fillna('Công việc được giao / định kì')
        if 'MucDoGhiNhan' not in df_save.columns: df_save['MucDoGhiNhan'] = '0% (Không ghi nhận)'
        df_save['MucDoGhiNhan'] = df_save['MucDoGhiNhan'].fillna('0% (Không ghi nhận)')
        
        df_save = df_save.where(pd.notnull(df_save), None)
        return safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False

# CSS DMT GROUP Branding Theme (Navy Blue & Orange Gold Accent)


# Main Header Title with DMT branding
st.markdown('<div class="main-title">DMT GROUP — QUẢN LÝ TIẾN ĐỘ</div>', unsafe_allow_html=True)

# Sidebar layout with logo image and fallback
logo_path = "logo.png" if os.path.exists("logo.png") else ("INPUT/logo.png" if os.path.exists("INPUT/logo.png") else None)


def clean_proj_name(name):
    return str(name).strip()
