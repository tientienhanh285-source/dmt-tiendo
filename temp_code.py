import re
content = open('app.py', encoding='utf-8').read()

with open('temp_code_out.txt', 'w', encoding='utf-8') as f:
    buttons = re.findall(r'st\.button\([\'"](.*?)[\'"]', content)
    f.write("BUTTONS:\n")
    for b in set(buttons):
        f.write("- " + b + "\n")

    f.write("\n--- ADD TASK LOGIC ---\n")
    add_blocks = re.findall(r'if st\.button\([\'"](?:Thêm|Lưu|Add).*?[\'"].*?:\n(?:    .*\n)*', content)
    for block in add_blocks:
        f.write(block[:1000] + "\n...\n")

    f.write("\n--- DELETE TASK LOGIC ---\n")
    del_blocks = re.findall(r'if st\.button\([\'"](?:Xóa|Del).*?[\'"].*?:\n(?:    .*\n)*', content)
    for block in del_blocks:
        f.write(block[:1000] + "\n...\n")
