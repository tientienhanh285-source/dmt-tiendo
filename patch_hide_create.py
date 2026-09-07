import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                    # 7 & 8. Status radio
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                    task_is_completed = (task_status_choice == status_opts[0])
                    task_has_issue = (task_status_choice == status_opts[1])
                    
                    # 10. Ghi chú vướng mắc
                    is_late = (task_deadline < today) and not task_is_completed
                    task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if is_late:
                        st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                        task_late_cause = st.radio(
                            "Phân loại nguyên nhân trễ hạn",
                            ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                            index=0,
                            label_visibility="collapsed",
                            key="new_task_late_cause"
                        )
                    if is_late or task_has_issue:
                        task_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
                    else:
                        task_explain = ""
                    
                    # 9. Kết quả / File đính kèm
                    if task_has_issue:
                        task_file = None
                        task_link_text = ""
                        result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                    else:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if task_is_completed:
                            st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                        else:
                            st.markdown("**Kết quả / File đính kèm**")
                        result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key="new_result_mode")
                        if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                            if task_is_completed:
                                st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                            else:
                                st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                            task_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link", height=100, label_visibility="collapsed", placeholder="Ví dụ: Báo cáo số 01/BC-DMT, đã trình sếp, hoặc dán link Google Drive...", key="new_result_text")
                            task_file = None
                        else:
                            task_file = st.file_uploader("Tải file đính kèm (PDF, Word, Excel, Ảnh...)", key="new_result_file")
                            task_link_text = ""
                    st.markdown("</div>", unsafe_allow_html=True)"""

new_block = """                    # 7 & 8. Status radio
                    st.markdown("<p style='font-size: 1.1rem; font-weight: 600; color: #1e3a8a; margin-top: 0;'>📌 Trạng thái công việc</p>", unsafe_allow_html=True)
                    status_opts = ["✅ Xác nhận ĐÃ HOÀN THÀNH công việc", "⚠️ Công việc CHƯA HOÀN THÀNH, đang VƯỚNG MẮC"]
                    task_status_choice = st.radio("Trạng thái công việc", status_opts, index=None, label_visibility="collapsed", key="new_status_choice")
                    task_is_completed = (task_status_choice == status_opts[0])
                    task_has_issue = (task_status_choice == status_opts[1])
                    
                    if task_status_choice is not None:
                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                        # 10. Ghi chú vướng mắc
                        is_late = (task_deadline < today) and not task_is_completed
                        task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                        if is_late:
                            st.markdown("**⚠️ Phân loại nguyên nhân trễ hạn**")
                            task_late_cause = st.radio(
                                "Phân loại nguyên nhân trễ hạn",
                                ["🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)", "👤 Do chủ quan"],
                                index=0,
                                label_visibility="collapsed",
                                key="new_task_late_cause"
                            )
                        if is_late or task_has_issue:
                            task_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key="new_task_explain")
                        else:
                            task_explain = ""
                        
                        # 9. Kết quả / File đính kèm
                        if task_has_issue:
                            task_file = None
                            task_link_text = ""
                            result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                        else:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if task_is_completed:
                                st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                            else:
                                st.markdown("**Kết quả / File đính kèm**")
                            result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key="new_result_mode")
                            if result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                                if task_is_completed:
                                    st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                                else:
                                    st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                                task_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link", height=100, label_visibility="collapsed", placeholder="Ví dụ: Báo cáo số 01/BC-DMT, đã trình sếp, hoặc dán link Google Drive...", key="new_result_text")
                                task_file = None
                            else:
                                task_file = st.file_uploader("Tải file đính kèm (PDF, Word, Excel, Ảnh...)", key="new_result_file")
                                task_link_text = ""
                    else:
                        task_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                        task_explain = ""
                        result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
                        task_link_text = ""
                        task_file = None
                        
                    st.markdown("</div>", unsafe_allow_html=True)"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    print("Could not find old_block in app.py")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
