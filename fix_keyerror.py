import re
app_file = "c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the KeyError by ensuring kpi_df has 'NguoiChuTri'
# I'll inject a safe check right after kpi_df = display_df.copy()
safe_check = """        kpi_df = display_df.copy()
        if 'NguoiChuTri' not in kpi_df.columns:
            kpi_df['NguoiChuTri'] = ''"""

content = content.replace("        kpi_df = display_df.copy()", safe_check)

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched kpi_df to prevent KeyError!")
