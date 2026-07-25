import streamlit as st
import pandas as pd
import datetime
import os
import re
import json
import plotly.express as px
import sqlite3

try:
    import google.generativeai as genai
except ImportError:
    st.error("Thư viện google-generativeai chưa được cài đặt. Vui lòng kiểm tra file requirements.txt.")

from datetime import datetime, date

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
            return 100.0
            
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
    "Ban Lãnh đạo": ["Trần Quốc Thể", "Thái Văn Thành", "Trần Cường"],
    "Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên"],
    "Ban Tài chính Kế toán": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"],
    "Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Trần Văn Trọng", "Trần Cường"],
    "Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phạm Quang Nghĩa", "Lê Thị Hải"],
    "Ban Kỹ thuật": ["Trần Văn Trọng", "Nguyễn Văn Sang", "Trương Ngọc Sỹ"],
    "Ban Đền bù Giải tỏa": ["Nguyễn Ngọc Tôn", "Mai Văn Châu", "Thái Hữu Quý"],
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


def safe_gsheets_read(conn, worksheet, ttl=0, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    kwargs = {"worksheet": worksheet, "ttl": ttl}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    try:
        df = conn.read(**kwargs)
        return df if df is not None else fallback_df
    except Exception as e:
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        return fallback_df

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
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        return False

def save_config(config_data):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa cấu hình Google Sheets (secrets.toml).")
        return False
    try:
        df_save = pd.DataFrame([{"config_json": json.dumps(config_data, ensure_ascii=False)}])
        safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
        return True
    except Exception as e:
        pass
        return False

def load_config():
    default_config = {
        "projects_by_category": {
            "BĐS & KDC": ["KDC Bàu Mạc", "KDC Nam Bàu Mạc", "KĐT Phước Lý & Phước Lý MR", "TĐC Phước Lý 2 & Hoà Liên 5", "Dự án Phong Nam", "Khu BT ST Hoà Ninh"],
            "HẠ TẦNG & GIAO THÔNG": ["Tuyến đường Lê Trọng Tấn", "Tuyến đường Lê Trọng Tấn - Hoà Nhơn", "Tuyến đường Trần Hưng Đạo (BT)", "Trục I Tây Bắc", "Khu TĐC Hoà Vang"],
            "THƯƠNG MẠI & KHÁCH SẠN": ["Khách sạn DMT-Group", "Du thuyền Happy Yacht (DMT Marina)"]
        },
        "departments": ["Ban Lãnh đạo", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán", "Ban Kế hoạch Đầu tư", "Ban Chuẩn bị Đầu tư", "Ban Kỹ thuật", "Ban Đền bù Giải tỏa", "Tổ KPI"],
        "personnel_by_department": DEFAULT_PERSONNEL.copy(),
        "cv_gsheet_url": ""
    }
    
    conn = get_gsheets_conn()
    if conn is None:
        return default_config
        
    try:
        df = safe_gsheets_read(conn, worksheet="CONFIG", ttl=0)
        if df is None or df.empty:
            df_save = pd.DataFrame([{"config_json": json.dumps(default_config, ensure_ascii=False)}])
            safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)
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
        "Ban Kỹ thuật": "Trần Văn Trọng",
        "Ban Đền bù Giải tỏa": "Nguyễn Ngọc Tôn",
        "Tổ KPI": ""
    },
    "CTY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT": {
        "Ban Lãnh đạo": "Thái Văn Thành",
        "Ban Hành chính Nhân sự": "Nguyễn Thị Mỹ Phương",
        "Ban Tài chính Kế toán": "Nguyễn Thị Ngọc Hà",
        "Ban Kế hoạch Đầu tư": "",
        "Ban Chuẩn bị Đầu tư": "",
        "Ban Kỹ thuật": "",
        "Ban Đền bù Giải tỏa": "",
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
            return ["Trần Cường"]
        elif dept == "Tổ KPI":
            return []
    elif is_traffic:
        if dept == "Ban Lãnh đạo":
            return ["Thái Văn Thành", "Trần Văn Trọng"]
        elif dept == "Ban Tài chính Kế toán":
            return ["Nguyễn Thị Ngọc Hà"]
        elif dept == "Ban Hành chính Nhân sự":
            return ["Nguyễn Thị Mỹ Phương"]
        else:
            return []
    else:
        if dept == "Ban Hành chính Nhân sự":
            return ["Nguyễn Thị Hạnh Tiên"]
        elif dept == "Ban Tài chính Kế toán":
            return ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
        elif dept == "Tổ KPI":
            return []
            
    # Mặc định lấy từ cấu hình cho các phòng ban khác
    return config.get("personnel_by_department", {}).get(dept, [])

def get_departments_for_company(company, all_departments):
    is_marina = False
    if isinstance(company, str):
        is_marina = "CTY CP DMT - MARINA" in company or "Du thuyền Happy Yacht" in company
    if is_marina:
        # Chỉ hiển thị 3 ban, ẩn tất cả các ban còn lại
        allowed = ["Ban Lãnh đạo", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán"]
        return [d for d in all_departments if d in allowed]
    return all_departments



# Generate flat list for dropdowns (brief clean names)
ALL_PROJECTS = []
for cat, projs in PROJECTS_BY_CATEGORY.items():
    for p in projs:
        ALL_PROJECTS.append(p)

DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

# Gantt DB Configuration
GANTT_DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

def read_gantt_db():
    conn = get_gsheets_conn()
    if conn is None:
        return pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])
        
    try:
        df = safe_gsheets_read(conn, worksheet="GANTT_KHDT", ttl=0)
        if df is None or df.empty or len(df.columns) < 2:
            dummy_data = [
                {
                    "ID": "GNT-001",
                    "TenDuAn": "Dự án Xây dựng Khu Đô thị Marina",
                    "TenCongViec": "Khảo sát thị trường & Khả thi",
                    "GiaiDoan": "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                    "NgayBatDau": "2026-01-01",
                    "NgayKetThuc": "2026-01-31",
                    "PhanTramHoanThanh": 100,
                    "Milestone": "",
                    "NgayCapNhat": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ]
            df = pd.DataFrame(dummy_data)
            safe_gsheets_update(conn, worksheet="GANTT_KHDT", data=df)
        else:
            df.columns = [str(c).strip() for c in df.columns]
    except Exception as e:
        pass
        df = pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])
        
    # Khởi tạo các cột thiếu
    for col in ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]:
        if col not in df.columns:
            df[col] = ""

            
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau'], errors='coerce').dt.date
    df['NgayKetThuc'] = pd.to_datetime(df['NgayKetThuc'], errors='coerce').dt.date
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

def save_gantt_db(df):
    conn = get_gsheets_conn()
    if conn is None:
        st.error("Chưa kết nối Google Sheets.")
        return False
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayKetThuc'] = df_save['NgayKetThuc'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        
        safe_gsheets_update(conn, worksheet="GANTT_KHDT", data=df_save)
        return True
    except Exception as e:
        pass
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
    
    # Convert today to datetime.date if it is datetime.datetime
    if isinstance(today, datetime.datetime):
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
            
        so_ky_hieu = str(row[so_ky_hieu_col]).strip() if not pd.isna(row[so_ky_hieu_col]) else f"VB-{datetime.datetime.now().strftime('%M%S')}"
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
                "NgayCapNhat": datetime.datetime.now(),
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
            docs_df.at[idx, "NgayCapNhat"] = datetime.datetime.now()
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
                "NgayCapNhat": datetime.datetime.now(),
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
            tasks_df.at[t_idx, "NgayCapNhat"] = datetime.datetime.now()
            
    if save_incoming_docs_db(docs_df) and save_db(tasks_df):
        return True, f"Đồng bộ thành công! Đã thêm mới {success_count} văn bản và cập nhật {update_count} văn bản."
    else:
        return False, "Không thể lưu dữ liệu vào cơ sở dữ liệu."

