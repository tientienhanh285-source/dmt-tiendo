with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(
    r'else:\n\s+grade = "D"\n\s+count_d \+= 1',
    'else:\n            if selected_year_full == today.year and m == today.month:\n                grade = "-"\n            else:\n                grade = "D"\n                count_d += 1',
    text
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
