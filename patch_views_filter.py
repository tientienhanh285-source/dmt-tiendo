import glob

filter_logic = """
# Apply Role-based Filtering globally for the view
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        display_df = display_df[display_df['NguoiChuTri'] == st.session_state.personal_user]
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        display_df = display_df[display_df['PhongBan'] == st.session_state.manager_dept]

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()
"""

for filepath in glob.glob("views/*.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We will replace "if 'df' not in locals():" to inject our filter right before it
    if "if 'df' not in locals():" in content:
        # replace the first occurrence
        parts = content.split("if 'df' not in locals():", 1)
        new_content = parts[0] + filter_logic + "\nif 'df_old_dummy' not in locals():" + parts[1]
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Injected role-based dataframe filter into all views")
