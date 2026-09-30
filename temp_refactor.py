import os
import ast
import re

def clean_core_logic():
    with open('core_logic.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove st.markdown(...)
    # Remove the first st.markdown block
    content = re.sub(r'st\.markdown\(\'\'\'.*?\'\'\',\s*unsafe_allow_html=True\)', '', content, flags=re.DOTALL)
    
    # Remove st.set_page_config
    content = re.sub(r'st\.set_page_config\([^)]+\)', '', content, flags=re.DOTALL)
    
    # Remove components.html
    content = re.sub(r'components\.html\([^)]+\)', '', content, flags=re.DOTALL)
    
    # Remove other st.markdown
    content = re.sub(r'st\.markdown\(""".*?<style>.*?</style>.*?""",\s*unsafe_allow_html=True\)', '', content, flags=re.DOTALL)
    
    # Write back
    with open('core_logic.py', 'w', encoding='utf-8') as f:
        f.write(content)

def clean_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find functions to remove
    tree = ast.parse("".join(lines))
    funcs_to_remove = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    
    # We want to remove lines that belong to these functions
    ranges = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            ranges.append((node.lineno, node.end_lineno))
            
    # Also remove the duplicate globals that are in core_logic
    globals_to_remove = ['SETTINGS_FILE', 'COMPANIES', 'CONFIG_FILE', 'DEFAULT_PERSONNEL', 'DB_FILE', 'GANTT_DB_FILE']
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in globals_to_remove:
                ranges.append((node.lineno, node.end_lineno))
    
    ranges.sort(key=lambda x: x[0])
    
    # Combine overlapping/adjacent ranges loosely, but we can just filter lines
    lines_to_keep = []
    for i, line in enumerate(lines):
        line_num = i + 1
        keep = True
        for start, end in ranges:
            if start <= line_num <= end:
                keep = False
                break
        
        # Actually ast includes decorators in lineno to end_lineno
        if keep:
            lines_to_keep.append(line)
            
    # Add from core_logic import * after import streamlit as st
    out_lines = []
    inserted = False
    for line in lines_to_keep:
        out_lines.append(line)
        if line.startswith('import streamlit as st') and not inserted:
            out_lines.append('from core_logic import *\n')
            inserted = True
            
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

if __name__ == '__main__':
    print("Cleaning core_logic.py...")
    clean_core_logic()
    print("Cleaning app.py...")
    clean_app_py()
    print("Done!")
