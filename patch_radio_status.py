import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Create form
old_create = """            # 7. Completed flag instead of manual progress slider
            task_is_completed = st.checkbox("Đã hoàn thành công việc", value=False)
            
            # 8. Issue flag
            task_has_issue = st.checkbox("Công việc chưa hoàn thành, đang vướng mắc", value=False)"""

new_create = """            # 7 & 8. Status radio
            status_choice = st.radio("Trạng thái công việc", ["🔄 Đang thực hiện", "✅ Đã hoàn thành", "⚠️ Đang vướng mắc"], horizontal=True, key="new_status_choice")
            task_is_completed = (status_choice == "✅ Đã hoàn thành")
            task_has_issue = (status_choice == "⚠️ Đang vướng mắc")"""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

# Update form
old_update = """                    default_is_completed = task_data['TrangThai'] == 'Hoàn thành'
                    u_is_completed = st.checkbox("Đã hoàn thành công việc", value=default_is_completed, key=f"u_is_completed_{task_data['ID']}")
                    
                    default_has_issue = task_data['TrangThai'] == 'Có vướng mắc'
                    u_has_issue = st.checkbox("Công việc chưa hoàn thành, đang vướng mắc", value=default_has_issue, key=f"u_has_issue_{task_data['ID']}")"""

new_update = """                    u_current_status = task_data.get('TrangThai', 'Đang thực hiện')
                    if u_current_status == 'Hoàn thành':
                        u_idx = 1
                    elif u_current_status == 'Có vướng mắc':
                        u_idx = 2
                    else:
                        u_idx = 0
                    u_status_choice = st.radio("Trạng thái công việc", ["🔄 Đang thực hiện", "✅ Đã hoàn thành", "⚠️ Đang vướng mắc"], index=u_idx, horizontal=True, key=f"u_status_choice_{task_data['ID']}")
                    u_is_completed = (u_status_choice == "✅ Đã hoàn thành")
                    u_has_issue = (u_status_choice == "⚠️ Đang vướng mắc")"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
