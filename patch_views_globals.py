import glob

global_vars = """
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
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Insert right before the actual logic
    if "config = load_config()" in content:
        content = content.replace("config = load_config()", "config = load_config()\n" + global_vars)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Patched all views with global variables")
