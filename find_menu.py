# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'BẢNG TỔNG QUAN' in line and ('if menu' in line or 'elif menu' in line):
        print(f"Line {i+1}: MATCH")