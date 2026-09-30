import os

file_path = r"views\5_Danh_Gia_KPI.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all occurrences of == 'Hoàn thành' with in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']
content = content.replace("== 'Hoàn thành'", "in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched 5_Danh_Gia_KPI.py successfully!")
