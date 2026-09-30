import re

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        demo_data_injection = """
        if "NhanSu" in df.columns and "config_json" in df.columns:
            rows = df[df["NhanSu"] == "APP_BSC_CONFIG"]
            if not rows.empty:
                json_str = rows.iloc[0]["config_json"]
                data = json.loads(json_str)
                for key in ["years", "quarters", "months"]:
                    if key not in data:
                        data[key] = {}
                        
                # Inject DEMO data if HCNS has no data
                demo_year_key = "Ban Hành chính Nhân sự_2026"
                demo_month_key = "Ban Hành chính Nhân sự_2026_10"
                if demo_year_key not in data["years"]:
                    data["years"][demo_year_key] = [
                        {"name": "Kiện toàn bộ hồ sơ PCCC, diễn tập, thẩm định định kỳ", "quarter": "Cả năm"},
                        {"name": "Xây dựng hệ thống cấp bậc chức danh, KPI toàn hệ thống (BCS)", "quarter": "Q4"},
                        {"name": "Rà soát toàn bộ hồ sơ Pháp lý - Cty CP Đầu tư ĐNMT", "quarter": "Q1"}
                    ]
                if demo_month_key not in data["months"]:
                    data["months"][demo_month_key] = [
                        {"name": "Hoàn thành quy trình tự kiểm tra PCCC cơ sở", "weight": 20},
                        {"name": "Thành lập đội KPIs Công ty và lập kế hoạch khung năng lực", "weight": 40},
                        {"name": "Rà soát đánh số danh mục Hồ sơ pháp lý Công ty BT1-BT5", "weight": 30}
                    ]
                return data
"""
        # Find the block inside load_bsc_config:
        old_block = """        if "NhanSu" in df.columns and "config_json" in df.columns:
            rows = df[df["NhanSu"] == "APP_BSC_CONFIG"]
            if not rows.empty:
                json_str = rows.iloc[0]["config_json"]
                data = json.loads(json_str)
                for key in ["years", "quarters", "months"]:
                    if key not in data:
                        data[key] = {}
                return data"""
                
        content = content.replace(old_block, demo_data_injection)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Injected DEMO data successfully!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
