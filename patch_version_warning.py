import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert a warning at the top
if 'st.warning("BẢN CẬP NHẬT MỚI NHẤT ĐÃ ĐƯỢC ÁP DỤNG")' not in content:
    content = content.replace('import streamlit as st', 'import streamlit as st\n\nst.warning("BẢN CẬP NHẬT MỚI NHẤT ĐÃ ĐƯỢC ÁP DỤNG. NẾU BẠN THẤY DÒNG NÀY, APP ĐÃ REFRESH.")')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
