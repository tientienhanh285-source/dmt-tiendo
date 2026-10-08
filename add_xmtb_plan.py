import json
import uuid

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

targets = [
    ("Điều động xe", "Quý IV/2026"),
    ("Cung cấp vật tư cho DA", "Quý IV/2026"),
    ("Đề xuất sửa xe", "Quý IV/2026")
]

for name, dl in targets:
    t_id = "T" + str(uuid.uuid4())[:8].upper()
    data.append({
        "target_id": t_id,
        "project_name": "Công tác Xe máy & Thiết bị",
        "department": "XN XMTB",
        "company": "CÔNG TY CP XÂY DỰNG CÔNG TRÌNH GIAO THÔNG ĐN-MT",
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

print("Added XN XMTB targets")
