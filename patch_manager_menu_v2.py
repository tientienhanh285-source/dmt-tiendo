import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Fix menu_options
for i, line in enumerate(lines):
    if line.strip() == "if st.session_state.is_admin_authenticated:" and "menu_options" in lines[i+1]:
        # Insert Manager menu logic right before this line
        manager_menu = """if st.session_state.get('is_manager_authenticated', False):
    menu_options = [
        "📊 BẢNG TỔNG QUAN (View)",
        "📋 Bảng theo dõi tiến độ công việc",
        "➕ Thêm / Cập Nhật Công Việc",
        "⚖️ Duyệt việc Khách quan",
        "📖 Sổ tay Hướng dẫn"
    ]

"""
        lines.insert(i, manager_menu)
        break

# 2. Fix the Duyệt việc Khách quan tab check
for i, line in enumerate(lines):
    if 'elif menu == ' in line and 'Khách quan' in line and 'Duyệt' in line:
        # Look for the if check in the next 10 lines
        for j in range(i, i+10):
            if 'if not st.session_state.is_admin_authenticated:' in lines[j]:
                lines[j] = lines[j].replace('if not st.session_state.is_admin_authenticated:', 'if not (st.session_state.is_admin_authenticated or st.session_state.get("is_manager_authenticated", False)):')
                break
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done")
