import os, textwrap

P = r'C:\Users\Admin\Desktop\AG\Theodoitiendo\kpi_demo.html'

PART1 = textwrap.dedent("""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Demo He thong KPI - DMT Group</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
<p>This is a placeholder test file.</p>
</body>
</html>
""")

with open(P, 'w', encoding='utf-8') as f:
    f.write(PART1)
print('Written:', os.path.getsize(P), 'bytes')
