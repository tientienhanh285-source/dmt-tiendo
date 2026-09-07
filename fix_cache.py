import os

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = '''def safe_gsheets_read(conn, worksheet, ttl=0, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    kwargs = {"worksheet": worksheet, "ttl": ttl}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    try:
        df = conn.read(**kwargs)
        return df if df is not None else fallback_df
    except Exception as e:
        import streamlit as st
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        return fallback_df'''

new_func = '''def safe_gsheets_read(conn, worksheet, ttl=0, fallback_df=None):
    if fallback_df is None:
        import pandas as pd
        fallback_df = pd.DataFrame()
    kwargs = {"worksheet": worksheet, "ttl": ttl}
    
    import streamlit as st
    url = st.session_state.get("gsheet_url", "").strip()
    if url:
        kwargs["spreadsheet"] = url
        
    cache_key = f"cached_df_{worksheet}"
    
    try:
        df = conn.read(**kwargs)
        if df is not None:
            st.session_state[cache_key] = df
            return df
        else:
            return st.session_state.get(cache_key, fallback_df)
    except Exception as e:
        import streamlit as st
        if "Spreadsheet must be specified" in str(e) or "Spreadsheet must be provided" in str(e):
            st.session_state["show_gsheet_input"] = True
        else:
            # We don't want to show toast on every network glitch if it's running in background, but keeping silent is fine too.
            pass
        return st.session_state.get(cache_key, fallback_df)'''

if old_func in text:
    text = text.replace(old_func, new_func)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed safe_gsheets_read')
else:
    print('Could not find old_func')
