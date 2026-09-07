import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Form Patch
old_update = """                    st.markdown("<br>", unsafe_allow_html=True)
                    current_link = task_data['LinkKetQua']
                    u_link_text = ""
                    u_file = None
                    if not u_has_issue:
                        if u_is_completed:
                            st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                        else:
                            st.markdown("**Cập nhật Kết quả / File đính kèm**")
                            
                        u_result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                        
                        if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            if u_is_completed:
                                st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                            else:
                                st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                            u_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", height=100, label_visibility="collapsed", placeholder="Ví dụ: Đã hoàn thành 50%, trình ký sếp...", key=f"u_result_text_{task_data['ID']}")
                        elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                            u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")
                            
                    st.markdown("<br>", unsafe_allow_html=True)
                    u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
                    u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if u_is_late:
                        u_options = ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                        u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                        u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                        u_late_cause = st.selectbox(
                            "Phân loại nguyên nhân trễ hạn",
                            u_options,
                            index=u_default_idx,
                            key=f"u_late_cause_sel_{task_data['ID']}"
                        )"""

new_update = """                    current_link = task_data['LinkKetQua']
                    u_link_text = ""
                    u_file = None
                    if not u_has_issue:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if u_is_completed:
                            st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                        else:
                            st.markdown("**Cập nhật Kết quả / File đính kèm**")
                            
                        u_result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                        
                        if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            if u_is_completed:
                                st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                            else:
                                st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                            u_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", height=100, label_visibility="collapsed", placeholder="Ví dụ: Đã hoàn thành 50%, trình ký sếp...", key=f"u_result_text_{task_data['ID']}")
                        elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                            u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")
                            
                    u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
                    u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if u_is_late:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                        u_options = ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"]
                        u_current_val = task_data.get('PhanLoaiTreHan', "🟢 Không trễ hạn / Đúng tiến độ")
                        u_default_idx = u_options.index(u_current_val) if u_current_val in u_options else 0
                        u_late_cause = st.radio(
                            "Phân loại nguyên nhân trễ hạn",
                            u_options,
                            index=u_default_idx,
                            label_visibility="collapsed",
                            key=f"u_late_cause_sel_{task_data['ID']}"
                        )"""

if old_update in content:
    content = content.replace(old_update, new_update)
else:
    print("Could not find old_update")

# 2. Create Form Patch
old_create = """            # 10. Ghi chú vướng mắc
            is_late = (task_deadline < today) and not task_is_completed
            task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
            if is_late:
                task_late_cause = st.selectbox(
                    "Phân loại nguyên nhân trễ hạn",
                    ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                    index=0,
                    key="new_task_late_cause"
                )"""

new_create = """            # 10. Ghi chú vướng mắc
            is_late = (task_deadline < today) and not task_is_completed
            task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
            if is_late:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                task_late_cause = st.radio(
                    "Phân loại nguyên nhân trễ hạn",
                    ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                    index=0,
                    label_visibility="collapsed",
                    key="new_task_late_cause"
                )"""

if old_create in content:
    content = content.replace(old_create, new_create)
else:
    print("Could not find old_create")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
