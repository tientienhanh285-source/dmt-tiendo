import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from core_logic import *

if 'role_mode' in st.session_state:
    role_mode = st.session_state['role_mode']
else:
    role_mode = 'Nhân viên'

if 'is_local' in st.session_state:
    is_local = st.session_state['is_local']
else:
    is_local = False

if 'selected_company' in st.session_state:
    selected_company = st.session_state['selected_company']
else:
    selected_company = "CTY CP ĐẦU TƯ ĐÀ NẴNG - MIỀN TRUNG"

if 'global_active_dept' in st.session_state:
    global_active_dept = st.session_state['global_active_dept']
else:
    global_active_dept = "Tất cả"

config = load_config()

# Fix missing globals
try:
    today = datetime.now().date()
except:
    from datetime import datetime
    today = datetime.now().date()

try:
    current_month = datetime.now().month
except:
    current_month = 9

db_filters = {}
if 'role_mode' in st.session_state:
    if st.session_state['role_mode'] == "Nhân viên" and st.session_state.get('is_personal_authenticated') and st.session_state.get('personal_user'):
        db_filters['NguoiChuTri'] = st.session_state.personal_user
    elif st.session_state['role_mode'] == "Quản lý" and st.session_state.get('is_manager_authenticated') and st.session_state.get('manager_dept'):
        db_filters['PhongBan'] = st.session_state.manager_dept

if 'display_df' not in locals():
    try:
        display_df = read_db(filters=db_filters if db_filters else None)
    except:
        pass

if 'df' in locals() or 'df' not in locals():
    df = display_df.copy()

if 'df_old_dummy' not in locals():
    try:
        df = display_df.copy()
    except:
        pass
        
if 'merged_projs' not in locals():
    merged_projs = []
if 'db_projs' not in locals():
    db_projs = []

if 'display_df' not in locals():
    import pandas as pd
    display_df = pd.DataFrame(columns=['TenDuAn', 'TrangThai', 'Deadline'])
if 'df' not in locals():
    df = display_df.copy()



st.markdown("### 🔍 Quản lý & Đối chiếu JD (Trí tuệ nhân tạo)")
st.info("💡 Hệ thống sử dụng **Trí tuệ nhân tạo (Google Gemini)** để phân tích tự động việc nhân sự làm có đúng chuyên môn trong Bản Mô tả công việc (JD) hay không.")

tab_hr, tab_ai = st.tabs(["📝 1. Cập nhật Mô tả công việc (Dành cho HR)", "🔍 2. AI Đối chiếu & Báo cáo (Dành cho Sếp)"])

