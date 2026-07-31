import streamlit as st
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
    """Tính % thời gian đã trôi qua giữa Ngày bắt đầu và Hạn chót"""
    if is_completed:
        return 100.0
    try:
        today = date.today()
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(deadline_date, str):
            deadline_date = datetime.strptime(deadline_date, "%Y-%m-%d").date()
            
        if not start_date or not deadline_date or start_date >= deadline_date:
            return 0.0
            
        total_days = (deadline_date - start_date).days
        elapsed_days = (today - start_date).days
        
        if elapsed_days <= 0:
            return 0.0
        if elapsed_days >= total_days:
            return 99.0
            
        return round((elapsed_days / total_days) * 100, 1)
    except Exception:
        return 0.0

# Page config - Light Theme is handled natively by Streamlit's default settings
st.set_page_config(
    page_title="Hệ thống Quản lý Tiến độ Công việc & KPI - DMT Group",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Standardized companies based on CIENCO, DMT Group, and DMT Marina documents
COMPANIES = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {},
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {},
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {}
}

# Configuration JSON logic for dynamic Projects and Departments
CONFIG_FILE = os.path.join("OUTPUT", "CONFIG_PROJECTS.json")

DEFAULT_PERSONNEL = {
    "Ban Lãnh đạo": ["Trần Quốc Thể", "Đoàn Thị Ngọc Nữ", "Đặng Ngọc Hoàng"],
    "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Thị Tú Uyên"],
    "Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"],
    "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Phan Thị Mỹ Hạnh", "Nguyễn Đức Lợi", "Trần Tin"],
    "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],
    "Ban Kỹ thuật": ["Nguyễn Văn Bồn"],
    "Ban Đền bù Giải tỏa": ["Nguyễn Ngọc Tôn", "Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Ban chỉ huy Công trường": ["Nguyễn Phong Trung", "Phạm Văn Long", "Lê Đông"],
    "Xí nghiệp xe máy thiết bị": ["Đặng Hiền"],
    "Ban Dự án": ["Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"],
    "Xí nghiệp DTBD": ["Mai Văn Châu"],
    "Sàn GDBĐS": ["Ngô Thị Tâm"],
    "Tổ KPI": []
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
    try:
        from streamlit_gsheets import GSheetsConnection
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.warning(f"Chưa cấu hình Google Sheets Connection: {e}")
        return None


def safe_gsheets_read(conn, worksheet, ttl=600, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    kwargs = {"worksheet": worksheet, "ttl": ttl}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    cache_key = f"cached_df_{worksheet}"
    
    try:
        df = conn.read(**kwargs)
        if df is not None:
            st.session_state[cache_key] = df
            return df
        else:
            return st.session_state.get(cache_key, fallback_df)
    except Exception as e:
        import streamlit as st
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e) or "Spreadsheet must not be None" in str(e):
            st.session_state["show_gsheet_input"] = True
        else:
            # We don't want to show toast on every network glitch if it's running in background, but keeping silent is fine too.
            pass
        return st.session_state.get(cache_key, fallback_df)

def safe_gsheets_update(conn, worksheet, data):
    kwargs = {"worksheet": worksheet, "data": data}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    try:
        conn.update(**kwargs)
        return True
    except Exception as e:
        import streamlit as st
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e) or "Spreadsheet must not be None" in str(e):
            st.session_state["show_gsheet_input"] = True
        else:
            # Ignore expected missing worksheets
            if str(e).strip("'\"") not in ["GANTT_KHDT", "VAN_BAN_DEN", "CONFIG"] and "WorksheetNotFound" not in str(type(e)):
                st.error(f"Lỗi lưu dữ liệu GSheets ({worksheet}): {str(e)}")
        return False

def save_config(config_data):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa cấu hình Google Sheets (secrets.toml).")
        return False
    try:
        df_save = pd.DataFrame([{"config_json": json.dumps(config_data, ensure_ascii=False)}])
        success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        if not success:
            st.error("⚠️ Lỗi: Không tìm thấy trang tính 'CONFIG' trên Google Sheets! Vui lòng mở Google Sheets, tạo một Sheet mới đặt tên là 'CONFIG', sau đó lưu lại.")
            return False
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False

def load_config():
    default_config = {
        "projects_by_category": {
            "BĐS & KDC": ["KDC Bàu Mạc", "KDC Nam Bàu Mạc", "KĐT Phước Lý & Phước Lý MR", "TĐC Phước Lý 2 & Hoà Liên 5", "Dự án Phong Nam", "Khu BT ST Hoà Ninh"],
            "HẠ TẦNG & GIAO THÔNG": ["Tuyến đường Lê Trọng Tấn", "Tuyến đường Lê Trọng Tấn - Hoà Nhơn", "Tuyến đường Trần Hưng Đạo (BT)", "Trục I Tây Bắc", "Khu TĐC Hoà Vang"],
            "THƯƠNG MẠI & KHÁCH SẠN": ["Khách sạn DMT-Group", "Du thuyền Happy Yacht (DMT Marina)"]
        },
        "departments": ["Ban Lãnh đạo", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán", "Ban Kế hoạch Đầu tư", "Ban Chuẩn bị Đầu tư", "Ban Kỹ thuật", "Ban Đền bù Giải tỏa", "Tổ KPI", "Ban chỉ huy Công trường", "Xí nghiệp xe máy thiết bị", "Ban Dự án", "Xí nghiệp DTBD", "Sàn GDBĐS"],
        "personnel_by_department": DEFAULT_PERSONNEL.copy(),
        "cv_gsheet_url": ""
    }
    
    conn = get_gsheets_conn()
    if conn is None:
        return default_config
        
    try:
        df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=600)
        if df is None or df.empty:
            return default_config
            
        json_str = df.iloc[0]["config_json"]
        data = json.loads(json_str)
        
        needs_save = False
        if "personnel_by_department" not in data:
            data["personnel_by_department"] = DEFAULT_PERSONNEL.copy()
            needs_save = True
            
        if "cv_gsheet_url" not in data:
            data["cv_gsheet_url"] = ""
            needs_save = True
            
        if needs_save:
            save_config(data)
            
        return data
    except Exception as e:
        pass
        return default_config

# Load current config dynamically
config = load_config()
PROJECTS_BY_CATEGORY = config.get("projects_by_category", {})
OFFICIAL_DEPARTMENTS = config.get("departments", [])

# Default owners by department and company for autofill
DEPT_LEADS = {
    "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG": {
        "Ban Lãnh đạo": "Trần Quốc Thể",
        "Ban Hành chính Nhân sự": "Nguyễn Thị Hạnh Tiên",
        "Ban Tài chính Kế toán": "Đồng Thị Nguyệt Nga",
        "Ban Kế hoạch Đầu tư": "Nguyễn Trần Thức",
        "Ban Chuẩn bị Đầu tư": "Hồ Văn Khoa",
        "Ban Kỹ thuật": "Nguyễn Văn Bồn",
        "Ban Đền bù Giải tỏa": "Nguyễn Ngọc Tôn",
        "Ban Dự án": "Nguyễn Đình Thắng",
        "Xí nghiệp DTBD": "Mai Văn Châu",
        "Sàn GDBĐS": "Ngô Thị Tâm",
        "Tổ KPI": ""
    },
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "Ban Lãnh đạo": "Thái Văn Thành",
        "Ban Hành chính Nhân sự": "Nguyễn Thị Mỹ Phương",
        "Ban Tài chính Kế toán": "Nguyễn Thị Ngọc Hà",
        "Ban Kỹ thuật": "Trần Văn Trọng",
        "Ban chỉ huy Công trường": "Nguyễn Phong Trung",
        "Xí nghiệp xe máy thiết bị": "Đặng Hiền",
        "Tổ KPI": ""
    },
    "CTY CP DMT - MARINA (Du thuyền Happy Yacht)": {
        "Ban Lãnh đạo": "Trần Cường",
        "Ban Hành chính Nhân sự": "Nguyễn Thị Hạnh Tiên",
        "Ban Tài chính Kế toán": "Lê Thị Hải",
        "Ban Kế hoạch Đầu tư": "Trần Cường",
        "Ban Chuẩn bị Đầu tư": "Lê Thị Hải",
        "Ban Kỹ thuật": "Trương Ngọc Sỹ",
        "Ban Đền bù Giải tỏa": "Thái Hữu Quý",
        "Tổ KPI": ""
    }
}

def get_personnel_for_company_dept(company, dept, config):
    is_marina = False
    is_traffic = False
    if isinstance(company, str):
        is_marina = "CTY CP DMT - MARINA" in company or "Du thuyền Happy Yacht" in company
        is_traffic = "XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT" in company
        
    if is_marina:
        if dept == "Ban Hành chính Nhân sự":
            return ["Nguyễn Thị Hạnh Tiên"]
        elif dept == "Ban Tài chính Kế toán":
            return ["Lê Thị Hải"]
        elif dept == "Ban Lãnh đạo":
            return ["Trần Cường", "Đặng Ngọc Hoàng"]
        elif dept == "Tổ KPI":
            return []
    elif is_traffic:
        if dept == "Ban Lãnh đạo":
            return ["Thái Văn Thành", "Trần Văn Trọng", "Đặng Thị Lan Ngọc"]
        elif dept == "Ban Kỹ thuật":
            return ["Trần Văn Trọng", "Phạm Quang Nghĩa"]
        elif dept == "Ban chỉ huy Công trường":
            return ["Nguyễn Phong Trung", "Phạm Văn Long", "Lê Đông"]
        elif dept == "Xí nghiệp xe máy thiết bị":
            return ["Đặng Hiền"]
        elif dept == "Ban Tài chính Kế toán":
            return ["Nguyễn Thị Ngọc Hà", "Nguyễn Thị Như Can"]
        elif dept == "Ban Hành chính Nhân sự":
            return ["Nguyễn Thị Mỹ Phương"]
        else:
            return []
    else:
        if dept == "Ban Hành chính Nhân sự":
            return ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Thị Tú Uyên"]
        elif dept == "Ban Tài chính Kế toán":
            return ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"]
        elif dept == "Tổ KPI":
            return []
            
    # Mặc định lấy từ cấu hình cho các phòng ban khác
    return config.get("personnel_by_department", {}).get(dept, [])

