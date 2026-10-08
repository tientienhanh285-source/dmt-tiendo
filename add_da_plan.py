import json
import uuid

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

targets = [
    ("Đề xuất Chủ đầu tư triển khai sớm mời thầu gói thầu MEP, PCCC", "Cuối tháng 10/2026"),
    ("Đề xuất triển khai các gói thầu hoàn thiện: nhôm kính, sơn bả, trần thạch cao", "Tháng 12/2026"),
    ("Tiếp tục làm việc với Notion thực hiện các nội dung theo hợp đồng", "Quý IV/2026"),
    ("Đề xuất, báo cáo xin ý kiến bù giá hạng mục hoàn thiện của nhà thầu Vinaconex 25", "Quý IV/2026"),
    ("Vinaconex 25 - Đổ bê tông dầm sàn tầng 16", "Cuối tháng 12/2026"),
    ("Vinaconex 25 - Defect toàn bộ tầng hầm", "Quý IV/2026"),
    ("Vinaconex 25 - Thi công các kết cấu phụ cầu thang bộ đến tầng 15", "Quý IV/2026"),
    ("Vinaconex 25 - Xây tường đến tầng 12", "Quý IV/2026"),
    ("Vinaconex 25 - Trát tường đến tầng 9", "Quý IV/2026"),
    ("Vinaconex 25 - Chống thấm đến tầng 6", "Quý IV/2026"),
    ("Nhà thầu Quang Anh: Hoàn thiện hồ sơ quyết toán", "Quý IV/2026"),
    ("Nhà thầu Bách Khoa: Hoàn thiện hồ sơ quyết toán", "Quý IV/2026"),
    ("Nhà thầu Toàn Chính: Thực hiện hợp đồng theo tiến độ của nhà thầu Vinaconex 25", "Quý IV/2026"),
]

for name, dl in targets:
    t_id = "T" + str(uuid.uuid4())[:8].upper()
    data.append({
        "target_id": t_id,
        "project_name": "Khách sạn DMT-Group",
        "department": "DA",
        "target_name": name,
        "deadline": dl,
        "status": "Chưa bắt đầu",
        "approved": False,
        "progress": 0,
        "budget_2026": 0,
        "disbursed_value": 0
    })

with open('project_targets.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Added DA targets")
