import os
import re

def patch_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where to insert
    target = """                    kpi_month_df[["Người thực hiện", "Phòng ban", "Số việc", "Điểm công việc", "Thưởng/Phạt", "TỔNG ĐIỂM", "Xếp loại"]],
                    column_config={
                        "TỔNG ĐIỂM": st.column_config.ProgressColumn("TỔNG ĐIỂM", format="%f", min_value=0, max_value=115),
                    },
                    use_container_width=True, hide_index=True
                )"""
                
    if target not in content:
        print("Cannot find target string in app.py")
        return

    insertion = """
                st.markdown("---")
                with st.expander("🤖 AI Phân tích Độ chuẩn xác JD (Quét Hàng Loạt Phòng Ban)", expanded=False):
                    st.info("💡 Tính năng này sẽ quét qua toàn bộ các nhân viên trong phòng ban trên để đối chiếu công việc với JD, nhằm tự động lọc ra những người có **tỷ lệ làm việc lặt vặt/ngoài lề cao**.")
                    
                    import os
                    api_key = ""
                    try:
                        if "gemini" in st.secrets and "api_key" in st.secrets["gemini"]:
                            api_key = st.secrets["gemini"]["api_key"]
                    except:
                        pass
                        
                    if not api_key:
                        api_key = os.environ.get("GEMINI_API_KEY", "")
                        
                    if not api_key:
                        api_key = st.text_input("🔑 Nhập khóa API Gemini (API Key) để sử dụng:", type="password", key="api_key_batch")
                        
                    if api_key:
                        if st.button("▶️ QUÉT AI TOÀN BỘ PHÒNG BAN TRÊN", type="primary", key="btn_scan_batch"):
                            import google.generativeai as genai
                            import json
                            genai.configure(api_key=api_key, transport='rest')
                            try:
                                valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                                model_name = 'gemini-3.6-flash' if 'models/gemini-3.6-flash' in valid_models else ('gemini-1.5-flash' if 'models/gemini-1.5-flash' in valid_models else 'gemini-pro')
                                model = genai.GenerativeModel(model_name)
                                
                                # Process all personnel in the current kpi_month_df
                                red_flag_reports = []
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                total_p = len(kpi_month_df)
                                for i, (_, row) in enumerate(kpi_month_df.iterrows()):
                                    p_name = row['Người thực hiện']
                                    status_text.text(f"Đang quét {i+1}/{total_p}: {p_name} ...")
                                    progress_bar.progress((i) / total_p)
                                    
                                    # Get JD
                                    jd_df = db.get("jd") if isinstance(db.get("jd"), pd.DataFrame) else pd.DataFrame([db.get("jd")] if db.get("jd") else [])
                                    if jd_df.empty:
                                        try:
                                            jd_df = pd.read_json("jd_db.json") if os.path.exists("jd_db.json") else pd.DataFrame()
                                        except: pass
                                    
                                    p_jd = jd_df[jd_df['TenNhanVien'].str.lower() == p_name.lower()] if not jd_df.empty and 'TenNhanVien' in jd_df.columns else pd.DataFrame()
                                    if p_jd.empty:
                                        # Khong co JD, bo qua hoac canh bao
                                        continue
                                        
                                    jd_source = p_jd.iloc[0].get('NoiDungJD', '')
                                    if not jd_source or len(str(jd_source)) < 10:
                                        continue
                                        
                                    # Get tasks
                                    ai_tasks = display_df[
                                        (display_df['NguoiChuTri'].str.lower() == p_name.lower()) & 
                                        (display_df['Deadline'].apply(lambda x: x.month == selected_month and x.year == selected_year if pd.notna(x) and hasattr(x, 'month') else False))
                                    ]
                                    
                                    if ai_tasks.empty:
                                        continue
                                        
                                    tasks_list = "\\n".join([f"- {r['TenCongViec']}" for _, r in ai_tasks.iterrows()])
                                    
                                    prompt = f\"\"\"Đóng vai Giám đốc nhân sự tinh tế.
                                    Mô tả công việc của {p_name}:
                                    {jd_source}
                                    
                                    Công việc thực hiện:
                                    {tasks_list}
                                    
                                    1. Đối chiếu từng công việc xem có khớp với chuyên môn trong JD không.
                                    2. Format kết quả đầu ra thành JSON thô (chỉ trả về JSON, không markdown ```json):
                                    {{
                                        "chi_tiet": [
                                            {{
                                                "ten_cong_viec": "<Tên>",
                                                "phan_loai": "<Chỉ điền 'Khớp JD' hoặc 'Ngoài JD'>"
                                            }}
                                        ]
                                    }}
                                    \"\"\"
                                    
                                    try:
                                        response = model.generate_content(
                                            prompt, 
                                            generation_config={"temperature": 0.0},
                                            request_options={"retry": None, "timeout": 30.0}
                                        )
                                        raw_text = response.text
                                        import re
                                        json_match = re.search(r'\\{.*\\}', raw_text, re.DOTALL)
                                        if json_match:
                                            ai_result = json.loads(json_match.group(0))
                                            out_of_jd_tasks = [t for t in ai_result.get("chi_tiet", []) if t.get("phan_loai", "") == "Ngoài JD"]
                                            if out_of_jd_tasks:
                                                red_flag_reports.append({
                                                    "Tên nhân viên": p_name,
                                                    "Phòng ban": row['Phòng ban'],
                                                    "Số việc ngoài JD": len(out_of_jd_tasks),
                                                    "Chi tiết": "\\n".join([f"- {t['ten_cong_viec']}" for t in out_of_jd_tasks])
                                                })
                                    except Exception as e:
                                        print(f"Error AI cho {p_name}: {e}")
                                        pass
                                
                                progress_bar.progress(1.0)
                                status_text.text(f"Hoàn thành quét {total_p} nhân sự!")
                                
                                if len(red_flag_reports) == 0:
                                    st.success("✅ Tuyệt vời! Toàn bộ phòng ban này đều làm việc đúng chuẩn JD, không phát hiện việc nào sai lệch chuyên môn.")
                                else:
                                    st.error(f"🚨 PHÁT HIỆN {len(red_flag_reports)} NHÂN SỰ CÓ CÔNG VIỆC NGOÀI CHUYÊN MÔN!")
                                    st.dataframe(pd.DataFrame(red_flag_reports), use_container_width=True)
                            except Exception as ex:
                                st.error(f"Lỗi AI: {ex}")
    """
    
    new_content = content.replace(target, target + insertion)
    
    if target + insertion in new_content:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched app.py!")
    else:
        print("Failed to patch")

if __name__ == '__main__':
    patch_app()
