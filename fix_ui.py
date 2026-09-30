import os
import shutil

# Rename pages to views to avoid Streamlit auto-routing
if os.path.exists('pages'):
    if os.path.exists('views'):
        shutil.rmtree('views')
    os.rename('pages', 'views')
else:
    os.makedirs('views', exist_ok=True)

# Create missing files
missing_files = ['1_Tong_Quan.py', '2_Tien_Do.py', '4_Nghiem_Thu.py', '4_Nghiem_Thu_KQ.py']
for f in missing_files:
    path = os.path.join('views', f)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as out:
            out.write("import streamlit as st\n")
            out.write("st.title('Đang cập nhật giao diện này...')\n")

# Update app.py to use views/ instead of pages/
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

app_code = app_code.replace("st.Page('pages/", "st.Page('views/")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Fixed.")