def get_departments_for_company(company, all_departments):
    is_marina = False
    is_traffic = False
    if isinstance(company, str):
        is_marina = "CTY CP DMT - MARINA" in company or "Du thuyền Happy Yacht" in company
        is_traffic = "XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT" in company
    if is_marina:
        # Chỉ hiển thị 3 ban, ẩn tất cả các ban còn lại
        allowed = ["Ban Lãnh đạo", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán"]
        return [d for d in all_departments if d in allowed]
    if is_traffic:
        allowed = ["Ban Lãnh đạo", "Ban Kỹ thuật", "Ban chỉ huy Công trường", "Xí nghiệp xe máy thiết bị", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán"]
        return [d for d in allowed]
        
    # For DMT (and any other), exclude CIENCO specific departments
    cienco_only = ["Ban chỉ huy Công trường", "Xí nghiệp xe máy thiết bị"]
    return [d for d in all_departments if d not in cienco_only]



def get_filtered_projects(company_name, all_projs, db_projs):
    merged = list(set(all_projs + db_projs))
    if not isinstance(company_name, str):
        return sorted(merged)
    
    is_marina = "CTY CP DMT - MARINA" in company_name or "Du thuyền Happy Yacht" in company_name
    marina_only_projs = ["Du thuyền Happy Yacht (DMT Marina)", "Du thuyền Happy Yacht", "HCNS", "TCKT"]
    happy_yacht_projs = ["Du thuyền Happy Yacht (DMT Marina)", "Du thuyền Happy Yacht"]
    
    if is_marina:
        return sorted([p for p in merged if p in marina_only_projs])
    else:
        # For other companies, hide Happy Yacht
        return sorted([p for p in merged if p not in happy_yacht_projs])

# Generate flat list for dropdowns (brief clean names)
ALL_PROJECTS = []
for cat, projs in PROJECTS_BY_CATEGORY.items():
    for p in projs:
        ALL_PROJECTS.append(p)

DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

# Gantt DB Configuration
GANTT_DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

def read_gantt_db():
    required_cols = ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "PhanTramHoanThanh", "Milestone", "QuanTrong", "KhanCap", "NgayCapNhat"]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="GANTT_KHDT", ttl=600)
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
        
    # Khởi tạo các cột thiếu
    for col in ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]:
        if col not in df.columns:
            df[col] = ""

            
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'], errors='coerce').dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'], errors='coerce').dt.date
    df['NgayCapNhat'] = pd.to_datetime(df['NgayCapNhat'], errors='coerce')
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
        df = safe_gsheets_read(conn, worksheet="KPI_ADJUSTMENTS", ttl=0)
        if df is None or df.empty:
            return empty_df
        for col in ["ID", "Thang", "Nam", "DiemDieuChinh"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        import streamlit as st
        st.error(f"Lỗi khi đọc trang tính KPI_ADJUSTMENTS: {e}")
        return empty_df

def add_kpi_adjustment(ten, thang, nam, loai, diem, lydo):
    import pandas as pd
    df = read_kpi_adjustments()
    new_id = 1 if df.empty else int(pd.to_numeric(df['ID'], errors='coerce').max(skipna=True) + 1 if not df['ID'].empty else 1)
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
                st.cache_data.clear()
                return True, ""
            else:
                return False, "Không thể cập nhật lên Google Sheets (lỗi đã ghi log)"
        except Exception as e:
            return False, str(e)
    return False, "Không kết nối được Google Sheets"

def save_gantt_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
        
        safe_gsheets_update(conn, worksheet="GANTT_KHDT", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
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
        
    # Load existing docs & tasks database
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
            
        so_ky_hieu = str(row[so_ky_hieu_col]).strip() if not pd.isna(row[so_ky_hieu_col]) else f"VB-{datetime.now().strftime('%M%S')}"
        co_quan_gui = str(row[mapping["ĐƠN VỊ"]]).strip() if mapping["ĐƠN VỊ"] and not pd.isna(row[mapping["ĐƠN VỊ"]]) else ""
        trich_yeu = str(row[content_col]).strip()
        
        ban_chu_tri_raw = str(row[mapping["Người/ Ban thực hiện"]]).strip() if mapping["Người/ Ban thực hiện"] and not pd.isna(row[mapping["Người/ Ban thực hiện"]]) else ""
        if ban_chu_tri_raw in OFFICIAL_DEPARTMENTS:
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
            if deadline_val < today:
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
                "DonVi": selected_company if selected_company != "Tất cả đơn vị" else "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG",
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
                "NgayCapNhat": datetime.now(),
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
            docs_df.at[idx, "NgayCapNhat"] = datetime.now()
            docs_df.at[idx, "GhiChu"] = ghi_chu
            update_count += 1
            
        # Update or create the associated Task in tasks_df
        task_name = f"📩 [Công văn đến] {trich_yeu} (Số: {so_ky_hieu})"
        duplicate_task = tasks_df[tasks_df['TenCongViec'].str.contains(so_ky_hieu, na=False)]
        
        task_status = "Đang thực hiện"
        if trang_thai == "✅ Đã xong":
            task_status = "Hoàn thành"
        elif deadline_val < today:
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
                "DonVi": selected_company if selected_company != "Tất cả đơn vị" else "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG",
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
                "NgayCapNhat": datetime.now(),
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
            tasks_df.at[t_idx, "NgayCapNhat"] = datetime.now()
            
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

        
    df['NgayBanHanh'] = pd.to_datetime(df['NgayBanHanh'], errors='coerce').dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'], errors='coerce').dt.date
    df['NgayCapNhat'] = pd.to_datetime(df['NgayCapNhat'], errors='coerce')
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
        df_save['NgayBanHanh'] = df_save['NgayBanHanh'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
        
        safe_gsheets_update(conn, worksheet="VAN_BAN_DEN", data=df_save)
        return True
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
        return False

def read_db():
    required_cols = [
        "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
        "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan", "TyTrongKPI"
    ]
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="Sheet1", ttl=600)
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


    # Check and initialize missing columns dynamically
    if "ChuKyTheoDoi" not in df.columns:
        df["ChuKyTheoDoi"] = "Theo dự án / Tự do"
    if "PhanLoaiTreHan" not in df.columns:
        df["PhanLoaiTreHan"] = "🟢 Không trễ hạn / Đúng tiến độ"
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # Clean data formats
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'], errors='coerce').dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline'], errors='coerce').dt.date
    df['NgayCapNhat'] = pd.to_datetime(df['NgayCapNhat'], errors='coerce')
    df['DonVi'] = df['DonVi'].fillna('CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
    df['TenDuAn'] = df['TenDuAn'].fillna('')
    df['MocTienDo'] = df['MocTienDo'].fillna('Tự do')
    df['SanPhamBanGiao'] = df['SanPhamBanGiao'].fillna('Xem chi tiết')
    df['LinkKetQua'] = df['LinkKetQua'].fillna('')
    df['GiaiTrinhDeXuat'] = df['GiaiTrinhDeXuat'].fillna('')
    df['ChuKyTheoDoi'] = df['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
    df['PhanLoaiTreHan'] = df['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
    df['ID'] = df['ID'].astype(str)
    
    for idx, row in df.iterrows():
        is_comp = str(row['TrangThai']).strip() == "Hoàn thành"
        start_d = row['NgayBatDau']
        end_d = row['Deadline']
        df.at[idx, 'PhanTramHoanThanh'] = calculate_time_progress(start_d, end_d, is_comp)
        
    return df

def save_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
        df_save['ChuKyTheoDoi'] = df_save['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
        
        df_save = df_save.fillna("")
        return safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)
    except Exception as e:
        st.error(f'Lỗi lưu Google Sheets: {e}')
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
st.markdown('<div class="main-title">⚓ DMT GROUP — QUẢN LÝ TIẾN ĐỘ</div>', unsafe_allow_html=True)

# Sidebar layout with logo image and fallback
logo_path = "logo.png" if os.path.exists("logo.png") else ("INPUT/logo.png" if os.path.exists("INPUT/logo.png") else None)
if logo_path:
    st.sidebar.image(logo_path, use_column_width=True)
else:
    st.sidebar.warning("💡 Vui lòng đặt file logo.png vào thư mục gốc của dự án để hiển thị logo.")
    st.sidebar.markdown("### ⚓ DMT GROUP")
st.sidebar.markdown("---")

# Link Google Sheets Config
st.sidebar.markdown("### 🔗 Kết Nối Google Sheets")
if "gsheet_url" not in st.session_state:
    st.session_state["gsheet_url"] = load_settings().get("gsheet_url", "")

gsheet_url_input = st.sidebar.text_input(
    "Link Google Sheets (DB chính)", 
    value=st.session_state["gsheet_url"], 
    placeholder="Dán link Google Sheets..."
)

if gsheet_url_input != st.session_state["gsheet_url"]:
    st.session_state["gsheet_url"] = gsheet_url_input
    settings = load_settings()
    settings["gsheet_url"] = gsheet_url_input
    save_settings(settings)
    st.cache_data.clear()
    st.rerun()


company_options = ["Tất cả đơn vị"] + list(COMPANIES.keys())
selected_company = st.sidebar.selectbox("CHỌN CÔNG TY / THÀNH VIÊN", company_options, index=1)

menu = st.sidebar.radio(
    "PHÂN HỆ CHỨC NĂNG",
    [
        "📊 Dashboard Tổng Quan",
        "📋 Bảng Tiến Độ Chi Tiết",
        "➕ Thêm / Cập Nhật Công Việc",
        "📊 SƠ ĐỒ GANTT DỰ ÁN DMT",
        "🏆 Đánh giá KPI & Xếp loại",
        "⚙️ Quản Lý Cấu HÌnh"
    ],
    index=0
)

st.sidebar.markdown("---")
role_mode = st.sidebar.selectbox("QUYỀN TRUY CẬP", ["Nhân viên", "Quản lý"], index=0)

if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False

if role_mode == "Quản lý":
    if not st.session_state.is_admin_authenticated:
        admin_pwd = st.sidebar.text_input("Nhập Mật khẩu Quản lý", type="password")
        if admin_pwd:
            if admin_pwd == "admindmt123":
                st.session_state.is_admin_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Mật khẩu không đúng!")
    
    if st.session_state.is_admin_authenticated:
        st.sidebar.success("Đã xác thực quyền Quản lý!")
        if st.sidebar.button("Đăng xuất"):
            st.session_state.is_admin_authenticated = False
            st.rerun()
else:
    st.session_state.is_admin_authenticated = False

st.sidebar.markdown("---")

# Current date
df = read_db()
gantt_df = read_gantt_db()
today = date.today()

# Filter display dataframe based on sidebar selected company
if selected_company != "Tất cả đơn vị":
    display_df = df
    
if 'NguoiChuTri' not in display_df.columns:
    display_df['NguoiChuTri'] = ''[df['DonVi'] == selected_company]
else:
    display_df = df
    
if 'NguoiChuTri' not in display_df.columns:
    display_df['NguoiChuTri'] = ''

# Statistics helpers
total_v = len(display_df)
done_v = len(display_df[display_df['TrangThai'] == 'Hoàn thành'])
issue_v = len(display_df[display_df['TrangThai'] == 'Có vướng mắc'])
overdue_v = len(display_df[(display_df['Deadline'] < today) & (display_df['TrangThai'] != 'Hoàn thành')])
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
            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
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
                if "chủ quan" in str(val).lower():
                    formatted_causes.append("[Do chủ quan]")
                elif "khách quan" in str(val).lower():
                    explain = row.get('GiaiTrinhDeXuat', '')
                    if explain and explain != "--" and str(explain).strip():
                        formatted_causes.append(f"[Do khách quan] - {str(explain).strip()}")
                    else:
                        formatted_causes.append("[Do khách quan]")
                else:
                    formatted_causes.append("")
                    
        tasks_df_copy['PhanLoaiTreHan'] = formatted_causes
        tasks_df_copy = tasks_df_copy.rename(columns={'PhanLoaiTreHan': 'Nguyên nhân trễ hạn'})
        
        if 'ID' in tasks_df_copy.columns:
            tasks_df_copy = tasks_df_copy.drop(columns=['ID'])
        if 'NgayCapNhat' in tasks_df_copy.columns:
            tasks_df_copy['NgayCapNhat'] = tasks_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
        tasks_df_copy.to_excel(writer, sheet_name="Sheet1", index=False)
        
        # Write GANTT_KHDT (Drop ID column if exists)
        df_copy = df.copy()
        if 'ID' in df_copy.columns:
            df_copy = df_copy.drop(columns=['ID'])
        if 'NgayCapNhat' in df_copy.columns:
            df_copy['NgayCapNhat'] = df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
        df_copy.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
        
        # Write VAN_BAN_DEN (Drop ID column if exists)
        try:
            docs_df = read_incoming_docs_db()
            docs_df_copy = docs_df.copy()
            if 'ID' in docs_df_copy.columns:
                docs_df_copy = docs_df_copy.drop(columns=['ID'])
            if 'NgayCapNhat' in docs_df_copy.columns:
                docs_df_copy['NgayCapNhat'] = docs_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (date, datetime)) else str(x))
            for col_name in ['NgayBanHanh', 'Deadline']:
                if col_name in docs_df_copy.columns:
                    docs_df_copy[col_name] = docs_df_copy[col_name].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (date, datetime)) else str(x))
            docs_df_copy = docs_df_copy.rename(columns={
                'SoKyHieu': 'Số / Ký hiệu văn bản',
                'NgayBanHanh': 'Ngày ban hành',
                'CoQuanGui': 'Cơ quan / Đơn vị gửi',
                'TrichYeu': 'Trích yếu nội dung',
                'TenDuAn': 'Dự án liên quan',
                'GanttTaskId': 'Mã CV Gantt liên kết',
                'BanChuTri': 'Bộ phận chủ trì xử lý',
                'Deadline': 'Hạn xử lý / Phản hồi',
                'LinkFile': 'Đính kèm Link / File',
                'TrangThai': 'Trạng thái xử lý',
                'NgayCapNhat': 'Thời gian cập nhật'
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
st.sidebar.markdown("### 📥 XUẤT DỮ LIỆU EXCEL")
try:
    df_for_excel = df
    styled_excel_data = generate_styled_excel(df, df_for_excel)
    st.sidebar.download_button(
        label="Tải xuống tệp Excel",
        data=styled_excel_data,
        file_name="DATA_TIEN_DO_KPI.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_sidebar_excel_dl"
    )
except Exception as e:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.sidebar.download_button(
                label="Tải xuống tệp Excel (Dự phòng)",
                data=f.read(),
                file_name="DATA_TIEN_DO_KPI.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_sidebar_excel_dl_fallback"
            )

# Sidebar Cloud Sync Status
st.sidebar.markdown("---")
st.sidebar.markdown("### ☁️ ĐỒNG BỘ CLOUD")
if is_gsheets_configured():
    st.sidebar.success("🟢 Google Sheets: Đã kết nối")
else:
    st.sidebar.warning("⚠️ Google Sheets: Chạy Offline")

# Helper function to clean project name whitespace
def clean_proj_name(name):
    return name.strip()

# ----------------- 1. DASHBOARD TỔNG QUAN -----------------
if menu == "📊 Dashboard Tổng Quan":
    st.markdown(f"### 📊 Dashboard Tổng Quan — {selected_company}")
    
    # 1. Filter cycle dropdown
    cycle_filter = st.selectbox(
        "📅 Lọc theo Chu kỳ theo dõi",
        ["Tất cả chu kỳ", "Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"],
        index=0
    )
    
    dash_df = display_df.copy()
    if cycle_filter != "Tất cả chu kỳ":
        dash_df = dash_df[dash_df['ChuKyTheoDoi'] == cycle_filter]
        
    # Overdue and due today/tomorrow alerts scanning (Group 1 & 2)
    def get_badge_and_urgency(deadline_val, today_dt):
        if not isinstance(deadline_val, date):
            if isinstance(deadline_val, datetime):
                deadline_val = deadline_val.date()
            else:
                return None, None
        if deadline_val < today_dt:
            days_late = (today_dt - deadline_val).days
            return f"🔴 [⚠️ Trễ {days_late} ngày]", 1
        elif deadline_val == today_dt:
            return "⏳ [Hạn hôm nay]", 2
        elif deadline_val == today_dt + timedelta(days=1):
            return "⚠️ [Hạn ngày mai]", 3
        return None, None

    alert_list = []
    for _, row in dash_df[dash_df['TrangThai'] != 'Hoàn thành'].iterrows():
        badge, urgency = get_badge_and_urgency(row['Deadline'], today)
        if badge:
            row_copy = row.copy()
            row_copy['Badge'] = badge
            row_copy['Urgency'] = urgency
            alert_list.append(row_copy)

    if alert_list:
        alert_df_show = pd.DataFrame(alert_list).sort_values(by=["Urgency", "Deadline"])
        st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(alert_df_show)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")
        alert_data = []
        for _, row in alert_df_show.iterrows():
            alert_data.append({
                "Ban phụ trách": row['PhongBan'],
                "Người phụ trách": row['NguoiChuTri'],
                "Dự án / Hạng mục": row['TenDuAn'],
                "Tên công việc": row['TenCongViec'],
                "Trạng thái thực tế": row['Badge']
            })
        st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        st.markdown("---")
    
    # Calculate stats based on filtered dash_df
    total_dash = len(dash_df)
    done_dash = len(dash_df[dash_df['TrangThai'] == 'Hoàn thành'])
    issue_dash = len(dash_df[dash_df['TrangThai'] == 'Có vướng mắc'])
    overdue_dash = len(dash_df[(dash_df['Deadline'] < today) & (dash_df['TrangThai'] != 'Hoàn thành')])
    doing_dash = total_dash - done_dash - issue_dash - overdue_dash
    if doing_dash < 0:
        doing_dash = 0
        
    # 4 metrics cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Tổng số việc", total_dash)
    with m_col2:
        st.metric("Đã xong", done_dash)
    with m_col3:
        st.metric("Đang làm", doing_dash)
    with m_col4:
        st.metric("🔴 Trễ hạn / Vướng mắc", issue_dash + overdue_dash)
        
    st.markdown("---")
    
    # Critical alert panel
    st.markdown("### ⚠️ Hạng mục cần lưu ý (Trễ hạn hoặc Sắp đến hạn)")
    
    if alert_list:
        alert_df_show = pd.DataFrame(alert_list).sort_values(by=["Urgency", "Deadline"])
        crit_display = pd.DataFrame()
        crit_display['Phòng ban'] = alert_df_show['PhongBan']
        crit_display['Người thực hiện'] = alert_df_show['NguoiChuTri']
        crit_display['Dự án / Hạng mục'] = alert_df_show['TenDuAn']
        crit_display['Tên công việc'] = alert_df_show['TenCongViec']
        crit_display['Hạn chót'] = alert_df_show['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (date, datetime)) else str(x))
        crit_display['Trạng thái thực tế'] = alert_df_show['Badge']
        crit_display['Ghi chú / Giải trình vướng mắc'] = alert_df_show['GiaiTrinhDeXuat']
        
        st.dataframe(
            crit_display,
            column_config={
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width="medium"),
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width="medium"),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Hạn chót": st.column_config.TextColumn("Hạn chót", width="small"),
                "Trạng thái thực tế": st.column_config.TextColumn("Trạng thái thực tế", width="small"),
                "Ghi chú / Giải trình vướng mắc": st.column_config.TextColumn("Ghi chú / Giải trình vướng mắc", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 Đảm bảo tiến độ: Không có công việc nào bị trễ hạn hoặc sắp đến hạn cần lưu ý!")
        
    st.markdown("---")


    
    # Performance Review Section
    st.markdown("### 📈 Bảng Đánh giá Hiệu suất (Performance Review)")
    st.markdown("*Hiệu suất trung bình (%) hoàn thành công việc theo từng Phòng ban & Chu kỳ:*")
    
    if not display_df.empty:
        perf_df = display_df.copy()
        
        # Ensure ChuKyTheoDoi has valid values
        perf_df['ChuKyTheoDoi'] = perf_df['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
        
        # Adjust progress for objective delay / on track so it doesn't deduct points
        # Only tasks with PhanLoaiTreHan == "👤 Do chủ quan" will keep their real (deducted) progress.
        # Other tasks (objective or on time) that are late will be treated as 100% to avoid deduction.
        for idx, row in perf_df.iterrows():
            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
            is_late = (row['Deadline'] < today) and not is_comp
            if is_late:
                if row.get('PhanLoaiTreHan') != "👤 Do chủ quan":
                    perf_df.at[idx, 'PhanTramHoanThanh'] = 100
        
        # Calculate pivot table
        try:
            perf_pivot = perf_df.pivot_table(
                index="PhongBan",
                columns="ChuKyTheoDoi",
                values="PhanTramHoanThanh",
                aggfunc="mean"
            ).fillna(0).astype(int)
            
            # Ensure all cycles are present
            for col in ["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]:
                if col not in perf_pivot.columns:
                    perf_pivot[col] = 0
            
            perf_pivot = perf_pivot[["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]]
            perf_pivot = perf_pivot.reset_index()
            perf_pivot.columns = ["Phòng ban", "Chu kỳ Tuần (%)", "Chu kỳ Tháng (%)", "Chu kỳ Quý (%)", "Dự án / Tự do (%)"]
            
            st.dataframe(
                perf_pivot,
                column_config={
                    "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                    "Chu kỳ Tuần (%)": st.column_config.ProgressColumn("Chu kỳ Tuần", format="%d%%", min_value=0, max_value=100),
                    "Chu kỳ Tháng (%)": st.column_config.ProgressColumn("Chu kỳ Tháng", format="%d%%", min_value=0, max_value=100),
                    "Chu kỳ Quý (%)": st.column_config.ProgressColumn("Chu kỳ Quý", format="%d%%", min_value=0, max_value=100),
                    "Dự án / Tự do (%)": st.column_config.ProgressColumn("Dự án / Tự do", format="%d%%", min_value=0, max_value=100)
                },
                use_container_width=True,
                hide_index=True
            )
        except Exception as pe:
            st.info(f"Không thể hiển thị bảng hiệu suất: {pe}")
    else:
        st.info("Chưa có dữ liệu để đánh giá hiệu suất.")

# ----------------- 2. BẢNG TIẾN ĐỘ CHI TIẾT -----------------
elif menu == "📋 Bảng Tiến Độ Chi Tiết":
    st.markdown(f"### 📋 Bảng Tiến Độ Công Việc Chi Tiết — {selected_company}")
    
    # Filter tools for Boss
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
        merged_projs = get_filtered_projects(selected_company, ALL_PROJECTS, db_projs)
        proj_options = ["Tất cả dự án"] + merged_projs
        sel_proj_filter = st.selectbox("Lọc nhanh theo Dự án / Hạng mục", proj_options)
        
    with col_filter2:
        allowed_depts = get_departments_for_company(selected_company, OFFICIAL_DEPARTMENTS)
        dept_options = ["Tất cả phòng ban"] + allowed_depts
        sel_dept_filter = st.selectbox("Lọc nhanh theo Phòng ban", dept_options)
        
    with col_filter3:
        months = set()
        if not display_df.empty:
            for _, row in display_df.iterrows():
                if pd.notna(row.get('NgayBatDau')) and hasattr(row['NgayBatDau'], 'strftime'):
                    months.add(row['NgayBatDau'].strftime('%m/%Y'))
                if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                    months.add(row['Deadline'].strftime('%m/%Y'))
        month_options = ["Tất cả các tháng"] + sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        sel_month_filter = st.selectbox("Lọc nhanh theo Tháng", month_options)
        
    # Apply filters
    table_df = display_df.copy()
    if sel_proj_filter != "Tất cả dự án":
        clean_proj = clean_proj_name(sel_proj_filter)
        table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
        
    if sel_dept_filter != "Tất cả phòng ban":
        table_df = table_df[table_df['PhongBan'] == sel_dept_filter]
        
    if sel_month_filter != "Tất cả các tháng":
        target_month = sel_month_filter
        mask = (
            table_df['NgayBatDau'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
        ) | (
            table_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == target_month
        )
        table_df = table_df[mask]
        
    if table_df.empty:
        st.info("Không có công việc nào phù hợp với bộ lọc.")
    else:
        df_display = pd.DataFrame()
        df_display['Phòng ban'] = table_df['PhongBan']
        df_display['Người thực hiện'] = table_df['NguoiChuTri']
        df_display['Dự án / Hạng mục'] = table_df['TenDuAn']
        df_display['Tên công việc'] = table_df['TenCongViec']
        df_display['Ngày bắt đầu'] = table_df['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (date, datetime)) else str(x))
        
        # Format Hạn chót
        def format_dl(row):
            prog = int(row['PhanTramHoanThanh'])
            date_str = row['Deadline'].strftime('%d/%m/%Y')
            
            if prog >= 100:
                return date_str
            
            # prog < 100
            days_left = (row['Deadline'] - today).days
            if days_left < 0:
                days_late = abs(days_left)
                return f"🔴 {date_str} (Trễ hạn {days_late} ngày)"
            elif days_left == 0:
                return f"⏳ {date_str} (Hạn hôm nay)"
            elif 1 <= days_left <= 3:
                return f"⚠️ {date_str} (Sắp hạn - Còn {days_left} ngày)"
            else:
                return date_str
        df_display['Hạn chót'] = table_df.apply(format_dl, axis=1)
        
        df_display['Tiến độ'] = table_df['PhanTramHoanThanh']
        
        # Format Trạng thái
        def format_status(row):
            prog = int(row['PhanTramHoanThanh'])
            is_issue = row['TrangThai'] == 'Có vướng mắc'
            
            if prog >= 100:
                return "✅ Đã xong"
                
            # prog < 100
            if row['Deadline'] < today:
                return "⚠️ Trễ hạn"
                
            if is_issue:
                return "🔴 Vướng mắc"
                
            if prog == 0 and row['NgayBatDau'] > today:
                return "❌ Chưa bắt đầu"
                
            # Default state based on start date
            if today >= row['NgayBatDau']:
                return "⏳ Đang thực hiện"
            else:
                return "❌ Chưa bắt đầu"
        df_display['Trạng thái'] = table_df.apply(format_status, axis=1)
        
        # Format Nguyên nhân trễ hạn
        def format_late_cause(row):
            is_comp = (row['TrangThai'] == 'Hoàn thành')
            is_late = (row['Deadline'] < today) and not is_comp
            if not is_late:
                return "--"
            
            val = row.get('PhanLoaiTreHan', '')
            if "chủ quan" in str(val).lower():
                return "🔴 [Do chủ quan]"
            elif "khách quan" in str(val).lower():
                explain = row.get('GiaiTrinhDeXuat', '')
                if explain and explain.strip():
                    return f"⚠️ [Do khách quan] - {explain.strip()}"
                return "⚠️ [Do khách quan]"
            else:
                return "--"
        df_display['Nguyên nhân trễ hạn'] = table_df.apply(format_late_cause, axis=1)
        
        # Format Kết quả / File đính kèm
        def format_notes(row):
            is_comp = (row['TrangThai'] == 'Hoàn thành')
            if is_comp:
                val = row['LinkKetQua']
                if not val or pd.isna(val):
                    return "Chưa đính kèm kết quả"
                if isinstance(val, str) and val.startswith("OUTPUT"):
                    display_name = os.path.basename(val)
                    if "_" in display_name:
                        display_name = display_name.split("_", 1)[1]
                    return f"📁 {display_name}"
                return str(val)
            else:
                return row['GiaiTrinhDeXuat'] if (isinstance(row['GiaiTrinhDeXuat'], str) and row['GiaiTrinhDeXuat']) else "--"
        df_display['Kết quả / File đính kèm'] = table_df.apply(format_notes, axis=1)
        
        # Render clean st.dataframe
        st.dataframe(
            df_display,
            column_config={
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width="medium"),
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width="medium"),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Ngày bắt đầu": st.column_config.TextColumn("Ngày bắt đầu", width="small"),
                "Hạn chót": st.column_config.TextColumn("Hạn chót", width="medium"),
                "Tiến độ": st.column_config.ProgressColumn(
                    "Tiến độ",
                    format="%d%%",
                    min_value=0,
                    max_value=100
                ),
                "Trạng thái": st.column_config.TextColumn("Trạng thái", width="small"),
                "Nguyên nhân trễ hạn": st.column_config.TextColumn("Nguyên nhân trễ hạn", width="medium"),
                "Kết quả / File đính kèm": st.column_config.LinkColumn(
                    "Kết quả / File đính kèm",
                    max_chars=300
                )
            },
            use_container_width=True,
            hide_index=True
        )

# ----------------- 3. THÊM / CẬP NHẬT CÔNG VIỆC -----------------
elif menu == "➕ Thêm / Cập Nhật Công Việc":
    st.markdown("### ✏️ Phân hệ Thêm / Cập Nhật Công Việc")
    
    tab_new, tab_update = st.tabs(["➕ Khởi tạo công việc mới", "✏️ Cập nhật tiến độ công việc"])
    
    # Form: Add New
    with tab_new:
        st.markdown("#### Thêm mới công việc tự do")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. Company selection
            company_list = list(COMPANIES.keys())
            default_company_idx = 0
            if selected_company in company_list:
                default_company_idx = company_list.index(selected_company)
            entry_company = st.selectbox("Đơn vị / Công ty thành viên", company_list, index=default_company_idx)
            
            # 4. Department
            allowed_depts = get_departments_for_company(entry_company, OFFICIAL_DEPARTMENTS)
            task_dept = st.selectbox("Phòng ban chịu trách nhiệm", allowed_depts)
            
            # 5. Owner (based on configuration with custom type option)
            dept_personnel = get_personnel_for_company_dept(entry_company, task_dept, config)
            owner_options = list(dept_personnel) + ["✍️ Nhập tên người khác..."]
            
            # Find default lead index if present in department personnel
            dept_lead = DEPT_LEADS.get(entry_company, {}).get(task_dept, "")
            default_lead_idx = 0
            if dept_lead in dept_personnel:
                default_lead_idx = dept_personnel.index(dept_lead)
            
            sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", owner_options, index=default_lead_idx)
            if sel_owner_opt == "✍️ Nhập tên người khác...":
                task_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value="")
            else:
                task_owner = sel_owner_opt
            
            # 2. Project selection (Categorized dropdown or custom)
            is_marina_co = "CTY CP DMT - MARINA" in entry_company or "Du thuyền Happy Yacht" in entry_company
            if False:
                proj_options_with_custom = ["➕ Tạo / Nhập Dự án mới..."]
            else:
                db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
                merged_projs = get_filtered_projects(entry_company, ALL_PROJECTS, db_projs)
                proj_options_with_custom = merged_projs + ["✍️ Tự nhập Dự án / Hạng mục khác..."]
                
            default_proj_opt = st.selectbox("Dự án / Hạng mục", proj_options_with_custom)
            
            if is_marina_co or default_proj_opt in ["✍️ Tự nhập Dự án / Hạng mục khác...", "➕ Tạo / Nhập Dự án mới..."]:
                project_name = st.text_input("Nhập tên Dự án / Hạng mục mới", value="")
            else:
                project_name = clean_proj_name(default_proj_opt)
            
            # 3. Task details
            task_name = st.text_input("Tên công việc (tự nhập tự do)", value="")
            
        with col2:
            # 6. Dates
            task_start = st.date_input("Ngày bắt đầu thực hiện", today, format="DD/MM/YYYY")
            task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today + timedelta(days=7), format="DD/MM/YYYY")
            
            # 7. Completed flag instead of manual progress slider
            task_is_completed = st.checkbox("Đã hoàn thành công việc", value=False)
            
            # 8. Issue flag
            task_has_issue = st.checkbox("Công việc đang gặp vướng mắc, cần hỗ trợ", value=False)
            
            # 9. Kết quả / File đính kèm
            st.markdown("**Kết quả / File đính kèm**")
            result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key="new_result_mode")
            if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                task_link_text = st.text_input("Nhập tên Báo cáo / Số hiệu Văn bản / Link", placeholder="https://... hoặc Báo cáo số 01/BC-DMT", key="new_result_text")
                task_file = None
            else:
                task_file = st.file_uploader("Tải file đính kèm (PDF, Word, Excel, Ảnh...)", key="new_result_file")
                task_link_text = ""
            
            # 10. Ghi chú vướng mắc
            is_late = (task_deadline < today) and not task_is_completed
            task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
            if is_late:
                task_late_cause = st.selectbox(
                    "Phân loại nguyên nhân trễ hạn",
                    ["🟢 Không trễ hạn / Đúng tiến độ", "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                    index=0,
                    key="new_task_late_cause"
                )
                if task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                    task_explain = st.text_area("Nội dung nguyên nhân khách quan & Phương án xử lý (Bắt buộc)", placeholder="Mô tả chi tiết khó khăn, nguyên nhân khách quan và phương án xử lý...", key="new_task_explain")
                else:
                    task_explain = ""
            else:
                if task_has_issue:
                    task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", key="new_task_explain")
                else:
                    task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Không bắt buộc)", placeholder="Mô tả chi tiết khó khăn...", key="new_task_explain")
            
            # 11. Chu kỳ theo dõi
            task_cycle = st.selectbox("Chu kỳ theo dõi", ["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"], index=3)
            
            # 12. Tỷ trọng KPI
            task_weight = st.number_input("Tỷ trọng KPI (%) (0 = Tự chia đều)", min_value=0, max_value=100, value=0)
            
        submit_new = st.button("💾 THÊM CÔNG VIỆC MỚI", type="primary")
        
        if submit_new:
            if not task_name.strip():
                st.error("⚠️ Vui lòng nhập Tên công việc!")
            elif not task_owner.strip():
                st.error("⚠️ Vui lòng nhập Người thực hiện!")
            else:
                # Calculate status and progress automatically
                if task_is_completed:
                    calc_status = "Hoàn thành"
                elif task_has_issue:
                    calc_status = "Có vướng mắc"
                elif task_deadline < today:
                    calc_status = "Quá hạn"
                elif today >= task_start:
                    calc_status = "Đang thực hiện"
                else:
                    calc_status = "Chưa bắt đầu"
                    
                task_progress = calculate_time_progress(task_start, task_deadline, task_is_completed)
                    
                # Constraints validation
                has_error = False
                if calc_status == "Hoàn thành":
                    if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)" and not task_link_text.strip():
                        st.error("⚠️ Bắt buộc điền 'Kết quả / File đính kèm'!")
                        has_error = True
                    elif result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and task_file is None:
                        st.error("⚠️ Bắt buộc tải file đính kèm!")
                        has_error = True
                        
                if is_late:
                    if task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                        if not task_explain.strip() or len(task_explain.strip()) < 5:
                            st.error("⚠️ Bắt buộc nhập chi tiết 'Nội dung nguyên nhân khách quan & Phương án xử lý' (tối thiểu 5 ký tự)!")
                            has_error = True
                elif calc_status == "Có vướng mắc":
                    if not task_explain.strip() or len(task_explain.strip()) < 5:
                        st.error("⚠️ Bắt buộc điền 'Ghi chú / Giải trình vướng mắc' chi tiết!")
                        has_error = True
                        
                if not has_error:
                    # Auto ID generator
                    next_id = 1
                    if not df.empty:
                        ids = df['ID'].tolist()
                        nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                        if nums:
                            next_id = max(nums) + 1
                    task_id = f"TSK-{next_id:03d}"
                    
                    saved_result = ""
                    if calc_status == "Hoàn thành":
                        if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            saved_result = task_link_text.strip()
                        elif result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and task_file is not None:
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
                        "MocTienDo": "Tự do",
                        "SanPhamBanGiao": "Xem chi tiết",
                        "TenCongViec": task_name.strip(),
                        "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
                        "NgayBatDau": task_start,
                        "Deadline": task_deadline,
                        "DoUuTien": "Trung bình",
                        "PhanTramHoanThanh": task_progress,
                        "TrangThai": calc_status,
                        "LinkKetQua": saved_result,
                        "GiaiTrinhDeXuat": task_explain.strip() if ((is_late and task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)") or (not is_late and calc_status == "Có vướng mắc")) else "",
                        "NgayCapNhat": datetime.now(),
                        "ChuKyTheoDoi": task_cycle,
                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                    }
                    
                    df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_db(df_updated):
                        st.success(f"🎉 Đã khởi tạo thành công công việc mã: {task_id}!")
                        st.cache_data.clear()
                        st.rerun()

    # Form: Update Progress
    with tab_update:
        st.markdown("#### Cập nhật tiến độ công việc đang chạy")
        
        # Display only items matching selected company
        avail_update_df = display_df
        
        # Filter by Department
        departments = ["Tất cả"] + sorted(list(avail_update_df['PhongBan'].dropna().unique()))
        filter_dept = st.selectbox("Lọc theo Phòng/Ban (Tuỳ chọn)", departments, key="filter_dept_update")
        
        if filter_dept != "Tất cả":
            avail_update_df = avail_update_df[avail_update_df['PhongBan'] == filter_dept]

        if avail_update_df.empty:
            st.info("Chưa có công việc nào khả dụng.")
        else:
            def format_task_option(task_id):
                row = df[df['ID'] == task_id].iloc[0]
                pic = row.get('NguoiChuTri', 'Chưa rõ')
                return f"{row['TenCongViec']} - Phụ trách: {pic}"
            
            selected_id = st.selectbox("Chọn công việc cần cập nhật", avail_update_df['ID'].tolist(), format_func=format_task_option)
            task_data = df[df['ID'] == selected_id].iloc[0]
            
            with st.container():
                col_u1, col_u2 = st.columns(2)
                
                with col_u1:
                    st.markdown(f"**Mã Hạng mục:** `{task_data['ID']}`")
                    st.markdown(f"**Đơn vị:** {task_data['DonVi']}")
                    st.markdown(f"**Phòng ban phụ trách:** {task_data['PhongBan']}")
                    
                    u_proj = st.text_input("Dự án / Hạng mục", value=task_data['TenDuAn'], key=f"u_proj_{task_data['ID']}")
                    u_name = st.text_input("Tên công việc", value=task_data['TenCongViec'], key=f"u_name_{task_data['ID']}")
                    
                    # Owner selection based on configuration
                    u_dept = task_data['PhongBan']
                    u_dept_personnel = get_personnel_for_company_dept(task_data['DonVi'], u_dept, config)
                    u_owner_options = list(u_dept_personnel) + ["✍️ Nhập tên người khác..."]
                    
                    current_owner = task_data['NguoiChuTri']
                    if current_owner in u_dept_personnel:
                        u_default_index = u_dept_personnel.index(current_owner)
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                        if u_sel_owner_opt == "✍️ Nhập tên người khác...":
                            u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value="", key=f"u_owner_custom_{task_data['ID']}")
                        else:
                            u_owner = u_sel_owner_opt
                    else:
                        u_default_index = len(u_owner_options) - 1
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key=f"u_owner_sel_{task_data['ID']}")
                        u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value=current_owner, key=f"u_owner_custom_{task_data['ID']}")
                    
                with col_u2:
                    u_start = st.date_input("Ngày bắt đầu thực hiện", value=task_data['NgayBatDau'], format="DD/MM/YYYY", key=f"u_start_{task_data['ID']}")
                    u_deadline = st.date_input("Hạn hoàn thành (Deadline)", value=task_data['Deadline'], format="DD/MM/YYYY", key=f"u_deadline_{task_data['ID']}")
                    
                    default_is_completed = task_data['TrangThai'] == 'Hoàn thành'
                    u_is_completed = st.checkbox("Đã hoàn thành công việc", value=default_is_completed, key=f"u_is_completed_{task_data['ID']}")
                    
                    default_has_issue = task_data['TrangThai'] == 'Có vướng mắc'
                    u_has_issue = st.checkbox("Công việc gặp vướng mắc, cần hỗ trợ", value=default_has_issue, key=f"u_has_issue_{task_data['ID']}")
                    
                    # 11. Chu kỳ theo dõi
                    current_cycle = task_data.get('ChuKyTheoDoi', 'Theo dự án / Tự do')
                    cycle_list = ["Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"]
                    default_cycle_idx = cycle_list.index(current_cycle) if current_cycle in cycle_list else 3
                    u_cycle = st.selectbox("Chu kỳ theo dõi", cycle_list, index=default_cycle_idx, key=f"u_cycle_sel_{task_data['ID']}")
                    
                    try:
                        current_weight = int(float(str(task_data.get('TyTrongKPI', 0)).strip() or 0))
                    except:
                        current_weight = 0
                    u_weight = st.number_input("Tỷ trọng KPI (%) (0 = Tự chia đều)", min_value=0, max_value=100, value=current_weight, key=f"u_weight_{task_data['ID']}")
                    
                st.markdown("#### ⚓ THÔNG TIN RÀNG BUỘC KẾT QUẢ & GIẢI TRÌNH")
                col_ub1, col_ub2 = st.columns(2)
                
                with col_ub1:
                    st.markdown("**Kết quả / File đính kèm hiện tại**")
                    current_link = task_data['LinkKetQua']
                    if current_link:
                        if isinstance(current_link, str) and current_link.startswith("OUTPUT") and os.path.exists(current_link):
                            display_name = os.path.basename(current_link)
                            if "_" in display_name:
                                display_name = display_name.split("_", 1)[1]
                            st.write(f"📁 **File:** `{display_name}`")
                            with open(current_link, "rb") as f:
                                st.download_button(
                                    label="📥 Tải file kết quả hiện tại",
                                    data=f.read(),
                                    file_name=display_name,
                                    mime="application/octet-stream",
                                    key=f"btn_download_file_{task_data['ID']}"
                                )
                        else:
                            st.write(f"✍️ **Nội dung:** `{current_link}`")
                    else:
                        st.write("*(Chưa có kết quả/file đính kèm)*")
                    
                    st.markdown("---")
                    st.markdown("**Cập nhật Kết quả / File đính kèm**")
                    u_result_mode = st.radio("Hình thức nộp", ["Giữ nguyên hiện tại", "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                    
                    u_link_text = ""
                    u_file = None
                    if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                        u_link_text = st.text_input("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", key=f"u_result_text_{task_data['ID']}")
                    elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                        u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")
                        
                with col_ub2:
                    u_is_late = (u_deadline < today) and not u_is_completed
                    u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if u_is_late:
                        u_options = ["🟢 Không trễ hạn / Đúng tiến độ", "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                        u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                        u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                        u_late_cause = st.selectbox(
                            "Phân loại nguyên nhân trễ hạn",
                            u_options,
                            index=u_default_idx,
                            key=f"u_late_cause_sel_{task_data['ID']}"
                        )
                        if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            u_explain = st.text_area("Nội dung nguyên nhân khách quan & Phương án xử lý (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                        else:
                            u_explain = ""
                    else:
                        if u_has_issue:
                            u_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                        else:
                            u_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Không bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                    
                btn_save, btn_del = st.columns([4, 1])
                with btn_save:
                    save_click = st.button("💾 LƯU CẬP NHẬT TIẾN ĐỘ", type="primary", key=f"btn_save_update_{task_data['ID']}")
                with btn_del:
                    del_click = st.button("🗑️ XÓA CÔNG VIỆC CHỌN", type="secondary", key=f"btn_del_update_{task_data['ID']}")
                    
                if save_click:
                    # Calculate status and progress automatically
                    if u_is_completed:
                        u_status = "Hoàn thành"
                    elif u_has_issue:
                        u_status = "Có vướng mắc"
                    elif u_deadline < today:
                        u_status = "Quá hạn"
                    elif today >= u_start:
                        u_status = "Đang thực hiện"
                    else:
                        u_status = "Chưa bắt đầu"
                        
                    u_progress = calculate_time_progress(u_start, u_deadline, u_is_completed)
                        
                    # Constraints validation
                    has_error = False
                    if u_status == "Hoàn thành":
                        if u_result_mode == "Giữ nguyên hiện tại" and not current_link:
                            st.error("⚠️ Bắt buộc điền 'Kết quả / File đính kèm' để hoàn thành công việc!")
                            has_error = True
                        elif u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)" and not u_link_text.strip():
                            st.error("⚠️ Bắt buộc điền 'Kết quả / File đính kèm' để hoàn thành công việc!")
                            has_error = True
                        elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and u_file is None:
                            st.error("⚠️ Bắt buộc tải file đính kèm để hoàn thành công việc!")
                            has_error = True
                            
                    if u_is_late:
                        if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            if not u_explain.strip() or len(u_explain.strip()) < 5:
                                st.error("⚠️ Bắt buộc nhập chi tiết 'Nội dung nguyên nhân khách quan & Phương án xử lý' (tối thiểu 5 ký tự)!")
                                has_error = True
                    elif u_status == "Có vướng mắc":
                        if not u_explain.strip() or len(u_explain.strip()) < 5:
                            st.error("⚠️ Bắt buộc điền 'Ghi chú / Giải trình vướng mắc' chi tiết!")
                            has_error = True
                            
                    if not has_error:
                        # Determine final link value
                        final_link = current_link
                        if u_status != "Hoàn thành":
                            final_link = ""
                        else:
                            if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                                final_link = u_link_text.strip()
                            elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)" and u_file is not None:
                                upload_dir = os.path.join("OUTPUT", "UPLOADED_FILES")
                                if not os.path.exists(upload_dir):
                                    os.makedirs(upload_dir, exist_ok=True)
                                safe_name = re.sub(r'[^\w\-_.]', '_', u_file.name)
                                file_name = f"{selected_id}_{safe_name}"
                                file_path = os.path.join(upload_dir, file_name)
                                with open(file_path, "wb") as f:
                                    f.write(u_file.getbuffer())
                                final_link = file_path
                                
                        df.loc[df['ID'] == selected_id, 'TenDuAn'] = u_proj.strip()
                        df.loc[df['ID'] == selected_id, 'TenCongViec'] = u_name.strip()
                        df.loc[df['ID'] == selected_id, 'NguoiChuTri'] = u_owner.strip()
                        df.loc[df['ID'] == selected_id, 'NgayBatDau'] = u_start
                        df.loc[df['ID'] == selected_id, 'Deadline'] = u_deadline
                        df.loc[df['ID'] == selected_id, 'PhanTramHoanThanh'] = u_progress
                        df.loc[df['ID'] == selected_id, 'TrangThai'] = u_status
                        df.loc[df['ID'] == selected_id, 'LinkKetQua'] = final_link
                        df.loc[df['ID'] == selected_id, 'GiaiTrinhDeXuat'] = u_explain.strip() if ((u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)") or (not u_is_late and u_status == "Có vướng mắc")) else ""
                        df.loc[df['ID'] == selected_id, 'NgayCapNhat'] = datetime.now()
                        df.loc[df['ID'] == selected_id, 'ChuKyTheoDoi'] = u_cycle
                        df.loc[df['ID'] == selected_id, 'PhanLoaiTreHan'] = u_late_cause if u_is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                        df.loc[df['ID'] == selected_id, 'TyTrongKPI'] = u_weight
                        
                        if save_db(df):
                            st.success(f"🎉 Đã lưu cập nhật công việc mã: {selected_id}!")
                            st.cache_data.clear()
                            st.rerun()
                            
                if del_click:
                    df_after_del = df[df['ID'] != selected_id]
                    if save_db(df_after_del):
                        st.success(f"🗑️ Đã xóa thành công công việc mã: {selected_id}!")
                        st.cache_data.clear()
                        st.rerun()

                st.markdown("---")
                with st.expander("🔄 Tái tạo công việc định kỳ (Nhân bản cho kỳ sau)"):
                    st.info("Tính năng này giúp nhân bản công việc hiện tại thành một công việc mới cho kỳ tiếp theo (dành cho các báo cáo tuần, giao ban tháng...).")
                    
                    rep_name = st.text_input("Tên công việc mới", value=f"{task_data['TenCongViec']} (Kỳ tiếp theo)", key=f"rep_name_{task_data['ID']}")
                    
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
                        rep_start = st.date_input("Ngày bắt đầu mới", value=default_start, key=f"rep_start_{task_data['ID']}")
                    with col_rep2:
                        rep_deadline = st.date_input("Hạn chót mới", value=default_deadline, key=f"rep_deadline_{task_data['ID']}")
                        
                    if st.button("🔄 TẠO CÔNG VIỆC CHO KỲ SAU", type="primary", key=f"btn_rep_{task_data['ID']}"):
                        next_id = 1
                        if not df.empty:
                            ids = df['ID'].tolist()
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
                            "MocTienDo": "Tự do",
                            "SanPhamBanGiao": "Xem chi tiết",
                            "TenCongViec": rep_name.strip(),
                            "PhanLoaiChiSo": "Chỉ số kết quả (Outcome Metric)",
                            "NgayBatDau": rep_start,
                            "Deadline": rep_deadline,
                            "DoUuTien": "Trung bình",
                            "PhanTramHoanThanh": 0,
                            "TrangThai": "Chưa bắt đầu" if today < rep_start else "Đang thực hiện",
                            "LinkKetQua": "",
                            "GiaiTrinhDeXuat": "",
                            "NgayCapNhat": datetime.now(),
                            "ChuKyTheoDoi": task_data['ChuKyTheoDoi'],
                            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ"
                        }
                        
                        df_rep = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        if save_db(df_rep):
                            st.success(f"🎉 Đã nhân bản thành công công việc mới mã: {new_id}!")
                            st.cache_data.clear()
                            st.rerun()

# ----------------- 4. SƠ ĐỒ GANTT DỰ ÁN KHĐT -----------------
elif menu == "📊 SƠ ĐỒ GANTT DỰ ÁN DMT":
    st.markdown("### 📊 Phân hệ Sơ đồ Gantt Dự án DMT")
    
    
    # 1. Select project (alphabetical order A-Z with default projects)
    is_marina_gantt = "CTY CP DMT - MARINA" in selected_company or "Du thuyền Happy Yacht" in selected_company
    
    if is_marina_gantt:
        gantt_project_options = ["➕ Tạo / Nhập Dự án mới..."]
    else:
        existing_db_projects = list(gantt_df['TenDuAn'].unique())
        existing_projects = get_filtered_projects(selected_company, ALL_PROJECTS, existing_db_projects)
        gantt_project_options = existing_projects + ["➕ Tạo Dự án KHĐT mới..."]
    
    selected_gantt_project = st.selectbox("Chọn Dự án KHĐT", gantt_project_options)
    
    if selected_gantt_project in ["➕ Tạo / Nhập Dự án mới...", "➕ Tạo Dự án KHĐT mới..."]:
        gantt_project_name = st.text_input("Tên Dự án KHĐT mới", value="")
    else:
        gantt_project_name = selected_gantt_project
        
    if gantt_project_name.strip():
        # Filter data for this project
        project_tasks_df = gantt_df[gantt_df['TenDuAn'] == gantt_project_name]
        
        # Overdue and due today/tomorrow alerts scanning for Gantt tasks (Group 1 & 2)
        ref_today = date.today()
        gantt_warn_list = []
        for _, row in project_tasks_df[project_tasks_df['PhanTramHoanThanh'] < 100].iterrows():
            deadline_val = row['Deadline']
            if isinstance(deadline_val, datetime):
                deadline_val = deadline_val.date()
                
            if deadline_val < ref_today:
                days_late = (ref_today - deadline_val).days
                badge = f"🔴 [⚠️ Trễ {days_late} ngày]"
                urgency = 1
            elif deadline_val == ref_today:
                badge = "⏳ [Hạn hôm nay]"
                urgency = 2
            elif deadline_val == ref_today + timedelta(days=1):
                badge = "⚠️ [Hạn ngày mai]"
                urgency = 3
            else:
                badge = None
                
            if badge:
                row_copy = row.copy()
                row_copy['Badge'] = badge
                row_copy['Urgency'] = urgency
                gantt_warn_list.append(row_copy)
                
        if gantt_warn_list:
            gantt_warn_df = pd.DataFrame(gantt_warn_list).sort_values(by=["Urgency", "Deadline"])
            st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(gantt_warn_df)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")
            g_alert_data = []
            for _, row in gantt_warn_df.iterrows():
                g_alert_data.append({
                    "Tên công việc": row['TenCongViec'],
                    "Giai đoạn": row['GiaiDoan'],
                    "Tiến độ hiện tại": f"{row['PhanTramHoanThanh']}%",
                    "Hạn chót": row['Deadline'].strftime('%d/%m/%Y') if isinstance(row['Deadline'], (date, datetime)) else str(row['Deadline']),
                    "Trạng thái thực tế": row['Badge']
                })
            st.dataframe(pd.DataFrame(g_alert_data), use_container_width=True, hide_index=True)
            st.markdown("---")
        
        # Sort and render Gantt chart if there is data
        if not project_tasks_df.empty:
            # Summary metric cards
            total_tasks = len(project_tasks_df)
            milestones_count = len(project_tasks_df[project_tasks_df['Milestone'].astype(str).str.strip() != ""])
            avg_progress = int(project_tasks_df['PhanTramHoanThanh'].mean()) if total_tasks > 0 else 0
            
            st.markdown("#### 📊 Tóm tắt chỉ số dự án")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Tổng số công việc", f"{total_tasks} việc")
            with col_m2:
                st.metric("Cột mốc quan trọng", f"{milestones_count} mốc")
            with col_m3:
                st.metric("Tiến độ trung bình", f"{avg_progress}%")
            
            # Sort tasks on Y-axis by Giai Doan (1 -> 8) and then by start date
            phase_order = [
                "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                "2. Pháp lý Dự án & Quy hoạch 1/500",
                "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                "Khác"
            ]
            project_tasks_df['GiaiDoan'] = pd.Categorical(project_tasks_df['GiaiDoan'], categories=phase_order, ordered=True)
            project_tasks_df = project_tasks_df.sort_values(by=["GiaiDoan", "NgayBatDau"], ascending=[True, True])
            
            # Form progress label text for Gantt bars
            project_tasks_df['Tiến độ %'] = project_tasks_df['PhanTramHoanThanh'].apply(lambda x: f"{x}%")
            
            # Draw Gantt Timeline using Plotly
            fig = px.timeline(
                project_tasks_df,
                x_start="NgayBatDau",
                x_end="Deadline",
                y="TenCongViec",
                color="TrangThai",
                text="Tiến độ %",
                hover_data=["PhanTramHoanThanh", "MocTienDo"]
            )
            
            # Format Chart Layout
            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textposition='inside', textfont=dict(color='white', weight='bold'))
            fig.update_layout(
                xaxis_title="Thời gian",
                yaxis_title="Tên công việc",
                height=min(400 + len(project_tasks_df) * 35, 750),
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="Trạng thái"
            )
            
            # Add vertical Today line (dynamic today)
            ref_today = date.today()
            fig.add_vline(x=ref_today.strftime("%Y-%m-%d"), line_width=2, line_dash="dash", line_color="red", annotation_text="Hôm nay", annotation_position="top right")
            
            # Add Milestones lines
            for idx, row in project_tasks_df.iterrows():
                if row['Milestone'] and str(row['Milestone']).strip():
                    m_date = row['Deadline']
                    m_label = str(row['Milestone']).strip()
                    fig.add_vline(
                        x=m_date.strftime("%Y-%m-%d"), 
                        line_width=1.5, 
                        line_dash="dot", 
                        line_color="#f97316", 
                        annotation_text=f"📌 {m_label}", 
                        annotation_position="bottom right"
                    )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # --- Biểu đồ Tiến độ Lũy kế S-Curve ---
            min_date = project_tasks_df['NgayBatDau'].min()
            max_date = project_tasks_df['Deadline'].max()
            
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = pd.date_range(start=min_date, end=max_date, freq='D').date
                s_curve_data = []
                
                ref_today = date.today()
                
                for d in date_range:
                    total_planned_p = 0
                    total_actual_p = 0
                    count = len(project_tasks_df)
                    
                    for _, row in project_tasks_df.iterrows():
                        start_d = row['NgayBatDau']
                        end_d = row['Deadline']
                        final_act = row['PhanTramHoanThanh']
                        
                        # Planned
                        if d < start_d:
                            planned_p = 0
                        elif d >= end_d:
                            planned_p = 100
                        else:
                            total_d = (end_d - start_d).days
                            elapsed_d = (d - start_d).days
                            planned_p = (elapsed_d / total_d * 100) if total_d > 0 else 100
                            
                        # Actual
                        if d < start_d:
                            actual_p = 0
                        else:
                            end_ref = min(end_d, ref_today)
                            if d >= end_ref:
                                actual_p = final_act
                            else:
                                total_act_days = (end_ref - start_d).days
                                elapsed_act_days = (d - start_d).days
                                actual_p = (elapsed_act_days / total_act_days * final_act) if total_act_days > 0 else final_act
                                
                        total_planned_p += planned_p
                        total_actual_p += actual_p
                        
                    avg_planned = total_planned_p / count if count > 0 else 0
                    avg_actual = total_actual_p / count if count > 0 else 0
                    
                    s_curve_data.append({
                        "Ngày": d,
                        "Tiến độ Kế hoạch (%)": round(avg_planned, 1),
                        "Tiến độ Thực tế (%)": round(avg_actual, 1)
                    })
                    
                s_curve_df = pd.DataFrame(s_curve_data)
                
                # Import Plotly Graph Objects
                import plotly.graph_objects as go
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(
                    x=s_curve_df['Ngày'], 
                    y=s_curve_df['Tiến độ Kế hoạch (%)'], 
                    name='Tiến độ Kế hoạch (%)', 
                    line=dict(color='#1e3a8a', width=3)
                ))
                fig_s.add_trace(go.Scatter(
                    x=s_curve_df['Ngày'], 
                    y=s_curve_df['Tiến độ Thực tế (%)'], 
                    name='Tiến độ Thực tế (%)', 
                    line=dict(color='#f97316', width=3)
                ))
                
                fig_s.update_layout(
                    title="📈 Đường cong Tiến độ Lũy kế S-Curve",
                    xaxis_title="Thời gian",
                    yaxis_title="Tiến độ lũy kế (%)",
                    yaxis=dict(range=[0, 105]),
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_s, use_container_width=True)
            
            # Task Table
            st.markdown("#### 📋 Bảng tiến độ chi tiết dự án")
            
            disp_table = project_tasks_df.copy()
            
            # Filter bar
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                filter_status = st.multiselect("🔍 Lọc theo trạng thái:", ["🟢 Hoàn thành", "🟡 Đang thực hiện", "🔴 Quá hạn", "⚪ Chưa bắt đầu"], default=[])
            with f_col2:
                filter_search = st.text_input("🔍 Tìm tên công việc:")
            
            # Auto-calculate status and remaining days
            today_date = date.today()
            def calc_status(row):
                if row['PhanTramHoanThanh'] >= 100: return "🟢 Hoàn thành"
                dl = row['Deadline']
                if isinstance(dl, datetime): dl = dl.date()
                st_d = row['NgayBatDau']
                if isinstance(st_d, datetime): st_d = st_d.date()
                
                if pd.notna(dl) and dl < today_date: return "🔴 Quá hạn"
                if pd.notna(st_d) and st_d > today_date: return "⚪ Chưa bắt đầu"
                return "🟡 Đang thực hiện"
                
            def calc_remaining(row):
                if row['PhanTramHoanThanh'] >= 100: return "✅ Đã xong"
                dl = row['Deadline']
                if isinstance(dl, datetime): dl = dl.date()
                if pd.isna(dl): return ""
                diff = (dl - today_date).days
                if diff < 0: return f"🚨 Vượt {-diff} ngày"
                if diff == 0: return "⏰ Đến hạn hôm nay"
                if diff <= 3: return f"⚠️ Còn {diff} ngày"
                return f"{diff} ngày"
            
            disp_table['Trạng Thái'] = disp_table.apply(calc_status, axis=1)
            disp_table['Số Ngày Còn Lại'] = disp_table.apply(calc_remaining, axis=1)
            
            # Ensure new columns exist
            for col in ['QuanTrong', 'KhanCap']:
                if col not in disp_table.columns:
                    disp_table[col] = False
                else:
                    disp_table[col] = disp_table[col].fillna(False).astype(bool)
            
            # Apply filters
            if filter_status:
                disp_table = disp_table[disp_table['Trạng Thái'].isin(filter_status)]
            if filter_search.strip():
                disp_table = disp_table[disp_table['TenCongViec'].str.contains(filter_search.strip(), case=False, na=False)]
            
            disp_table['NgayBatDau'] = disp_table['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else "")
            disp_table['Deadline'] = disp_table['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else "")
            
            st.dataframe(
                disp_table[["Trạng Thái", "TenCongViec", "GiaiDoan", "NgayBatDau", "Deadline", "Số Ngày Còn Lại", "PhanTramHoanThanh", "QuanTrong", "KhanCap", "Milestone"]],
                column_config={
                    "Trạng Thái": st.column_config.TextColumn("Trạng thái", width="medium"),
                    "TenCongViec": st.column_config.TextColumn("Tên công việc", width="large"),
                    "GiaiDoan": st.column_config.TextColumn("Giai đoạn"),
                    "NgayBatDau": st.column_config.TextColumn("Ngày bắt đầu"),
                    "Deadline": st.column_config.TextColumn("Hạn chót"),
                    "Số Ngày Còn Lại": st.column_config.TextColumn("Thời gian còn lại"),
                    "PhanTramHoanThanh": st.column_config.ProgressColumn("Tiến độ %", format="%d%%", min_value=0, max_value=100),
                    "QuanTrong": st.column_config.CheckboxColumn("Quan trọng 🌟", default=False),
                    "KhanCap": st.column_config.CheckboxColumn("Khẩn cấp ⚡", default=False),
                    "Milestone": st.column_config.TextColumn("Cột mốc quan trọng")
                },
                use_container_width=True,
                hide_index=True
            )
        st.markdown("---")
        st.markdown("### ✏️ Quản lý Công việc Gantt")

        st.markdown("### ✏️ Quản lý Công việc Gantt")
        g_tab_new, g_tab_edit = st.tabs(["➕ Thêm công việc Gantt mới", "✏️ Sửa / Xóa công việc Gantt"])
        
        with g_tab_new:
            st.markdown("#### Thêm công việc mới vào dự án KHĐT")
            g_col1, g_col2 = st.columns(2)
            
            g_phase_suggestions = {
                "6. Thi công Xây lắp & Lắp đặt Thiết bị": [
                    "Bàn giao mặt bằng, dựng lán trại & Đấu nối điện nước thi công",
                    "Định vị tim mốc & Đào đất hố móng",
                    "Thi công Cọc & Kết cấu Móng / Bể ngầm",
                    "Thi công Kết cấu Khung Thân (Cột, Dầm, Sàn các tầng)",
                    "Xây tường bao & Tường ngăn",
                    "Thi công lắp đặt Đường ống MEP (Điện - Nước - PCCC) âm tường/sàn",
                    "Thi công Kết cấu Mái & Chống thấm"
                ]
            }
            
            with g_col1:
                g_phase = st.selectbox("Nhóm / Giai đoạn (Phase)", [
                    "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                    "2. Pháp lý Dự án & Quy hoạch 1/500",
                    "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                    "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                    "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                    "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                    "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                    "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                    "Khác"
                ], key="g_phase_new")
                
                # Check for suggestions
                suggested_tasks = g_phase_suggestions.get(g_phase, [])
                g_task_name_val = ""
                if suggested_tasks:
                    selected_suggestion = st.selectbox("💡 Gợi ý công việc mẫu:", ["-- Tự nhập tên công việc --"] + suggested_tasks, key="g_suggest_new")
                    if selected_suggestion != "-- Tự nhập tên công việc --":
                        g_task_name_val = selected_suggestion
                        
                g_task_name = st.text_input("Tên công việc", value=g_task_name_val, key="g_task_name_new")
                g_progress = st.slider("Tiến độ %", 0, 100, 0, key="g_progress_new")
            with g_col2:
                today_ref = date.today()
                g_start = st.date_input("Ngày bắt đầu", value=today_ref, key="g_start_new", format="DD/MM/YYYY")
                g_end = st.date_input("Ngày kết thúc", value=today_ref + timedelta(days=7), key="g_end_new", format="DD/MM/YYYY")
                g_milestone = st.text_input("Cột mốc quan trọng (Nếu có)", placeholder="ví dụ: Mốc 1: Phê duyệt Pháp lý & GPXD, Mốc 2: Cất nóc công trình...", key="g_milestone_new")
                
                # Sequential template loader button
                if g_phase == "6. Thi công Xây lắp & Lắp đặt Thiết bị":
                    st.markdown("💡 *Hoặc bạn có thể nạp nhanh toàn bộ 7 bước thi công mẫu bên dưới:*")
                    if st.button("⚡ NẠP NHANH 7 BƯỚC THI CÔNG MẪU", key="btn_g_load_template_phase6"):
                        new_rows = []
                        start_date = today_ref
                        for idx, task_name in enumerate(g_phase_suggestions["6. Thi công Xây lắp & Lắp đặt Thiết bị"]):
                            next_id = 1
                            if not gantt_df.empty:
                                g_ids = gantt_df['ID'].tolist() + [r['ID'] for r in new_rows]
                                nums = [int(m[0]) for idx_id in g_ids for m in [re.findall(r'\d+', str(idx_id))] if m]
                                if nums:
                                    next_id = max(nums) + 1
                            g_task_id = f"GNT-{next_id:03d}"
                            
                            end_date = start_date + timedelta(days=7)
                            new_rows.append({
                                "ID": g_task_id,
                                "TenDuAn": gantt_project_name.strip(),
                                "TenCongViec": task_name,
                                "GiaiDoan": g_phase,
                                "NgayBatDau": start_date,
                                "NgayKetThuc": end_date,
                                "PhanTramHoanThanh": 0,
                                "Milestone": "",
                                "NgayCapNhat": datetime.now()
                            })
                            start_date = end_date # Sequential
                            
                        gantt_df_updated = pd.concat([gantt_df, pd.DataFrame(new_rows)], ignore_index=True)
                        if save_gantt_db(gantt_df_updated):
                            st.success("🎉 Đã tự động nạp thành công 7 bước thi công mẫu tuần tự vào dự án!")
                            st.cache_data.clear()
                            st.rerun()
                
            g_submit = st.button("💾 THÊM CÔNG VIỆC GANTT", type="primary")
            if g_submit:
                if not g_task_name.strip():
                    st.error("⚠️ Vui lòng nhập Tên công việc!")
                elif g_start > g_end:
                    st.error("⚠️ Ngày bắt đầu không được lớn hơn ngày kết thúc!")
                else:
                    # Auto ID generator for Gantt
                    next_id = 1
                    if not gantt_df.empty:
                        g_ids = gantt_df['ID'].tolist()
                        nums = [int(m[0]) for idx in g_ids for m in [re.findall(r'\d+', str(idx))] if m]
                        if nums:
                            next_id = max(nums) + 1
                    g_task_id = f"GNT-{next_id:03d}"
                    
                    new_g_row = {
                        "ID": g_task_id,
                        "TenDuAn": gantt_project_name.strip(),
                        "TenCongViec": g_task_name.strip(),
                        "GiaiDoan": g_phase,
                        "NgayBatDau": g_start,
                        "NgayKetThuc": g_end,
                        "PhanTramHoanThanh": g_progress,
                        "Milestone": g_milestone.strip(),
                        "QuanTrong": False,
                        "KhanCap": False,
                        "NgayCapNhat": datetime.now()
                    }
                    
                    gantt_df_updated = pd.concat([gantt_df, pd.DataFrame([new_g_row])], ignore_index=True)
                    if save_gantt_db(gantt_df_updated):
                        st.success(f"🎉 Đã thêm thành công công việc mã: {g_task_id}!")
                        st.cache_data.clear()
                        st.rerun()
                        
        with g_tab_edit:
            st.markdown("#### Chỉnh sửa hoặc Xóa công việc")
            if project_tasks_df.empty:
                st.info("Chưa có công việc nào để chỉnh sửa.")
            else:
                edit_options = []
                for _, row in project_tasks_df.iterrows():
                    edit_options.append(f"{row['ID']} - {row['TenCongViec']}")
                
                selected_edit_task = st.selectbox("Chọn công việc cần cập nhật", edit_options, key="g_edit_sel")
                selected_g_id = selected_edit_task.split(" - ")[0]
                g_task_data = gantt_df[gantt_df['ID'] == selected_g_id].iloc[0]
                
                g_col_u1, g_col_u2 = st.columns(2)
                with g_col_u1:
                    u_g_task_name = st.text_input("Tên công việc", value=g_task_data['TenCongViec'], key="u_g_task_name")
                    u_g_phase = st.selectbox("Nhóm / Giai đoạn (Phase)", [
                        "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                        "2. Pháp lý Dự án & Quy hoạch 1/500",
                        "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                        "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                        "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                        "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                        "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                        "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                        "Khác"
                    ], index=[
                        "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                        "2. Pháp lý Dự án & Quy hoạch 1/500",
                        "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                        "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                        "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                        "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                        "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                        "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                        "Khác"
                    ].index(g_task_data['GiaiDoan']) if g_task_data['GiaiDoan'] in [
                        "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                        "2. Pháp lý Dự án & Quy hoạch 1/500",
                        "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                        "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                        "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                        "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                        "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                        "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                        "Khác"
                    ] else [
                        "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                        "2. Pháp lý Dự án & Quy hoạch 1/500",
                        "3. Thiết kế Cơ sở & Báo cáo Tự đánh giá / ĐTM",
                        "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                        "5. Cấp phép Xây dựng & Lựa chọn Nhà thầu",
                        "6. Thi công Xây lắp & Lắp đặt Thiết bị",
                        "7. Nghiệm thu, Phê duyệt PCCC & Hoàn công",
                        "8. Bàn giao & Đưa vào Vận hành / Khai thác",
                        "Khác"
                    ].index('Khác'), key="u_g_phase")
                    u_g_progress = st.slider("Tiến độ %", 0, 100, int(g_task_data['PhanTramHoanThanh']), key="u_g_progress")
                with g_col_u2:
                    u_g_start = st.date_input("Ngày bắt đầu", value=g_task_data['NgayBatDau'], key="u_g_start", format="DD/MM/YYYY")
                    u_g_end = st.date_input("Ngày kết thúc", value=g_task_data['NgayKetThuc'], key="u_g_end", format="DD/MM/YYYY")
                    u_g_milestone = st.text_input("Cột mốc quan trọng", value=g_task_data['Milestone'], key="u_g_milestone")
                    u_g_important = st.checkbox("Quan trọng 🌟", value=bool(g_task_data.get("QuanTrong", False)), key="u_g_important")
                    u_g_urgent = st.checkbox("Khẩn cấp ⚡", value=bool(g_task_data.get("KhanCap", False)), key="u_g_urgent")
                    
                btn_g_save, btn_g_del = st.columns([4, 1])
                with btn_g_save:
                    g_save_click = st.button("💾 LƯU CẬP NHẬT GANTT", type="primary", key="btn_g_save")
                with btn_g_del:
                    g_del_click = st.button("🗑️ XÓA CÔNG VIỆC GANTT", type="secondary", key="btn_g_del")
                    
                if g_save_click:
                    if not u_g_task_name.strip():
                        st.error("⚠️ Vui lòng nhập Tên công việc!")
                    elif u_g_start > u_g_end:
                        st.error("⚠️ Ngày bắt đầu không được lớn hơn ngày kết thúc!")
                    else:
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'TenCongViec'] = u_g_task_name.strip()
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'GiaiDoan'] = u_g_phase
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'NgayBatDau'] = u_g_start
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'NgayKetThuc'] = u_g_end
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'PhanTramHoanThanh'] = u_g_progress
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'Milestone'] = u_g_milestone.strip()
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'QuanTrong'] = u_g_important
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'KhanCap'] = u_g_urgent
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'NgayCapNhat'] = datetime.now()
                        
                        if save_gantt_db(gantt_df):
                            st.success(f"🎉 Đã lưu cập nhật công việc mã: {selected_g_id}!")
                            st.cache_data.clear()
                            st.rerun()
                            
                if g_del_click:
                    gantt_df_after_del = gantt_df[gantt_df['ID'] != selected_g_id]
                    if save_gantt_db(gantt_df_after_del):
                        st.success(f"🗑️ Đã xóa thành công công việc mã: {selected_g_id}!")
                        st.cache_data.clear()
                        st.rerun()
