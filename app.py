import streamlit as st
import pandas as pd
import datetime
import os
import re
import json
import plotly.express as px

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

def init_config():
    if not os.path.exists("OUTPUT"):
        os.makedirs("OUTPUT", exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "projects_by_category": {
                "BĐS & KDC": [
                    "KDC Bàu Mạc", 
                    "KDC Nam Bàu Mạc", 
                    "KĐT Phước Lý & Phước Lý MR", 
                    "TĐC Phước Lý 2 & Hoà Liên 5", 
                    "Dự án Phong Nam", 
                    "Khu BT ST Hoà Ninh"
                ],
                "HẠ TẦNG & GIAO THÔNG": [
                    "Tuyến đường Lê Trọng Tấn", 
                    "Tuyến đường Lê Trọng Tấn - Hoà Nhơn", 
                    "Tuyến đường Trần Hưng Đạo (BT)", 
                    "Trục I Tây Bắc", 
                    "Khu TĐC Hoà Vang"
                ],
                "THƯƠNG MẠI & KHÁCH SẠN": [
                    "Khách sạn DMT-Group", 
                    "Du thuyền Happy Yacht (DMT Marina)"
                ]
            },
            "departments": [
                "Ban Lãnh đạo",
                "Ban Hành chính Nhân sự",
                "Ban Tài chính Kế toán",
                "Ban Kế hoạch Đầu tư",
                "Ban Chuẩn bị Đầu tư",
                "Ban Kỹ thuật",
                "Ban Đền bù Giải tỏa",
                "Tổ KPI"
            ],
            "personnel_by_department": DEFAULT_PERSONNEL
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu cấu hình: {e}")
        return False

def load_config():
    init_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        needs_save = False
        if "personnel_by_department" not in data:
            data["personnel_by_department"] = DEFAULT_PERSONNEL.copy()
            needs_save = True
        
        # Specific overrides/migration matching user request for default personnel
        kpi_p = data["personnel_by_department"].get("Tổ KPI", [])
        if kpi_p == ["Nguyễn Băng Trinh", "Nguyễn Thị Mỹ Phương", "Lê Thị Hải"]:
            data["personnel_by_department"]["Tổ KPI"] = []
            needs_save = True
            
        hcns_p = data["personnel_by_department"].get("Ban Hành chính Nhân sự", [])
        if hcns_p == ["Nguyễn Băng Trinh", "Nguyễn Thị Mỹ Phương", "Nguyễn Thị Hạnh Tiên"]:
            data["personnel_by_department"]["Ban Hành chính Nhân sự"] = ["Nguyễn Thị Hạnh Tiên"]
            needs_save = True
            
        tckt_p = data["personnel_by_department"].get("Ban Tài chính Kế toán", [])
        if tckt_p == ["Đồng Thị Nguyệt Nga", "Nguyễn Thị Ngọc Hà", "Lê Thị Hải"]:
            data["personnel_by_department"]["Ban Tài chính Kế toán"] = ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
            needs_save = True
        
        for dept in data.get("departments", []):
            if dept not in data["personnel_by_department"]:
                data["personnel_by_department"][dept] = []
                needs_save = True
                
        if needs_save:
            save_config(data)
            
        return data
    except Exception as e:
        st.error(f"Lỗi đọc cấu hình: {e}")
        return {
            "projects_by_category": {
                "BĐS & KDC": ["KDC Bàu Mạc", "KDC Nam Bàu Mạc", "KĐT Phước Lý & Phước Lý MR", "TĐC Phước Lý 2 & Hoà Liên 5", "Dự án Phong Nam", "Khu BT ST Hoà Ninh"],
                "HẠ TẦNG & GIAO THÔNG": ["Tuyến đường Lê Trọng Tấn", "Tuyến đường Lê Trọng Tấn - Hoà Nhơn", "Tuyến đường Trần Hưng Đạo (BT)", "Trục I Tây Bắc", "Khu TĐC Hoà Vang"],
                "THƯƠNG MẠI & KHÁCH SẠN": ["Khách sạn DMT-Group", "Du thuyền Happy Yacht (DMT Marina)"]
            },
            "departments": ["Ban Lãnh đạo", "Ban Hành chính Nhân sự", "Ban Tài chính Kế toán", "Ban Kế hoạch Đầu tư", "Ban Chuẩn bị Đầu tư", "Ban Kỹ thuật", "Ban Đền bù Giải tỏa", "Tổ KPI"],
            "personnel_by_department": DEFAULT_PERSONNEL.copy()
        }

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

def is_gsheets_configured():
    try:
        # Check if connections.gsheets exists in secrets
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return True
    except Exception:
        pass
    return False

def get_gsheets_conn():
    if is_gsheets_configured():
        try:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            return conn
        except Exception:
            # Tra ve None de chay offline neu co loi kết nối hoac import
            pass
    return None

# Generate flat list for dropdowns (brief clean names)
ALL_PROJECTS = []
for cat, projs in PROJECTS_BY_CATEGORY.items():
    for p in projs:
        ALL_PROJECTS.append(p)

DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

# Gantt DB Configuration
GANTT_DB_FILE = os.path.join("OUTPUT", "DATA_TIEN_DO_KPI.xlsx")

def init_gantt_db():
    if not os.path.exists("OUTPUT"):
        os.makedirs("OUTPUT", exist_ok=True)
    try:
        if os.path.exists(GANTT_DB_FILE):
            xls = pd.ExcelFile(GANTT_DB_FILE)
            if "GANTT_KHDT" in xls.sheet_names:
                df = pd.read_excel(GANTT_DB_FILE, sheet_name="GANTT_KHDT")
                if not df.empty:
                    return
        
        # Populate dummy data with localized Phase 1 - 8 names
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
            },
            {
                "ID": "GNT-002",
                "TenDuAn": "Dự án Xây dựng Khu Đô thị Marina",
                "TenCongViec": "Thiết kế quy hoạch & Kiến trúc",
                "GiaiDoan": "2. Pháp lý Dự án & Quy hoạch 1/500",
                "NgayBatDau": "2026-02-01",
                "NgayKetThuc": "2026-03-15",
                "PhanTramHoanThanh": 80,
                "Milestone": "",
                "NgayCapNhat": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                "ID": "GNT-003",
                "TenDuAn": "Dự án Xây dựng Khu Đô thị Marina",
                "TenCongViec": "Phê duyệt Pháp lý & Báo cáo KHĐT",
                "GiaiDoan": "2. Pháp lý Dự án & Quy hoạch 1/500",
                "NgayBatDau": "2026-02-01",
                "NgayKetThuc": "2026-03-02",
                "PhanTramHoanThanh": 100,
                "Milestone": "Mốc 1: Phê duyệt Pháp lý & GPXD",
                "NgayCapNhat": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                "ID": "GNT-004",
                "TenDuAn": "Dự án Xây dựng Khu Đô thị Marina",
                "TenCongViec": "Báo cáo Nghiên cứu Tiền khả thi",
                "GiaiDoan": "1. Chuẩn bị Đầu tư & Nghiên cứu Tiền khả thi",
                "NgayBatDau": "2026-03-15",
                "NgayKetThuc": "2026-04-15",
                "PhanTramHoanThanh": 40,
                "Milestone": "",
                "NgayCapNhat": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                "ID": "GNT-005",
                "TenDuAn": "Dự án Xây dựng Khu Đô thị Marina",
                "TenCongViec": "Trình duyệt Thẩm định Đầu tư",
                "GiaiDoan": "4. Thiết kế Bản vẽ Thi công & Thẩm định",
                "NgayBatDau": "2026-04-01",
                "NgayKetThuc": "2026-05-01",
                "PhanTramHoanThanh": 10,
                "Milestone": "Mốc 2: Cất nóc công trình",
                "NgayCapNhat": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        df_dummy = pd.DataFrame(dummy_data)
        if os.path.exists(GANTT_DB_FILE):
            with pd.ExcelWriter(GANTT_DB_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
                df_dummy.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
        else:
            with pd.ExcelWriter(GANTT_DB_FILE, engine="openpyxl") as writer:
                df_dummy.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
                
        # Sync GSheets if configured
        conn = get_gsheets_conn()
        if conn is not None:
            try:
                conn.update(worksheet="GANTT_KHDT", data=df_dummy)
            except Exception:
                pass
    except Exception as e:
        st.error(f"Lỗi khởi tạo Gantt DB: {e}")

def read_gantt_db():
    init_gantt_db()
    conn = get_gsheets_conn()
    df = None
    if conn is not None:
        try:
            df = conn.read(worksheet="GANTT_KHDT", ttl="0")
            if df is None or df.empty or len(df.columns) < 2:
                df = pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])
                conn.update(worksheet="GANTT_KHDT", data=df)
            else:
                df.columns = [str(c).strip() for c in df.columns]
                with pd.ExcelWriter(GANTT_DB_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
                    df.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
        except Exception as e:
            st.warning(f"Không thể đồng bộ Gantt từ Google Sheets (đang dùng cục bộ): {e}")

    if df is None:
        try:
            df = pd.read_excel(GANTT_DB_FILE, sheet_name="GANTT_KHDT")
        except Exception:
            df = pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])
            
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau']).dt.date
    df['NgayKetThuc'] = pd.to_datetime(df['NgayKetThuc']).dt.date
    df['NgayCapNhat'] = pd.to_datetime(df['NgayCapNhat'])
    df['ID'] = df['ID'].astype(str)
    df['TenDuAn'] = df['TenDuAn'].fillna('Dự án mặc định')
    df['TenCongViec'] = df['TenCongViec'].fillna('')
    df['GiaiDoan'] = df['GiaiDoan'].fillna('Khác')
    df['Milestone'] = df['Milestone'].fillna('')
    df['PhanTramHoanThanh'] = pd.to_numeric(df['PhanTramHoanThanh'], errors='coerce').fillna(0).astype(int)
    
    # Map old English/Vietnamese names to new standardized Phase 1 - 8 names if they exist
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
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayKetThuc'] = df_save['NgayKetThuc'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        
        with pd.ExcelWriter(GANTT_DB_FILE, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            df_save.to_excel(writer, sheet_name="GANTT_KHDT", index=False)
            
        conn = get_gsheets_conn()
        if conn is not None:
            try:
                conn.update(worksheet="GANTT_KHDT", data=df_save)
            except Exception as e:
                st.error(f"Lỗi đồng bộ dữ liệu Gantt lên Google Sheets: {e}")
        return True
    except Exception as e:
        st.error(f"Lỗi ghi dữ liệu Gantt: {e}")
        return False

def init_db():
    if not os.path.exists("OUTPUT"):
        os.makedirs("OUTPUT", exist_ok=True)
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=[
            "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
            "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
            "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat"
        ])
        df.to_excel(DB_FILE, index=False)

