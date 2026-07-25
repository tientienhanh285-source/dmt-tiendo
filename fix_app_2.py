import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add column initialization to read_incoming_docs_db
docs_init = """    except Exception as e:
        pass
        df = pd.DataFrame(columns=required_cols)

    # Khởi tạo các cột thiếu để tránh KeyError
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
"""
content = re.sub(
    r'    except Exception as e:\n        pass\n        df = pd\.DataFrame\(columns=required_cols\)',
    docs_init,
    content
)

# 2. Add column initialization to read_gantt_db
gantt_init = """    except Exception as e:
        pass
        df = pd.DataFrame(columns=["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"])
        
    # Khởi tạo các cột thiếu
    for col in ["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"]:
        if col not in df.columns:
            df[col] = ""
"""
content = re.sub(
    r'    except Exception as e:\n        pass\n        df = pd\.DataFrame\(columns=\["ID", "TenDuAn", "TenCongViec", "GiaiDoan", "NgayBatDau", "NgayKetThuc", "PhanTramHoanThanh", "Milestone", "NgayCapNhat"\]\)',
    gantt_init,
    content
)


# 3. Add errors='coerce' to all pd.to_datetime
content = content.replace("pd.to_datetime(df['NgayBanHanh'])", "pd.to_datetime(df['NgayBanHanh'], errors='coerce')")
content = content.replace("pd.to_datetime(df['Deadline'])", "pd.to_datetime(df['Deadline'], errors='coerce')")
content = content.replace("pd.to_datetime(df['NgayCapNhat'])", "pd.to_datetime(df['NgayCapNhat'], errors='coerce')")
content = content.replace("pd.to_datetime(df['NgayBatDau'])", "pd.to_datetime(df['NgayBatDau'], errors='coerce')")
content = content.replace("pd.to_datetime(df['NgayKetThuc'])", "pd.to_datetime(df['NgayKetThuc'], errors='coerce')")

# 4. Gemini AI error handling - change st.error to st.warning
content = content.replace('st.error(f"❌ Có lỗi xảy ra trong quá trình gọi AI: {e}")', 'st.warning(f"❌ Có lỗi kết nối AI (Sai Key/Hết Quota): {e}")')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied fixes to app.py")
