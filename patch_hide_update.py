import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
                u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                if u_is_late:
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
                    )
                if u_is_late or u_has_issue:
                    u_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key=f"u_explain_txt_{task_data['ID']}")
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
                    u_chamchuoc = '0% (Không ghi nhận)'
                

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
                        u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")"""

new_block = """                u_is_late = (u_deadline is not None and u_deadline < today) and not u_is_completed
                if u_status_choice is not None:
                    st.markdown("<div style='padding: 15px; border-radius: 8px; border: 1px dashed #ccc; background-color: #f9f9f9; margin-top: 15px;'>", unsafe_allow_html=True)
                    u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    if u_is_late:
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
                        )
                    if u_is_late or u_has_issue:
                        u_explain = st.text_area("📝 Chi tiết vướng mắc / Giải trình nguyên nhân (Bắt buộc)", value=task_data.get('GiaiTrinhDeXuat', ''), placeholder="Mô tả chi tiết nguyên nhân trễ hạn hoặc vướng mắc gặp phải...", height=120, key=f"u_explain_txt_{task_data['ID']}")
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
                        u_chamchuoc = '0% (Không ghi nhận)'
                    

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
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    u_late_cause = "🟢 Không trễ hạn / Đúng tiến độ"
                    u_explain = ""
                    u_chamchuoc = '0% (Không ghi nhận)'
                    u_link_text = ""
                    u_file = None
                    u_result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    print("Could not find old_block in app.py")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
