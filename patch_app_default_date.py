import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change today + timedelta(days=7) to today
content = content.replace("value=today + timedelta(days=7)", "value=today")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
