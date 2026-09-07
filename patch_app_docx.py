import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

t = """                    tasks = [{'TenCV': 'Công việc mẫu', 'TyTrong': 100, 'Diem': 100}]
                    word_data = kpi_reports.generate_individual_docx(emp_to_export, selected_month, selected_year, 100, tasks, [])"""

r = """                    # Collect real tasks and penalties
                    emp_tasks = []
                    kpi_score = 100
                    if personnel_kpi:
                        for p in personnel_kpi:
                            if p['Nhân viên'] == emp_to_export:
                                kpi_score = p['Điểm công việc']
                                break
                    
                    e_kpi_df = kpi_df[kpi_df['NguoiChuTri'] == emp_to_export]
                    # Calc weights again if needed, or just display raw tasks
                    explicit_weight_sum = e_kpi_df[e_kpi_df['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
                    unweighted_count = len(e_kpi_df[e_kpi_df['TyTrongKPI'] <= 0])
                    remaining_weight = max(0, 100 - explicit_weight_sum)
                    auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
                    
                    for idx, row in e_kpi_df.iterrows():
                        w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                        pt = row.get('PhanTramHoanThanh', 0)
                        if pd.isna(pt): pt = 0
                        
                        diem_tru = w - (pt / 100.0 * w)
                        emp_tasks.append({
                            'TenCV': row['TenCongViec'],
                            'TgianYC': str(row['Deadline']),
                            'KetQua': f"{pt}% (Tỷ trọng: {w:.1f}%)",
                            'DiemTru': round(diem_tru, 1)
                        })
                        
                    e_adj_df = adj_df[adj_df['TenNhanVien'] == emp_to_export]
                    penalties = e_adj_df.to_dict('records')
                    
                    word_data = kpi_reports.generate_individual_docx(emp_to_export, selected_month, selected_year, kpi_score, emp_tasks, penalties)"""

if t in content:
    content = content.replace(t, r)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched app.py OK")
else:
    print("Failed to patch app.py")
