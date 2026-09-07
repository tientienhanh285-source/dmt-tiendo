import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any hiding of header, MainMenu, footer
content = re.sub(r'\.stApp > header \{visibility: hidden !important;\}', '', content)
content = re.sub(r'\.stApp > header \{visibility: hidden;\}', '', content)
content = re.sub(r'#MainMenu \{visibility: hidden;\}', '', content)
content = re.sub(r'footer \{visibility: hidden;\}', '', content)
content = re.sub(r'\[data-testid="stHeader"\] \{visibility: hidden !important;\}', '', content)
content = re.sub(r'\[data-testid="stHeader"\] \{visibility: hidden;\}', '', content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
