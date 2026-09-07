import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the value=... for u_start and u_deadline to ensure they are python datetime.date objects
old_u_start = "u_start = st.date_input(\"Ngày bắt đầu thực hiện\", value=task_data['NgayBatDau'] if pd.notna(task_data['NgayBatDau']) else None, key=f\"u_start_{task_data['ID']}\")"
new_u_start = "u_start = st.date_input(\"Ngày bắt đầu thực hiện\", value=pd.to_datetime(task_data['NgayBatDau']).date() if pd.notna(task_data['NgayBatDau']) and str(task_data['NgayBatDau']).strip() != '' else today, key=f\"u_start_{task_data['ID']}\")"

old_u_deadline = "u_deadline = st.date_input(\"Hạn hoàn thành (Deadline)\", value=task_data['Deadline'] if pd.notna(task_data['Deadline']) else None, key=f\"u_deadline_{task_data['ID']}\")"
new_u_deadline = "u_deadline = st.date_input(\"Hạn hoàn thành (Deadline)\", value=pd.to_datetime(task_data['Deadline']).date() if pd.notna(task_data['Deadline']) and str(task_data['Deadline']).strip() != '' else today, key=f\"u_deadline_{task_data['ID']}\")"

# To avoid encoding mismatch in python strings, we can just replace the specific substring
content = content.replace("value=task_data['NgayBatDau'] if pd.notna(task_data['NgayBatDau']) else None", "value=pd.to_datetime(task_data['NgayBatDau']).date() if pd.notna(task_data['NgayBatDau']) and str(task_data['NgayBatDau']).strip() else today")
content = content.replace("value=task_data['Deadline'] if pd.notna(task_data['Deadline']) else None", "value=pd.to_datetime(task_data['Deadline']).date() if pd.notna(task_data['Deadline']) and str(task_data['Deadline']).strip() else today")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
