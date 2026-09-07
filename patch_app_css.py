import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix CSS for header so it doesn't hide the calendar header
content = content.replace("header {visibility: hidden !important;}", '[data-testid="stHeader"] {visibility: hidden !important;}')
content = content.replace("header {visibility: hidden;}", '[data-testid="stHeader"] {visibility: hidden;}')

# Fix default deadline for task_deadline in 'Khởi tạo công việc mới'
content = content.replace(
    'task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today + timedelta(days=7)',
    'task_deadline = st.date_input("Hạn hoàn thành (Deadline)", today'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
