import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Swap for Update Form
update_result_start = content.find("                current_link = task_data['LinkKetQua']")
update_result_end = content.find("                u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed")

if update_result_start != -1 and update_result_end != -1:
    result_block = content[update_result_start:update_result_end]
    
    update_late_end = content.find("                btn_save, btn_del = st.columns([3, 2])", update_result_end)
    late_block = content[update_result_end:update_late_end]
    
    # Swap them!
    content = content[:update_result_start] + late_block + "\n" + result_block + "\n" + content[update_late_end:]
    print("Update Form swapped.")

# 2. Swap for Create Form
create_result_start = content.find("            # 9. Kết quả / File đính kèm")
create_result_end = content.find("            # 10. Ghi chú vướng mắc")

if create_result_start != -1 and create_result_end != -1:
    result_block = content[create_result_start:create_result_end]
    
    create_late_end = content.find("            # 11. Chu kỳ theo dõi", create_result_end)
    late_block = content[create_result_end:create_late_end]
    
    # Swap them!
    content = content[:create_result_start] + late_block + "\n" + result_block + "\n" + content[create_late_end:]
    print("Create Form swapped.")


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
