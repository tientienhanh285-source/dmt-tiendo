import codecs

with codecs.open('views/4_Nghiem_Thu.py', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'elif new_val == "❌ Từ chối (Làm lại)":' in line:
        skip = True
        continue
    if skip:
        if 'changed = True' in line:
            skip = False
            continue
        elif 'update_task' in line:
            continue
    new_lines.append(line)

with codecs.open('views/4_Nghiem_Thu.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)

# Also check 4_Nghiem_Thu_KQ.py if it exists
try:
    with codecs.open('views/4_Nghiem_Thu_KQ.py', 'r', 'utf-8') as f:
        lines2 = f.readlines()
        
    new_lines2 = []
    skip2 = False
    for line in lines2:
        if 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)", "❌ Từ chối (Làm lại)"],' in line:
            line = line.replace('options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)", "❌ Từ chối (Làm lại)"],', 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)"],')
        if 'elif new_val == "❌ Từ chối (Làm lại)":' in line:
            skip2 = True
            continue
        if skip2:
            if 'changed = True' in line:
                skip2 = False
                continue
            elif 'update_task' in line:
                continue
        new_lines2.append(line)
        
    with codecs.open('views/4_Nghiem_Thu_KQ.py', 'w', 'utf-8') as f:
        f.writelines(new_lines2)
except Exception:
    pass
