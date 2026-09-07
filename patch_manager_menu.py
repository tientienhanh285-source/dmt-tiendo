import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_menu = """menu_options = [
    "📊 BẢNG TỔNG QUAN (View)",
    "📋 Bảng theo dõi tiến độ công việc",
    "➕ Thêm / Cập Nhật Công Việc",
    "📖 Sổ tay Hướng dẫn"
]

if st.session_state.is_admin_authenticated:"""

new_menu = """menu_options = [
    "📊 BẢNG TỔNG QUAN (View)",
    "📋 Bảng theo dõi tiến độ công việc",
    "➕ Thêm / Cập Nhật Công Việc",
    "📖 Sổ tay Hướng dẫn"
]

if st.session_state.get('is_manager_authenticated', False):
    menu_options = [
        "📊 BẢNG TỔNG QUAN (View)",
        "📋 Bảng theo dõi tiến độ công việc",
        "➕ Thêm / Cập Nhật Công Việc",
        "⚖️ Duyệt việc Khách quan",
        "📖 Sổ tay Hướng dẫn"
    ]

if st.session_state.is_admin_authenticated:"""

if old_menu in content:
    content = content.replace(old_menu, new_menu)
else:
    print("Could not find old_menu")

old_tab_check = """elif menu == "⚖️ Duyệt việc Khách quan":
    st.header("⚖️ Duyệt lý do trễ hạn khách quan")
    
    if not st.session_state.is_admin_authenticated:"""

new_tab_check = """elif menu == "⚖️ Duyệt việc Khách quan":
    st.header("⚖️ Duyệt lý do trễ hạn khách quan")
    
    if not (st.session_state.is_admin_authenticated or st.session_state.get('is_manager_authenticated', False)):"""

if old_tab_check in content:
    content = content.replace(old_tab_check, new_tab_check)
else:
    print("Could not find old_tab_check")


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
