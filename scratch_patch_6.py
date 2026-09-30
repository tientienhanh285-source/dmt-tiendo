import os
import re

# 1. Update views/3_Cap_Nhat.py for Chờ nghiệm thu (Trễ hạn) and Audit Log
with open(r"views\3_Cap_Nhat.py", "r", encoding="utf-8") as f:
    c3 = f.read()

# For add task
old_add_status = """            if task_is_completed:
                calc_status = "Chờ nghiệm thu"
            elif task_has_issue:"""
new_add_status = """            if task_is_completed:
                if task_deadline < today:
                    calc_status = "Chờ nghiệm thu (Trễ hạn)"
                else:
                    calc_status = "Chờ nghiệm thu"
            elif task_has_issue:"""
c3 = c3.replace(old_add_status, new_add_status)

# For update task
old_upd_status = """                    if u_is_completed:
                        u_status = "Chờ nghiệm thu"
                    elif u_has_issue:"""
new_upd_status = """                    if u_is_completed:
                        if u_deadline < today:
                            u_status = "Chờ nghiệm thu (Trễ hạn)"
                        else:
                            u_status = "Chờ nghiệm thu"
                    elif u_has_issue:"""
c3 = c3.replace(old_upd_status, new_upd_status)

# Add Audit Log on update
old_upd_call = """                            if update_task(selected_id, update_dict):
                                st.session_state["success_msg"] = f"🎉 Đã lưu cập nhật công việc mã: {selected_id}!"
                                st.rerun()"""
new_upd_call = """                            if update_task(selected_id, update_dict):
                                try:
                                    conn = get_gsheets_conn()
                                    if conn:
                                        import json
                                        user_name = st.session_state.get("username", "Unknown")
                                        action_txt = f"Cập nhật tiến độ thành {u_progress}% | Trạng thái: {u_status}"
                                        row = {
                                            "NhanSu": selected_id,
                                            "PhongBan": str(datetime.now())[:19],
                                            "Role": "AUDIT_LOG",
                                            "config_json": json.dumps({"user": user_name, "action": action_txt, "time": str(datetime.now())[:19]})
                                        }
                                        conn.table("kpi_config").insert(row).execute()
                                except:
                                    pass
                                st.session_state["success_msg"] = f"🎉 Đã lưu cập nhật công việc mã: {selected_id}!"
                                st.rerun()"""
c3 = c3.replace(old_upd_call, new_upd_call)

with open(r"views\3_Cap_Nhat.py", "w", encoding="utf-8") as f:
    f.write(c3)


# 2. Update views/4_Nghiem_Thu.py to handle "Chờ nghiệm thu (Trễ hạn)" -> "Hoàn thành (Trễ hạn)"
with open(r"views\4_Nghiem_Thu.py", "r", encoding="utf-8") as f:
    c4 = f.read()

# Filter condition
c4 = c4.replace("avail_df = display_df[display_df['TrangThai'] == 'Chờ nghiệm thu'].copy()",
                "avail_df = display_df[display_df['TrangThai'].isin(['Chờ nghiệm thu', 'Chờ nghiệm thu (Trễ hạn)'])].copy()")

# Approve button logic
old_appr = """                        if st.button("✅ Duyệt / Đánh giá ĐẠT", type="primary", key=f"btn_appr_{task_id}"):
                            # 1. Update task status to "Hoàn thành"
                            update_dict = {
                                "TrangThai": "Hoàn thành",
                                "MucDoGhiNhan": "Mức 3 (100%)",
                                "PhanTramHoanThanh": 100,
                                "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            if update_task(task_id, update_dict):"""
                            
new_appr = """                        if st.button("✅ Duyệt / Đánh giá ĐẠT", type="primary", key=f"btn_appr_{task_id}"):
                            # 1. Update task status to "Hoàn thành"
                            new_status = "Hoàn thành (Trễ hạn)" if task_data.get("TrangThai") == "Chờ nghiệm thu (Trễ hạn)" else "Hoàn thành"
                            update_dict = {
                                "TrangThai": new_status,
                                "MucDoGhiNhan": "Mức 3 (100%)",
                                "PhanTramHoanThanh": 100,
                                "NgayCapNhat": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            if update_task(task_id, update_dict):
                                try:
                                    conn = get_gsheets_conn()
                                    if conn:
                                        import json
                                        user_name = st.session_state.get("username", "Manager")
                                        row = {
                                            "NhanSu": task_id,
                                            "PhongBan": str(datetime.now())[:19],
                                            "Role": "AUDIT_LOG",
                                            "config_json": json.dumps({"user": user_name, "action": f"Quản lý Nghiệm thu ({new_status})", "time": str(datetime.now())[:19]})
                                        }
                                        conn.table("kpi_config").insert(row).execute()
                                except:
                                    pass
"""
c4 = c4.replace(old_appr, new_appr)

