import json

mapping = {
    "CBĐT": "Ban Chuẩn bị Đầu tư",
    "HCNS": "Ban Hành chính Nhân sự",
    "TCKT": "Ban Tài chính Kế toán",
    "ĐBGT": "Ban Đền bù Giải tỏa"
}

with open('project_targets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for t in data:
    if t.get("department") in mapping:
        t["department"] = mapping[t["department"]]

with open('project_targets.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated department names in project_targets.json")
