import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the UI Dropdowns
content = content.replace(
    'task_nguon = st.selectbox("Nguồn giao việc", ["Công việc được giao / định kì", \'Công việc trong "Giao ban"\'])',
    'task_nguon = st.selectbox("Nguồn giao việc", ["Công việc được giao / định kì", \'CV giao ban / VB đến\'])'
)

content = content.replace(
    'u_nguon_opts = ["Công việc được giao / định kì", \'Công việc trong "Giao ban"\']',
    'u_nguon_opts = ["Công việc được giao / định kì", \'CV giao ban / VB đến\']'
)

# 2. Update KPI Logic to support BOTH old data and new data
content = content.replace(
    "ke_hoach_tasks = group_copy[group_copy['NguonGiaoViec'] != 'Công việc trong \"Giao ban\"']",
    "ke_hoach_tasks = group_copy[~group_copy['NguonGiaoViec'].isin(['Công việc trong \"Giao ban\"', 'CV giao ban / VB đến'])]"
)

content = content.replace(
    "giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'] == 'Công việc trong \"Giao ban\"']",
    "giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'].isin(['Công việc trong \"Giao ban\"', 'CV giao ban / VB đến'])]"
)

content = content.replace(
    "ke_hoach_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] != 'Công việc trong \"Giao ban\"']",
    "ke_hoach_tasks_y = m_df_copy[~m_df_copy['NguonGiaoViec'].isin(['Công việc trong \"Giao ban\"', 'CV giao ban / VB đến'])]"
)

content = content.replace(
    "giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] == 'Công việc trong \"Giao ban\"']",
    "giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'].isin(['Công việc trong \"Giao ban\"', 'CV giao ban / VB đến'])]"
)

content = content.replace(
    "if row.get('NguonGiaoViec', '') == 'Công việc trong \"Giao ban\"':",
    "if row.get('NguonGiaoViec', '') in ['Công việc trong \"Giao ban\"', 'CV giao ban / VB đến']:"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
