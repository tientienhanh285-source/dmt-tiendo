                    u_weight = task_data.get('TyTrongKPI', '')
                    
                
                    st.markdown("<br>", unsafe_allow_html=True)
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
                    )
                    if u_late_cause == "🌧️ Do khách quan (Pháp lý, Đối tác, Thời tiết, Cơ quan nhà nước...)":
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
                        u_explain = ""
                
                btn_save, btn_del = st.columns([3, 2])
                
                with btn_save:
                    save_click = st.button("💾 LƯU CẬP NHẬT TIẾN ĐỘ", type="primary", key=f"btn_save_update_{task_data['ID']}")
