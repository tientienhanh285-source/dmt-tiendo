import glob

for filepath in glob.glob("views/3_Cap_Nhat.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Move current_link definition outside the if block
    content = content.replace(
        "current_link = task_data['LinkKetQua']",
        ""
    )
    
    content = content.replace(
        "if u_status_choice is not None:",
        "current_link = task_data.get('LinkKetQua', '')\n            if u_status_choice is not None:"
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed current_link NameError in 3_Cap_Nhat.py")
