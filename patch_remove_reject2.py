import codecs

with codecs.open('views/4_Nghiem_Thu.py', 'r', 'utf-8') as f:
    text = f.read()

bad2 = '''                            elif new_val == "❌ Từ chối (Làm lại)":
                                update_task(task_id, {'TrangThai': 'Đang thực hiện', 'PhanTramHoanThanh': 0})
                                changed = True'''

text = text.replace(bad2, '')

# There might be a second one for tab_khachquan
bad3 = '''                            elif new_val == "❌ Từ chối (Làm lại)":
                                update_task(task_id, {'TrangThai': 'Đang thực hiện', 'PhanTramHoanThanh': 0})
                                changed = True'''
text = text.replace(bad3, '')

with codecs.open('views/4_Nghiem_Thu.py', 'w', 'utf-8') as f:
    f.write(text)
