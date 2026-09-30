import glob

fallback = """
if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()
"""

for filepath in glob.glob("views/*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "df = display_df.copy()" in content:
        # Just append at the end of the config block
        content = content.replace("db_projs = []", "db_projs = []\n" + fallback)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Added robust fallbacks")
