import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add format="DD/MM/YYYY" to task_start and task_deadline
content = content.replace('task_start = st.date_input("Ngày bắt đầu thực hiện", today)', 'task_start = st.date_input("Ngày bắt đầu thực hiện", today, format="DD/MM/YYYY")')
content = content.replace('task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today)', 'task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today, format="DD/MM/YYYY")')

# Add format="DD/MM/YYYY" to u_start and u_deadline
content = content.replace('key=f"u_start_{task_data[\'ID\']}"', 'format="DD/MM/YYYY", key=f"u_start_{task_data[\'ID\']}"')
content = content.replace('key=f"u_deadline_{task_data[\'ID\']}"', 'format="DD/MM/YYYY", key=f"u_deadline_{task_data[\'ID\']}"')

# Add format="DD/MM/YYYY" to rep_start and rep_deadline
content = content.replace('key=f"rep_start_{task_data[\'ID\']}"', 'format="DD/MM/YYYY", key=f"rep_start_{task_data[\'ID\']}"')
content = content.replace('key=f"rep_deadline_{task_data[\'ID\']}"', 'format="DD/MM/YYYY", key=f"rep_deadline_{task_data[\'ID\']}"')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
