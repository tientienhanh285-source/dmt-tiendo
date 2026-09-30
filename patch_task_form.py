import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Function to load project targets
load_target_func = """
def load_project_targets():
    import json
    import os
    target_file = 'project_targets.json'
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []
"""

# Insert function if not exists
if "def load_project_targets" not in content:
    content = content.replace("def read_db():", load_target_func + "\ndef read_db():")


old_block = """            # 2. Project selection (Categorized dropdown or custom)
            is_marina_co = "CTY CP DMT - MARINA" in entry_company or "Du thuyền Happy Yacht" in entry_company
            if False:
                proj_options_with_custom = ["➕ Tạo / Nhập Dự án mới..."]
            else:
                db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
                merged_projs = get_filtered_projects(entry_company, config, db_projs)
                proj_options_with_custom = merged_projs + ["✍️ Tự nhập Dự án / Hạng mục khác..."]
                
            default_proj_opt = st.selectbox("Dự án / Hạng mục", proj_options_with_custom)
            
            if is_marina_co or default_proj_opt in ["✍️ Tự nhập Dự án / Hạng mục khác...", "➕ Tạo / Nhập Dự án mới..."]:
                project_name = st.text_input("Nhập tên Dự án / Hạng mục mới", value="")
            else:
                project_name = clean_proj_name(default_proj_opt)
            
            # 3. Task details"""

new_block = """            # 2. Project selection (Categorized dropdown or custom)
            project_targets = load_project_targets()
            khdt_projects = []
            for t in project_targets:
                if t.get("department") == task_dept and t.get("project_name") not in khdt_projects:
                    khdt_projects.append(t.get("project_name"))
                    
            db_projs = list(display_df["TenDuAn"].dropna().unique()) if not display_df.empty else []
            merged_projs = get_filtered_projects(entry_company, config, db_projs)
            
            for p in khdt_projects:
                if p not in merged_projs:
                    merged_projs.append(p)
                    
            proj_options_with_custom = merged_projs + ["✍️ Tự nhập Dự án / Hạng mục khác..."]
                
            default_proj_opt = st.selectbox("Dự án / Hạng mục", proj_options_with_custom)
            
            if default_proj_opt in ["✍️ Tự nhập Dự án / Hạng mục khác...", "➕ Tạo / Nhập Dự án mới..."]:
                project_name = st.text_input("Nhập tên Dự án / Hạng mục mới", value="")
            else:
                project_name = clean_proj_name(default_proj_opt)
                
            # 2.1 Target (Chỉ tiêu) selection
            associated_targets = [t["target_name"] for t in project_targets if t.get("project_name") == project_name and t.get("department") == task_dept]
            
            selected_target = ""
            if associated_targets:
                st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #d97706; margin-bottom: 5px; margin-top: 15px;'>🎯 Thuộc Chỉ tiêu (Kế hoạch năm)</p>", unsafe_allow_html=True)
                target_options = associated_targets + ["Tự do / Không thuộc Chỉ tiêu nào"]
                selected_target = st.selectbox("Chọn Chỉ tiêu", target_options, label_visibility="collapsed")
            else:
                selected_target = "Tự do / Không thuộc Chỉ tiêu nào"
            
            # 3. Task details"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Replaced old_block with new_block successfully.")
else:
    print("Could not find old_block in app.py!")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")
