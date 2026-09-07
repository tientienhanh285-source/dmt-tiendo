import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """                        "ChuKyTheoDoi": task_cycle,
                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ"
                    }"""

replace1 = """                        "ChuKyTheoDoi": task_cycle,
                        "PhanLoaiTreHan": task_late_cause if is_late else "🟢 Không trễ hạn / Đúng tiến độ",
                        "TyTrongKPI": task_weight
                    }"""

if target1 in content:
    content = content.replace(target1, replace1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced target1 successfully')
else:
    print('target1 not found')
