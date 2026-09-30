import re

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Add st.cache_data.clear() in save_bsc_config
        content = content.replace('success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)\n        return success', 'success = safe_gsheets_update(conn, worksheet="CONFIG", data=df_save)\n        import streamlit as st\n        st.cache_data.clear()\n        return success')
        
        # 2. Fix the display logic to use the selected values, not manager_dept
        content = content.replace("year_key_sel = f\"{st.session_state.get('manager_dept', dept)}_{target_year}\"", "year_key_sel = f\"{dept}_{target_year}\"")
        
        content = content.replace("month_key_sel = f\"{st.session_state.get('manager_dept', m_dept)}_{m_year}_{m_month}\"", "month_key_sel = f\"{m_dept}_{m_year}_{m_month}\"")
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Fixed display logic!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
