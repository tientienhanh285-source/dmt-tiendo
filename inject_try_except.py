import glob

for filepath in glob.glob("views/3_Cap_Nhat.py"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Wrap the entire file in try-except
    lines = content.split('\n')
    new_lines = []
    imports = []
    rest = []
    
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
        else:
            rest.append(line)
            
    wrapped_rest = ["try:"] + ["    " + line for line in rest] + [
        "except Exception as e:",
        "    import traceback",
        "    st.error('LỖI CHI TIẾT ĐỂ BÁO CÁO IT:')",
        "    st.code(traceback.format_exc(), language='python')"
    ]
    
    new_content = "\n".join(imports + ["import traceback"] + wrapped_rest)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Injected try-except into 3_Cap_Nhat.py")
