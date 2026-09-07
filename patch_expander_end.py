import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_end = """                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                task_is_completed = False
                task_has_issue = False
                task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                task_explain = ""
                result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                task_link_text = ""
                task_file = None"""

new_end = """                    st.markdown("</div>", unsafe_allow_html=True)"""

if old_end in content:
    content = content.replace(old_end, new_end)
else:
    print("Could not find old_end")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
