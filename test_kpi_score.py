import pandas as pd
from datetime import datetime, date

# Simulating the new logic
def test_kpi_calc():
    try:
        from core_logic import read_db
        df = read_db()
    except Exception as e:
        print(f"Error reading DB: {e}")
        return

    # Filter some random user
    if df.empty:
        print("DB is empty")
        return
        
    users = [u for u in df['NguoiChuTri'].unique() if pd.notnull(u) and str(u).strip() != '']
    if len(users) == 0:
        print("No users found")
        return
        
    # We test for up to 3 users
    for person in list(users)[:3]:
        print(f"\n--- Testing User: {person} ---")
        group = df[df['NguoiChuTri'] == person]
        total_tasks = len(group)
        print(f"Total tasks: {total_tasks}")
        
        group_copy = group.copy()
        group_copy['TyTrongKPI'] = pd.to_numeric(group_copy.get('TyTrongKPI', pd.Series(0, index=group_copy.index)), errors='coerce').fillna(0)
        
        today = date.today()
        for idx, row in group_copy.iterrows():
            is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
            is_late = False
            dl = row['Deadline']
            if isinstance(dl, str):
                try: dl = datetime.strptime(dl, "%Y-%m-%d").date()
                except: pass
            if isinstance(dl, datetime): dl = dl.date()
            if isinstance(dl, date): is_late = (dl < today) and not is_comp
            
            if is_late and row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                group_copy.at[idx, 'PhanTramHoanThanh'] = 100
                
        explicit_weight_sum = group_copy[group_copy['TyTrongKPI'] > 0]['TyTrongKPI'].sum()
        unweighted_count = len(group_copy[group_copy['TyTrongKPI'] <= 0])
        remaining_weight = max(0, 100 - explicit_weight_sum)
        auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0
        print(f"Explicit weight sum: {explicit_weight_sum}, Unweighted count: {unweighted_count}, Auto weight: {auto_weight}")
        
        def calc_score_for_group(grp):
            if grp.empty: return 0
            t_score = 0
            total_w = 0
            is_local = True
            for idx, row in grp.iterrows():
                w = row['TyTrongKPI'] if row['TyTrongKPI'] > 0 else auto_weight
                
                if is_local:
                    muc_dat = str(row.get('MucDoGhiNhan', 'Mức 3'))
                    if 'Mức 4' in muc_dat: p = 125
                    elif 'Mức 3' in muc_dat: p = 100
                    elif 'Mức 2' in muc_dat: p = 75
                    elif 'Mức 1' in muc_dat: p = 50
                    elif 'Mức 0' in muc_dat: p = 0
                    elif 'Mức -1' in muc_dat: p = -50
                    elif 'Mức -2' in muc_dat: p = -75
                    elif 'Mức -3' in muc_dat: p = -100
                    else:
                        is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                        p = 100 if is_comp else 0
                else:
                    is_comp = (str(row.get('TrangThai')).strip() == 'Hoàn thành')
                    p = 100 if is_comp else 0
                    
                    if not is_comp and "khách quan" in str(row.get('PhanLoaiTreHan')).lower():
                        cc = row.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                        if cc == "Miễn trừ (Loại bỏ KPI)":
                            w = 0
                            p = 0
                        elif cc == "50%": p = 50
                        elif cc == "80%": p = 80
                        elif cc == "90%": p = 90
                        else: p = 0

                t_score += (p / 100.0) * w
                total_w += w
                print(f"Task: {row['TenCongViec']} - Weight: {w}% - P-Score: {p} - Added to total: {(p / 100.0) * w}")
                
            if total_w > 0:
                return (t_score / total_w) * 100
            return 0

        task_score = calc_score_for_group(group_copy)
        print(f"Final calculated task score: {task_score}")

if __name__ == "__main__":
    test_kpi_calc()