def calculate_time_progress(start_d, end_d, is_comp):
    if is_comp:
        return 100
    # Reference date (2026-07-23)
    today = datetime.date(2026, 7, 23)
    
    if not isinstance(start_d, (datetime.date, datetime.datetime)) or not isinstance(end_d, (datetime.date, datetime.datetime)):
        return 0
    if isinstance(start_d, datetime.datetime):
        start_d = start_d.date()
    if isinstance(end_d, datetime.datetime):
        end_d = end_d.date()
        
    if today < start_d:
        return 0
    if today > end_d:
        return 99
    
    total_days = (end_d - start_d).days
    if total_days <= 0:
        return 99
    
    elapsed_days = (today - start_d).days
    prog = int((elapsed_days / total_days) * 100)
    return min(max(prog, 0), 99)

def read_db():
    init_db()
    
    # Try to sync from Google Sheets first if configured
    conn = get_gsheets_conn()
    df = None
    if conn is not None:
        try:
            # Disable caching by setting ttl to 0 so we always get the fresh data on reload
            df = conn.read(worksheet="Sheet1", ttl="0")
            
            # Auto-initialize headers if Sheet1 is new/empty
            required_cols = [
                "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
                "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
                "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat"
            ]
            if df is None or df.empty or len(df.columns) < 2:
                df = pd.DataFrame(columns=required_cols)
                conn.update(worksheet="Sheet1", data=df)
            else:
                # Normalize column headers
                df.columns = [str(c).strip() for c in df.columns]
                # Sync back to local Excel
                df.to_excel(DB_FILE, index=False)
        except Exception as e:
            st.warning(f"Không thể đồng bộ từ Google Sheets (đang dùng dữ liệu cục bộ): {e}")

    if df is None:
        try:
            df = pd.read_excel(DB_FILE)
        except Exception as e:
            st.error(f"Lỗi đọc DB cục bộ: {e}")
            df = pd.DataFrame(columns=[
                "ID", "DonVi", "PhongBan", "NguoiChuTri", "TenDuAn", "MocTienDo", "SanPhamBanGiao",
                "TenCongViec", "PhanLoaiChiSo", "NgayBatDau", "Deadline", "DoUuTien", 
                "PhanTramHoanThanh", "TrangThai", "LinkKetQua", "GiaiTrinhDeXuat", "NgayCapNhat"
            ])

    # Clean data formats
    df['NgayBatDau'] = pd.to_datetime(df['NgayBatDau']).dt.date
    df['Deadline'] = pd.to_datetime(df['Deadline']).dt.date
    df['NgayCapNhat'] = pd.to_datetime(df['NgayCapNhat'])
    df['DonVi'] = df['DonVi'].fillna('CTY CP DMT - MARINA (Du thuyền Happy Yacht)')
    df['TenDuAn'] = df['TenDuAn'].fillna('')
    df['MocTienDo'] = df['MocTienDo'].fillna('Tự do')
    df['SanPhamBanGiao'] = df['SanPhamBanGiao'].fillna('Xem chi tiết')
    df['LinkKetQua'] = df['LinkKetQua'].fillna('')
    df['GiaiTrinhDeXuat'] = df['GiaiTrinhDeXuat'].fillna('')
    df['ID'] = df['ID'].astype(str)
    
    # Calculate progress dynamically based on time and status
    for idx, row in df.iterrows():
        is_comp = str(row['TrangThai']).strip() == "Hoàn thành"
        start_d = row['NgayBatDau']
        end_d = row['Deadline']
        df.at[idx, 'PhanTramHoanThanh'] = calculate_time_progress(start_d, end_d, is_comp)
        
    return df

