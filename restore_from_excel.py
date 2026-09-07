import pandas as pd
from supabase import create_client
import sys

SUPABASE_URL = 'https://xlfnxyerpcebqxgmfngd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsZm54eWVycGNlYnF4Z21mbmdkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjYwNTAzNSwiZXhwIjoyMTAyMTgxMDM1fQ.qZsoZu8HaFpbvsG6siw76M5QXmX5bwipLV1qWeGG89s'
conn = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Reading Excel...")
df = pd.read_excel('data_dump.xlsx')

if 'ID' not in df.columns and 'Mã CV' in df.columns:
    df['ID'] = df['Mã CV']

print(f"Total rows in Excel: {len(df)}")
updated_count = 0

for index, row in df.iterrows():
    if pd.notna(row.get('ID')) and str(row['ID']).strip() != "":
        task_id = str(row['ID']).strip()
        update_data = {}
        
        if pd.notna(row.get('NgayBatDau')):
            try:
                update_data['NgayBatDau'] = pd.to_datetime(row['NgayBatDau']).strftime('%Y-%m-%d')
            except Exception as e:
                pass
                
        if pd.notna(row.get('Deadline')):
            try:
                update_data['Deadline'] = pd.to_datetime(row['Deadline']).strftime('%Y-%m-%d')
            except Exception as e:
                pass
                
        if update_data:
            try:
                conn.table("tasks").update(update_data).eq("ID", task_id).execute()
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} records...")
            except Exception as e:
                print(f"Failed to update {task_id}: {e}")

print(f"Done! Successfully updated {updated_count} records in Supabase.")
