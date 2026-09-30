# -*- coding: utf-8 -*-
import codecs

with codecs.open('c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py', 'r', 'utf-8') as f:
    lines = f.readlines()

with codecs.open('debug_load_config_2.txt', 'w', 'utf-8') as out:
    for i, line in enumerate(lines):
        if 'def load_config():' in line:
            for j in range(i+80, min(len(lines), i+150)):
                out.write(lines[j])
            break
