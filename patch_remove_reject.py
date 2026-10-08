import codecs

with codecs.open('views/4_Nghiem_Thu.py', 'r', 'utf-8') as f:
    text = f.read()

bad1 = 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)", "❌ Từ chối (Làm lại)"],'
good1 = 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)"],'

if bad1 in text:
    text = text.replace(bad1, good1)
    print("Replaced bad1")
else:
    print("bad1 not found")

bad2 = '''                            elif new_val == "❌ Từ chối (Làm lại)":
                                update_task(task_id, {'TrangThai': 'Đang thực hiện', 'PhanTramHoanThanh': 0})
                                changed = True'''
if bad2 in text:
    text = text.replace(bad2, '')
    print("Replaced bad2")
else:
    print("bad2 not found")

# There might also be a second tab with identical logic in 4_Nghiem_Thu.py
# If there is another tab, it will be replaced by text.replace

with codecs.open('views/4_Nghiem_Thu.py', 'w', 'utf-8') as f:
    f.write(text)
