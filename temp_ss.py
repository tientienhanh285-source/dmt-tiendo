import sys
with open('app_fixed.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('temp_out.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if 'st.session_state' in line:
            f.write(f"{i}: {line}")
