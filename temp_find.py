lines = open('app.py', encoding='utf-8').readlines()
with open('temp_out.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines):
        if 'NgayCapNhat' in line:
            f.write(f'{i}: {line.strip()}\n')