def read_incoming_docs_db():
    conn = get_gsheets_conn()
    required_cols = [
        "ID", "DonVi", "SoKyHieu", "NgayBanHanh", "CoQuanGui", "TrichYeu", 
        "TenDuAn", "GanttTaskId", "BanChuTri", "Deadline", "LinkFile", 
        "TrangThai", "NgayCapNhat", "GhiChu"
    ]
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="VAN_BAN_DEN", ttl=0)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
            safe_gsheets_update(conn, worksheet="VAN_BAN_DEN", data=df)
        else:
            df.columns = [str(c).strip() for c in df.columns]
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
    
    today_dt = datetime.date.today()
    for idx, row in df.iterrows():
        deadline_val = row['Deadline']
        status_val = str(row['TrangThai']).strip()
        
        if isinstance(deadline_val, str):
            try:
                deadline_val = datetime.datetime.strptime(deadline_val, '%Y-%m-%d').date()
            except Exception:
                pass
                
        if isinstance(deadline_val, datetime.datetime):
            deadline_val = deadline_val.date()
            
        if isinstance(deadline_val, datetime.date):
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
        df_save['NgayBanHanh'] = df_save['NgayBanHanh'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        
        safe_gsheets_update(conn, worksheet="VAN_BAN_DEN", data=df_save)
        return True
    except Exception as e:
        pass
        return False

def read_db():
    conn = get_gsheets_conn()
    required_cols = [
        "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
        "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
        "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat", "ChuKyTheoDoi", "PhanLoaiTreHan"
    ]
    if conn is None:
        return pd.DataFrame(columns=required_cols)
        
    try:
        df = safe_gsheets_read(conn, worksheet="Sheet1", ttl=0)
        if df is None or df.empty or len(df.columns) < 2:
            df = pd.DataFrame(columns=required_cols)
            safe_gsheets_update(conn, worksheet="Sheet1", data=df)
        else:
            df.columns = [str(c).strip() for c in df.columns]
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
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['ChuKyTheoDoi'] = df_save['ChuKyTheoDoi'].fillna('Theo dự án / Tự do')
        df_save['PhanLoaiTreHan'] = df_save['PhanLoaiTreHan'].fillna('🟢 Không trễ hạn / Đúng tiến độ')
        
        safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)
        return True
    except Exception as e:
        pass
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
    st.session_state["gsheet_url"] = ""

gsheet_url_input = st.sidebar.text_input(
    "Link Google Sheets (DB chính)", 
    value=st.session_state["gsheet_url"], 
    placeholder="Dán link Google Sheets..."
)

if gsheet_url_input != st.session_state["gsheet_url"]:
    st.session_state["gsheet_url"] = gsheet_url_input
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
        "📩 Quản Lý Văn Bản Đến",
        "📄 Trích Xuất Việc Từ TBGB",
        "⚙️ Quản Lý Cấu HÌnh"
    ],
    index=0
)

st.sidebar.markdown("---")

# Current date
df = read_db()
today = datetime.date.today()

# Filter display dataframe based on sidebar selected company
if selected_company != "Tất cả đơn vị":
    display_df = df[df['DonVi'] == selected_company]
else:
    display_df = df

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

