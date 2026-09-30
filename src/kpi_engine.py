import sqlite3
import pandas as pd
from datetime import datetime
import db_handler

def calculate_kpi(month, year):
    """
    Tính điểm KPI theo nguyên tắc 100 điểm trừ từ dữ liệu thật.
    - Điểm gốc: 100
    - Trễ hạn: -10 điểm/task
    """
    conn = db_handler.get_connection()
    cursor = conn.cursor()
    
    users = db_handler.get_all_users()
    results = []
    
    for u in users:
        base_score = 100
        penalty = 0
        bonus = 0
        
        # Lấy tất cả task của nhân viên này trong tháng
        # Trong thực tế sẽ filter theo tháng, ở bản demo lấy tất cả
        cursor.execute('''
            SELECT status FROM Tasks WHERE assignee_id = ?
        ''', (u['id'],))
        tasks = cursor.fetchall()
        
        for task in tasks:
            if task['status'] == 'Trễ hạn':
                penalty += 10
            elif task['status'] == 'Hoàn thành xuất sắc':
                bonus += 5
                
        final_score = base_score - penalty + bonus
        
        # Grading Logic
        if final_score > 100:
            grade = "A*"
        elif 92 <= final_score <= 100:
            grade = "A"
        elif 82 <= final_score <= 91:
            grade = "B"
        elif 72 <= final_score <= 81:
            grade = "C"
        else:
            grade = "D"
            
        results.append({
            "Mã NV": u['id'],
            "Họ tên": u['full_name'],
            "Phòng ban": u['department_name'],
            "Điểm Chuẩn": base_score,
            "Điểm Phạt": penalty,
            "Điểm Thưởng": bonus,
            "Tổng Điểm": final_score,
            "Xếp Loại": grade
        })
        
    conn.close()
    return pd.DataFrame(results)

def export_kpi_excel(df, filename="BaoCao_KPI.xlsx"):
    """
    Xuất dataframe ra file Excel.
    """
    df.to_excel(filename, index=False)
    return filename
