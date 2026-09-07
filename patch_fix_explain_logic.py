import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Patch Create Form
old_create_explain = """                if task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                    task_explain = st.text_area("📝 Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý (Bắt buộc)", placeholder="Ví dụ: Bị vướng pháp lý do đối tác chậm cung cấp hồ sơ. Đề xuất xin dời sang tuần sau...", height=120, key="new_task_explain")
                else:
                    task_explain = ""
            else:
                if task_has_issue:
                    task_explain = st.text_area("📝 Chi tiết vướng mắc & Đề xuất hỗ trợ (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", height=120, key="new_task_explain")
                else:
                    task_explain = \"\""""

new_create_explain = """            if (is_late and task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)") or task_has_issue:
                task_explain = st.text_area("📝 Chi tiết vướng mắc / Nguyên nhân khách quan (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân khách quan hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
            else:
                task_explain = \"\""""

if old_create_explain in content:
    content = content.replace(old_create_explain, new_create_explain)
else:
    print("Could not find old_create_explain")

# 2. Patch Update Form
old_update_explain = """                    if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                        u_explain = st.text_area("📝 Chi tiết nguyên nhân khách quan & Đề xuất phương án xử lý (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Ví dụ: Bị vướng pháp lý do đối tác chậm cung cấp hồ sơ. Đề xuất xin dời sang tuần sau...", height=120, key=f"u_explain_txt_{task_data['ID']}")
                        
                        if st.session_state.is_admin_authenticated:
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            chamchuoc_opts = ["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"]
                            idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                            u_chamchuoc = st.selectbox("Mức độ ghi nhận (Dành cho Quản lý)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                        else:
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            u_chamchuoc = current_chamchuoc
                            if current_chamchuoc != '0% (Không ghi nhận)':
                                st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                    else:
                        u_explain = ""
                        u_chamchuoc = '0% (Không ghi nhận)'
                else:
                    u_chamchuoc = '0% (Không ghi nhận)'

                    if u_has_issue:
                        u_explain = st.text_area("📝 Chi tiết vướng mắc & Đề xuất hỗ trợ (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Mô tả chi tiết vướng mắc...", height=120, key=f"u_explain_txt_{task_data['ID']}")
                    else:
                        u_explain = \"\""""

new_update_explain = """                if (u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)") or u_has_issue:
                    u_explain = st.text_area("📝 Chi tiết vướng mắc / Nguyên nhân khách quan (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Mô tả chi tiết nguyên nhân khách quan hoặc vướng mắc gặp phải...", height=120, key=f"u_explain_txt_{task_data['ID']}")
                    if u_is_late and u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                        if st.session_state.is_admin_authenticated:
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            chamchuoc_opts = ["0% (Không ghi nhận)", "Miễn trừ (Loại bỏ KPI)", "50%", "80%", "90%"]
                            idx_cc = chamchuoc_opts.index(current_chamchuoc) if current_chamchuoc in chamchuoc_opts else 0
                            u_chamchuoc = st.selectbox("Mức độ ghi nhận (Dành cho Quản lý)", chamchuoc_opts, index=idx_cc, key=f"u_cc_{task_data['ID']}")
                        else:
                            current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                            u_chamchuoc = current_chamchuoc
                            if current_chamchuoc != '0% (Không ghi nhận)':
                                st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                    else:
                        u_chamchuoc = '0% (Không ghi nhận)'
                else:
                    u_explain = ""
                    u_chamchuoc = '0% (Không ghi nhận)'"""

if old_update_explain in content:
    content = content.replace(old_update_explain, new_update_explain)
else:
    print("Could not find old_update_explain")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
