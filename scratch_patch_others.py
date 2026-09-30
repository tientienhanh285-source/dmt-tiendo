import os

files_to_patch = [
    r"views\1_Tong_Quan.py",
    r"views\2_Tien_Do.py",
]

for file_path in files_to_patch:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace("== 'Hoàn thành'", "in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']")
        content = content.replace('== "Hoàn thành"', 'in ["Hoàn thành", "Hoàn thành (Trễ hạn)"]')

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Patched {file_path} successfully!")
