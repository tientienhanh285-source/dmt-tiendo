import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Monthly KPI KeyError
old_monthly = '''                # Calculate score dynamically based on NguonGiaoViec (70/30 rule)
                ke_hoach_tasks = group_copy[group_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']'''

new_monthly = '''                # Calculate score dynamically based on NguonGiaoViec (70/30 rule)
                if 'NguonGiaoViec' not in group_copy.columns:
                    group_copy['NguonGiaoViec'] = 'Công việc được giao / định kì'
                ke_hoach_tasks = group_copy[group_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                giao_ban_tasks = group_copy[group_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']'''

content = content.replace(old_monthly, new_monthly)

# Fix Yearly KPI KeyError
old_yearly = '''                        ke_hoach_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                        giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']'''

new_yearly = '''                        if 'NguonGiaoViec' not in m_df_copy.columns:
                            m_df_copy['NguonGiaoViec'] = 'Công việc được giao / định kì'
                        ke_hoach_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] != 'Công việc trong "Giao ban"']
                        giao_ban_tasks_y = m_df_copy[m_df_copy['NguonGiaoViec'] == 'Công việc trong "Giao ban"']'''

content = content.replace(old_yearly, new_yearly)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
