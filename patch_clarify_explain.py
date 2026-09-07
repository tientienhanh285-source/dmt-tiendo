import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace in Create Form
content = content.replace(
    'task_explain = st.text_area("Nội dung nguyên nhân khách quan & Phương án xử lý (Bắt buộc)", placeholder="Mô tả chi tiết khó khăn, nguyên nhân khách quan và phương án xử lý...", key="new_task_explain")',
    'task_explain = st.text_area("📝 Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý (Bắt buộc)", placeholder="Ví dụ: Bị vướng pháp lý do đối tác chậm cung cấp hồ sơ. Đề xuất xin dời sang tuần sau...", height=120, key="new_task_explain")'
)

# Replace in Update Form
content = re.sub(
    r'u_explain = st\.text_area\("Nội dung nguyên nhân khách quan & Phương án xử lý \(Bắt buộc\)", value=task_data\.get\(\'GiaiTrinhDeXuat\', \'\'\), key=f"u_explain_txt_\{task_data\[\'ID\'\]\}"\)',
    'u_explain = st.text_area("📝 Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý (Bắt buộc)", value=task_data.get(\'GiaiTrinhDeXuat\', \'\'), placeholder="Ví dụ: Bị vướng pháp lý do đối tác chậm cung cấp hồ sơ. Đề xuất xin dời sang tuần sau...", height=120, key=f"u_explain_txt_{task_data[\'ID\']}")',
    content
)

# Replace validation error messages
content = content.replace(
    'st.error("⚠️ Bắt buộc nhập chi tiết \'Nội dung nguyên nhân khách quan & Phương án xử lý\' (tối thiểu 5 ký tự)!")',
    'st.error("⚠️ Bắt buộc nhập \'Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý\' (tối thiểu 5 ký tự)!")'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
