import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the yellow warning box
content = content.replace('st.warning("BẢN CẬP NHẬT MỚI NHẤT ĐÃ ĐƯỢC ÁP DỤNG. NẾU BẠN THẤY DÒNG NÀY, APP ĐÃ REFRESH.")\n\n', '')
content = content.replace('st.warning("BẢN CẬP NHẬT MỚI NHẤT ĐÃ ĐƯỢC ÁP DỤNG. NẾU BẠN THẤY DÒNG NÀY, APP ĐÃ REFRESH.")', '')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
