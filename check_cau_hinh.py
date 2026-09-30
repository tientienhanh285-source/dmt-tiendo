# -*- coding: utf-8 -*-
import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/views/7_Cau_Hinh.py', 'r', 'utf-8') as f:
    lines = f.readlines()

with codecs.open('debug_cau_hinh3.txt', 'w', 'utf-8') as out:
    for i, line in enumerate(lines):
        if 'config =' in line or 'config=' in line:
            out.write(f"{i}: {line}")
