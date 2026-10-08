with open('core_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"DA": []', '"DA": ["Nguyễn Quốc Vinh"]')
content = content.replace('"Ban Dự án": []', '"Ban Dự án": ["Nguyễn Quốc Vinh"]')

with open('core_logic.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated core_logic.py")
