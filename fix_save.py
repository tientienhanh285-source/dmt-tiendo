import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix safe_gsheets_update to log errors
pattern_safe_update = r'    except Exception as e:\n        if "Spreadsheet must be specified"'
replacement_safe_update = r'    except Exception as e:\n        st.error(f"Lỗi cập nhật GSheets: {e}")\n        if "Spreadsheet must be specified"'
content = content.replace('    except Exception as e:\n        if "Spreadsheet must be specified"', '    except Exception as e:\n        import streamlit as st\n        st.error(f"Lỗi cập nhật GSheets: {e}")\n        if "Spreadsheet must be specified"')

# 2. Fix save_db to return the result of safe_gsheets_update and fillna
def fix_save_db(match):
    return match.group(0).replace(
        'safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)\n        return True',
        'df_save = df_save.fillna("")\n        return safe_gsheets_update(conn, worksheet="Sheet1", data=df_save)'
    )
content = re.sub(r'def save_db\(df\):.*?return True', fix_save_db, content, flags=re.DOTALL)

# 3. Fix save_incoming_docs_db to return the result and fillna
def fix_save_docs(match):
    return match.group(0).replace(
        'safe_gsheets_update(conn, worksheet="VB_DEN", data=df_save)\n        return True',
        'df_save = df_save.fillna("")\n        return safe_gsheets_update(conn, worksheet="VB_DEN", data=df_save)'
    )
content = re.sub(r'def save_incoming_docs_db\(df\):.*?return True', fix_save_docs, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed save_db and safe_gsheets_update')
