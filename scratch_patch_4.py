with open(r"views\5_Danh_Gia_KPI.py", "r", encoding="utf-8") as f:
    content = f.read()

old_code = """        if not display_df.empty:
            df_quy = display_df.copy()
            df_quy['Thang_Deadline'] = df_quy['Deadline'].dt.month
            df_quy['Nam_Deadline'] = df_quy['Deadline'].dt.year"""

new_code = """        if not display_df.empty:
            df_quy = display_df.copy()
            df_quy['Deadline'] = pd.to_datetime(df_quy['Deadline'], errors='coerce')
            df_quy['Thang_Deadline'] = df_quy['Deadline'].dt.month
            df_quy['Nam_Deadline'] = df_quy['Deadline'].dt.year"""

content = content.replace(old_code, new_code)

with open(r"views\5_Danh_Gia_KPI.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fix datetime error complete")
