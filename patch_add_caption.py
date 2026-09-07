import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Create Form Patch
old_create = """                        if is_late or task_has_issue:
                            task_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
                        else:
                            task_explain = \"\""""

new_create = """                        if is_late or task_has_issue:
                            task_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
                            if is_late and task_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
                                st.caption("💡 **Lưu ý:** Giải trình này sẽ được hệ thống gửi đến Quản lý để xem xét mức độ ghi nhận KPI.")
                        else:
                            task_explain = \"\""""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

# Update Form Patch
old_update = """                            else:
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                                u_chamchuoc = current_chamchuoc
                                if current_chamchuoc != '0% (Không ghi nhận)':
                                    st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                        else:"""

new_update = """                            else:
                                current_chamchuoc = task_data.get('MucDoGhiNhan', '0% (Không ghi nhận)')
                                u_chamchuoc = current_chamchuoc
                                if current_chamchuoc != '0% (Không ghi nhận)':
                                    st.info(f"Đã được Quản lý ghi nhận mức độ KPI: **{current_chamchuoc}**")
                                else:
                                    st.caption("💡 **Lưu ý:** Giải trình này sẽ được hệ thống gửi đến Quản lý để xem xét mức độ ghi nhận KPI.")
                        else:"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
