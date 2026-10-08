import json

mapping = {
    "Ban Chuẩn bị Đầu tư": "CBĐT",
    "Ban Hành chính Nhân sự": "HCNS",
    "Ban Tài chính Kế toán": "TCKT",
    "Ban Đền bù Giải tỏa": "ĐBGT",
    "Ban Kế hoạch Đầu tư": "KHĐT"
}

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for t in data:
    if t.get("department") in mapping:
        t["department"] = mapping[t["department"]]

with open('project_targets.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Reverted department names in project_targets.json")
