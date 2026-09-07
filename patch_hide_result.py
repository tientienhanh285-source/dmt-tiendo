import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Hide Create Form result box when task_has_issue is True
old_create_block = """            # 9. Kết quả / File đính kèm
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
                task_link_text = "" """

new_create_block = """            # 9. Kết quả / File đính kèm
            if task_has_issue:
                task_file = None
                task_link_text = ""
                result_mode = "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)"
            else:
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
                    task_link_text = "" """

if old_create_block in content:
    content = content.replace(old_create_block, new_create_block)
else:
    print("Could not find old_create_block")

# 2. Hide Update Form result box when u_has_issue is True
old_update_block = """                    if u_is_completed:
                        st.markdown("🚨 **<span style='color:red; font-size: 17px;'>ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY:</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown("**Cập nhật Kết quả / File đính kèm**")
                        
                    u_result_mode = st.radio("Hình thức nộp kết quả", ["✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)", "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)"], horizontal=True, key=f"u_result_mode_{task_data['ID']}")
                    
                    u_link_text = ""
                    u_file = None
                    if u_result_mode == "✍️ Nhập tên Báo cáo / Số hiệu Văn bản / Link (Dạng text tự do)":
                        if u_is_completed:
                            st.warning("⚠️ **VUI LÒNG NHẬP NỘI DUNG KẾT QUẢ / BÁO CÁO VÀO Ô BÊN DƯỚI:**")
                        else:
                            st.info("💡 **Ghi chú nội dung/tiến độ công việc vào ô bên dưới:**")
                        u_link_text = st.text_area("Nhập tên Báo cáo / Số hiệu Văn bản / Link mới", height=100, label_visibility="collapsed", placeholder="Ví dụ: Đã hoàn thành 50%, trình ký sếp...", key=f"u_result_text_{task_data['ID']}")
                    elif u_result_mode == "📁 Tải file đính kèm (PDF, Word, Excel, Ảnh...)":
                        u_file = st.file_uploader("Tải file đính kèm mới", key=f"u_result_file_{task_data['ID']}")"""

new_update_block = """                    u_link_text = ""
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

if old_update_block in content:
    content = content.replace(old_update_block, new_update_block)
else:
    print("Could not find old_update_block")

# Make the explanation text area clearer as requested previously but applied to the other box just in case
# Original code: task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", key="new_task_explain")
content = content.replace(
    'task_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", key="new_task_explain")',
    'task_explain = st.text_area("📝 Chi tiết vướng mắc & Đề xuất hỗ trợ (Bắt buộc)", placeholder="Mô tả chi tiết vướng mắc...", height=120, key="new_task_explain")'
)
content = content.replace(
    'u_explain = st.text_area("Ghi chú / Giải trình vướng mắc (Bắt buộc)", value=task_data.get(\'GiaiTrinhDeXuat\', \'\'), key=f"u_explain_txt_{task_data[\'ID\']}")',
    'u_explain = st.text_area("📝 Chi tiết vướng mắc & Đề xuất hỗ trợ (Bắt buộc)", value=task_data.get(\'GiaiTrinhDeXuat\', \'\'), placeholder="Mô tả chi tiết vướng mắc...", height=120, key=f"u_explain_txt_{task_data[\'ID\']}")'
)
content = content.replace(
    'st.error("⚠️ Bắt buộc điền \'Ghi chú / Giải trình vướng mắc\' chi tiết!")',
    'st.error("⚠️ Bắt buộc nhập \'Chi tiết vướng mắc & Đề xuất hỗ trợ\'!")'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
