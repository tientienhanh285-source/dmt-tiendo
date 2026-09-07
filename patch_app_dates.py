import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from datetime import date' not in content[:500]:
    content = content.replace('import streamlit as st', 'import streamlit as st\nfrom datetime import date', 1)

# Modify date_input calls
content = re.sub(
    r'st\.date_input\((.*?),\s*format="DD/MM/YYYY"(.*?)\)',
    r'st.date_input(\1, min_value=date(2020, 1, 1), max_value=date(2035, 12, 31), format="DD/MM/YYYY"\2)',
    content
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
