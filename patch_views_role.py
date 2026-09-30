import glob

header_addition = """
if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False
"""

for filepath in glob.glob("views/*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Insert right after `config = load_config()` or something
    if "config = load_config()" in content:
        content = content.replace("config = load_config()", "config = load_config()\n" + header_addition)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Patched all views")
