from pypdf import PdfReader
import os

pdf_dir = r'C:/Users/Admin/.gemini/antigravity-ide/brain/486cd980-e5c0-4bf4-a71f-bcaf77e9bce1/.user_uploaded/'
text = ''
try:
    for f in os.listdir(pdf_dir):
        if f.endswith('.pdf'):
            reader = PdfReader(os.path.join(pdf_dir, f))
            for p in reader.pages:
                text += p.extract_text() + '\n'
    
    with open('pdf_text_dump.txt', 'w', encoding='utf-8') as out:
        out.write(text)
    print("Done extracting PDFs.")
except Exception as e:
    print(f"Error: {e}")
