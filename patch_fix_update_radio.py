import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the two specific <br> tags in Update Form that cause gap
content = content.replace('                    st.markdown("<br>", unsafe_allow_html=True)\n                current_link = task_data[\'LinkKetQua\']', '                current_link = task_data[\'LinkKetQua\']')
content = content.replace('                    st.markdown("<br>", unsafe_allow_html=True)\n                u_is_late = ', '                u_is_late = ')

# Replace selectbox with radio in Update Form
old_selectbox = """                if u_is_late:
                    u_options = ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                    u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                    u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                    u_late_cause = st.selectbox(
                        "Phân loại nguyên nhân trễ hạn",
                        u_options,
                        index=u_default_idx,
                        key=f"u_late_cause_sel_{task_data['ID']}"
                    )"""

new_radio = """                if u_is_late:
                    st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                    u_options = ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                    u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                    u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                    u_late_cause = st.radio(
                        "Phân loại nguyên nhân trễ hạn",
                        u_options,
                        index=u_default_idx,
                        label_visibility="collapsed",
                        key=f"u_late_cause_sel_{task_data['ID']}"
                    )"""

if old_selectbox in content:
    content = content.replace(old_selectbox, new_radio)
else:
    print("Could not find old_selectbox")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
