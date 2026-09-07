import sys

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    insertion_point = """            if ai_person:
                jd_source_data = config.get("job_descriptions", {}).get(selected_company, {}).get(ai_person, "")"""

    batch_code = """
            # --- BATCH AI SCAN ---
            st.markdown("---")
            with st.expander("⚡ Quét nhanh toàn bộ Phòng ban (Batch AI Scan)", expanded=False):
                st.info("Tính năng này sẽ tự động kiểm tra JD của tất cả nhân sự trong phòng ban. Những ai chưa có kết quả sẽ tự động gọi AI để phân tích. Khuyên dùng khi bạn muốn kiểm tra tổng thể cả phòng.")
                
                batch_api_key = ""
                try:
                    if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
                        batch_api_key = st.secrets["gemini"]["api_key"]
                except:
                    pass
                if not batch_api_key:
                    import os
                    batch_api_key = os.environ.get("GEMINI_API_KEY", "")
                    
                if not batch_api_key:
                    batch_api_key = st.text_input("🔑 Nhập khóa API Gemini để quét hàng loạt:", type="password", key="batch_api_key_input")
                
                if st.button("🚀 Bắt đầu Quét toàn bộ", type="primary"):
                    if not batch_api_key:
                        st.error("Vui lòng nhập API Key!")
                    elif not ai_personnel:
                        st.warning("Phòng ban không có nhân sự.")
                    else:
                        import google.generativeai as genai
                        import hashlib
                        import json
                        import time
                        
                        genai.configure(api_key=batch_api_key, transport='rest')
                        valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        model_name = 'gemini-3.6-flash' if 'models/gemini-3.6-flash' in valid_models else ('gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else 'gemini-pro')
                        model = genai.GenerativeModel(model_name)
                        
                        results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def is_same_person_batch(db_name, target_name):
                            db_str = str(db_name).strip().lower()
                            tgt_str = str(target_name).strip().lower()
                            if db_str == tgt_str: return True
                            tgt_parts = tgt_str.split()
                            if len(tgt_parts) >= 2:
                                return tgt_parts[0] in db_str and tgt_parts[-1] in db_str
                            return False
                        
                        total_people = len(ai_personnel)
                        
                        for idx, p in enumerate(ai_personnel):
                            status_text.text(f"Đang phân tích ({idx+1}/{total_people}): {p}...")
                            
                            # Lọc công việc
                            p_tasks = display_df[
                                (display_df['NguoiChuTri'].apply(lambda x: is_same_person_batch(x, p))) & 
                                (display_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == ai_month)
                            ]
                            
                            if p_tasks.empty:
                                results.append({"Nhân sự": p, "Kết quả": "Trống", "Tỷ lệ khớp": None, "Chi tiết": "Không có công việc trong tháng này"})
                            else:
                                jd_data = config.get("job_descriptions", {}).get(selected_company, {}).get(p, "")
                                jd_str = jd_data if isinstance(jd_data, str) else jd_data.get("jd_text", "")
                                
                                if not jd_str.strip():
                                    results.append({"Nhân sự": p, "Kết quả": "Thiếu JD", "Tỷ lệ khớp": None, "Chi tiết": "Chưa khai báo Mô tả công việc"})
                                else:
                                    tasks_list = "\\n".join([f"- {row['TenCongViec']}" for _, row in p_tasks.iterrows()])
                                    prompt = f\"\"\"
                                    Đóng vai một Giám đốc nhân sự cực kỳ tinh tế. 
                                    Dưới đây là Bản Mô tả công việc (JD) của nhân viên {p}:
                                
                                    [BẢN MÔ TẢ CÔNG VIỆC]
                                    {jd_str}
                                    [KẾT THÚC JD]
                                
                                    Và đây là danh sách công việc họ thực hiện trong tháng:
                                    {tasks_list}
                                
                                    NHIỆM VỤ CỦA BẠN:
                                    1. Đối chiếu TỪNG công việc xem nó có KHỚP với chuyên môn quy định trong JD không. 
                                    (Lưu ý: Tên công việc thực tế có thể chi tiết và từ ngữ khác biệt so với JD văn xuôi. Hãy dùng tư duy suy luận về bản chất và mục đích để phán đoán).
                                    2. Nếu khớp, giải thích vì nó phục vụ cho mục nào trong JD. Nếu ngoài JD, ghi rõ là công việc phát sinh.
                                    3. Format kết quả đầu ra thành đúng định dạng chuỗi JSON thô như sau (chỉ trả về JSON, không chứa dấu tick markdown ```json):
                                    {{
                                        "ty_le_khop": <số nguyên từ 0-100, ví dụ 80>,
                                        "chi_tiet": [
                                            {{
                                                "ten_cong_viec": "<Tên công việc y nguyên trong danh sách>",
                                                "phan_loai": "<Chỉ điền 'Khớp JD' hoặc 'Ngoài JD'>",
                                                "nhan_xet": "<Phân tích ngắn gọn 1-2 câu>"
                                            }}
                                        ]
                                    }}
                                    \"\"\"
                                    
                                    prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
                                    cache_file = f".ai_cache_{prompt_hash}.txt"
                                    
                                    try:
                                        if os.path.exists(cache_file):
                                            with open(cache_file, "r", encoding="utf-8") as f:
                                                raw_text = f.read()
                                        else:
                                            # Gọi API
                                            response = model.generate_content(
                                                prompt, 
                                                generation_config={"temperature": 0.0},
                                                request_options={"retry": None, "timeout": 30.0}
                                            )
                                            raw_text = response.text
                                            if raw_text:
                                                with open(cache_file, "w", encoding="utf-8") as f:
                                                    f.write(raw_text)
                                            time.sleep(2) # Tránh rate limit
                                            
                                        cleaned = raw_text.strip()
                                        if cleaned.startswith("```json"):
                                            cleaned = cleaned[7:]
                                        if cleaned.endswith("```"):
                                            cleaned = cleaned[:-3]
                                        
                                        data = json.loads(cleaned)
                                        ty_le = data.get("ty_le_khop", 0)
                                        ngoai_jd_count = sum(1 for c in data.get("chi_tiet", []) if "Ngoài JD" in c.get("phan_loai", ""))
                                        
                                        if ty_le == 100:
                                            res_text = "🟢 Tốt (100% khớp)"
                                        elif ty_le >= 50:
                                            res_text = f"🟡 Cảnh báo ({ty_le}% khớp)"
                                        else:
                                            res_text = f"🔴 Lệch JD ({ty_le}% khớp)"
                                            
                                        chi_tiet_text = f"{ngoai_jd_count} việc ngoài JD" if ngoai_jd_count > 0 else "Hoàn toàn khớp"
                                        
                                        results.append({"Nhân sự": p, "Kết quả": res_text, "Tỷ lệ khớp": ty_le, "Chi tiết": chi_tiet_text})
                                    except Exception as e:
                                        results.append({"Nhân sự": p, "Kết quả": "Lỗi AI", "Tỷ lệ khớp": None, "Chi tiết": str(e)})
                            
                            progress_bar.progress((idx + 1) / total_people)
                            
                        status_text.success("✅ Đã hoàn thành phân tích toàn bộ phòng ban!")
                        
                        if results:
                            df_res = pd.DataFrame(results)
                            st.dataframe(df_res, use_container_width=True, hide_index=True)
                            
            st.markdown("---")
"""

    if "# --- BATCH AI SCAN ---" not in content:
        content = content.replace(insertion_point, batch_code + "\n" + insertion_point)
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Patched successfully!")
    else:
        print("Already patched.")

if __name__ == "__main__":
    main()
