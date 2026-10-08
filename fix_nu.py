import os

def fix_core_logic():
    filepath = 'core_logic.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix DEFAULT_PERSONNEL
    old_str_1 = '"Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"]'
    new_str_1 = '"Ban Tài chính Kế toán": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang"]'
    content = content.replace(old_str_1, new_str_1)
    
    # Wait, she might also be in the JSON config string inside core_logic.py!
    old_str_2 = r'\"Ban Tài chính Kế toán\": [\"Đồng Thị Nguyệt Nga\", \"Huỳnh Thị Hoàng Hà\", \"Nguyễn Thị Nhật Sang\", \"Đoàn Thị Ngọc Nữ\"]'
    new_str_2 = r'\"Ban Tài chính Kế toán\": [\"Đồng Thị Nguyệt Nga\", \"Huỳnh Thị Hoàng Hà\", \"Nguyễn Thị Nhật Sang\"]'
    content = content.replace(old_str_2, new_str_2)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
fix_core_logic()