def generate_styled_excel(tasks_df, gantt_df):
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
                    deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
                except Exception:
                    pass
            ref_today = today
            if isinstance(ref_today, datetime.datetime):
                ref_today = ref_today.date()
            if isinstance(deadline, datetime.datetime):
                deadline = deadline.date()
                
            is_late = False
            if isinstance(deadline, datetime.date):
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
            tasks_df_copy['NgayCapNhat'] = tasks_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        tasks_df_copy.to_excel(writer, sheet_name="Sheet1", index=False)
        
        # Write GANTT_KHDT (Drop ID column if exists)
        gantt_df_copy = gantt_df.copy()
        if 'ID' in gantt_df_copy.columns:
            gantt_df_copy = gantt_df_copy.drop(columns=['ID'])
        if 'NgayCapNhat' in gantt_df_copy.columns:
            gantt_df_copy['NgayCapNhat'] = gantt_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        gantt_df_copy.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
        
        # Write VAN_BAN_DEN (Drop ID column if exists)
        try:
            docs_df = read_incoming_docs_db()
            docs_df_copy = docs_df.copy()
            if 'ID' in docs_df_copy.columns:
                docs_df_copy = docs_df_copy.drop(columns=['ID'])
            if 'NgayCapNhat' in docs_df_copy.columns:
                docs_df_copy['NgayCapNhat'] = docs_df_copy['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
            for col_name in ['NgayBanHanh', 'Deadline']:
                if col_name in docs_df_copy.columns:
                    docs_df_copy[col_name] = docs_df_copy[col_name].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
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
                    if col_name in ["ID", "STT", "NgayBatDau", "NgayKetThuc", "Deadline", "PhanTramHoanThanh", "TrangThai", "NgayCapNhat"]:
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
    gantt_df_for_excel = read_gantt_db()
    styled_excel_data = generate_styled_excel(df, gantt_df_for_excel)
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
    st.sidebar.warning("🟡 Google Sheets: Chạy Offline")

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
        if not isinstance(deadline_val, datetime.date):
            if isinstance(deadline_val, datetime.datetime):
                deadline_val = deadline_val.date()
            else:
                return None, None
        if deadline_val < today_dt:
            days_late = (today_dt - deadline_val).days
            return f"🔴 [⚠️ Trễ {days_late} ngày]", 1
        elif deadline_val == today_dt:
            return "🟠 [⏳ Hạn hôm nay]", 2
        elif deadline_val == today_dt + datetime.timedelta(days=1):
            return "🟠 [⏳ Hạn ngày mai]", 3
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
                "Tên công việc": row['TenCongViec'],
                "Dự án / Hạng mục": row['TenDuAn'],
                "Ban phụ trách": row['PhongBan'],
                "Người phụ trách": row['NguoiChuTri'],
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
        crit_display['Dự án / Hạng mục'] = alert_df_show['TenDuAn']
        crit_display['Tên công việc'] = alert_df_show['TenCongViec']
        crit_display['Phòng ban'] = alert_df_show['PhongBan']
        crit_display['Người thực hiện'] = alert_df_show['NguoiChuTri']
        crit_display['Hạn chót'] = alert_df_show['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        crit_display['Trạng thái thực tế'] = alert_df_show['Badge']
        crit_display['Ghi chú / Giải trình vướng mắc'] = alert_df_show['GiaiTrinhDeXuat']
        
        st.dataframe(
            crit_display,
            column_config={
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width="medium"),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width="medium"),
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

    # Dashboard incoming docs section
    docs_df = read_incoming_docs_db()
    if selected_company != "Tất cả đơn vị":
        dash_docs = docs_df[docs_df['DonVi'] == selected_company]
    else:
        dash_docs = docs_df
        
    total_docs = len(dash_docs)
    pending_docs = len(dash_docs[dash_docs['TrangThai'] == '⏳ Đang xử lý'])
    late_docs = len(dash_docs[dash_docs['TrangThai'].astype(str).str.contains('Trễ hạn', na=False)])
    done_docs = len(dash_docs[dash_docs['TrangThai'] == '✅ Đã xong'])
    
    st.markdown("### 📩 Thống kê Văn bản đến")
    
    # Red warnings for late docs
    late_docs_list = dash_docs[dash_docs['TrangThai'].astype(str).str.contains('Trễ hạn', na=False)]
    if not late_docs_list.empty:
        st.error("🚨 **CẢNH BÁO: CÓ VĂN BẢN ĐẾN TRỄ HẠN XỬ LÝ / PHẢN HỒI**")
        alert_docs_data = []
        for _, row in late_docs_list.iterrows():
            deadline_val = row['Deadline']
            if isinstance(deadline_val, str):
                try:
                    deadline_val = datetime.datetime.strptime(deadline_val, '%Y-%m-%d').date()
                except Exception:
                    pass
            ref_today = today
            if isinstance(ref_today, datetime.datetime):
                ref_today = ref_today.date()
            if isinstance(deadline_val, datetime.datetime):
                deadline_val = deadline_val.date()
                
            days_late = 0
            if isinstance(deadline_val, datetime.date):
                days_late = (ref_today - deadline_val).days
            
            alert_docs_data.append({
                "Số / Ký hiệu": row['SoKyHieu'],
                "Đơn vị gửi": row['CoQuanGui'],
                "Trích yếu nội dung": row['TrichYeu'],
                "Hạn xử lý": row['Deadline'].strftime('%d/%m/%Y') if isinstance(row['Deadline'], (datetime.date, datetime.datetime)) else str(row['Deadline']),
                "Số ngày trễ": f"{days_late} ngày"
            })
        st.dataframe(pd.DataFrame(alert_docs_data), use_container_width=True, hide_index=True)
        
    doc_m1, doc_m2, doc_m3, doc_m4 = st.columns(4)
    with doc_m1:
        st.metric("Tổng số VB đến", total_docs)
    with doc_m2:
        st.metric("VB Đang xử lý", pending_docs)
    with doc_m3:
        st.metric("VB Trễ hạn", late_docs)
    with doc_m4:
        st.metric("VB Đã hoàn thành", done_docs)
        
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
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        proj_options = ["Tất cả dự án"] + ALL_PROJECTS
        sel_proj_filter = st.selectbox("Lọc nhanh theo Dự án / Hạng mục", proj_options)
        
    with col_filter2:
        allowed_depts = get_departments_for_company(selected_company, OFFICIAL_DEPARTMENTS)
        dept_options = ["Tất cả phòng ban"] + allowed_depts
        sel_dept_filter = st.selectbox("Lọc nhanh theo Phòng ban chịu trách nhiệm", dept_options)
        
    # Apply filters
    table_df = display_df.copy()
    if sel_proj_filter != "Tất cả dự án":
        clean_proj = clean_proj_name(sel_proj_filter)
        table_df = table_df[table_df['TenDuAn'].str.contains(clean_proj, case=False, na=False)]
        
    if sel_dept_filter != "Tất cả phòng ban":
        table_df = table_df[table_df['PhongBan'] == sel_dept_filter]
        
    if table_df.empty:
        st.info("Không có công việc nào phù hợp với bộ lọc.")
    else:
        df_display = pd.DataFrame()
        df_display['Dự án / Hạng mục'] = table_df['TenDuAn']
        df_display['Tên công việc'] = table_df['TenCongViec']
        df_display['Phòng ban'] = table_df['PhongBan']
        df_display['Người thực hiện'] = table_df['NguoiChuTri']
        df_display['Ngày bắt đầu'] = table_df['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        
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
                return f"🟠 {date_str} (Hạn hôm nay)"
            elif 1 <= days_left <= 3:
                return f"🟡 {date_str} (Sắp hạn - Còn {days_left} ngày)"
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
                    return f"🟠 [Do khách quan] - {explain.strip()}"
                return "🟠 [Do khách quan]"
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
                "Dự án / Hạng mục": st.column_config.TextColumn("Dự án / Hạng mục", width="medium"),
                "Tên công việc": st.column_config.TextColumn("Tên công việc", width="large"),
                "Phòng ban": st.column_config.TextColumn("Phòng ban", width="medium"),
                "Người thực hiện": st.column_config.TextColumn("Người thực hiện", width="medium"),
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
            
            # 2. Project selection (Categorized dropdown or custom)
            is_marina_co = "CTY CP DMT - MARINA" in entry_company or "Du thuyền Happy Yacht" in entry_company
            if is_marina_co:
                proj_options_with_custom = ["➕ Tạo / Nhập Dự án mới..."]
            else:
                proj_options_with_custom = ALL_PROJECTS + ["✍️ Tự nhập Dự án / Hạng mục khác..."]
                
            default_proj_opt = st.selectbox("Dự án / Hạng mục", proj_options_with_custom)
            
            if is_marina_co or default_proj_opt in ["✍️ Tự nhập Dự án / Hạng mục khác...", "➕ Tạo / Nhập Dự án mới..."]:
                project_name = st.text_input("Nhập tên Dự án / Hạng mục mới", value="")
            else:
                project_name = clean_proj_name(default_proj_opt)
            
            # 3. Task details
            task_name = st.text_input("Tên công việc (tự nhập tự do)", value="")
            
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
            
        with col2:
            # 6. Dates
            task_start = st.date_input("Ngày bắt đầu thực hiện", today, format="DD/MM/YYYY")
            task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today + datetime.timedelta(days=7), format="DD/MM/YYYY")
            
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
                        "NgayCapNhat": datetime.datetime.now(),
                        "ChuKyTheoDoi": task_cycle,
                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                    }
                    
                    df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_db(df_updated):
                        st.success(f"🎉 Đã khởi tạo thành công công việc mã: {task_id}!")
                        st.rerun()

    # Form: Update Progress
    with tab_update:
        st.markdown("#### Cập nhật tiến độ công việc đang chạy")
        
        # Display only items matching selected company
        avail_update_df = display_df
        
        if avail_update_df.empty:
            st.info("Chưa có công việc nào khả dụng.")
        else:
            task_options = []
            for _, row in avail_update_df.iterrows():
                task_options.append(f"{row['ID']} - {row['PhongBan']} - {row['TenCongViec']}")
                
            selected_task = st.selectbox("Chọn công việc cần cập nhật", task_options)
            selected_id = selected_task.split(" - ")[0]
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
                        df.loc[df['ID'] == selected_id, 'NgayCapNhat'] = datetime.datetime.now()
                        df.loc[df['ID'] == selected_id, 'ChuKyTheoDoi'] = u_cycle
                        df.loc[df['ID'] == selected_id, 'PhanLoaiTreHan'] = u_late_cause if u_is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                        
                        if save_db(df):
                            st.success(f"🎉 Đã lưu cập nhật công việc mã: {selected_id}!")
                            st.rerun()
                            
                if del_click:
                    df_after_del = df[df['ID'] != selected_id]
                    if save_db(df_after_del):
                        st.success(f"🗑️ Đã xóa thành công công việc mã: {selected_id}!")
                        st.rerun()

# ----------------- 4. SƠ ĐỒ GANTT DỰ ÁN KHĐT -----------------
elif menu == "📊 SƠ ĐỒ GANTT DỰ ÁN DMT":
    st.markdown("### 📊 Phân hệ Sơ đồ Gantt Dự án DMT")
    
    gantt_df = read_gantt_db()
    
    # 1. Select project (alphabetical order A-Z with default projects)
    is_marina_gantt = "CTY CP DMT - MARINA" in selected_company or "Du thuyền Happy Yacht" in selected_company
    
    if is_marina_gantt:
        gantt_project_options = ["➕ Tạo / Nhập Dự án mới..."]
    else:
        default_projects = [
            "KDC Bàu Mạc",
            "KDC Nam Bàu Mạc",
            "KĐT Phước Lý & Phước Lý MR",
            "TĐC Phước Lý 2 & Hoà Liên 5",
            "Dự án Phong Nam",
            "Khu BT ST Hoà Ninh",
            "Tuyến đường Lê Trọng Tấn",
            "Tuyến đường Lê Trọng Tấn - Hoà Nhơn",
            "Tuyến đường Trần Hưng Đạo (BT)",
            "Trục I Tây Bắc",
            "Khu TĐC Hoà Vang",
            "Khách sạn DMT Group",
            "Khách sạn DMT Măng Đen"
        ]
        existing_db_projects = list(gantt_df['TenDuAn'].unique())
        merged_projects = list(set(default_projects + existing_db_projects))
        existing_projects = sorted(merged_projects)
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
        ref_today = datetime.date.today()
        gantt_warn_list = []
        for _, row in project_tasks_df[project_tasks_df['PhanTramHoanThanh'] < 100].iterrows():
            deadline_val = row['NgayKetThuc']
            if isinstance(deadline_val, datetime.datetime):
                deadline_val = deadline_val.date()
                
            if deadline_val < ref_today:
                days_late = (ref_today - deadline_val).days
                badge = f"🔴 [⚠️ Trễ {days_late} ngày]"
                urgency = 1
            elif deadline_val == ref_today:
                badge = "🟠 [⏳ Hạn hôm nay]"
                urgency = 2
            elif deadline_val == ref_today + datetime.timedelta(days=1):
                badge = "🟠 [⏳ Hạn ngày mai]"
                urgency = 3
            else:
                badge = None
                
            if badge:
                row_copy = row.copy()
                row_copy['Badge'] = badge
                row_copy['Urgency'] = urgency
                gantt_warn_list.append(row_copy)
                
        if gantt_warn_list:
            gantt_warn_df = pd.DataFrame(gantt_warn_list).sort_values(by=["Urgency", "NgayKetThuc"])
            st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(gantt_warn_df)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")
            g_alert_data = []
            for _, row in gantt_warn_df.iterrows():
                g_alert_data.append({
                    "Tên công việc": row['TenCongViec'],
                    "Giai đoạn": row['GiaiDoan'],
                    "Tiến độ hiện tại": f"{row['PhanTramHoanThanh']}%",
                    "Hạn chót": row['NgayKetThuc'].strftime('%d/%m/%Y') if isinstance(row['NgayKetThuc'], (datetime.date, datetime.datetime)) else str(row['NgayKetThuc']),
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
                x_end="NgayKetThuc",
                y="TenCongViec",
                color="GiaiDoan",
                text="Tiến độ %",
                hover_data=["PhanTramHoanThanh", "Milestone"]
            )
            
            # Format Chart Layout
            fig.update_yaxes(autorange="reversed")
            fig.update_traces(textposition='inside', textfont=dict(color='white', weight='bold'))
            fig.update_layout(
                xaxis_title="Thời gian",
                yaxis_title="Tên công việc",
                height=min(400 + len(project_tasks_df) * 35, 750),
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="Giai đoạn"
            )
            
            # Add vertical Today line (dynamic today)
            ref_today = datetime.date.today()
            fig.add_vline(x=ref_today.strftime("%Y-%m-%d"), line_width=2, line_dash="dash", line_color="red", annotation_text="Hôm nay", annotation_position="top right")
            
            # Add Milestones lines
            for idx, row in project_tasks_df.iterrows():
                if row['Milestone'] and str(row['Milestone']).strip():
                    m_date = row['NgayKetThuc']
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
            max_date = project_tasks_df['NgayKetThuc'].max()
            
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = pd.date_range(start=min_date, end=max_date, freq='D').date
                s_curve_data = []
                
                ref_today = datetime.date.today()
                
                for d in date_range:
                    total_planned_p = 0
                    total_actual_p = 0
                    count = len(project_tasks_df)
                    
                    for _, row in project_tasks_df.iterrows():
                        start_d = row['NgayBatDau']
                        end_d = row['NgayKetThuc']
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
            disp_table['NgayBatDau'] = disp_table['NgayBatDau'].apply(lambda x: x.strftime('%d/%m/%Y'))
            disp_table['NgayKetThuc'] = disp_table['NgayKetThuc'].apply(lambda x: x.strftime('%d/%m/%Y'))
            st.dataframe(
                disp_table[["TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone"]],
                column_config={
                    "TenCongViec": st.column_config.TextColumn("Tên công việc", width="large"),
                    "GiaiDoan": st.column_config.TextColumn("Giai đoạn"),
                    "NgayBatDau": st.column_config.TextColumn("Ngày bắt đầu"),
                    "NgayKetThuc": st.column_config.TextColumn("Ngày kết thúc"),
                    "PhanTramHoanThanh": st.column_config.ProgressColumn("Tiến độ %", format="%d%%", min_value=0, max_value=100),
                    "Milestone": st.column_config.TextColumn("Cột mốc quan trọng")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Chưa có công việc nào trong dự án này. Vui lòng thêm mới bên dưới!")
            
        st.markdown("---")
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
                today_ref = datetime.date.today()
                g_start = st.date_input("Ngày bắt đầu", value=today_ref, key="g_start_new", format="DD/MM/YYYY")
                g_end = st.date_input("Ngày kết thúc", value=today_ref + datetime.timedelta(days=7), key="g_end_new", format="DD/MM/YYYY")
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
                            
                            end_date = start_date + datetime.timedelta(days=7)
                            new_rows.append({
                                "ID": g_task_id,
                                "TenDuAn": gantt_project_name.strip(),
                                "TenCongViec": task_name,
                                "GiaiDoan": g_phase,
                                "NgayBatDau": start_date,
                                "NgayKetThuc": end_date,
                                "PhanTramHoanThanh": 0,
                                "Milestone": "",
                                "NgayCapNhat": datetime.datetime.now()
                            })
                            start_date = end_date # Sequential
                            
                        gantt_df_updated = pd.concat([gantt_df, pd.DataFrame(new_rows)], ignore_index=True)
                        if save_gantt_db(gantt_df_updated):
                            st.success("🎉 Đã tự động nạp thành công 7 bước thi công mẫu tuần tự vào dự án!")
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
                        "NgayCapNhat": datetime.datetime.now()
                    }
                    
                    gantt_df_updated = pd.concat([gantt_df, pd.DataFrame([new_g_row])], ignore_index=True)
                    if save_gantt_db(gantt_df_updated):
                        st.success(f"🎉 Đã thêm thành công công việc mã: {g_task_id}!")
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
                        gantt_df.loc[gantt_df['ID'] == selected_g_id, 'NgayCapNhat'] = datetime.datetime.now()
                        
                        if save_gantt_db(gantt_df):
                            st.success(f"🎉 Đã lưu cập nhật công việc mã: {selected_g_id}!")
                            st.rerun()
                            
                if g_del_click:
                    gantt_df_after_del = gantt_df[gantt_df['ID'] != selected_g_id]
                    if save_gantt_db(gantt_df_after_del):
                        st.success(f"🗑️ Đã xóa thành công công việc mã: {selected_g_id}!")
                        st.rerun()

# ----------------- 5. QUẢN LÝ VĂN BẢN ĐẾN -----------------
elif menu == "📩 Quản Lý Văn Bản Đến":
    st.markdown("### 📩 Phân hệ Quản Lý Văn Bản Đến")
    
    docs_df = read_incoming_docs_db()
    # Filter by selected company
    if selected_company != "Tất cả đơn vị":
        display_docs_df = docs_df[docs_df['DonVi'] == selected_company]
    else:
        display_docs_df = docs_df
        
    st.markdown("#### 📋 Danh sách Văn bản đến")
    if display_docs_df.empty:
        st.info("Chưa có văn bản đến nào được ghi nhận.")
    else:
        df_docs_show = pd.DataFrame()
        
        # 1. Ngày
        if 'NgayBanHanh' in display_docs_df.columns:
            df_docs_show['Ngày'] = display_docs_df['NgayBanHanh'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        elif 'Ngay' in display_docs_df.columns:
            df_docs_show['Ngày'] = display_docs_df['Ngay'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        else:
            df_docs_show['Ngày'] = ''
            
        # 2. Đơn vị
        if 'CoQuanGui' in display_docs_df.columns:
            df_docs_show['Đơn vị'] = display_docs_df['CoQuanGui'].fillna('')
        elif 'DonVi' in display_docs_df.columns:
            df_docs_show['Đơn vị'] = display_docs_df['DonVi'].fillna('')
        else:
            df_docs_show['Đơn vị'] = ''
            
        # 3. Nội dung
        if 'TrichYeu' in display_docs_df.columns:
            df_docs_show['Nội dung'] = display_docs_df['TrichYeu'].fillna('')
        elif 'NoiDung' in display_docs_df.columns:
            df_docs_show['Nội dung'] = display_docs_df['NoiDung'].fillna('')
        else:
            df_docs_show['Nội dung'] = ''
            
        # 4. Thời hạn hoàn thành
        if 'Deadline' in display_docs_df.columns:
            df_docs_show['Thời hạn hoàn thành'] = display_docs_df['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        else:
            df_docs_show['Thời hạn hoàn thành'] = ''
            
        # 5. Trạng thái
        if 'TrangThai' in display_docs_df.columns:
            df_docs_show['Trạng thái'] = display_docs_df['TrangThai'].fillna('')
        elif 'Trangthai' in display_docs_df.columns:
            df_docs_show['Trạng thái'] = display_docs_df['Trangthai'].fillna('')
        else:
            df_docs_show['Trạng thái'] = '⏳ Đang xử lý'
            
        # 6. Người/Ban thực hiện
        if 'BanChuTri' in display_docs_df.columns:
            df_docs_show['Người/Ban thực hiện'] = display_docs_df['BanChuTri'].fillna('')
        elif 'PhongBan' in display_docs_df.columns:
            df_docs_show['Người/Ban thực hiện'] = display_docs_df['PhongBan'].fillna('')
        else:
            df_docs_show['Người/Ban thực hiện'] = ''
            
        # 7. Ghi chú
        if 'Ghi chú' in display_docs_df.columns:
            df_docs_show['Ghi chú'] = display_docs_df['Ghi chú'].fillna('')
        elif 'GhiChu' in display_docs_df.columns:
            df_docs_show['Ghi chú'] = display_docs_df['GhiChu'].fillna('')
        elif 'ghi chú' in display_docs_df.columns:
            df_docs_show['Ghi chú'] = display_docs_df['ghi chú'].fillna('')
        else:
            df_docs_show['Ghi chú'] = ''
        
        # Báo đỏ toàn dòng cảnh báo trễ hạn
        def highlight_overdue_rows(row):
            if "Trễ hạn" in str(row['Trạng thái']):
                return ['background-color: #FEE2E2; color: #DC2626; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        styled_df = df_docs_show.style.apply(highlight_overdue_rows, axis=1)
        
        st.dataframe(
            styled_df,
            column_config={
                "Ngày": st.column_config.TextColumn("Ngày", width="small"),
                "Đơn vị": st.column_config.TextColumn("Đơn vị", width="medium"),
                "Nội dung": st.column_config.TextColumn("Nội dung", width="large"),
                "Thời hạn hoàn thành": st.column_config.TextColumn("Thời hạn hoàn thành", width="small"),
                "Trạng thái": st.column_config.TextColumn("Trạng thái", width="medium"),
                "Người/Ban thực hiện": st.column_config.TextColumn("Người/Ban thực hiện", width="medium"),
                "Ghi chú": st.column_config.TextColumn("Ghi chú", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )
        
    st.markdown("---")
    
    # Giao diện tối giản (Chỉ dùng Google Sheets)
    st.markdown("#### 🔗 Đồng bộ từ Google Sheets")
    saved_gsheet_url = config.get("cv_gsheet_url", "")
    
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        gsheet_input = st.text_input(
            "🔗 Link Google Sheets Quản lý Văn bản đến", 
            value=saved_gsheet_url, 
            placeholder="https://docs.google.com/spreadsheets/d/...", 
            label_visibility="collapsed",
            key="cv_gsheet_input_minimal"
        )
    with col_btn:
        btn_sync = st.button("🔄 Đồng bộ dữ liệu", key="btn_sync_cv_gsheet_minimal", use_container_width=True)
        
    if btn_sync:
        if not gsheet_input.strip():
            st.warning("⚠️ Vui lòng nhập link Google Sheets trước.")
        else:
            csv_url = convert_gsheet_to_csv_url(gsheet_input)
            try:
                import_df = pd.read_csv(csv_url)
                
                # Cập nhật và lưu cấu hình
                config_data = load_config()
                config_data["cv_gsheet_url"] = gsheet_input.strip()
                save_config(config_data)
                
                success, msg = sync_incoming_docs_from_df(import_df, selected_company, today)
                if success:
                    st.success(f"🎉 {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            except Exception as e:
                st.error(f"❌ Lỗi đọc Google Sheets: {e}")
                st.info("💡 Hướng dẫn: Đảm bảo Google Sheets được chia sẻ ở chế độ công khai ('Bất kỳ ai có liên kết đều có thể xem').")
                
    st.markdown("---")
    
    # Form tabs
    tab_new_doc, tab_update_doc = st.tabs(["➕ Đăng ký Văn bản đến mới", "✏️ Cập nhật thông tin Văn bản"])
    
    # Tab 1: New Document
    with tab_new_doc:
        st.markdown("#### Khởi tạo thông tin Văn bản đến")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            doc_company = st.selectbox("Đơn vị / Công ty nhận", list(COMPANIES.keys()), key="doc_co_new")
            doc_number = st.text_input("Số / Ký hiệu văn bản", placeholder="Ví dụ: 102/CV-DMT", key="doc_num_new")
            doc_date = st.date_input("Ngày ban hành", today, key="doc_date_new")
            doc_sender = st.text_input("Tên cơ quan / Đơn vị gửi", placeholder="Ví dụ: Sở Xây dựng TP. Đà Nẵng", key="doc_sender_new")
            doc_summary = st.text_area("Trích yếu nội dung văn bản", placeholder="Mô tả tóm tắt nội dung văn bản...", key="doc_sum_new")
            
        with col_d2:
            doc_project = st.selectbox("Dự án liên quan", ["Không liên kết"] + ALL_PROJECTS, key="doc_proj_new")
            
            # Gantt task dropdown filterable
            gantt_df = read_gantt_db()
            gantt_opts = ["Không liên kết GANTT"]
            for _, row in gantt_df.iterrows():
                if doc_project == "Không liên kết" or clean_proj_name(row['TenDuAn']) == clean_proj_name(doc_project):
                    gantt_opts.append(f"{row['ID']} - {row['TenDuAn']} - {row['TenCongViec']}")
            
            selected_gantt_opt = st.selectbox("Gắn vào công việc trong Sơ đồ Gantt", gantt_opts, key="doc_gantt_new")
            
            allowed_depts = get_departments_for_company(doc_company, OFFICIAL_DEPARTMENTS)
            doc_dept = st.selectbox("Ban / Bộ phận chủ trì xử lý", allowed_depts, key="doc_dept_new")
            doc_deadline = st.date_input("Hạn chót phải xử lý / Phản hồi", today + datetime.timedelta(days=7), key="doc_dl_new")
            
            st.markdown("**Đính kèm văn bản**")
            doc_file_mode = st.radio("Hình thức nộp", ["✍️ Nhập Link văn bản (Dạng text/Drive)", "📁 Tải file đính kèm (PDF, Ảnh...)"], horizontal=True, key="doc_file_mode_new")
            if doc_file_mode == "✍️ Nhập Link văn bản (Dạng text/Drive)":
                doc_link = st.text_input("Nhập Link văn bản", placeholder="https://drive.google.com/...", key="doc_link_new")
                doc_file = None
            else:
                doc_file = st.file_uploader("Tải file đính kèm", key="doc_file_upload_new")
                doc_link = ""
                
            doc_status = st.selectbox("Trạng thái xử lý", ["⏳ Đang xử lý", "✅ Đã xong", "⚠️ Trễ hạn"], index=0, key="doc_status_new")
            
        submit_doc = st.button("💾 ĐĂNG KÝ VĂN BẢN ĐẾN", type="primary", key="btn_doc_submit_new")
        if submit_doc:
            if not doc_number.strip():
                st.error("⚠️ Vui lòng nhập Số / Ký hiệu văn bản!")
            elif not doc_sender.strip():
                st.error("⚠️ Vui lòng nhập Tên cơ quan / Đơn vị gửi!")
            elif not doc_summary.strip():
                st.error("⚠️ Vui lòng nhập Trích yếu nội dung!")
            else:
                calc_status = doc_status
                if doc_deadline < today and doc_status != "✅ Đã xong":
                    calc_status = "⚠️ Trễ hạn"
                    
                # Auto ID generator
                next_id = 1
                if not docs_df.empty:
                    ids = docs_df['ID'].tolist()
                    nums = [int(m[0]) for idx in ids for m in [re.findall(r'\d+', str(idx))] if m]
                    if nums:
                        next_id = max(nums) + 1
                doc_id = f"DOC-{next_id:03d}"
                
                # Attachment file saving
                saved_attachment = ""
                if doc_file_mode == "✍️ Nhập Link văn bản (Dạng text/Drive)":
                    saved_attachment = doc_link.strip()
                elif doc_file is not None:
                    upload_dir = os.path.join("OUTPUT", "UPLOADED_DOCUMENTS")
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir, exist_ok=True)
                    safe_name = re.sub(r'[^\w\-_.]', '_', doc_file.name)
                    file_name = f"{doc_id}_{safe_name}"
                    file_path = os.path.join(upload_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(doc_file.getbuffer())
                    saved_attachment = file_path
                
                gantt_id = ""
                if selected_gantt_opt != "Không liên kết GANTT":
                    gantt_id = selected_gantt_opt.split(" - ")[0]
                    
                new_doc_row = {
                    "ID": doc_id,
                    "DonVi": doc_company,
                    "SoKyHieu": doc_number.strip(),
                    "NgayBanHanh": doc_date,
                    "CoQuanGui": doc_sender.strip(),
                    "TrichYeu": doc_summary.strip(),
                    "TenDuAn": doc_project if doc_project != "Không liên kết" else "",
                    "GanttTaskId": gantt_id,
                    "BanChuTri": doc_dept,
                    "Deadline": doc_deadline,
                    "LinkFile": saved_attachment,
                    "TrangThai": calc_status,
                    "NgayCapNhat": datetime.datetime.now()
                }
                
                docs_df_updated = pd.concat([docs_df, pd.DataFrame([new_doc_row])], ignore_index=True)
                if save_incoming_docs_db(docs_df_updated):
                    st.success(f"🎉 Đăng ký thành công văn bản đến mã: {doc_id}!")
                    st.rerun()

    # Tab 2: Update Document
    with tab_update_doc:
        st.markdown("#### Cập nhật thông tin Văn bản đến")
        if display_docs_df.empty:
            st.info("Chưa có văn bản đến nào khả dụng để cập nhật.")
        else:
            doc_options_list = [f"{row['ID']} - {row['SoKyHieu']} ({row['CoQuanGui']})" for _, row in display_docs_df.iterrows()]
            selected_update_doc_opt = st.selectbox("Chọn văn bản cần cập nhật", doc_options_list, key="sel_doc_to_update")
            selected_doc_id = selected_update_doc_opt.split(" - ")[0]
            doc_data = docs_df[docs_df['ID'] == selected_doc_id].iloc[0]
            
            with st.container():
                col_du1, col_du2 = st.columns(2)
                
                with col_du1:
                    u_doc_company = st.selectbox("Đơn vị / Công ty nhận", list(COMPANIES.keys()), index=list(COMPANIES.keys()).index(doc_data['DonVi']) if doc_data['DonVi'] in COMPANIES else 0, key="doc_co_up")
                    u_doc_number = st.text_input("Số / Ký hiệu văn bản", value=doc_data['SoKyHieu'], key="doc_num_up")
                    u_doc_date = st.date_input("Ngày ban hành", value=doc_data['NgayBanHanh'], key="doc_date_up")
                    u_doc_sender = st.text_input("Tên cơ quan / Đơn vị gửi", value=doc_data['CoQuanGui'], key="doc_sender_up")
                    u_doc_summary = st.text_area("Trích yếu nội dung văn bản", value=doc_data['TrichYeu'], key="doc_sum_up")
                    
                with col_du2:
                    current_proj = doc_data['TenDuAn'] if doc_data['TenDuAn'] else "Không liên kết"
                    proj_list = ["Không liên kết"] + ALL_PROJECTS
                    default_proj_idx = proj_list.index(current_proj) if current_proj in proj_list else 0
                    u_doc_project = st.selectbox("Dự án liên quan", proj_list, index=default_proj_idx, key="doc_proj_up")
                    
                    gantt_df = read_gantt_db()
                    gantt_opts_up = ["Không liên kết GANTT"]
                    for _, row in gantt_df.iterrows():
                        if u_doc_project == "Không liên kết" or clean_proj_name(row['TenDuAn']) == clean_proj_name(u_doc_project):
                            gantt_opts_up.append(f"{row['ID']} - {row['TenDuAn']} - {row['TenCongViec']}")
                            
                    current_gantt_id = doc_data.get('GanttTaskId', '')
                    default_gantt_idx = 0
                    if current_gantt_id and str(current_gantt_id).strip():
                        for idx, opt in enumerate(gantt_opts_up):
                            if opt.startswith(str(current_gantt_id).strip() + " - "):
                                default_gantt_idx = idx
                                break
                    u_selected_gantt_opt = st.selectbox("Gắn vào công việc trong Sơ đồ Gantt", gantt_opts_up, index=default_gantt_idx, key="doc_gantt_up")
                    
                    u_allowed_depts = get_departments_for_company(u_doc_company, OFFICIAL_DEPARTMENTS)
                    default_dept_idx = u_allowed_depts.index(doc_data['BanChuTri']) if doc_data['BanChuTri'] in u_allowed_depts else 0
                    u_doc_dept = st.selectbox("Ban / Bộ phận chủ trì xử lý", u_allowed_depts, index=default_dept_idx, key="doc_dept_up")
                    u_doc_deadline = st.date_input("Hạn chót phải xử lý / Phản hồi", value=doc_data['Deadline'], key="doc_dl_up")
                    
                    st.markdown("**Đính kèm văn bản hiện tại**")
                    curr_file = doc_data['LinkFile']
                    if curr_file:
                        if isinstance(curr_file, str) and curr_file.startswith("OUTPUT") and os.path.exists(curr_file):
                            display_file_name = os.path.basename(curr_file)
                            if "_" in display_file_name:
                                display_file_name = display_file_name.split("_", 1)[1]
                            st.write(f"📁 **File:** `{display_file_name}`")
                            with open(curr_file, "rb") as f:
                                st.download_button(
                                    label="📥 Tải file văn bản hiện tại",
                                    data=f.read(),
                                    file_name=display_file_name,
                                    mime="application/octet-stream",
                                    key="btn_download_doc_file"
                                )
                        else:
                            st.write(f"✍️ **Link:** `{curr_file}`")
                    else:
                        st.write("*(Chưa có tài liệu đính kèm)*")
                        
                    st.markdown("---")
                    st.markdown("**Cập nhật Đính kèm**")
                    u_doc_file_mode = st.radio("Cập nhật hình thức nộp", ["Giữ nguyên hiện tại", "✍️ Nhập Link văn bản mới", "📁 Tải file đính kèm mới"], horizontal=True, key="doc_file_mode_up")
                    u_doc_link = ""
                    u_doc_file = None
                    if u_doc_file_mode == "✍️ Nhập Link văn bản mới":
                        u_doc_link = st.text_input("Nhập Link văn bản mới", key="doc_link_up")
                    elif u_doc_file_mode == "📁 Tải file đính kèm mới":
                        u_doc_file = st.file_uploader("Tải file đính kèm mới", key="doc_file_upload_up")
                        
                    status_list = ["⏳ Đang xử lý", "✅ Đã xong", "⚠️ Trễ hạn"]
                    default_status_idx = status_list.index(doc_data['TrangThai']) if doc_data['TrangThai'] in status_list else 0
                    u_doc_status = st.selectbox("Trạng thái xử lý", status_list, index=default_status_idx, key="doc_status_up")
                    
                btn_doc_save, btn_doc_del = st.columns([4, 1])
                with btn_doc_save:
                    save_doc_click = st.button("💾 LƯU CẬP NHẬT VĂN BẢN", type="primary", key="btn_doc_save_up")
                with btn_doc_del:
                    del_doc_click = st.button("🗑️ XÓA VĂN BẢN NÀY", type="secondary", key="btn_doc_del_up")
                    
                if save_doc_click:
                    if not u_doc_number.strip():
                        st.error("⚠️ Vui lòng nhập Số / Ký hiệu văn bản!")
                    elif not u_doc_sender.strip():
                        st.error("⚠️ Vui lòng nhập Tên cơ quan / Đơn vị gửi!")
                    elif not u_doc_summary.strip():
                        st.error("⚠️ Vui lòng nhập Trích yếu nội dung!")
                    else:
                        calc_doc_status = u_doc_status
                        if u_doc_deadline < today and u_doc_status != "✅ Đã xong":
                            calc_doc_status = "⚠️ Trễ hạn"
                            
                        final_attachment = curr_file
                        if u_doc_file_mode == "✍️ Nhập Link văn bản mới":
                            final_attachment = u_doc_link.strip()
                        elif u_doc_file_mode == "📁 Tải file đính kèm mới" and u_doc_file is not None:
                            upload_dir = os.path.join("OUTPUT", "UPLOADED_DOCUMENTS")
                            if not os.path.exists(upload_dir):
                                os.makedirs(upload_dir, exist_ok=True)
                            safe_name = re.sub(r'[^\w\-_.]', '_', u_doc_file.name)
                            file_name = f"{selected_doc_id}_{safe_name}"
                            file_path = os.path.join(upload_dir, file_name)
                            with open(file_path, "wb") as f:
                                f.write(u_doc_file.getbuffer())
                            final_attachment = file_path
                            
                        u_gantt_id = ""
                        if u_selected_gantt_opt != "Không liên kết GANTT":
                            u_gantt_id = u_selected_gantt_opt.split(" - ")[0]
                            
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'DonVi'] = u_doc_company
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'SoKyHieu'] = u_doc_number.strip()
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'NgayBanHanh'] = u_doc_date
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'CoQuanGui'] = u_doc_sender.strip()
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'TrichYeu'] = u_doc_summary.strip()
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'TenDuAn'] = u_doc_project if u_doc_project != "Không liên kết" else ""
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'GanttTaskId'] = u_gantt_id
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'BanChuTri'] = u_doc_dept
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'Deadline'] = u_doc_deadline
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'LinkFile'] = final_attachment
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'TrangThai'] = calc_doc_status
                        docs_df.loc[docs_df['ID'] == selected_doc_id, 'NgayCapNhat'] = datetime.datetime.now()
                        
                        if save_incoming_docs_db(docs_df):
                            st.success(f"🎉 Đã lưu cập nhật văn bản mã: {selected_doc_id}!")
                            st.rerun()
                            
                if del_doc_click:
                    docs_df_after_del = docs_df[docs_df['ID'] != selected_doc_id]
                    if save_incoming_docs_db(docs_df_after_del):
                        st.success(f"🗑️ Đã xóa thành công văn bản mã: {selected_doc_id}!")
                        st.rerun()

