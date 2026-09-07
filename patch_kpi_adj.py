import os

app_file = 'app.py'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modify add_kpi_adjustment to prevent duplicates
old_add = '''def add_kpi_adjustment(ten, thang, nam, loai, diem, lydo):
    import pandas as pd
    df = read_kpi_adjustments()
    new_id = 1 if df.empty else int(pd.to_numeric(df['ID'], errors='coerce').max(skipna=True) + 1 if not df['ID'].empty else 1)'''

new_add = '''def add_kpi_adjustment(ten, thang, nam, loai, diem, lydo):
    import pandas as pd
    df = read_kpi_adjustments()
    if not df.empty:
        dup = df[(df['TenNhanVien'] == ten) & (df['Thang'] == thang) & (df['Nam'] == nam) & (df['LoaiHanhVi'] == loai) & (df['DiemDieuChinh'] == diem) & (df['LyDo'] == lydo)]
        if not dup.empty:
            return True, ""
    new_id = 1 if df.empty else int(pd.to_numeric(df['ID'], errors='coerce').max(skipna=True) + 1 if not df['ID'].empty else 1)'''

content = content.replace(old_add, new_add)

# 2. Add edit_kpi_adjustment and delete_kpi_adjustment
add_funcs = '''
def edit_kpi_adjustment(adj_id, ten, thang, nam, loai, diem, lydo):
    import pandas as pd
    df = read_kpi_adjustments()
    if df.empty: return False, "Dữ liệu trống"
    idx = df[df['ID'] == adj_id].index
    if len(idx) == 0: return False, "Không tìm thấy ID"
    df.loc[idx[0], 'TenNhanVien'] = ten
    df.loc[idx[0], 'Thang'] = thang
    df.loc[idx[0], 'Nam'] = nam
    df.loc[idx[0], 'LoaiHanhVi'] = loai
    df.loc[idx[0], 'DiemDieuChinh'] = diem
    df.loc[idx[0], 'LyDo'] = lydo
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            success = safe_gsheets_update(conn, worksheet="KPI_ADJUSTMENTS", data=df)
            if success:
                import streamlit as st
                st.cache_data.clear()
                return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Lỗi kết nối"

def delete_kpi_adjustment(adj_id):
    import pandas as pd
    df = read_kpi_adjustments()
    if df.empty: return False, "Dữ liệu trống"
    df = df[df['ID'] != adj_id]
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            success = safe_gsheets_update(conn, worksheet="KPI_ADJUSTMENTS", data=df)
            if success:
                import streamlit as st
                st.cache_data.clear()
                return True, ""
        except Exception as e:
            return False, str(e)
    return False, "Lỗi kết nối"
'''

if 'def edit_kpi_adjustment' not in content:
    old_func_end = '''    return False, "Không kết nối được Google Sheets"'''
    content = content.replace(old_func_end, old_func_end + '\\n' + add_funcs, 1)

# 3. Add UI in kpi_tab3
old_ui = '''            st.markdown("##### Lịch sử Thưởng / Phạt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                st.dataframe(hist_df.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có lịch sử điều chỉnh.")'''

new_ui = '''            st.markdown("##### Lịch sử Thưởng / Phạt")
            hist_df = read_kpi_adjustments()
            if not hist_df.empty:
                st.dataframe(hist_df.sort_values(by="ID", ascending=False), use_container_width=True, hide_index=True)
                
                st.markdown("##### ✏️ Sửa / Xóa Lịch sử Điều chỉnh")
                adj_opts = hist_df.apply(lambda row: f"[{row['ID']}] {row['TenNhanVien']} - T{row['Thang']}/{row['Nam']}: {row['DiemDieuChinh']} điểm ({row['LyDo']})", axis=1).tolist()
                sel_adj_str = st.selectbox("Chọn bản ghi để thao tác:", ["-- Chọn bản ghi --"] + adj_opts)
                if sel_adj_str != "-- Chọn bản ghi --":
                    sel_adj_id = int(sel_adj_str.split("]")[0].replace("[", ""))
                    adj_row = hist_df[hist_df['ID'] == sel_adj_id].iloc[0]
                    
                    st.markdown(f"**Chỉnh sửa bản ghi ID: {sel_adj_id}**")
                    u_adj_ten = st.selectbox("Tên nhân viên", all_p_list, index=all_p_list.index(adj_row['TenNhanVien']) if adj_row['TenNhanVien'] in all_p_list else 0, key="u_adj_ten")
                    u_adj_thang = st.selectbox("Tháng", list(range(1, 13)), index=int(adj_row['Thang'])-1, key="u_adj_thang")
                    u_adj_nam = st.selectbox("Năm", [today.year - 1, today.year, today.year + 1], index=[today.year - 1, today.year, today.year + 1].index(int(adj_row['Nam'])), key="u_adj_nam")
                    u_adj_loai = st.radio("Loại hành vi", ["⭐ Thưởng điểm", "🛑 Phạt điểm"], index=0 if adj_row['LoaiHanhVi'] == "⭐ Thưởng điểm" else 1, key="u_adj_loai")
                    u_adj_diem = st.number_input("Điểm điều chỉnh", value=int(abs(adj_row['DiemDieuChinh'])), key="u_adj_diem")
                    u_adj_lydo = st.text_input("Lý do", value=adj_row['LyDo'], key="u_adj_lydo")
                    
                    col_sa, col_sd = st.columns(2)
                    with col_sa:
                        if st.button("💾 Lưu thay đổi", type="primary", key="btn_save_adj"):
                            actual_val = u_adj_diem if u_adj_loai == "⭐ Thưởng điểm" else -u_adj_diem
                            if edit_kpi_adjustment(sel_adj_id, u_adj_ten, u_adj_thang, u_adj_nam, u_adj_loai, actual_val, u_adj_lydo):
                                st.success("Cập nhật thành công!")
                                st.rerun()
                    with col_sd:
                        if st.button("🗑️ Xóa bản ghi", type="secondary", key="btn_del_adj"):
                            if delete_kpi_adjustment(sel_adj_id):
                                st.success("Xóa thành công!")
                                st.rerun()
            else:
                st.info("Chưa có lịch sử điều chỉnh.")'''

content = content.replace(old_ui, new_ui)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)
