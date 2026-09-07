import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("if u_is_completed and not current_link:", "if u_is_completed:")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