with tab_hr:
    st.markdown("#### Khai báo JD nguyên bản cho Nhân sự")
    st.write("Vui lòng mở file Word Mô tả công việc của nhân sự, copy phần **TRÁCH NHIỆM CÔNG VIỆC** và dán vào đây.")
    
    # Select personnel
    if selected_company == "Tất cả đơn vị":
        st.warning("⚠️ Vui lòng chọn cụ thể Công ty ở cột trái.")
    else:
        comp_data = config.get("companies", {}).get(selected_company, {})
        all_depts = comp_data.get("departments", [])
        sel_dept = st.selectbox("Chọn Phòng ban", all_depts, key="jd_dept")
        
        personnel = comp_data.get("personnel_by_department", {}).get(sel_dept, [])
        if personnel:
            sel_person = st.selectbox("Chọn Nhân sự", personnel, key="jd_person")
            
            if "job_descriptions" not in config:
                config["job_descriptions"] = {}
            if selected_company not in config["job_descriptions"]:
                config["job_descriptions"][selected_company] = {}
                
            existing_jd_data = config["job_descriptions"][selected_company].get(sel_person, "")
            if isinstance(existing_jd_data, str):
                existing_jd_text = existing_jd_data
            else:
                existing_jd_text = existing_jd_data.get("jd_text", "")
                
            st.write("---")
            st.markdown("**Cách 1: Nhập văn bản hoặc dán (Copy/Paste)**")
            jd_text = st.text_area("Nội dung Mô tả công việc:", value=existing_jd_text, height=200, key=f"jd_text_{sel_person}")
            
            st.markdown("**Cách 2: Tải lên file Word/PDF (Tự động đọc nội dung)**")
            uploaded_file = st.file_uploader("Kéo thả file JD vào đây", type=['docx', 'pdf'], key=f"jd_upload_{sel_person}")
            
            if uploaded_file is not None:
                if st.button("Trích xuất nội dung từ File"):
                    with st.spinner("Đang đọc file..."):
                        try:
                            text = ""
                            if uploaded_file.name.endswith(".docx"):
                                import docx
                                doc = docx.Document(uploaded_file)
                                text = "\n".join([p.text for p in doc.paragraphs])
                            elif uploaded_file.name.endswith(".pdf"):
                                import pypdf
                                pdf = pypdf.PdfReader(uploaded_file)
                                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                            
                            if not text.strip():
                                st.warning("⚠️ Không thể đọc được chữ từ file này (có thể đây là file scan/ảnh). Vui lòng copy và dán văn bản thủ công vào ô phía trên.")
                            else:
                                st.session_state[f"extracted_text_{sel_person}"] = text
                        except Exception as e:
                            st.error(f"Lỗi đọc file: {e}")
            
            if st.session_state.get(f"extracted_text_{sel_person}"):
                st.success("Đã trích xuất thành công! Bạn có thể xem và chỉnh sửa trước khi lưu:")
                jd_text = st.text_area("Nội dung trích xuất", value=st.session_state[f"extracted_text_{sel_person}"], height=200, key=f"jd_text_ext_{sel_person}")
            
            if st.button("💾 Lưu Mô tả công việc", type="primary"):
                if not jd_text.strip():
                    st.error("⚠️ Nội dung Mô tả công việc đang trống! Vui lòng nhập nội dung hoặc trích xuất từ file trước khi lưu.")
                else:
                    if isinstance(existing_jd_data, dict):
                        new_data = existing_jd_data.copy()
                        new_data["jd_text"] = jd_text
                    else:
                        new_data = {"jd_text": jd_text}
                        
                    config["job_descriptions"][selected_company][sel_person] = new_data
                    if save_config(config):
                        st.success(f"✅ Đã lưu Bản mô tả công việc (JD) thành công cho nhân sự **{sel_person}**!")
                        import time
                        time.sleep(1)
                        st.rerun()
        else:
            st.warning("Phòng ban này chưa có nhân sự.")

