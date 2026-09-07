import re
content = open('app.py', encoding='utf-8').read()

with open('temp_main.txt', 'w', encoding='utf-8') as f:
    save_blocks = re.findall(r'.{0,300}st\.button\([\'"]💾 Lưu[\'"].{0,2000}', content, re.DOTALL)
    for block in save_blocks:
        f.write(block + "\n\n====\n\n")

    del_blocks = re.findall(r'.{0,300}st\.button\([\'"]🗑️ XÓA CÔNG VIỆC CHỌN[\'"].{0,2000}', content, re.DOTALL)
    for block in del_blocks:
        f.write(block + "\n\n====\n\n")
