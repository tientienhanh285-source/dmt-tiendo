with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'elif f_score > 71:' in line:
        # We need to fix the lines from here until months_grades
        lines[i+1] = '                            grade = "C"\n'
        lines[i+2] = '                            count_c += 1\n'
        lines[i+3] = '                        else:\n'
        lines[i+4] = '                            if selected_year_full == today.year and m == today.month:\n'
        lines[i+5] = '                                grade = "-"\n'
        lines[i+6] = '                            else:\n'
        lines[i+7] = '                                grade = "D"\n'
        lines[i+8] = '                                count_d += 1\n'
        lines[i+9] = '                            \n'
        lines[i+10] = '                        months_grades[f"Tháng {m}"] = grade\n'
        break

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
