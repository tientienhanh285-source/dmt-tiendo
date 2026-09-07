import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Create Form
old_create = """                    # 7 & 8. Status radio
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                    task_is_completed = (task_status_choice == status_opts[0])
                    task_has_issue = (task_status_choice == status_opts[1])"""

new_create = """                    # 7 & 8. Status radio
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    is_late_for_status = (task_deadline < today)
                    if is_late_for_status:
                        status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    else:
                        status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc"]
                    task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                    task_is_completed = (task_status_choice == "✅ Xác nhận ĐÃ HOÀN THÀNH công việc")
                    task_has_issue = (task_status_choice == "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC")"""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

# 2. Update Form
old_update = """                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
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

new_update = """                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    u_current_status = task_data.get('TrangThai', 'Đang thực hiện')
                    u_is_late_for_status = (u_deadline is not None and u_deadline < today)
                    if u_is_late_for_status or u_current_status == 'Có vướng mắc':
                        u_status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    else:
                        u_status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc"]
                    
                    if u_current_status == 'Hoàn thành':
                        u_status_idx = 0
                    elif u_current_status == 'Có vướng mắc':
                        u_status_idx = 1
                    else:
                        u_status_idx = None
                        
                    u_status_choice = st.radio("Trạng thái công việc", u_status_opts, index=u_status_idx, label_visibility="collapsed", key=f"u_status_choice_{task_data['ID']}")
                    u_is_completed = (u_status_choice == "✅ Xác nhận ĐÃ HOÀN THÀNH công việc")
                    u_has_issue = (u_status_choice == "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC")"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
