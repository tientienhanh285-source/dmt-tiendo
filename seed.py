import sqlite3
conn = sqlite3.connect('kpi_system.db')
cursor = conn.cursor()
cursor.execute("INSERT OR IGNORE INTO MasterPlans (id, name, year, department_id) VALUES (1, 'Kế hoạch HCNS 2026', 2026, 1)")
cursor.execute("INSERT OR IGNORE INTO Indicators (id, name, master_plan_id) VALUES (1, 'Tuyển 50 Kỹ sư', 1)")
cursor.execute("INSERT OR IGNORE INTO Indicators (id, name, master_plan_id) VALUES (2, 'Đào tạo nội bộ', 1)")
conn.commit()
conn.close()
print('Seed data done')
