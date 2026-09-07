import os
import json
import pandas as pd
import google.generativeai as genai
import re



# Setup Gemini
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    # Try reading from secrets.toml if exists
    try:
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        api_key = secrets.get("gemini", {}).get("api_key", "")
    except:
        pass

if not api_key:
    print("NO API KEY")
    exit()

genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel('gemini-1.5-flash')

p_name = "Nguyễn Thị Hạnh Tiên"

# Load JD
try:
    jd_df = pd.read_json("jd_db.json")
except:
    jd_df = pd.DataFrame()

p_jd = jd_df[jd_df['TenNhanVien'].str.lower() == p_name.lower()]
jd_source = p_jd.iloc[0].get('NoiDungJD', '') if not p_jd.empty else ''

# Load tasks
display_df = pd.read_excel("data_dump.xlsx") if os.path.exists("data_dump.xlsx") else pd.DataFrame()
if display_df.empty:
    print("NO DATA DUMP")
    exit()

selected_month = 8
selected_year = 2026

ai_tasks = display_df[
    (display_df['NguoiChuTri'].astype(str).str.lower() == p_name.lower()) & 
    (display_df['Deadline'].apply(lambda x: x.month == selected_month and x.year == selected_year if pd.notna(x) and hasattr(x, 'month') else False))
]

tasks_list = "\n".join([f"- {r['TenCongViec']}" for _, r in ai_tasks.iterrows()])

print(f"TASKS TO EVALUATE ({len(ai_tasks)}):\n{tasks_list}\n")

prompt = f"""
Đóng vai một Giám đốc nhân sự cực kỳ tinh tế. 
Dưới đây là Bản Mô tả công việc (JD) của nhân viên {p_name}:

[BẢN MÔ TẢ CÔNG VIỆC]
{jd_source}
[KẾT THÚC JD]

Và đây là danh sách công việc họ thực hiện trong tháng:
{tasks_list}

NHIỆM VỤ CỦA BẠN:
1. Đối chiếu TỪNG công việc xem nó có KHỚP với chuyên môn quy định trong JD không. 
(Lưu ý: Tên công việc thực tế có thể chi tiết và từ ngữ khác biệt so với JD văn xuôi. Hãy dùng tư duy suy luận về bản chất và mục đích để phán đoán).
2. Nếu khớp, giải thích vì nó phục vụ cho mục nào trong JD. Nếu ngoài JD, ghi rõ là công việc phát sinh.
3. Format kết quả đầu ra thành đúng định dạng chuỗi JSON thô như sau (chỉ trả về JSON, không chứa dấu tick markdown ```json):
{{
    "chi_tiet": [
        {{
            "ten_cong_viec": "<Tên công việc y nguyên trong danh sách>",
            "phan_loai": "<Chỉ điền 'Khớp JD' hoặc 'Ngoài JD'>",
            "nhan_xet": "<Phân tích ngắn gọn 1-2 câu>"
        }}
    ]
}}
"""

response = model.generate_content(
    prompt, 
    generation_config={"temperature": 0.0},
    request_options={"retry": None, "timeout": 30.0}
)
raw_text = response.text
print("RAW TEXT:")
print(raw_text)

json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
if json_match:
    ai_result = json.loads(json_match.group(0))
    def is_out_of_jd(item):
        pl = item.get("phan_loai", "").lower()
        is_match = "khớp" in pl and "không" not in pl and "ngoài" not in pl
        return not is_match
        
    out_of_jd_tasks = [t for t in ai_result.get("chi_tiet", []) if is_out_of_jd(t)]
    print("\nOUT OF JD TASKS DETECTED:", out_of_jd_tasks)
