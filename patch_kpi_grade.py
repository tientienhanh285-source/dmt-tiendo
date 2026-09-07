import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Monthly Late Task Progress Logic
old_m_late = '''                    if is_late and row.get('PhanLoaiTreHan') != "👤 Do chủ quan":
                        group_copy.at[idx, 'PhanTramHoanThanh'] = 100'''

new_m_late = '''                    if is_late and row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                        group_copy.at[idx, 'PhanTramHoanThanh'] = 100'''

# Fix 2: Monthly Auto Weight Logic
old_m_weight = '''                remaining_weight = max(0, 100 - explicit_weight_sum)
                auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0'''

new_m_weight = '''                remaining_weight = max(0, 100 - explicit_weight_sum)
                if (selected_year > 2026) or (selected_year == 2026 and selected_month >= 8):
                    auto_weight = 0
                else:
                    auto_weight = remaining_weight / unweighted_count if unweighted_count > 0 else 0'''

# Fix 3: Yearly Late Task Progress Logic
old_y_late = '''                            if is_late and row.get('PhanLoaiTreHan') != "👤 Do chủ quan":
                                m_df_copy.at[idx, 'PhanTramHoanThanh'] = 100'''

new_y_late = '''                            if is_late and row.get('PhanLoaiTreHan') == "🌍 Do khách quan":
                                m_df_copy.at[idx, 'PhanTramHoanThanh'] = 100'''

# Fix 4: Yearly Auto Weight Logic
old_y_weight = '''                        uw_count = len(m_df_copy[m_df_copy['TyTrongKPI'] <= 0])
                        auto_w = max(0, 100 - explicit_weight) / uw_count if uw_count > 0 else 0'''

new_y_weight = '''                        uw_count = len(m_df_copy[m_df_copy['TyTrongKPI'] <= 0])
                        if (selected_year_full > 2026) or (selected_year_full == 2026 and m >= 8):
                            auto_w = 0
                        else:
                            auto_w = max(0, 100 - explicit_weight) / uw_count if uw_count > 0 else 0'''

if old_m_late in content and old_m_weight in content and old_y_late in content and old_y_weight in content:
    content = content.replace(old_m_late, new_m_late)
    content = content.replace(old_m_weight, new_m_weight)
    content = content.replace(old_y_late, new_y_late)
    content = content.replace(old_y_weight, new_y_weight)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("Failed to find some chunks:")
    if old_m_late not in content: print("Missing old_m_late")
    if old_m_weight not in content: print("Missing old_m_weight")
    if old_y_late not in content: print("Missing old_y_late")
    if old_y_weight not in content: print("Missing old_y_weight")
