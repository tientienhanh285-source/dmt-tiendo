import os
import codecs

def patch_file(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as f:
        content = f.read()
    
    # 5_Danh_Gia_KPI.py Line 154
    content = content.replace(
        "group['TrangThai'] in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']",
        "group['TrangThai'].isin(['Hoàn thành', 'Hoàn thành (Trễ hạn)'])"
    )
    
    # 2_Tien_Do.py Line 87
    content = content.replace(
        "dash_df['TrangThai'] in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']",
        "dash_df['TrangThai'].isin(['Hoàn thành', 'Hoàn thành (Trễ hạn)'])"
    )
    
    # 2_Tien_Do.py Line 404
    content = content.replace(
        "gb_df['TrangThai'] in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']",
        "gb_df['TrangThai'].isin(['Hoàn thành', 'Hoàn thành (Trễ hạn)'])"
    )
    
    # 1_Tong_Quan.py Line 155
    content = content.replace(
        "table_df['TrangThai'] in ['Hoàn thành', 'Hoàn thành (Trễ hạn)']",
        "table_df['TrangThai'].isin(['Hoàn thành', 'Hoàn thành (Trễ hạn)'])"
    )
    
    with codecs.open(file_path, 'w', 'utf-8') as f:
        f.write(content)

for filename in ["views/1_Tong_Quan.py", "views/2_Tien_Do.py", "views/5_Danh_Gia_KPI.py"]:
    fpath = os.path.join(r"c:\Users\Admin\Desktop\AG\Theodoitiendo", filename)
    patch_file(fpath)

print("Patched all pandas 'in' Series errors!")
