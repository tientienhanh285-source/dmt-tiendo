import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_ui = '''                        if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            u_explain = st.text_area("Nội dung nguyên nhân khách quan & Phương án xử lý (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                        else:
                            u_explain = ""
                    else:'''

new_ui = '''                        if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                            u_explain = st.text_area("Nội dung nguyên nhân khách quan & Phương án xử lý (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), key=f"u_explain_txt_{task_data['ID']}")
                            
                            if st.session_state.is_admin_authenticated:
                                current_chamchuoc = task_data.get('MucDoChamChuoc', '0% (Không ghi nhận)')
                                chamchuoc_opts = ["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"]
                                idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                                u_chamchuoc = st.selectbox("Mức độ ghi nhận (Dành cho Quản lý)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                            else:
                                current_chamchuoc = task_data.get('MucDoChamChuoc', '0% (Không ghi nhận)')
                                u_chamchuoc = current_chamchuoc
                                if current_chamchuoc != '0% (Không ghi nhận)':
                                    st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                        else:
                            u_explain = ""
                            u_chamchuoc = '0% (Không ghi nhận)'
                    else:
                        u_chamchuoc = '0% (Không ghi nhận)'
'''

content = content.replace(old_ui, new_ui)

# Update KPI logic in monthly
old_kpi_m = '''                            if row.get('PhanLoaiTreHan') == "🌍 Do khách quan":'''
new_kpi_m = '''                            if "khách quan" in str(row.get('PhanLoaiTreHan')).lower():'''

content = content.replace(old_kpi_m, new_kpi_m)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching UI complete.")
