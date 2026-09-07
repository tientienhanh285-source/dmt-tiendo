import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make the red warning text match exactly
content = content.replace(
    "ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC CẬP NHẬT KẾT QUẢ DƯỚI ĐÂY",
    "ĐỂ XÁC NHẬN HOÀN THÀNH, BẮT BUỘC NHẬP BÁO CÁO HOẶC TẢI FILE DƯỚI ĐÂY"
)

# Make the radio label match exactly ("Hình thức nộp" -> "Hình thức nộp kết quả")
content = content.replace(
    "u_result_mode = st.radio(\"Hình thức nộp\",",
    "u_result_mode = st.radio(\"Hình thức nộp kết quả\","
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
