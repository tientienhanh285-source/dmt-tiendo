import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the undefined current_weight with the existing value from task_data
content = content.replace("u_weight = current_weight", "u_weight = task_data.get('TyTrongKPI', '')")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