with tab_ai:
    st.markdown("#### 🔍 Phân tích độ phủ công việc thực tế với JD")
    if selected_company == "Tất cả đơn vị":
        st.warning("⚠️ Vui lòng chọn cụ thể Công ty ở cột trái.")
    else:
        comp_data = config.get("companies", {}).get(selected_company, {})
        
        months = set()
        if not display_df.empty:
            for _, row in display_df.iterrows():
                if pd.notna(row.get('Deadline')) and hasattr(row['Deadline'], 'strftime'):
                    months.add(row['Deadline'].strftime('%m/%Y'))
        month_options = sorted(list(months), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)
        if not month_options: month_options = [today.strftime('%m/%Y')]
        
        c1, c2, c3 = st.columns(3)
        with c1: ai_month = st.selectbox("Tháng đánh giá", month_options, key="ai_month_select")
        with c2: ai_dept = st.selectbox("Phòng ban", comp_data.get("departments", []), key="ai_dept_select")
        
        ai_personnel = comp_data.get("personnel_by_department", {}).get(ai_dept, [])
        with c3:
            if ai_personnel:
                ai_person = st.selectbox("Nhân sự", ai_personnel, key="ai_person_select")
            else:
                ai_person = None
                st.warning("Trống")
        

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
                                tasks_list = "\n".join([f"- {row['TenCongViec']}" for _, row in p_tasks.iterrows()])
                                prompt = f"""
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
                                """
                                
                                prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
                                cache_file = f".ai_cache_{prompt_hash}.txt"
                                
                                try:
                                    if os.path.exists(cache_file):
                                        with open(cache_file, "r", encoding="utf-8") as f:
                                            raw_text = f.read()
                                    else:
                                        max_retries = 3
                                        for attempt in range(max_retries):
                                            try:
                                                response = model.generate_content(
                                                    prompt, 
                                                    generation_config={"temperature": 0.0},
                                                    request_options={"timeout": 60.0}
                                                )
                                                raw_text = response.text
                                                break
                                            except Exception as api_err:
                                                if attempt == max_retries - 1:
                                                    raise api_err
                                                time.sleep(3 * (attempt + 1))
                                                
                                        if raw_text:
                                            with open(cache_file, "w", encoding="utf-8") as f:
                                                f.write(raw_text)
                                        time.sleep(3) # Tránh rate limit

                                        
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

        if ai_person:
            jd_source_data = config.get("job_descriptions", {}).get(selected_company, {}).get(ai_person, "")
            if isinstance(jd_source_data, str):
                jd_source = jd_source_data
            else:
                jd_source = jd_source_data.get("jd_text", "")
                
            if not jd_source.strip():
                st.error(f"⚠️ Nhân sự **{ai_person}** chưa được khai báo Mô tả công việc. Vui lòng sang tab bên cạnh để cập nhật JD trước khi AI có thể quét.")
            else:
                with st.expander("Xem trước JD gốc (Làm cơ sở chấm) 👀", expanded=False):
                    st.text(jd_source)
                    
                # Filter tasks for this person in this month flexibly to handle name changes (e.g. Lê Ngọc Tú Uyên vs Lê Thị Tú Uyên)
                def is_same_person(db_name, target_name):
                    db_str = str(db_name).strip().lower()
                    tgt_str = str(target_name).strip().lower()
                    if db_str == tgt_str: return True
                    
                    # Match first and last name if exact match fails
                    tgt_parts = tgt_str.split()
                    if len(tgt_parts) >= 2:
                        return tgt_parts[0] in db_str and tgt_parts[-1] in db_str
                    return False
                    
                ai_tasks = display_df[
                    (display_df['NguoiChuTri'].apply(lambda x: is_same_person(x, ai_person))) & 
                    (display_df['Deadline'].apply(lambda x: x.strftime('%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else '') == ai_month)
                ]
                
                if ai_tasks.empty:
                    st.info(f"Không có công việc nào được đăng ký trong tháng {ai_month}.")
                else:
                    st.write(f"Tìm thấy **{len(ai_tasks)}** đầu công việc do nhân sự đăng ký trong tháng.")
                    
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
                        api_key = st.text_input("🔑 Nhập khóa API Gemini (API Key) của bạn để tiếp tục:", type="password")
                        
                    if not api_key:
                        st.warning("⚠️ Vui lòng cấu hình API Key hoặc nhập vào ô trống bên trên để sử dụng AI.")
                    else:
                        if st.button("🔍 CHẠY AI QUÉT ĐỘ PHỦ (GEMINI)", type="primary"):
                            with st.spinner("🧠 AI đang đọc JD và suy luận công việc... (Có thể mất 5-10 giây)"):
                                try:
                                    import google.generativeai as genai
                                    genai.configure(api_key=api_key, transport='rest')
                                    
                                    # Tự động dò model khả dụng cho API Key này
                                    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                                    model_name = 'gemini-3.6-flash'
                                    if 'models/gemini-3.6-flash' in valid_models:
                                        model_name = 'gemini-3.6-flash'
                                    elif 'models/gemini-1.5-flash' in valid_models:
                                        model_name = 'gemini-1.5-flash'
                                    elif 'models/gemini-pro' in valid_models:
                                        model_name = 'gemini-pro'
                                    elif valid_models:
                                        # Tránh chọn các model cũ hoặc bị deprecate nằm ở đầu danh sách
                                        model_name = valid_models[-1].replace('models/', '')
                                        
                                    model = genai.GenerativeModel(model_name)
                                    
                                    # Rút gọn danh sách công việc
                                    tasks_list = "\n".join([f"- {row['TenCongViec']}" for _, row in ai_tasks.iterrows()])
                                
                                    prompt = f"""
                                    Đóng vai một Giám đốc nhân sự cực kỳ tinh tế. 
                                    Dưới đây là Bản Mô tả công việc (JD) của nhân viên {ai_person}:
                                
                                    [BẢN MÔ TẢ CÔNG VIỆC]
                                    {jd_source}
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
                                            }}, ...
                                        ]
                                    }}
                                    """
                                
                                    import hashlib
                                    import os
                                    
                                    prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
                                    cache_file = f".ai_cache_{prompt_hash}.txt"
                                    
                                    if os.path.exists(cache_file):
                                        with open(cache_file, "r", encoding="utf-8") as f:
                                            raw_text = f.read()
                                    else:
                                        max_retries = 3
                                        for attempt in range(max_retries):
                                            try:
                                                response = model.generate_content(
                                                    prompt, 
                                                    generation_config={"temperature": 0.0},
                                                    request_options={"timeout": 60.0}
                                                )
                                                raw_text = response.text
                                                break
                                            except Exception as api_err:
                                                if attempt == max_retries - 1:
                                                    raise api_err
                                                import time
                                                time.sleep(4 * (attempt + 1))
                                                
                                        if raw_text:
                                            with open(cache_file, "w", encoding="utf-8") as f:
                                                f.write(raw_text)
                                
                                    import re
                                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                                    if json_match:
                                        res_json = json.loads(json_match.group())
                                    
                                        st.markdown("### 📊 KẾT QUẢ ĐỐI CHIẾU JD VÀ CÔNG VIỆC ĐĂNG KÝ")
                                    
                                        # Pie chart
                                        match_rate = res_json.get("ty_le_khop", 0)
                                        m_data = pd.DataFrame({
                                            "Phân loại": ["Khớp chuyên môn (JD)", "Công việc ngoài JD"],
                                            "Tỷ lệ": [match_rate, 100 - match_rate]
                                        })
                                        fig = px.pie(m_data, values='Tỷ lệ', names='Phân loại', color='Phân loại',
                                                     color_discrete_map={"Khớp chuyên môn (JD)": "#22c55e", "Công việc ngoài JD": "#f97316"},
                                                     title=f"Độ phủ JD Tháng {ai_month}", hole=0.4)
                                        st.plotly_chart(fig, use_container_width=True)
                                    
                                        # Table
                                        res_df = pd.DataFrame(res_json.get("chi_tiet", []))
                                        if not res_df.empty:
                                            # Format columns for display
                                            res_df = res_df.rename(columns={
                                                "ten_cong_viec": "Công việc",
                                                "phan_loai": "Đánh giá của AI",
                                                "nhan_xet": "Nhận xét chi tiết"
                                            })
                                            res_df.insert(0, 'STT', range(1, len(res_df) + 1))
                                        
                                            def color_ph(val):
                                                if "Khớp" in str(val):
                                                    return 'color: #166534; background-color: #dcfce7; font-weight: bold; border-radius: 4px;'
                                                else:
                                                    return 'color: #9a3412; background-color: #ffedd5; font-weight: bold; border-radius: 4px;'
                                                
                                            st.dataframe(res_df.style.map(color_ph, subset=['Đánh giá của AI']), use_container_width=True, hide_index=True)
                                    else:
                                        st.error("Lỗi: AI trả về kết quả không mong muốn. Vui lòng thử lại.")
                                        with st.expander("Dữ liệu thô AI trả về"):
                                            st.write(raw_text)
                                    
                                except ImportError:
                                    st.error("Chưa cài đặt thư viện `google-generativeai`. Vui lòng chạy `pip install google-generativeai`.")
                                except Exception as e:
                                    st.error(f"Lỗi hệ thống khi gọi AI: {e}")

