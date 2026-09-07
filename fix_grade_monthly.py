with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(
    r'else: grade = "D"',
    'else:\n                if selected_year == today.year and selected_month == today.month:\n                    grade = "-"\n                else:\n                    grade = "D"',
    text
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
