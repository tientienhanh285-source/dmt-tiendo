import sys

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """            # --- 🚀 TÍNH NĂNG MỚI: TAGGING MỤC TIÊU QUÝ ---
            st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #1e3a8a; margin-bottom: 5px; margin-top: 15px;'>📌 Gắn với Mục tiêu Quý</p>", unsafe_allow_html=True)
            
            # Lấy danh sách Mục tiêu Quý
            current_year = str(today.year)
            year_key = f"{task_dept}_{current_year}"
            
            bsc_goals = []
            if "bsc_data" in st.session_state and "years" in st.session_state.bsc_data:
                if year_key in st.session_state.bsc_data["years"]:
                    bsc_goals = [f"[{g['quarter']}] {g['name']}" for g in st.session_state.bsc_data["years"][year_key]]
            
            if not bsc_goals:
                bsc_goals = ["Không có Mục tiêu Quý nào được thiết lập (Liên hệ Quản lý)"]
                
            task_moc_tien_do = st.selectbox("Chọn Mục tiêu Quý", ["Tự do / Không gắn mục tiêu"] + bsc_goals, label_visibility="collapsed")"""

replacement = """            task_moc_tien_do = "Tự do / Không gắn mục tiêu"
            if is_local:
                # --- 🚀 TÍNH NĂNG MỚI: TAGGING MỤC TIÊU QUÝ ---
                st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #1e3a8a; margin-bottom: 5px; margin-top: 15px;'>📌 Gắn với Mục tiêu Quý</p>", unsafe_allow_html=True)
                
                # Lấy danh sách Mục tiêu Quý
                current_year = str(today.year)
                year_key = f"{task_dept}_{current_year}"
                
                bsc_goals = []
                if "bsc_data" in st.session_state and "years" in st.session_state.bsc_data:
                    if year_key in st.session_state.bsc_data["years"]:
                        bsc_goals = [f"[{g['quarter']}] {g['name']}" for g in st.session_state.bsc_data["years"][year_key]]
                
                if not bsc_goals:
                    bsc_goals = ["Không có Mục tiêu Quý nào được thiết lập (Liên hệ Quản lý)"]
                    
                task_moc_tien_do = st.selectbox("Chọn Mục tiêu Quý", ["Tự do / Không gắn mục tiêu"] + bsc_goals, label_visibility="collapsed")"""

content = content.replace(target, replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied successfully!')
