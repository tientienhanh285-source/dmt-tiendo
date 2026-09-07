import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """            # 9. Kết quả / File đính kèm
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

new_block = """            # 9. Kết quả / File đính kèm
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

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    print("Could not find old_block in app.py")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