with open(r"views\4_Nghiem_Thu.py", "w", encoding="utf-8") as f:
    f.write(c4)


# 3. Add Tab 4 in views/8_Quan_Tri_BSC.py (Nghiệm thu Chỉ tiêu BSC & Khống chế 99%)
with open(r"views\8_Quan_Tri_BSC.py", "r", encoding="utf-8") as f:
    c8 = f.read()

c8 = c8.replace('tab1, tab2, tab3 = st.tabs(["1. Thiết lập Kế hoạch Năm & Quý", "2. Phân rã Mục tiêu Tháng", "3. Giao việc từ Mục tiêu"])',
                'tab1, tab2, tab3, tab4 = st.tabs(["1. Kế hoạch Năm", "2. Mục tiêu Tháng", "3. Giao việc", "4. Nghiệm thu Chỉ tiêu"])')

tab4_code = """
    with tab4:
        st.subheader("Kiểm soát & Nghiệm thu Chỉ tiêu Tháng (Max 99%)")
        st.info("Hệ thống tự động cộng dồn tiến độ các công việc con. Tuy nhiên, thanh tiến độ Chỉ tiêu sẽ bị khống chế ở mức 99%. Quản lý phải bấm 'Duyệt' để xác nhận đạt 100%.")
        
        t4_year = st.selectbox("Năm", ["2025", "2026", "2027"], key="t4_year")
        t4_month = st.selectbox("Tháng", [str(i) for i in range(1, 13)], key="t4_month")
        t4_dept = st.selectbox("Phòng ban", get_departments_for_company(selected_company, config), key="t4_dept")
        
        month_key = f"{t4_dept}_{t4_year}_{t4_month}"
        
        if month_key in bsc_data["months"] and bsc_data["months"][month_key]:
            approved_goals = bsc_data.get("approved_goals", [])
            for goal in bsc_data["months"][month_key]:
                goal_name = goal["name"]
                # Lấy các task thuộc mục tiêu này
                goal_tasks = df[df["SanPhamBanGiao"] == goal_name] if not df.empty else pd.DataFrame()
                
                avg_prog = 0
                if not goal_tasks.empty:
                    goal_tasks['PhanTramHoanThanh'] = pd.to_numeric(goal_tasks['PhanTramHoanThanh'], errors='coerce').fillna(0)
                    avg_prog = goal_tasks['PhanTramHoanThanh'].mean()
                
                # Khống chế 99%
                is_approved = f"{month_key}_{goal_name}" in approved_goals
                if avg_prog >= 99.9 and not is_approved:
                    display_prog = 99.0
                elif avg_prog >= 99.9 and is_approved:
                    display_prog = 100.0
                else:
                    display_prog = round(avg_prog, 1)
                
                st.markdown(f"**🎯 Chỉ tiêu:** {goal_name} (Tỷ trọng: {goal['weight']}%)")
                st.progress(int(display_prog) / 100.0)
                st.caption(f"Tiến độ hiện tại: {display_prog}% ({len(goal_tasks)} công việc)")
                
                if display_prog == 99.0:
                    if st.button(f"✅ Duyệt Hoàn thành 100% Chỉ tiêu này", key=f"btn_appr_goal_{goal_name}"):
                        if "approved_goals" not in bsc_data:
                            bsc_data["approved_goals"] = []
                        bsc_data["approved_goals"].append(f"{month_key}_{goal_name}")
                        save_bsc_config(bsc_data)
                        st.success("Đã nghiệm thu hoàn thành Chỉ tiêu!")
                        st.rerun()
                st.write("---")
        else:
            st.info("Không có chỉ tiêu tháng nào để nghiệm thu.")
"""

c8 += tab4_code

with open(r"views\8_Quan_Tri_BSC.py", "w", encoding="utf-8") as f:
    f.write(c8)

print("Deploy features complete!")
