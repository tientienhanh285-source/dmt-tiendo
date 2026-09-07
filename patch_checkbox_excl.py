import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Create form
old_create = """            # 7 & 8. Status radio
            status_choice = st.radio("Trạng thái công việc", ["🔄 Đang thực hiện", "✅ Đã hoàn thành", "⚠️ Đang vướng mắc"], horizontal=True, key="new_status_choice")
            task_is_completed = (status_choice == "✅ Đã hoàn thành")
            task_has_issue = (status_choice == "⚠️ Đang vướng mắc")"""

new_create = """            # 7 & 8. Status checkboxes
            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
            task_is_completed = st.checkbox("✅ Xác nhận ĐÃ HOÀN THÀNH công việc", value=False)
            task_has_issue = st.checkbox("⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC", value=False)
            if task_is_completed and task_has_issue:
                st.error("⚠️ Không thể chọn cả 2 trạng thái cùng lúc! Vui lòng bỏ tick 1 ô.")
                st.stop()"""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

# Update form
old_update = """                    u_current_status = task_data.get('TrangThai', 'Đang thực hiện')
                    if u_current_status == 'Hoàn thành':
                        u_idx = 1
                    elif u_current_status == 'Có vướng mắc':
                        u_idx = 2
                    else:
                        u_idx = 0
                    u_status_choice = st.radio("Trạng thái công việc", ["🔄 Đang thực hiện", "✅ Đã hoàn thành", "⚠️ Đang vướng mắc"], index=u_idx, horizontal=True, key=f"u_status_choice_{task_data['ID']}")
                    u_is_completed = (u_status_choice == "✅ Đã hoàn thành")
                    u_has_issue = (u_status_choice == "⚠️ Đang vướng mắc")"""

new_update = """                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    default_is_completed = task_data['TrangThai'] == 'Hoàn thành'
                    u_is_completed = st.checkbox("✅ Xác nhận ĐÃ HOÀN THÀNH công việc", value=default_is_completed, key=f"u_is_completed_{task_data['ID']}")
                    
                    default_has_issue = task_data['TrangThai'] == 'Có vướng mắc'
                    u_has_issue = st.checkbox("⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC", value=default_has_issue, key=f"u_has_issue_{task_data['ID']}")
                    if u_is_completed and u_has_issue:
                        st.error("⚠️ Không thể chọn cả 2 trạng thái cùng lúc! Vui lòng bỏ tick 1 ô.")
                        st.stop()"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
