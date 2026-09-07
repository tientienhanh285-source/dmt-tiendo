import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the <br> in Create Form late cause
content = content.replace(
    '            if is_late:\n                st.markdown("<br>", unsafe_allow_html=True)\n                st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")',
    '            if is_late:\n                st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
