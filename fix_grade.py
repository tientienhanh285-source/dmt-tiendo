#
# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = '''        if f_score > 91:
            grade = "A"
            count_a += 1
        elif f_score > 81:
            grade = "B"
            count_b += 1
        elif f_score > 71:
            grade = "C"
            count_c += 1
        else:
            grade = "D"
            count_d += 1'''

new_block = '''        if f_score > 91:
            grade = "A"
            count_a += 1
        elif f_score > 81:
            grade = "B"
            count_b += 1
        elif f_score > 71:
            grade = "C"
            count_c += 1
        else:
            if selected_year_full == today.year and m == today.month:
                grade = "-"
            else:
                grade = "D"
                count_d += 1'''

text = text.replace(old_block, new_block)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
