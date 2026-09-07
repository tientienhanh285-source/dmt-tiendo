import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the arguments causing issues
content = content.replace(', min_value=date(2020, 1, 1), max_value=date(2035, 12, 31), format="DD/MM/YYYY"', '')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