def save_db(df):
    try:
        df_save = df.copy()
        df_save['NgayBatDau'] = df_save['NgayBatDau'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['Deadline'] = df_save['Deadline'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        df_save['NgayCapNhat'] = df_save['NgayCapNhat'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (datetime.date, datetime.datetime)) else str(x))
        
        # Save local Excel first
        df_save.to_excel(DB_FILE, index=False)
        
        # Save to Google Sheets if configured
        conn = get_gsheets_conn()
        if conn is not None:
            try:
                conn.update(worksheet="Sheet1", data=df_save)
            except Exception as e:
                st.error(f"Lỗi đồng bộ dữ liệu lên Google Sheets: {e}")
                
        return True
    except Exception as e:
        st.error(f"Lỗi ghi DB: {e}")
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

company_options = ["Tất cả đơn vị"] + list(COMPANIES.keys())
selected_company = st.sidebar.selectbox("CHỌN CÔNG TY / THÀNH VIÊN", company_options, index=1)

menu = st.sidebar.radio(
    "PHÂN HỆ CHỨC NĂNG",
    [
        "📊 Dashboard Tổng Quan",
        "📋 Bảng Tiến Độ Chi Tiết",
        "➕ Thêm / Cập Nhật Công Việc",
        "📊 SƠ ĐỒ GANTT DỰ ÁN DMT",
        "⚙️ Quản Lý Cấu Hình"
    ],
    index=0
)

st.sidebar.markdown("---")
work_mode = st.sidebar.radio(
    "👥 CHẾ ĐỘ GIAO DIỆN",
    [
        "👁️ Chế độ Xem (Lãnh đạo)",
        "✏️ Chế độ Cập nhật (Ban/Bộ phận)"
    ],
    index=0
)

# Reference date (2026-07-23)
df = read_db()
today = datetime.date(2026, 7, 23)

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
    
    # Overdue alerts scanning
    overdue_tasks = display_df[(display_df['Deadline'] < today) & (display_df['TrangThai'] != 'Hoàn thành')]
    if not overdue_tasks.empty:
        st.error("🚨 **CẢNH BÁO: PHÁT HIỆN CÔNG VIỆC TRỄ TIẾN ĐỘ / HẠN CHÓT**")
        alert_data = []
        for _, row in overdue_tasks.iterrows():
            days_late = (today - row['Deadline']).days
            alert_data.append({
                "Tên công việc": row['TenCongViec'],
                "Dự án / Hạng mục": row['TenDuAn'],
                "Ban phụ trách": row['PhongBan'],
                "Người phụ trách": row['NguoiChuTri'],
                "Số ngày trễ": f"{days_late} ngày"
            })
        st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        st.markdown("---")
    
    # 4 metrics cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Tổng số việc", total_v)
    with m_col2:
        st.metric("Đã xong", done_v)
    with m_col3:
        st.metric("Đang làm", doing_v)
    with m_col4:
        st.metric("🔴 Trễ hạn / Vướng mắc", issue_v + overdue_v)
        
    st.markdown("---")
    
    # Critical alert panel
    st.markdown("### ⚠️ Hạng mục cần lưu ý (Trễ hạn hoặc Có vướng mắc)")
    
    display_df['IsRealOverdue'] = (display_df['Deadline'] < today) & (display_df['TrangThai'] != 'Hoàn thành')
    critical_df = display_df[
        (display_df['TrangThai'] == 'Có vướng mắc') | 
        (display_df['TrangThai'] == 'Quá hạn') | 
        (display_df['IsRealOverdue'] == True)
    ]
    
    if not critical_df.empty:
        crit_display = pd.DataFrame()
        crit_display['Dự án / Hạng mục'] = critical_df['TenDuAn']
        crit_display['Tên công việc'] = critical_df['TenCongViec']
        crit_display['Phòng ban'] = critical_df['PhongBan']
        crit_display['Người thực hiện'] = critical_df['NguoiChuTri']
        crit_display['Hạn chót'] = critical_df['Deadline'].apply(lambda x: x.strftime('%d/%m/%Y'))
        crit_display['Trạng thái thực tế'] = critical_df.apply(
            lambda r: "⚠️ Trễ hạn" if (r['Deadline'] < today and r['TrangThai'] != 'Hoàn thành') else "🔴 Vướng mắc", 
            axis=1
        )
        crit_display['Ghi chú / Giải trình vướng mắc'] = critical_df['GiaiTrinhDeXuat']
        
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
        st.success("🎉 Đảm bảo tiến độ: Không có công việc nào bị trễ hạn hoặc gặp vướng mắc!")

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
                return f"⚠️ {date_str} (Trễ hạn)"
            elif 0 <= days_left <= 5:
                return f"⚠️ {date_str} (Sắp hạn)"
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
                
            days_left = (row['Deadline'] - today).days
            if 0 <= days_left <= 5:
                return "⏳ Đang thực hiện"
                
            if prog == 0 and row['NgayBatDau'] > today:
                return "❌ Chưa bắt đầu"
                
            # Default state based on start date
            if today >= row['NgayBatDau']:
                return "⏳ Đang thực hiện"
            else:
                return "❌ Chưa bắt đầu"
        df_display['Trạng thái'] = table_df.apply(format_status, axis=1)
        
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
    
    if work_mode == "👁️ Chế độ Xem (Lãnh đạo)":
        st.warning("🔒 **Chế độ Xem (Dành cho Lãnh đạo) đang kích hoạt.** Phân hệ này yêu cầu quyền cập nhật. Vui lòng chuyển sang **'Chế độ Cập nhật (Ban/Bộ phận)'** ở thanh Sidebar để chỉnh sửa/thêm dữ liệu.")
        st.stop()
        
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
            task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Nếu trễ hạn hoặc gặp vướng mắc)", placeholder="Mô tả chi tiết khó khăn...")
            
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
                        
                if calc_status in ["Có vướng mắc", "Quá hạn"]:
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
                        "GiaiTrinhDeXuat": task_explain.strip() if (calc_status in ["Có vướng mắc", "Quá hạn"]) else "",
                        "NgayCapNhat": datetime.datetime.now()
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
                    
                    u_proj = st.text_input("Dự án / Hạng mục", value=task_data['TenDuAn'])
                    u_name = st.text_input("Tên công việc", value=task_data['TenCongViec'])
                    
                    # Owner selection based on configuration
                    u_dept = task_data['PhongBan']
                    u_dept_personnel = get_personnel_for_company_dept(task_data['DonVi'], u_dept, config)
                    u_owner_options = list(u_dept_personnel) + ["✍️ Nhập tên người khác..."]
                    
                    current_owner = task_data['NguoiChuTri']
                    if current_owner in u_dept_personnel:
                        u_default_index = u_dept_personnel.index(current_owner)
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key="u_owner_sel")
                        if u_sel_owner_opt == "✍️ Nhập tên người khác...":
                            u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value="", key="u_owner_custom")
                        else:
                            u_owner = u_sel_owner_opt
                    else:
                        u_default_index = len(u_owner_options) - 1
                        u_sel_owner_opt = st.selectbox("Người thực hiện / Phụ trách", u_owner_options, index=u_default_index, key="u_owner_sel")
                        u_owner = st.text_input("✍️ Nhập tên người thực hiện khác...", value=current_owner, key="u_owner_custom")
                    
                with col_u2:
                    u_start = st.date_input("Ngày bắt đầu thực hiện", value=task_data['NgayBatDau'], format="DD/MM/YYYY")
                    u_deadline = st.date_input("Hạn hoàn thành (Deadline)", value=task_data['Deadline'], format="DD/MM/YYYY")
                    
                    default_is_completed = task_data['TrangThai'] == 'Hoàn thành'
                    u_is_completed = st.checkbox("Đã hoàn thành công việc", value=default_is_completed, key="u_is_completed")
                    
                    default_has_issue = task_data['TrangThai'] == 'Có vướng mắc'
                    u_has_issue = st.checkbox("Công việc gặp vướng mắc, cần hỗ trợ", value=default_has_issue)
                    
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
                                    key="btn_download_file"
                                )
                        else:
                            st.write(f"✍️ **Nội dung:** `{current_link}`")
                    else:
                        st.write("*(Chưa có kết quả/file đính kèm)*")
                    
                    st.markdown("---")
                    st.markdown("**Cập nhật Kết quả / File đính kèm**")
                    u_result_mode = st.radio("Hình thức nộp", ["Giữ nguyên hiện tại", "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key="u_result_mode")
                    
                    u_link_text = ""
                    u_file = None
                    if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                        u_link_text = st.text_input("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", key="u_result_text")
                    elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                        u_file = st.file_uploader("Tải file đính kèm mới", key="u_result_file")
                        
                with col_ub2:
                    u_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc nếu trễ hoặc gặp vướng mắc)", value=task_data['GiaiTrinhDeXuat'])
                    
                btn_save, btn_del = st.columns([4, 1])
                with btn_save:
                    save_click = st.button("💾 LƯU CẬP NHẬT TIẾN ĐỘ", type="primary", key="btn_save_update")
                with btn_del:
                    del_click = st.button("🗑️ XÓA CÔNG VIỆC CHỌN", type="secondary", key="btn_del_update")
                    
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
                            
                    if u_status in ["Có vướng mắc", "Quá hạn"]:
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
                        df.loc[df['ID'] == selected_id, 'GiaiTrinhDeXuat'] = u_explain.strip() if (u_status in ["Có vướng mắc", "Quá hạn"]) else ""
                        df.loc[df['ID'] == selected_id, 'NgayCapNhat'] = datetime.datetime.now()
                        
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
        
        # Overdue alerts scanning for Gantt tasks
        ref_today = datetime.date(2026, 7, 23)
        overdue_gantt = project_tasks_df[(project_tasks_df['NgayKetThuc'] < ref_today) & (project_tasks_df['PhanTramHoanThanh'] < 100)]
        if not overdue_gantt.empty:
            st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(overdue_gantt)} CÔNG VIỆC BỊ TRỄ TIẾN ĐỘ / HẠN CHÓT**")
            g_alert_data = []
            for _, row in overdue_gantt.iterrows():
                days_late = (ref_today - row['NgayKetThuc']).days
                g_alert_data.append({
                    "Tên công việc": row['TenCongViec'],
                    "Giai đoạn": row['GiaiDoan'],
                    "Tiến độ hiện tại": f"{row['PhanTramHoanThanh']}%",
                    "Số ngày trễ": f"{days_late} ngày"
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
            
            # Add vertical Today line (2026-07-23 is reference)
            ref_today = datetime.date(2026, 7, 23)
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
                
                ref_today = datetime.date(2026, 7, 23)
                
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
        if work_mode == "👁️ Chế độ Xem (Lãnh đạo)":
            st.warning("🔒 **Chỉnh sửa công việc Gantt đang bị khóa.** Vui lòng chuyển sang **'Chế độ Cập nhật (Ban/Bộ phận)'** trong thanh Sidebar để thêm/sửa/xóa công việc.")
            st.stop()
            
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
                today_ref = datetime.date(2026, 7, 23)
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

# ----------------- 5. QUẢN LÝ CẤU HÌNH (ADMIN) -----------------
else:
    st.markdown("### ⚙️ Phân hệ Quản Lý Cấu Hình (Admin)")
    
    if work_mode == "👁️ Chế độ Xem (Lãnh đạo)":
        st.warning("🔒 **Chế độ Xem (Dành cho Lãnh đạo) đang kích hoạt.** Tính năng cấu hình danh mục dự án, phòng ban và Google Sheets yêu cầu quyền cập nhật. Vui lòng chuyển sang **'Chế độ Cập nhật (Ban/Bộ phận)'** ở thanh Sidebar để chỉnh sửa.")
        st.stop()
        
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
