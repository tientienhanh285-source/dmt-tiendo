import os

def patch_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove Nguyễn Đình Thắng from exceptions
    content = content.replace(
        'exceptions = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Mai Văn Châu", "Nguyễn Đình Thắng", "Nguyễn Văn Bồn"]',
        'exceptions = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Mai Văn Châu", "Nguyễn Văn Bồn"]'
    )

    # 2. Remove overrides for Nữ and Thể
    # We will just replace the exact block if it exists
    block_to_remove = '''            if "TCKT" in new_personnel and "Đoàn Thị Ngọc Nữ" not in new_personnel["TCKT"]:
                new_personnel["TCKT"].append("Đoàn Thị Ngọc Nữ")
            if "KHĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["KHĐT"]:
                new_personnel["KHĐT"].append("Trần Quốc Thể")
            if "CBĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["CBĐT"]:
                new_personnel["CBĐT"].append("Trần Quốc Thể")'''
    
    if block_to_remove in content:
        content = content.replace(block_to_remove, '')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched app.py")

def patch_views():
    for f_name in os.listdir('views'):
        if f_name.endswith('.py'):
            f_path = os.path.join('views', f_name)
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace Thể
            # It could be: "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"]
            # Or with more: "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn", "Ngô Thị Tâm", "Nguyễn Đình Thắng", "Nguyễn Đình Hiếu"]
            
            import re
            content = re.sub(
                r'"Trần Quốc Thể":\s*\["Trần Quốc Thể",\s*"Hồ Văn Khoa",\s*"Nguyễn Trần Thức",\s*"Mai Văn Châu",\s*"Nguyễn Văn Bồn"(?:,\s*"Ngô Thị Tâm",\s*"Nguyễn Đình Thắng",\s*"Nguyễn Đình Hiếu")?\]',
                r'"Trần Quốc Thể": ["Trần Quốc Thể", "Mai Văn Châu"]',
                content
            )
            
            # Replace Nữ
            content = re.sub(
                r'"Đoàn Thị Ngọc Nữ":\s*\["Đoàn Thị Ngọc Nữ",\s*"Đồng Thị Nguyệt Nga",\s*"Huỳnh Thị Hoàng Hà",\s*"Nguyễn Thị Nhật Sang",\s*"Nguyễn Thị Như Can"\]',
                r'"Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ"]',
                content
            )
            
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {f_path}")

if __name__ == '__main__':
    patch_app_py()
    patch_views()
