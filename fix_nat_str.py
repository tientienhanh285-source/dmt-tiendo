import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace else str(x) with else None in lambda x: x.strftime(...)
text = re.sub(r'(\.apply\(lambda x: x\.strftime\([^\)]+\)\s+if\s+pd\.notna\(x\)\s+and\s+isinstance\(x,\s+\(date,\s+datetime\)\)\s+else\s+)str\(x\)', r'\g<1>None', text)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
