import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "#### ⚓ THÔNG TIN RÀNG BUỘC KẾT QUẢ & GIẢI TRÌNH" in line:
        continue # Skip the header
    
    if "**Kết quả / File đính kèm hiện tại**" in line:
        continue # Skip this, we will add it inside the if block
        
    if "current_link = task_data['LinkKetQua']" in line:
        new_lines.append(line)
        continue
        
    if "if current_link:" in line and "isinstance" not in line and "and not current_link" not in line:
        new_lines.append(line)
        # Add the title inside the if block
        indent = line.split("if current_link:")[0] + "    "
        new_lines.append(indent + "st.markdown(\"**Kết quả / File đính kèm hiện tại**\")\n")
        continue

    if 'st.write("*(Chưa có kết quả/file đính kèm)*")' in line:
        # We need to skip this line and the 'else:' before it.
        # So we pop the previous line if it was 'else:'
        if new_lines[-1].strip() == "else:":
            new_lines.pop()
        continue
        
    # We also need to move the `st.markdown("---")` inside the `if current_link:` block? 
    # Or keep it out? Actually if there's no link, we don't need the separator either, but maybe we do.
    # The user just said "bỏ ni đi" for the text. Let's keep `st.markdown("---")` out or remove it.
    # If we remove the text, having an empty block with a separator is fine or we can put it in the `if` block.
    # Let's put the separator inside the `if current_link:` block so it only shows if there's a link.
    if 'st.markdown("---")' in line and i > 2630 and i < 2650:
        indent = line.split("st.markdown")[0]
        new_lines.append(indent + "if current_link:\n")
        new_lines.append(indent + "    st.markdown(\"---\")\n")
        continue

    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done")
