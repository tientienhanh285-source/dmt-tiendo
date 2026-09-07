import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """    # 1. Filter cycle dropdown
    cycle_filter = st.selectbox(
        "📅 Lọc theo Chu kỳ theo dõi",
        ["Tất cả chu kỳ", "Hàng tuần", "Hàng tháng", "Hàng quý", "Theo dự án / Tự do"],
        index=0
    )
    
    dash_df = display_df.copy()
    if cycle_filter != "Tất cả chu kỳ":
        dash_df = dash_df[dash_df['ChuKyTheoDoi'] == cycle_filter]"""

replace1 = """    dash_df = display_df.copy()"""


target2 = """    if alert_list:
        alert_df_show = pd.DataFrame(alert_list).sort_values(by=["Urgency", "Deadline"])
        st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(alert_df_show)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")
        alert_data = []
        for _, row in alert_df_show.iterrows():
            alert_data.append({
                "Ban phụ trách": row['PhongBan'],
                "Người phụ trách": row['NguoiChuTri'],
                "Dự án / Hạng mục": row['TenDuAn'],
                "Tên công việc": row['TenCongViec'],
                "Trạng thái thực tế": row['Badge']
            })
        st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        st.markdown("---")"""

replace2 = """    if alert_list:
        alert_df_show = pd.DataFrame(alert_list).sort_values(by=["Urgency", "Deadline"])
        st.error(f"🚨 **CẢNH BÁO: DỰ ÁN CÓ {len(alert_df_show)} HẠNG MỤC CẦN LƯU Ý (TRỄ HẠN / SẮP ĐẾN HẠN)**")"""

count = 0
if target1 in content:
    content = content.replace(target1, replace1)
    count += 1
if target2 in content:
    content = content.replace(target2, replace2)
    count += 1

if count > 0:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Replaced {count} targets successfully')
else:
    print('Targets not found')