elif menu == "📄 Trích Xuất Việc Từ TBGB":
    import io
    st.markdown("### 📄 Trích xuất Công việc từ Thông báo Giao ban bằng AI")
    
    st.markdown("Hệ thống sử dụng AI để tự động đọc nội dung văn bản (PDF, DOCX, Ảnh) và trích xuất thành danh sách công việc tương ứng.")
    
    saved_api_key = config.get("gemini_api_key", "")
    
    with st.expander("🔑 Cấu hình Gemini API Key", expanded=(not saved_api_key)):
        gemini_key = st.text_input(
            "Nhập Gemini API Key của bạn", 
            value=saved_api_key, 
            type="password", 
            help="API Key sẽ được lưu trong file cấu hình dự án để sử dụng cho các lần sau.",
            key="gemini_api_key_input"
        )
        if gemini_key:
            st.info("💡 Bạn có thể đăng ký API Key miễn phí tại Google AI Studio.")
            
    st.markdown("#### 📤 Tải lên tài liệu Giao ban")
    uploaded_file = st.file_uploader(
        "Chọn tệp Thông báo Giao ban (.pdf, .docx, .png, .jpg, .jpeg)", 
        type=["pdf", "docx", "png", "jpg", "jpeg"], 
        key="tbgb_file_uploader"
    )
    
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        btn_extract = st.button("🔍 Phân tích & Trích xuất bằng AI", type="primary", use_container_width=True, key="btn_run_tbgb_ai")
    with col_action2:
        btn_demo = st.button("⚙️ Chạy Demo với Dữ liệu mẫu", type="secondary", use_container_width=True, key="btn_run_tbgb_demo")
        
    if btn_extract:
        if not gemini_key.strip():
            st.error("⚠️ Vui lòng cấu hình Gemini API Key trước khi sử dụng tính năng trích xuất bằng AI.")
        elif uploaded_file is None:
            st.error("⚠️ Vui lòng tải lên tệp văn bản hoặc hình ảnh Thông báo Giao ban.")
        else:
            with st.spinner("AI đang đọc và bóc tách dữ liệu... Vui lòng đợi trong giây lát..."):
                file_bytes = uploaded_file.getvalue()
                file_name = uploaded_file.name
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Update saved API Key
                config_data = load_config()
                config_data["gemini_api_key"] = gemini_key.strip()
                save_config(config_data)
                
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=gemini_key.strip())
                    
                    # Lấy danh sách các model khả dụng có hỗ trợ generateContent
                    available_models = [
                        m.name
                        for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods
                    ]

                    # Chọn model phù hợp nhất (ưu tiên flash -> pro -> bất kỳ model nào có sẵn)
                    selected_model_name = None
                    for pref in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "models/gemini-1.5-flash"]:
                        for m in available_models:
                            if pref in m:
                                selected_model_name = m
                                break
                        if selected_model_name:
                            break

                    if not selected_model_name and available_models:
                        selected_model_name = available_models[0]

                    # Khởi tạo model từ tên chính xác được lấy từ list_models
                    model = genai.GenerativeModel(selected_model_name)


                    extracted_text = ""
                    # 1. If docx, extract text first
                    if file_ext == ".docx":
                        try:
                            import docx
                            doc = docx.Document(io.BytesIO(file_bytes))
                            paras = [p.text for p in doc.paragraphs]
                            tables_text = []
                            for tbl in doc.tables:
                                for row in tbl.rows:
                                    for cell in row.cells:
                                        tables_text.append(cell.text)
                            extracted_text = "\n".join(paras + tables_text)
                        except Exception as e_docx:
                            st.error(f"Lỗi đọc file DOCX: {e_docx}")
                            
                    # Prepare Prompt
                    prompt_text = f"""
Hãy phân tích nội dung văn bản Thông báo Giao ban (TBGB) này và trích xuất toàn bộ các chỉ đạo, công việc cần thực hiện thành danh sách có cấu trúc.
Yêu cầu trả về dữ liệu dưới dạng JSON (mảng các đối tượng) với các thuộc tính:
- TenCongViec: Tên công việc hoặc nội dung chỉ đạo cụ thể (ngắn gọn, rõ ràng).
- TenDuAn: Dự án hoặc hạng mục liên quan (Nếu có dự án cụ thể, hãy chọn một trong các dự án sau: KDC Bàu Mạc, KDC Nam Bàu Mạc, KĐT Phước Lý & Phước Lý MR, TĐC Phước Lý 2 & Hoà Liên 5, Dự án Phong Nam, Khu BT ST Hoà Ninh, Tuyến đường Lê Trọng Tấn, Tuyến đường Lê Trọng Tấn - Hoà Nhơn, Tuyến đường Trần Hưng Đạo (BT), Trục I Tây Bắc, Khu TĐC Hoà Vang, Khách sạn DMT-Group, Du thuyền Happy Yacht (DMT Marina), Quản lý Công văn đến. Nếu không liên quan dự án nào hoặc không tìm thấy, hãy điền chuỗi trống "").
- PhongBan: Ban hoặc bộ phận chịu trách nhiệm chính thực hiện (chọn một trong các phòng ban: Ban Lãnh đạo, Ban Hành chính Nhân sự, Ban Tài chính Kế toán, Ban Kế hoạch Đầu tư, Ban Chuẩn bị Đầu tư, Ban Kỹ thuật, Ban Đền bù Giải tỏa, Tổ KPI. Nếu không có ban cụ thể, hãy phân tích xem nhiệm vụ thuộc về ban nào hợp lý nhất).
- Deadline: Hạn chót hoàn thành. Hãy quy đổi sang định dạng YYYY-MM-DD. Nếu không ghi hạn cụ thể, hãy lấy ngày hiện tại cộng thêm 7 ngày (Ngày hiện tại: {today.strftime('%Y-%m-%d')}).

Chỉ trả về định dạng chuỗi JSON hợp lệ bắt đầu bằng [ và kết thúc bằng ], không bọc trong thẻ markdown ```json hay thêm bất cứ văn bản nào khác ngoài JSON.
"""
                    
                    if file_ext == ".docx":
                        response = model.generate_content([extracted_text, prompt_text])
                    else:
                        # Multimodal for PDF/Image
                        mime_type = "application/pdf"
                        if file_ext == ".png":
                            mime_type = "image/png"
                        elif file_ext in [".jpg", ".jpeg"]:
                            mime_type = "image/jpeg"
                            
                        response = model.generate_content([
                            {
                                "mime_type": mime_type,
                                "data": file_bytes
                            },
                            prompt_text
                        ])
                        
                    raw_result = response.text
                    
                    # Clean response to parse JSON
                    def clean_json_string(text):
                        text = text.strip()
                        if text.startswith("```json"):
                            text = text[7:]
                        elif text.startswith("```"):
                            text = text[3:]
                        if text.endswith("```"):
                            text = text[:-3]
                        text = text.strip()
                        
                        start_idx = text.find("[")
                        end_idx = text.rfind("]")
                        if start_idx != -1 and end_idx != -1:
                            text = text[start_idx:end_idx+1]
                        return text
                        
                    clean_json = clean_json_string(raw_result)
                    parsed_tasks = json.loads(clean_json)
                    
                    st.session_state["tbgb_tasks"] = parsed_tasks
                    st.success("🎉 Đã phân tích và trích xuất dữ liệu thành công bằng AI!")
                except Exception as e:
                    st.warning(f"❌ Có lỗi kết nối AI (Sai Key/Hết Quota): {e}")
                    
    if btn_demo:
        demo_data = [
            {
                "TenCongViec": "Hoàn thành Báo cáo nghiên cứu khả thi Dự án KDC Bàu Mạc",
                "TenDuAn": "KDC Bàu Mạc",
                "PhongBan": "Ban Kế hoạch Đầu tư",
                "Deadline": (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
            },
            {
                "TenCongViec": "Chuẩn bị hồ sơ xin cấp phép xây dựng tuyến đường Lê Trọng Tấn",
                "TenDuAn": "Tuyến đường Lê Trọng Tấn",
                "PhongBan": "Ban Kỹ thuật",
                "Deadline": (today + datetime.timedelta(days=15)).strftime("%Y-%m-%d")
            },
            {
                "TenCongViec": "Tuyển dụng bổ sung nhân sự chuyên trách cho Tổ KPI",
                "TenDuAn": "",
                "PhongBan": "Ban Hành chính Nhân sự",
                "Deadline": (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
            }
        ]
        st.session_state["tbgb_tasks"] = demo_data
        st.success("🎉 Đã nạp dữ liệu mẫu chạy thử nghiệm thành công!")
        
    st.markdown("---")
    
    if "tbgb_tasks" in st.session_state and st.session_state["tbgb_tasks"]:
        st.markdown("#### 📋 Kiểm tra & Chỉnh sửa danh sách công việc trích xuất")
        st.info("Nhấp đúp chuột vào các ô dưới đây để bổ sung hoặc sửa đổi thông tin trực tiếp nếu cần thiết:")
        
        editor_df = pd.DataFrame(st.session_state["tbgb_tasks"])
        
        if "TenCongViec" not in editor_df.columns:
            editor_df["TenCongViec"] = ""
        if "TenDuAn" not in editor_df.columns:
            editor_df["TenDuAn"] = ""
        if "PhongBan" not in editor_df.columns:
            editor_df["PhongBan"] = "Ban Lãnh đạo"
        if "Deadline" not in editor_df.columns:
            editor_df["Deadline"] = (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            
        edited_df = st.data_editor(
            editor_df,
            column_config={
                "TenCongViec": st.column_config.TextColumn("Tên công việc / Chỉ đạo giao ban", width="large", required=True),
                "TenDuAn": st.column_config.SelectboxColumn("Dự án liên quan", options=ALL_PROJECTS + [""], width="medium"),
                "PhongBan": st.column_config.SelectboxColumn("Ban / Bộ phận thực hiện", options=OFFICIAL_DEPARTMENTS, width="medium"),
                "Deadline": st.column_config.TextColumn("Hạn chót (YYYY-MM-DD)", width="small", required=True)
            },
            num_rows="dynamic",
            use_container_width=True,
            key="tbgb_editor_component"
        )
        
        st.session_state["tbgb_tasks"] = edited_df.to_dict(orient="records")
        
        col_btn1, col_btn2 = st.columns([3, 1])
        
        with col_btn1:
            btn_confirm = st.button("✅ Xác nhận & Đồng bộ vào Hệ thống Tiến độ", type="primary", use_container_width=True, key="btn_confirm_tbgb_sync")
            if btn_confirm:
                if not st.session_state["tbgb_tasks"]:
                    st.warning("⚠️ Danh sách công việc rỗng. Không có gì để lưu.")
                else:
                    tasks_df = read_db()
                    success_count = 0
                    
                    for row in st.session_state["tbgb_tasks"]:
                        task_name_raw = str(row.get("TenCongViec", "")).strip()
                        if not task_name_raw:
                            continue
                            
                        proj_name = str(row.get("TenDuAn", "")).strip()
                        dept_name = str(row.get("PhongBan", "")).strip()
                        if dept_name not in OFFICIAL_DEPARTMENTS:
                            dept_name = "Ban Lãnh đạo"
                            
                        try:
                            deadline_val = pd.to_datetime(row.get("Deadline")).date()
                        except Exception:
                            deadline_val = today + datetime.timedelta(days=7)
                            
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
                            "PhongBan": dept_name,
                            "NguoiChuTri": "Ban Lãnh đạo",
                            "TenDuAn": proj_name if proj_name else "Chỉ đạo Giao ban",
                            "MocTienDo": "Tự do",
                            "SanPhamBanGiao": "Xem báo cáo",
                            "TenCongViec": f"📋 [Chỉ đạo Giao ban] {task_name_raw}",
                            "PhanLoaiChiSo": "Chỉ số hành động (Activity Metric)",
                            "NgayBatDau": today,
                            "Deadline": deadline_val,
                            "DoUuTien": "Cao",
                            "PhanTramHoanThanh": 0,
                            "TrangThai": "Đang thực hiện",
                            "LinkKetQua": "",
                            "GiaiTrinhDeXuat": "",
                            "NgayCapNhat": datetime.datetime.now(),
                            "ChuKyTheoDoi": "Theo dự án / Tự do",
                            "PhanLoaiTreHan": "🟢 Không trễ hạn / Đúng tiến độ"
                        }
                        tasks_df = pd.concat([tasks_df, pd.DataFrame([new_task_row])], ignore_index=True)
                        success_count += 1
                        
                    if success_count > 0:
                        if save_db(tasks_df):
                            st.success(f"🎉 Đồng bộ thành công! Đã thêm {success_count} công việc chỉ đạo vào hệ thống.")
                            st.session_state["tbgb_tasks"] = []
                            st.rerun()
                            
        with col_btn2:
            btn_clear = st.button("🗑️ Xóa danh sách này", type="secondary", use_container_width=True, key="btn_clear_tbgb_tasks")
            if btn_clear:
                st.session_state["tbgb_tasks"] = []
                st.rerun()

# ----------------- 5. QUẢN LÝ CẤU HÌNH (ADMIN) -----------------
else:
    st.markdown("### ⚙️ Phân hệ Quản Lý Cấu Hình (Admin)")
    
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
