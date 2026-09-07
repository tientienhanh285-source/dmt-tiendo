import re
app_file = "c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# Make absolutely sure NguoiChuTri exists in display_df globally
safe_check2 = """    display_df = df
    
if 'NguoiChuTri' not in display_df.columns:
    display_df['NguoiChuTri'] = ''"""

content = content.replace("    display_df = df", safe_check2)

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched display_df globally!")
