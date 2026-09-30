import json
import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add to menu_options
content = content.replace('"📖 Sổ tay Hướng dẫn"', '"📊 Quản trị BSC - KPI",\n        "📖 Sổ tay Hướng dẫn"')

# Add routing
routing_code = '''elif menu == "📊 Quản trị BSC - KPI":
    st.header("📊 Quản trị BSC - KPI (Local Demo)")
    st.info("Giao diện này đang sử dụng file kpi_data.json cục bộ để mô phỏng tính năng do chưa có Database Supabase.")
    import json
    import os
    kpi_file = 'kpi_data.json'
    
    if os.path.exists(kpi_file):
        with open(kpi_file, 'r', encoding='utf-8') as f:
            kpi_data = json.load(f)
    else:
        kpi_data = {'company_targets': [], 'department_targets': [], 'employee_targets': []}
        
    tab1, tab2 = st.tabs(["Mục tiêu Công ty", "Mục tiêu Phòng/Ban"])
    with tab1:
        st.subheader("Danh sách KPI Công ty (Kế hoạch Năm)")
        if not kpi_data['company_targets']:
            st.write("Chưa có mục tiêu nào.")
        else:
            st.table(kpi_data['company_targets'])
            
        with st.expander("Thêm Mục tiêu Công ty mới"):
            with st.form("add_comp_kpi"):
                t_name = st.text_input("Tên Mục tiêu")
                t_weight = st.number_input("Trọng số (%)", min_value=0, max_value=100, value=20)
                t_target = st.number_input("Chỉ tiêu giao (Kế hoạch)", min_value=0)
                if st.form_submit_button("Thêm"):
                    if t_name:
                        kpi_data['company_targets'].append({
                            'id': f'C-{len(kpi_data["company_targets"])+1}',
                            'name': t_name,
                            'weight': t_weight,
                            'target': t_target
                        })
                        with open(kpi_file, 'w', encoding='utf-8') as f:
                            json.dump(kpi_data, f, ensure_ascii=False, indent=4)
                        st.success("Đã thêm thành công!")
                        st.rerun()

    with tab2:
        st.subheader("Danh sách KPI Phòng ban")
        st.write("Đang phát triển...")
        
elif menu == "📖 Sổ tay Hướng dẫn":'''

content = content.replace('elif menu == "📖 Sổ tay Hướng dẫn":', routing_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched app.py successfully')
