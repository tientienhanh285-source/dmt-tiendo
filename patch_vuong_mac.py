import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rename the checkboxes
content = content.replace(
    'task_has_issue = st.checkbox("Công việc đang gặp vướng mắc, cần hỗ trợ", value=False)',
    'task_has_issue = st.checkbox("Công việc chưa hoàn thành, đang vướng mắc", value=False)'
)
content = content.replace(
    'u_has_issue = st.checkbox("Công việc gặp vướng mắc, cần hỗ trợ", value=default_has_issue',
    'u_has_issue = st.checkbox("Công việc chưa hoàn thành, đang vướng mắc", value=default_has_issue'
)

# 2. Hide text_area for task_has_issue
# In Create form:
old_task_explain = """            else:
                if task_has_issue:
                    task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", key="new_task_explain")
                else:
                    task_explain = "" """
new_task_explain = """            else:
                task_explain = "" """
content = content.replace(old_task_explain, new_task_explain)

# In Update form:
old_u_explain = """                        if u_has_issue:
                            u_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                        else:
                            u_explain = "" """
new_u_explain = """                        u_explain = task_data.get('GiaiTrinhDeXuat', '') if pd.notna(task_data.get('GiaiTrinhDeXuat')) else "" """
content = content.replace(old_u_explain, new_u_explain)

# 3. Remove validation blocks
# Create form validation
old_val_1 = """            elif calc_status == "Có vướng mắc":
                if not task_explain or task_explain.strip() == "":
                    st.error("⚠️ Bắt buộc điền 'Ghi chú / Giải trình vướng mắc' chi tiết!")
                    return"""
content = content.replace(old_val_1, "")

# Update form validation
old_val_2 = """                    elif u_status == "Có vướng mắc":
                        if not u_explain or u_explain.strip() == "":
                            st.error("⚠️ Bắt buộc điền 'Ghi chú / Giải trình vướng mắc' chi tiết!")
                            return"""
content = content.replace(old_val_2, "")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
