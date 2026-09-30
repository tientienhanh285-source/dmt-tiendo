import re

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Modify format_task_option in "Cập nhật tiến độ"
        old_format_task = """            def format_task_option(task_id):
                row = df[df['ID'] == task_id].iloc[0]
                pic = row.get('NguoiChuTri', 'Chưa rõ')
                return f"{row['TenCongViec']} - Phụ trách: {pic}"
"""
        new_format_task = """            def format_task_option(task_id):
                row = df[df['ID'] == task_id].iloc[0]
                pic = row.get('NguoiChuTri', 'Chưa rõ')
                prefix = "🌟 [QUẢN LÝ GIAO] " if ("[Mục tiêu" in str(row.get('GiaiTrinhDeXuat', ''))) else ""
                return f"{prefix}{row['TenCongViec']} - Phụ trách: {pic}"
"""
        content = content.replace(old_format_task, new_format_task)
        
        # 2. Modify df_display['Tên công việc'] in Bảng theo dõi tiến độ
        old_df_cols = """        ordered_cols = ['Ngày bắt đầu', 'Hạn chót', 'Tiến độ', 'Trạng thái', 'Người thực hiện', 'Phòng ban', 'Dự án / Hạng mục', 'Tên công việc']
        df_display = df_display[ordered_cols]
"""
        new_df_cols = """        def add_prefix_to_name(row):
            prefix = "🌟 [QUẢN LÝ GIAO] " if ("[Mục tiêu" in str(row.get('GiaiTrinhDeXuat', ''))) else ""
            return f"{prefix}{row['TenCongViec']}"
        df_display['Tên công việc'] = table_df.apply(add_prefix_to_name, axis=1)

        ordered_cols = ['Ngày bắt đầu', 'Hạn chót', 'Tiến độ', 'Trạng thái', 'Người thực hiện', 'Phòng ban', 'Dự án / Hạng mục', 'Tên công việc']
        df_display = df_display[ordered_cols]
"""
        content = content.replace(old_df_cols, new_df_cols)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Patched highlighting successfully!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
