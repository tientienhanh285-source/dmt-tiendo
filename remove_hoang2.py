import os
import glob
import re

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    old_str = '"HĐQT": ["Đặng Thanh Bình"]'
    new_str = '"HĐQT": ["Đặng Thanh Bình"]'
    
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced in {filepath}")

for f in glob.glob("*.py") + glob.glob("views/*.py"):
    replace_in_file(f)
