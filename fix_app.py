import os
import re

def fix_app():
    filepath = 'app.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will remove DEPT_ABBR and DEPT_LEADS from app.py
    # They are from line 153 to 198 approx.
    
    pattern = re.compile(r'# Default owners by department and company for autofill\nDEPT_ABBR = \{.*?\n\}\n\nDEPT_LEADS = \{.*?\n\}\n', re.DOTALL)
    
    new_content, count = pattern.subn('', content)
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Removed DEPT_ABBR and DEPT_LEADS from app.py")
    else:
        print("Not found in app.py")

fix_app()
