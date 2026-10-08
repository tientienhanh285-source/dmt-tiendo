import re
with open('core_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove Đặng Ngọc Hoàng from HCNS
content = content.replace('"Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên", "Đặng Ngọc Hoàng"],',
                          '"Ban Hành chính Nhân sự": ["Nguyễn Thị Hạnh Tiên", "Nguyễn Băng Trinh", "Lê Ngọc Tú Uyên"],')

# Update Ban Chuẩn bị Đầu tư
content = content.replace('"Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Phan Thị Kim Cúc"],',
                          '"Ban Chuẩn bị Đầu tư": ["Hồ Văn Khoa", "Phan Thị Mỹ Hạnh", "Cao Thuỷ Tiên"],')

# Wait, if Cao Thuỷ Tiên is moved to CBĐT, should we remove her from KHĐT?
content = content.replace('"Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Cao Thuỷ Tiên", "Trần Tin"],',
                          '"Ban Kế hoạch Đầu tư": ["Nguyễn Trần Thức", "Nguyễn Đức Lợi", "Trần Tin"],')

with open('core_logic.py', 'w', encoding='utf-8') as f:
    f.write(content)
