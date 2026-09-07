import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix CSS to only target the main app header, not the calendar header in portals
content = content.replace('[data-testid="stHeader"] {visibility: hidden !important;}', '.stApp > header {visibility: hidden !important;}')
content = content.replace('[data-testid="stHeader"] {visibility: hidden;}', '.stApp > header {visibility: hidden;}')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
