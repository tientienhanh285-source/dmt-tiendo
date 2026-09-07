#
# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("(1 đổi Tháng/Năm ở trên cùng)", "(1 quay lại tab 'Đánh giá theo Tháng' để đổi Tháng/Năm)")
text = text.replace("(1 xuất tháng khác, vui lòng đổi Tháng/Năm ở trên cùng)", "(1 quay lại tab 'Đánh giá theo Tháng' đổi)")
text = text.replace("(Để xuất tháng khác, vui lòng đổi Tháng/Năm ở trên cùng)", "(1 quay lại tab 'Đánh giá theo Tháng' để chọn)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
