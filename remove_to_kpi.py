import codecs
import json
import re

def remove_to_kpi():
    # 1. Update app.py
    app_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/app.py'
    with codecs.open(app_file, 'r', 'utf-8') as f:
        app_content = f.read()

    app_content = re.sub(r'\s*"Tổ KPI":\s*"Tổ KPI",?', '', app_content)
    app_content = re.sub(r'\s*"Tổ KPI":\s*\[\],?', '', app_content)

    with codecs.open(app_file, 'w', 'utf-8') as f:
        f.write(app_content)

    # 2. Update core_logic.py
    core_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/core_logic.py'
    with codecs.open(core_file, 'r', 'utf-8') as f:
        core_content = f.read()

    core_content = re.sub(r'\s*"Tổ KPI":\s*\[\],?', '', core_content)
    core_content = re.sub(r'\s*"Tổ KPI":\s*"Tổ KPI",?', '', core_content)

    with codecs.open(core_file, 'w', 'utf-8') as f:
        f.write(core_content)

    # 3. Update CONFIG_PROJECTS.json
    config_file = 'c:/Users/Admin/Desktop/AG/Theodoitiendo/OUTPUT/CONFIG_PROJECTS.json'
    try:
        with codecs.open(config_file, 'r', 'utf-8') as f:
            config = json.load(f)
            
        if 'departments' in config and 'Tổ KPI' in config['departments']:
            config['departments'].remove('Tổ KPI')
            
        if 'personnel_by_department' in config and 'Tổ KPI' in config['personnel_by_department']:
            del config['personnel_by_department']['Tổ KPI']

        with codecs.open(config_file, 'w', 'utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            
        print("Tổ KPI removed successfully.")
    except Exception as e:
        print(f"Error updating config: {e}")

remove_to_kpi()
