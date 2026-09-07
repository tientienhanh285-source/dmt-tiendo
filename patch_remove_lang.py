import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the line that sets the lang to 'vi'
content = re.sub(r"window\.parent\.document\.documentElement\.lang\s*=\s*'vi';", "", content)
content = re.sub(r'window\.parent\.document\.documentElement\.lang\s*=\s*"vi";', "", content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
