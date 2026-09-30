import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

injection = """
# Ghi lại các biến toàn cục quan trọng vào session_state để các trang có thể truy cập
st.session_state['role_mode'] = role_mode if 'role_mode' in locals() else 'Nhân viên'
st.session_state['is_local'] = is_local if 'is_local' in locals() else False

pg = st.navigation(pages)
"""

code = code.replace("pg = st.navigation(pages)", injection)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched app.py")
