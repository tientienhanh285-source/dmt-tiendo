import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

force_css = """
# Force calendar header visible to fix caching issues
st.markdown('''
    <style>
        div[data-baseweb="calendar"] header {
            visibility: visible !important;
            display: flex !important;
        }
    </style>
''', unsafe_allow_html=True)
"""

if '# Force calendar header visible' not in content:
    content = content.replace('import streamlit as st', 'import streamlit as st\n' + force_css, 1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
