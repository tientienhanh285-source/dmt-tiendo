import os
import re

def patch_all_py_files():
    for f_name in os.listdir('.'):
        if f_name.endswith('.py'):
            with open(f_name, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            
            # 1. Remove Nguyễn Đình Thắng from exceptions
            content = content.replace(
                'exceptions = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Mai Văn Châu", "Nguyễn Đình Thắng", "Nguyễn Văn Bồn"]',
                'exceptions = ["Nguyễn Thị Hạnh Tiên", "Ngô Thị Tâm", "Mai Văn Châu", "Nguyễn Văn Bồn"]'
            )

            # 2. Remove override blocks
            block1 = '''            if "TCKT" in new_personnel and "Đoàn Thị Ngọc Nữ" not in new_personnel["TCKT"]:
                new_personnel["TCKT"].append("Đoàn Thị Ngọc Nữ")
            if "KHĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["KHĐT"]:
                new_personnel["KHĐT"].append("Trần Quốc Thể")
            if "CBĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["CBĐT"]:
                new_personnel["CBĐT"].append("Trần Quốc Thể")
            if "XN DTBD" in new_personnel and "Trần Quốc Thể" not in new_personnel["XN DTBD"]:
                new_personnel["XN DTBD"].append("Trần Quốc Thể")'''
            
            block2 = '''            if "TCKT" in new_personnel and "Đoàn Thị Ngọc Nữ" not in new_personnel["TCKT"]:
                new_personnel["TCKT"].append("Đoàn Thị Ngọc Nữ")
            if "KHĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["KHĐT"]:
                new_personnel["KHĐT"].append("Trần Quốc Thể")
            if "CBĐT" in new_personnel and "Trần Quốc Thể" not in new_personnel["CBĐT"]:
                new_personnel["CBĐT"].append("Trần Quốc Thể")'''
                
            content = content.replace(block1, '').replace(block2, '')

            # 3. Modify inline DEPT_LEADS dict
            content = re.sub(
                r'"TCKT":\s*\["Đoàn Thị Ngọc Nữ",\s*"Đồng Thị Nguyệt Nga"\]',
                r'"TCKT": ["Đồng Thị Nguyệt Nga"]',
                content
            )
            content = re.sub(
                r'"KHĐT":\s*\["Nguyễn Trần Thức",\s*"Trần Quốc Thể"\]',
                r'"KHĐT": ["Nguyễn Trần Thức"]',
                content
            )
            content = re.sub(
                r'"CBĐT":\s*\["Hồ Văn Khoa",\s*"Trần Quốc Thể"\]',
                r'"CBĐT": ["Hồ Văn Khoa"]',
                content
            )
            content = re.sub(
                r'"KT":\s*\["Trần Quốc Thể"\]',
                r'"KT": []',
                content
            )
            content = re.sub(
                r'"DA":\s*\["Nguyễn Đình Thắng"\]',
                r'"DA": []',
                content
            )
            content = re.sub(
                r'"XN DTBD":\s*\["Mai Văn Châu",\s*"Trần Quốc Thể"\]',
                r'"XN DTBD": ["Mai Văn Châu"]',
                content
            )

            if content != original:
                with open(f_name, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Patched {f_name}")

if __name__ == '__main__':
    patch_all_py_files()
