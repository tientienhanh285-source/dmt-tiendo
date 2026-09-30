import sqlite3
import pandas as pd

try:
    db = sqlite3.connect("kpi_system.db")
    df_users = pd.read_sql_query("SELECT * FROM Users", db)
    df_users.to_csv("scratch_users.csv", index=False, encoding='utf-8')
    print("Exported users")
    db.close()
except Exception as e:
    print(e)
