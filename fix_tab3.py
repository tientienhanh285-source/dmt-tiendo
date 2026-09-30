import re

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix t3_dept to be a selectbox instead of forcing session state
        old_t3 = "t3_dept = st.session_state.get('manager_dept', get_departments_for_company(selected_company, config)[0])"
        new_t3 = """
            # Use a selectbox so HR or Manager can change the department
            default_t3 = get_departments_for_company(selected_company, config)[0]
            if st.session_state.get('manager_dept') in get_departments_for_company(selected_company, config):
                default_t3 = st.session_state.manager_dept
            t3_dept = st.selectbox("Phòng ban", get_departments_for_company(selected_company, config), index=get_departments_for_company(selected_company, config).index(default_t3) if default_t3 in get_departments_for_company(selected_company, config) else 0)
        """
        
        content = content.replace(old_t3, new_t3)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Fixed tab 3!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
