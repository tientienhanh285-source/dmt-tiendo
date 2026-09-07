import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace in Create Form
old_create = """            # 7 & 8. Status checkboxes
            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
            task_is_completed = st.checkbox("✅ Xác nhận ĐÃ HOÀN THÀNH công việc", value=False)
            task_has_issue = st.checkbox("⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC", value=False)
            if task_is_completed and task_has_issue:
                st.error("⚠️ Không thể chọn cả 2 trạng thái cùng lúc! Vui lòng bỏ tick 1 ô.")
                st.stop()"""

new_create = """            # 7 & 8. Status radio
            st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
            status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
            task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
            task_is_completed = (task_status_choice == status_opts[0])
            task_has_issue = (task_status_choice == status_opts[1])"""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

# 2. Replace in Update Form
old_update = """                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    default_is_completed = task_data['TrangThai'] == 'Hoàn thành'
                    u_is_completed = st.checkbox("✅ Xác nhận ĐÃ HOÀN THÀNH công việc", value=default_is_completed, key=f"u_is_completed_{task_data['ID']}")
                    
                    default_has_issue = task_data['TrangThai'] == 'Có vướng mắc'
                    u_has_issue = st.checkbox("⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC", value=default_has_issue, key=f"u_has_issue_{task_data['ID']}")
                    if u_is_completed and u_has_issue:
                        st.error("⚠️ Không thể chọn cả 2 trạng thái cùng lúc! Vui lòng bỏ tick 1 ô.")
                        st.stop()"""

new_update = """                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    u_status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    
                    u_current_status = task_data.get('TrangThai', 'Đang thực hiện')
                    if u_current_status == 'Hoàn thành':
                        u_status_idx = 0
                    elif u_current_status == 'Có vướng mắc':
                        u_status_idx = 1
                    else:
                        u_status_idx = None
                        
                    u_status_choice = st.radio("Trạng thái công việc", u_status_opts, index=u_status_idx, label_visibility="collapsed", key=f"u_status_choice_{task_data['ID']}")
                    u_is_completed = (u_status_choice == u_status_opts[0])
                    u_has_issue = (u_status_choice == u_status_opts[1])"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
