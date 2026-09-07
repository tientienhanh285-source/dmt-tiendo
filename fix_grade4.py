#
# -*- coding: utf-8 -*-
import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_text = re.sub(
    r'elif f_score > 71:\s+grade = "C"\s+count_c \+= 1\s+else:\s+grade = "D"\s+count_d \+= 1',
    'elif f_score > 71:\n                    grade = "C"\n                    count_c += 1\n                else:\n                    if selected_year_full == today.year and m == today.month:\n                        grade = "-"\n                    else:\n                        grade = "D"\n                        count_d += 1',
    text
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
