import codecs

with codecs.open('views/4_Nghiem_Thu.py', 'r', 'utf-8') as f:
    text = f.read()

bad_tab2 = 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)", "❌ Từ chối (Làm lại)"],'
good_tab2 = 'options=["Chờ duyệt", "✅ Duyệt (Hoàn thành)"],'

if bad_tab2 in text:
    text = text.replace(bad_tab2, good_tab2)
    print("Replaced in tab 2")

with codecs.open('views/4_Nghiem_Thu.py', 'w', 'utf-8') as f:
    f.write(text)
