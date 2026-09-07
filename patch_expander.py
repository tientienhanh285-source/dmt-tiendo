import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = """            st.markdown("<br>", unsafe_allow_html=True)
            quick_complete = st.checkbox("🚀 Tiến hành cập nhật trạng thái / nộp kết quả ngay (Quick Complete)", value=False, key="quick_complete")
            
            if quick_complete:
                with st.container():"""

new_start = """            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🔽 Tùy chọn nâng cao: Ghi nhận trạng thái / Nộp kết quả ngay", expanded=False):
                with st.container():"""

if old_start in content:
    content = content.replace(old_start, new_start)
else:
    print("Could not find old_start")

old_end = """                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                task_is_completed = False
                task_has_issue = False
                task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                task_explain = ""
                result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                task_link_text = ""
                task_file = None
                
            # 11. Chu kỳ theo dõi"""

new_end = """                    st.markdown("</div>", unsafe_allow_html=True)
                
            # 11. Chu kỳ theo dõi"""

if old_end in content:
    content = content.replace(old_end, new_end)
else:
    print("Could not find old_end")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