# ----------------- 5. ĐÁNH GIÁ KPI & XẾP LOẠI -----------------
elif menu == "🏆 Đánh giá KPI & Xếp loại":
    st.markdown(f"### 🏆 Đánh giá KPI & Xếp loại Cá nhân — {selected_company}")
    
    if role_mode == "Quản lý" and st.session_state.is_admin_authenticated:
        kpi_tab1, kpi_tab2, kpi_tab3, kpi_tab4 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)", "⚖️ Thưởng / Phạt Điểm", "📈 Phân tích & Xuất Báo cáo"])
    else:
        kpi_tab1, kpi_tab2 = st.tabs(["📅 Đánh giá theo Tháng", "🏅 Tổng kết KPI Cả Năm (Tháng 13)"])
    
    with kpi_tab1:
        st.markdown("#### Đánh giá và Xếp loại KPI Tháng")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            selected_month = st.selectbox("Chọn Tháng", list(range(1, 13)), index=today.month - 1)
        with col_m2:
            selected_year = st.selectbox("Chọn Năm", [today.year - 1, today.year, today.year + 1], index=1)
            
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
            
        kpi_df = kpi_df[kpi_df['Deadline'].apply(lambda x: is_in_month(x, selected_month, selected_year))]
        
        adj_df = read_kpi_adjustments()
        adj_df = adj_df[(adj_df['Thang'] == selected_month) & (adj_df['Nam'] == selected_year)]
        
        if kpi_df.empty and adj_df.empty:
            st.info(f"Không có dữ liệu công việc hoặc điểm thưởng/phạt nào trong Tháng {selected_month}/{selected_year}.")
        else:
            import pandas as pd
            from datetime import datetime, date
            personnel_kpi = []
            
            all_p = set(kpi_df['NguoiChuTri'].dropna().unique())
            all_p.update(adj_df['TenNhanVien'].dropna().unique())
            
            for person in all_p:
                if not str(person).strip(): continue
                group = kpi_df[kpi_df['NguoiChuTri'] == person]
                total_tasks = len(group)
                done_tasks = len(group[group['TrangThai'] == 'Hoàn thành'])
                
                group_copy = group.copy()
                group_copy['TyTrongKPI'] = pd.to_numeric(group_copy.get('TyTrongKPI', 0), errors='coerce').fillna(0)
                
                for idx, row in group_copy.iterrows():
                    is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                    is_late = False
                    dl = row['Deadline']
                    if isinstance(dl, str):
                        try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                        except: pass
                    if isinstance(dl, datetime): dl = dl.date()
                    if isinstance(dl, date): is_late = (dl < today) and not is_comp
                    
                    if is_late and row.get('PhanLoaiTreHan') != "👤 Do chủ quan":
                        group_copy.at[idx, 'PhanTramHoanThanh'] = 100
                        
                explicit_weight_sum = group_copy[group_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                unweighted_count = len(group_copy[group_copy['TyTrongKPI'] <= 0])
                
                remaining_weight = max(0, 100 - explicit_weight_sum)
                auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
                
                task_score = 0
                for idx, row in group_copy.iterrows():
                    weight = row['TyTrongKPI']
                    if weight <= 0:
                        weight = auto_weight
                    
                    pt_hoan_thanh = row.get('PhanTramHoanThanh', 0)
                    if pd.isna(pt_hoan_thanh): pt_hoan_thanh = 0
                    
                    task_score += (pt_hoan_thanh / 100.0) * weight
                
                p_adj_df = adj_df[adj_df['TenNhanVien'] == person]
                adj_score = p_adj_df['DiemDieuChinh'].sum()
                
                final_score = min(115, max(0, round(task_score + adj_score, 2)))
                
                # Xếp loại mới
                if final_score > 91: grade = "A"
                elif final_score > 81: grade = "B"
                elif final_score > 71: grade = "C"
                else: grade = "D"
                
                pb = group['PhongBan'].iloc[0] if not group.empty else ""
                
                personnel_kpi.append({
                    "Người thực hiện": person,
                    "Phòng ban": pb,
                    "Số việc": total_tasks,
                    "Điểm công việc": round(task_score, 1),
                    "Thưởng/Phạt": adj_score,
                    "TỔNG ĐIỂM": final_score,
                    "Xếp loại": grade
                })
                
            if personnel_kpi:
                kpi_month_df = pd.DataFrame(personnel_kpi)
                st.dataframe(
                    kpi_month_df,
                    column_config={
                        "TỔNG ĐIỂM": st.column_config.ProgressColumn("TỔNG ĐIỂM", format="%f", min_value=0, max_value=115),
                    },
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Không có dữ liệu cá nhân hợp lệ.")

    with kpi_tab2:
        st.markdown("#### Tổng kết KPI Cả Năm & Xếp loại thưởng Tháng 13")
        selected_year_full = st.selectbox("Chọn Năm Tổng Kết", [today.year - 1, today.year, today.year + 1], index=1, key="year_full")
        
        if st.button("🔄 Chạy / Cập nhật Báo cáo Tổng kết Năm", type="primary"):
            with st.spinner("Đang tính toán dữ liệu 12 tháng..."):
                import pandas as pd
                from datetime import datetime, date
                all_personnel = list(display_df['NguoiChuTri'].unique())
                adj_year_df = read_kpi_adjustments()
                adj_year_df = adj_year_df[adj_year_df['Nam'] == selected_year_full]
                all_personnel.extend(adj_year_df['TenNhanVien'].unique())
                
                all_personnel = list(set([p for p in all_personnel if str(p).strip()]))
                
                yearly_data = []
                for person in all_personnel:
                    person_df = display_df[display_df['NguoiChuTri'] == person].copy()
                    
                    months_grades = {}
                    count_a = 0
                    count_b = 0
                    count_c = 0
                    count_d = 0
                    
                    for m in range(1, 13):
                        def is_in_m(d):
                            if pd.isna(d): return False
                            if isinstance(d, str):
                                try: d = datetime.strptime(d, "%Y-%m-%d").date()
                                except: return False
                            if isinstance(d, datetime): d = d.date()
                            if isinstance(d, date): return d.month == m and d.year == selected_year_full
                            return False
                            
                        m_df = person_df[person_df['Deadline'].apply(is_in_m)]
                        m_adj_df = adj_year_df[(adj_year_df['TenNhanVien'] == person) & (adj_year_df['Thang'] == m)]
                        
                        if m_df.empty and m_adj_df.empty:
                            months_grades[f"Tháng {m}"] = "-"
                            continue
                            
                        m_df_copy = m_df.copy()
                        m_df_copy['TyTrongKPI'] = pd.to_numeric(m_df_copy.get('TyTrongKPI', 0), errors='coerce').fillna(0)
                        
                        for idx, row in m_df_copy.iterrows():
                            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                            is_late = False
                            dl = row['Deadline']
                            if isinstance(dl, str):
                                try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                                except: pass
                            if isinstance(dl, datetime): dl = dl.date()
                            if isinstance(dl, date): is_late = (dl < today) and not is_comp
                            if is_late and row.get('PhanLoaiTreHan') != "👤 Do chủ quan":
                                m_df_copy.at[idx, 'PhanTramHoanThanh'] = 100
                                
                        explicit_weight = m_df_copy[m_df_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                        uw_count = len(m_df_copy[m_df_copy['TyTrongKPI'] <= 0])
                        auto_w = max(0, 100 - explicit_weight) / uw_count if uw_count > 0 else 0
                        
                        t_score = 0
                        for idx, row in m_df_copy.iterrows():
                            w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_w
                            p = row.get('PhanTramHoanThanh', 0)
                            t_score += (p / 100.0) * w
                        
                        f_score = min(115, max(0, round(t_score + m_adj_df['DiemDieuChinh'].sum(), 2)))
                        
                        if f_score > 91: 
                            grade = "A"
                            count_a += 1
                        elif f_score > 81: 
                            grade = "B"
                            count_b += 1
                        elif f_score > 71: 
                            grade = "C"
                            count_c += 1
                        else: 
                            grade = "D"
                            count_d += 1
                            
                        months_grades[f"Tháng {m}"] = grade
                        
                    # Logic xếp loại năm mới
                    if count_c > 0 or count_d > 0:
                        final_grade = "C"
                        bonus = "60%"
                    elif count_b >= 2:
                        final_grade = "B"
                        bonus = "80%"
                    elif count_a >= 11:
                        final_grade = "A"
                        bonus = "100%"
                    else:
                        if all(v == "-" for v in months_grades.values()):
                            final_grade = "-"
                            bonus = "-"
                        else:
                            final_grade = "B"
                            bonus = "80%"
                            
                    row_data = {
                        "Người thực hiện": person,
                        "Phòng ban": person_df['PhongBan'].mode()[0] if not person_df.empty else ""
                    }
                    row_data.update(months_grades)
                    row_data["Xếp loại Năm"] = final_grade
                    row_data["Mức hưởng T13"] = bonus
                    yearly_data.append(row_data)
                    
                if yearly_data:
                    yearly_df = pd.DataFrame(yearly_data)
                    st.dataframe(yearly_df, use_container_width=True, hide_index=True)
                    
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        yearly_df.to_excel(writer, index=False, sheet_name="KPI_TongKet")
                    st.download_button("📥 Xuất Báo cáo Excel", data=output.getvalue(), file_name=f"TongKet_KPI_{selected_year_full}.xlsx")
                else:
                    st.info("Không có dữ liệu.")

    if role_mode == "Quản lý" and st.session_state.is_admin_authenticated:
        with kpi_tab3:
            st.markdown("#### ⚖️ Điều chỉnh Điểm Thưởng / Phạt")
            all_p_list = []
            for dept, persons in config.get("personnel_by_department", {}).items():
                all_p_list.extend(persons)
            all_p_list = sorted(list(set(all_p_list)))
            if not all_p_list:
                all_p_list = ["(Chưa có nhân sự)"]
                
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                adj_person = st.selectbox("Tên nhân viên", all_p_list)
                adj_month = st.selectbox("Tháng áp dụng", list(range(1, 13)), index=today.month - 1)
                adj_year = st.selectbox("Năm áp dụng", [today.year - 1, today.year, today.year + 1], index=1)
            
            with col_f2:
                adj_template = st.selectbox("Lý do mẫu", ["Đi trễ, về sớm", "Quên chấm công", "Lý do khác"])
                
                # Fetch existing records to count
                hist_df_all = read_kpi_adjustments()
                count_violations = 0
                if not hist_df_all.empty:
                    count_violations = len(hist_df_all[
                        (hist_df_all['TenNhanVien'].str.strip() == adj_person.strip()) & 
                        (hist_df_all['Thang'] == adj_month) & 
                        (hist_df_all['Nam'] == adj_year) & 
                        (hist_df_all['LyDo'].str.startswith(f"[{adj_template}]", na=False))
                    ])
                current_time = count_violations + 1
                
                if adj_template == "Đi trễ, về sớm":
                    st.info(f"ℹ️ Đã vi phạm {count_violations} lần trong tháng {adj_month}. Lần nhập này là lần thứ {current_time}.")
                    if current_time >= 6:
                        sugg_val = 2
                        st.warning("⚠️ Từ lần 6 trở đi: Đề xuất trừ 2 điểm.")
                    else:
                        sugg_val = 0
                        st.success("✅ Dưới 6 lần: Chưa bị trừ điểm.")
                    adj_type = "🛑 Phạt điểm"
                    adj_val = st.number_input("Số điểm trừ", min_value=0, max_value=15, value=sugg_val)
                    adj_reason = st.text_input("Ghi chú thêm (Tùy chọn)")
                    
                elif adj_template == "Quên chấm công":
                    st.info(f"ℹ️ Đã vi phạm {count_violations} lần trong tháng {adj_month}. Lần nhập này là lần thứ {current_time}.")
                    if current_time >= 3:
                        sugg_val = 1
                        st.warning("⚠️ Từ lần 3 trở đi: Đề xuất trừ 1 điểm.")
                    else:
                        sugg_val = 0
                        st.success("✅ Dưới 3 lần: Chưa bị trừ điểm.")
                    adj_type = "🛑 Phạt điểm"
                    adj_val = st.number_input("Số điểm trừ", min_value=0, max_value=15, value=sugg_val)
                    adj_reason = st.text_input("Ghi chú thêm (Tùy chọn)")
                    
                else:
                    adj_type = st.radio("Phân loại hành vi", ["⭐ Thưởng điểm", "🛑 Phạt điểm"], horizontal=True)
                    adj_val = st.number_input("Số điểm", min_value=0, max_value=15, value=5)
                    adj_reason = st.text_area("Lý do chi tiết (Bắt buộc)")
                    
            if st.button("Lưu Điểm Điều Chỉnh", type="primary"):
                if adj_template == "Lý do khác" and not adj_reason.strip():
                    st.error("⚠️ Vui lòng nhập lý do chi tiết!")
                else:
                    actual_val = adj_val if adj_type == "⭐ Thưởng điểm" else -adj_val
                    final_reason = f"[{adj_template}] {adj_reason.strip()}".strip() if adj_template != "Lý do khác" else adj_reason.strip()
                    add_kpi_adjustment(adj_person, adj_month, adj_year, adj_type, actual_val, final_reason)
                    st.success("🎉 Đã lưu điều chỉnh điểm thành công!")
                    st.rerun()

        with kpi_tab4:
            st.markdown("### Tùy chọn Xuất Báo Cáo & Phân tích")
            col_x1, col_x2 = st.columns(2)
            
            with col_x1:
                st.markdown("#### 1. Báo Cáo Phòng Ban (Excel)")
                if st.button("Tải Báo cáo Phòng Ban"):
                    data_rows = []
                    for i, person in enumerate(all_p_list):
                        data_rows.append({
                            'HoTen': person, 'ChucVu': 'Nhân viên',
                            'SoLanTre': 0, 'SoLanSom': 0, 'SoLanKhongCC': 0,
                            'DiemTruTre': 0, 'DiemTruSom': 0, 'DiemTruKhongCC': 0,
                            'TongTru': 0, 'DiemConLai': 100, 'XepLoai': 'A', 'GhiChu': ''
                        })
                    excel_data = kpi_reports.generate_department_excel(selected_company, selected_month, selected_year, data_rows)
                    st.download_button("📥 Tải Báo Cáo Excel", data=excel_data, file_name=f"KPI_Thang_{selected_month}_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            with col_x2:
                st.markdown("#### 2. Phiếu KPI Cá Nhân (Word)")
                emp_to_export = st.selectbox("Chọn nhân viên", all_p_list, key='emp_export')
                if st.button("Tạo Phiếu Đánh Giá"):
                    tasks = [{'TenCV': 'Công việc mẫu', 'TyTrong': 100, 'Diem': 100}]
                    word_data = kpi_reports.generate_individual_docx(emp_to_export, selected_month, selected_year, 100, tasks, [])
                    st.download_button("📥 Tải Phiếu Cá Nhân (Word)", data=word_data, file_name=f"Phieu_KPI_{emp_to_export}_{selected_month}_{selected_year}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    
            st.divider()
            st.info("Để xem Biểu đồ Phân tích, vui lòng qua tab 'Tổng kết KPI Cả Năm' và bấm 'Chạy / Cập nhật' trước.")

                        
            st.markdown("##### Lịch sử Thưởng / Phạt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                st.dataframe(hist_df.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có lịch sử điều chỉnh.")

# ----------------- 6. QUẢN LÝ CẤU HÌNH -----------------# ----------------- 6. QUẢN LÝ CẤU HÌNH -----------------
elif menu == "⚙️ Quản Lý Cấu HÌnh":
    st.markdown("### ⚙️ Quản Lý Cấu Hình Hệ Thống")
    tab_proj, tab_dept, tab_gsheets = st.tabs(["📁 Quản lý Dự án", "🏢 Quản lý Phòng ban", "📊 Đồng bộ Google Sheets"])
    
    with tab_proj:
        st.markdown("#### Quản lý Danh mục Dự án")
        
        # Show existing categories
        cats = list(PROJECTS_BY_CATEGORY.keys())
        sel_cat = st.selectbox("Chọn Lĩnh vực dự án", cats)
        projs_in_cat = PROJECTS_BY_CATEGORY.get(sel_cat, [])
        
        st.markdown(f"**Danh sách dự án hiện tại trong [{sel_cat}]:**")
        st.write(", ".join(projs_in_cat) if projs_in_cat else "Chưa có dự án nào")
        
        st.markdown("---")
        
        col_add, col_edit, col_del = st.columns(3)
        
        with col_add:
            st.markdown("**➕ Thêm dự án mới**")
            new_proj_name = st.text_input("Tên dự án mới", key="admin_add_proj")
            if st.button("Thêm dự án", type="primary"):
                if new_proj_name.strip():
                    if new_proj_name.strip() not in projs_in_cat:
                        PROJECTS_BY_CATEGORY[sel_cat].append(new_proj_name.strip())
                        config["projects_by_category"] = PROJECTS_BY_CATEGORY
                        if save_config(config):
                            st.success(f"Đã thêm dự án: {new_proj_name}")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Dự án đã tồn tại!")
                else:
                    st.error("Tên dự án không được để trống!")
                    
        with col_edit:
            st.markdown("**✏️ Đổi tên dự án**")
            if projs_in_cat:
                proj_to_edit = st.selectbox("Chọn dự án cần sửa", projs_in_cat, key="admin_edit_proj_sel")
                edited_proj_name = st.text_input("Tên dự án mới", value=proj_to_edit, key="admin_edit_proj_val")
                if st.button("Lưu đổi tên"):
                    if edited_proj_name.strip():
                        idx = PROJECTS_BY_CATEGORY[sel_cat].index(proj_to_edit)
                        PROJECTS_BY_CATEGORY[sel_cat][idx] = edited_proj_name.strip()
                        config["projects_by_category"] = PROJECTS_BY_CATEGORY
                        if save_config(config):
                            st.success(f"Đã đổi tên thành: {edited_proj_name}")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Tên mới không được để trống!")
            else:
                st.write("Không có dự án để sửa.")
                
        with col_del:
            st.markdown("**🗑️ Xóa dự án**")
            if projs_in_cat:
                proj_to_del = st.selectbox("Chọn dự án cần xóa", projs_in_cat, key="admin_del_proj_sel")
                if st.button("Xác nhận xóa dự án", type="secondary"):
                    PROJECTS_BY_CATEGORY[sel_cat].remove(proj_to_del)
                    config["projects_by_category"] = PROJECTS_BY_CATEGORY
                    if save_config(config):
                        st.success(f"Đã xóa dự án: {proj_to_del}")
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.write("Không có dự án để xóa.")

    with tab_dept:
        st.markdown("#### Quản lý Danh sách Phòng ban")
        st.markdown(f"**Danh sách phòng ban hiện tại ({len(OFFICIAL_DEPARTMENTS)} phòng ban):**")
        st.write(", ".join(OFFICIAL_DEPARTMENTS) if OFFICIAL_DEPARTMENTS else "Chưa có phòng ban nào")
        
        st.markdown("---")
        
        col_d_add, col_d_edit, col_d_del = st.columns(3)
        
        with col_d_add:
            st.markdown("**➕ Thêm phòng ban mới**")
            new_dept_name = st.text_input("Tên phòng ban mới", key="admin_add_dept")
            if st.button("Thêm phòng ban", type="primary"):
                if new_dept_name.strip():
                    if new_dept_name.strip() not in OFFICIAL_DEPARTMENTS:
                        OFFICIAL_DEPARTMENTS.append(new_dept_name.strip())
                        config["departments"] = OFFICIAL_DEPARTMENTS
                        if save_config(config):
                            st.success(f"Đã thêm phòng ban: {new_dept_name}")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Phòng ban đã tồn tại!")
                else:
                    st.error("Tên không được để trống!")
                    
        with col_d_edit:
            st.markdown("**✏️ Đổi tên phòng ban**")
            if OFFICIAL_DEPARTMENTS:
                dept_to_edit = st.selectbox("Chọn phòng ban cần sửa", OFFICIAL_DEPARTMENTS, key="admin_edit_dept_sel")
                edited_dept_name = st.text_input("Tên phòng ban mới", value=dept_to_edit, key="admin_edit_dept_val")
                if st.button("Lưu đổi tên phòng"):
                    if edited_dept_name.strip():
                        idx = OFFICIAL_DEPARTMENTS.index(dept_to_edit)
                        OFFICIAL_DEPARTMENTS[idx] = edited_dept_name.strip()
                        config["departments"] = OFFICIAL_DEPARTMENTS
                        # Update personnel keys as well
                        if "personnel_by_department" in config:
                            config["personnel_by_department"][edited_dept_name.strip()] = config["personnel_by_department"].pop(dept_to_edit, [])
                        if save_config(config):
                            st.success(f"Đã đổi tên thành: {edited_dept_name}")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Tên mới không được để trống!")
            else:
                st.write("Không có phòng ban để sửa.")
                
        with col_d_del:
            st.markdown("**🗑️ Xóa phòng ban**")
            if OFFICIAL_DEPARTMENTS:
                dept_to_del = st.selectbox("Chọn phòng ban cần xóa", OFFICIAL_DEPARTMENTS, key="admin_del_dept_sel")
                if st.button("Xác nhận xóa phòng", type="secondary"):
                    OFFICIAL_DEPARTMENTS.remove(dept_to_del)
                    config["departments"] = OFFICIAL_DEPARTMENTS
                    # Remove personnel mapping too
                    if "personnel_by_department" in config:
                        config["personnel_by_department"].pop(dept_to_del, None)
                    if save_config(config):
                        st.success(f"Đã xóa phòng ban: {dept_to_del}")
                        st.cache_data.clear()
                        st.rerun()
            else:
                st.write("Không có phòng ban để xóa.")

        st.markdown("---")
        st.markdown("#### 👥 Quản lý Nhân sự theo Phòng ban")
        
        if OFFICIAL_DEPARTMENTS:
            sel_dept_p = st.selectbox("Chọn phòng ban để quản lý nhân sự", OFFICIAL_DEPARTMENTS, key="admin_sel_dept_p")
            
            if sel_dept_p in ["Ban Hành chính Nhân sự", "Ban Tài chính Kế toán", "Ban Lãnh đạo", "Tổ KPI"]:
                st.info("ℹ️ Nhân sự của phòng ban này được cấu hình tự động theo logic Công ty / Thành viên.")
                
            # Load personnel list
            current_p_list = config.get("personnel_by_department", {}).get(sel_dept_p, [])
            
            st.markdown(f"**Danh sách nhân sự thuộc [{sel_dept_p}] ({len(current_p_list)} người):**")
            st.write(", ".join(current_p_list) if current_p_list else "Chưa có nhân sự nào")
            
            st.markdown("---")
            
            col_p_add, col_p_edit, col_p_del = st.columns(3)
            
            with col_p_add:
                st.markdown("**➕ Thêm nhân sự mới**")
                new_p_name = st.text_input("Tên nhân sự mới", key="admin_add_p_name")
                if st.button("Thêm nhân sự", type="primary", key="btn_admin_add_p"):
                    if new_p_name.strip():
                        if new_p_name.strip() not in current_p_list:
                            current_p_list.append(new_p_name.strip())
                            config["personnel_by_department"][sel_dept_p] = current_p_list
                            if save_config(config):
                                st.success(f"Đã thêm nhân sự: {new_p_name.strip()}")
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            st.error("Nhân sự đã tồn tại trong phòng ban này!")
                    else:
                        st.error("Tên nhân sự không được để trống!")
                        
            with col_p_edit:
                st.markdown("**✏️ Sửa tên nhân sự**")
                if current_p_list:
                    p_to_edit = st.selectbox("Chọn nhân sự cần sửa", current_p_list, key="admin_edit_p_sel")
                    edited_p_name = st.text_input("Tên nhân sự mới", value=p_to_edit, key="admin_edit_p_val")
                    if st.button("Lưu thay đổi", key="btn_admin_edit_p"):
                        if edited_p_name.strip():
                            if edited_p_name.strip() not in current_p_list or edited_p_name.strip() == p_to_edit:
                                idx = current_p_list.index(p_to_edit)
                                current_p_list[idx] = edited_p_name.strip()
                                config["personnel_by_department"][sel_dept_p] = current_p_list
                                if save_config(config):
                                    st.success(f"Đã cập nhật tên nhân sự thành: {edited_p_name.strip()}")
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.error("Tên mới đã tồn tại trong phòng ban này!")
                        else:
                            st.error("Tên mới không được để trống!")
                else:
                    st.write("Không có nhân sự để sửa.")
                    
            with col_p_del:
                st.markdown("**🗑️ Xóa nhân sự**")
                if current_p_list:
                    p_to_del = st.selectbox("Chọn nhân sự cần xóa", current_p_list, key="admin_del_p_sel")
                    if st.button("Xác nhận xóa", type="secondary", key="btn_admin_del_p"):
                        current_p_list.remove(p_to_del)
                        config["personnel_by_department"][sel_dept_p] = current_p_list
                        if save_config(config):
                            st.success(f"Đã xóa nhân sự: {p_to_del}")
                            st.cache_data.clear()
                            st.rerun()
                else:
                    st.write("Không có nhân sự để xóa.")
        else:
            st.warning("Vui lòng tạo ít nhất một phòng ban trước khi cấu hình nhân sự.")

    with tab_gsheets:
        st.markdown("#### 📊 Cấu hình kết nối Google Sheets")
        if is_gsheets_configured():
            st.success("🎉 Hệ thống đã kết nối thành công với Google Sheets! Mọi thay đổi dữ liệu sẽ được tự động đồng bộ thời gian thực.")
            try:
                st.info(f"**Spreadsheet URL:** `{st.secrets['connections']['gsheets']['spreadsheet']}`")
            except Exception:
                pass
        else:
            st.warning("⚠️ Hiện tại hệ thống đang hoạt động ở chế độ ngoại tuyến (Offline) bằng file Excel cục bộ.")
            
        st.markdown("""
        ### 📝 Hướng dẫn kết nối Google Sheets trên Streamlit Cloud
        Để đồng bộ dữ liệu trực tuyến, vui lòng thực hiện các bước sau:
        
        1. **Tạo Google Sheet**: Tạo một bảng tính Google Sheets mới. Đảm bảo sheet đầu tiên có tên là `Sheet1`.
        2. **Định cấu hình cột mẫu**: Bạn có thể tải file Excel hiện tại từ sidebar xuống và copy cấu trúc cột sang Google Sheets. Các cột gồm:
           `ID`, `DonVi`, `PhongBan`, `NguoiChuTri`, `TenDuAn`, `MocTienDo`, `SanPhamBanGiao`, `TenCongViec`, `PhanLoaiChiSo`, `NgayBatDau`, `Deadline`, `DoUuTien`, `PhanTramHoanThanh`, `TrangThai`, `LinkKetQua`, `GiaiTrinhDeXuat`, `NgayCapNhat`
        3. **Chia sẻ quyền chỉnh sửa**: Chia sẻ Google Sheet đó với tài khoản **Google Service Account** của bạn (cấp quyền **Editor**).
        4. **Cấu hình Secrets trên Streamlit Cloud**:
           - Truy cập Dashboard của Streamlit Cloud -> Vào ứng dụng -> Chọn **Settings** -> **Secrets**.
           - Nhập thông tin cấu hình Service Account theo định dạng sau:
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
        5. **Khởi động lại (Reboot) app**: Lưu lại Secrets, Streamlit sẽ tự động đồng bộ và nạp dữ liệu từ Google Sheets.
        """)
