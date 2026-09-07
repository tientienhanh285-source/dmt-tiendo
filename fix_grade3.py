#
# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_text = '''        elif f_score > 71:
            grade = "C"
            count_c += 1
        else:
            grade = "D"
            count_d += 1
        
        months_grades[f"Tháng {m}"] = grade'''

new_text = '''        elif f_score > 71:
            grade = "C"
            count_c += 1
        else:
            if selected_year_full == today.year and m == today.month:
                grade = "-"
            else:
                grade = "D"
                count_d += 1
        
        months_grades[f"Tháng {m}"] = grade'''

text = text.replace(old_text, new_text)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
