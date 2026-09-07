import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                    for m in range(1, 13):
                        def is_in_m(d):"""

replacement = """                    for m in range(1, 13):
                        if selected_year_full > today.year or (selected_year_full == today.year and m > today.month):
                            months_grades[f"Tháng {m}"] = "-"
                            continue
                        
                        def is_in_m(d):"""

if target in content:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print('Replaced target successfully')
else:
    print('Target not found')
