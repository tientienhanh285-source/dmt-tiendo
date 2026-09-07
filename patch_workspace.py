import re
import sys

def run():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Menu
    old_menu = '''    [
        "📊 Dashboard Tổng Quan",
        "📋 Bảng Tiến Độ Chi Tiết",'''
    new_menu = '''    [
        "🚀 Trạm Điều Hành",'''
    content = content.replace(old_menu, new_menu)

    # 2. Extract and replace the UI sections
    dash_start_marker = 'if menu == "📊 Dashboard Tổng Quan":'
    dash_start_idx = content.find(dash_start_marker)
    
    add_task_marker = 'elif menu == "➕ Thêm / Cập Nhật Công Việc":'
    add_task_idx = content.find(add_task_marker)
    
    if dash_start_idx == -1 or add_task_idx == -1:
        print("Could not find markers")
        return

    old_block = content[dash_start_idx:add_task_idx]

    bang_tien_do_marker = 'elif menu == "📋 Bảng Tiến Độ Chi Tiết":'
    btd_start_idx = old_block.find(bang_tien_do_marker)
    
    if btd_start_idx == -1:
        print("Could not find Bảng Tiến Độ")
        return
        
    dashboard_code = old_block[:btd_start_idx]
    btd_code = old_block[btd_start_idx:]
    
    dashboard_lines = dashboard_code.split('\n')
    dashboard_body = "\n".join(dashboard_lines[1:])
    
    btd_lines = btd_code.split('\n')
    btd_body = "\n".join(btd_lines[1:])
    
    metrics_pattern = r"(\s+# Calculate stats based on filtered dash_df.*?\s+with m_col4:\s+st\.metric[^\n]+\n)"
    metrics_match = re.search(metrics_pattern, dashboard_body, flags=re.DOTALL)
    
    metrics_code = ""
    if metrics_match:
        metrics_code = metrics_match.group(1)
        dashboard_body = dashboard_body.replace(metrics_code, "")
        
    dashboard_body = re.sub(r'\s*st\.markdown\("### 📊 Dashboard Tổng Quan — [^\n]+', '', dashboard_body, count=1)
    btd_body = re.sub(r'\s*st\.markdown\("### 📋 Bảng Tiến Độ Công Việc Chi Tiết — [^\n]+', '', btd_body, count=1)

    def indent(text, spaces=4):
        return "\n".join((" " * spaces) + line if line.strip() else line for line in text.split('\n'))

    new_block = f"""if menu == "🚀 Trạm Điều Hành":
    st.info("💡 **Dành cho người mới:**\\n1. Vào mục Thêm công việc để ghi nhận việc mới 👉\\n2. Khi làm xong, vào mục Cập nhật tiến độ để kéo lên 100% 👉\\n3. Theo dõi hạn chót ở Dashboard.")
    
    st.markdown(f"### 🚀 Trạm Điều Hành — {{selected_company}}")
{metrics_code}
    st.markdown("---")
    
    tab_report, tab_data = st.tabs(["📊 Góc nhìn Báo cáo", "📋 Góc nhìn Bảng dữ liệu"])
    
    with tab_report:
{indent(dashboard_body, 4)}

    with tab_data:
{indent(btd_body, 4)}

"""
    
    new_content = content[:dash_start_idx] + new_block + content[add_task_idx:]
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Patched successfully")

if __name__ == "__main__":
    run()
