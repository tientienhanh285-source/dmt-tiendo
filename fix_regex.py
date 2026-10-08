import os
import glob
import re

new_dict_content = """
    "Trần Quốc Thể": ["Trần Quốc Thể", "Hồ Văn Khoa", "Nguyễn Trần Thức", "Mai Văn Châu", "Nguyễn Văn Bồn"],
    "Đoàn Thị Ngọc Nữ": ["Đoàn Thị Ngọc Nữ", "Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà", "Nguyễn Thị Nhật Sang", "Nguyễn Thị Như Can"],
    "Nguyễn Ngọc Tôn": ["Nguyễn Ngọc Tôn", "Đặng Công Nhựt", "Đặng Thị Mỹ Hạnh", "Đặng Thanh Quang"],
    "Đặng Ngọc Hoàng": ["Đặng Ngọc Hoàng", "Nguyễn Thị Hạnh Tiên", "Trần Cường", "Ngô Thị Tâm"],
    "Thái Văn Thành": ["Thái Văn Thành", "Trần Văn Trọng", "Nguyễn Thị Ngọc Hà", "Nguyễn Thị Mỹ Phương", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền", "Lê Nho Tân", "Nguyễn Văn Bồn"],
    "Trần Văn Trọng": ["Lê Nho Tân", "Phạm Quang Nghĩa", "Nguyễn Phong Trung", "Lê Đông", "Phạm Văn Long", "Lê Văn Thành", "Ngô Văn Hoàng", "Đặng Hiền"],
    "Trần Cường": ["Trần Cường"],
    "Nguyễn Thị Ngọc Hà": ["Nguyễn Thị Ngọc Hà", "Huỳnh Thị Hoàng Hà"],
    "Đồng Thị Nguyệt Nga": ["Đồng Thị Nguyệt Nga", "Huỳnh Thị Hoàng Hà"]
"""

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = re.compile(r'([ \t]*)bld_hierarchy\s*=\s*\{(.*?)\n\1\}', re.DOTALL)
    
    def repl(match):
        indent = match.group(1)
        lines = new_dict_content.strip("\n").split("\n")
        indented_lines = [(indent + "    " + line.strip()) for line in lines]
        new_inner = "\n".join(indented_lines) + "\n"
        return f"{indent}bld_hierarchy = {{\n{new_inner}{indent}}}"

    new_content, count = pattern.subn(repl, content)
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Replaced {count} instances in {filepath}")

for f in glob.glob("views/*.py"):
    replace_in_file(f)
