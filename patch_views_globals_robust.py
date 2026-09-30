import glob

global_vars = """
if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

if 'display_df' not in locals():
    try:
        display_df = read_db()
    except:
        pass

if 'df' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []
"""

for filepath in glob.glob("views/*.py"):
    # Re-extract the original file from backup to be absolutely clean
    with open('extract_from_backup.py', 'r', encoding='utf-8') as f:
        pass
    
    # We will just inject it. The re-extraction was already done cleanly.
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove old manual config = load_config() if any
    content = content.replace("config = load_config()\n", "")
    
    lines = content.split('\n')
    
    # Find last import
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i
            
    # Inject
    lines.insert(last_import_idx + 1, global_vars)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))

print("Patched all views with PROPER global variables")
