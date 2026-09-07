import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace all df.fillna("") or df_save.fillna("") to avoid empty strings passing to Supabase dates
# Wait, replacing all fillna("") might break string columns that NEED to be "".
# It's better to replace NaN with None for everything, or let Supabase insert None natively!
# But pandas `.where(pd.notnull(df), None)` is best.
# Let's replace `fillna("")` with `where(pd.notnull(df_save), None)`
text = re.sub(r'df_save\s*=\s*df_save\.fillna\([\'\"].*?[\'\"]\)', 'df_save = df_save.where(pd.notnull(df_save), None)', text)

# We also need to fix `fillna("")` in `safe_gsheets_update` if there's any.
text = re.sub(r'df_copy\.fillna\([\'\"].*?[\'\"]\)', 'df_copy.where(pd.notnull(df_copy), None)', text)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
