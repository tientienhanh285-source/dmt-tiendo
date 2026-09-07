import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "u_cycle = st.selectbox(\"Chu kỳ theo dõi\"" in line:
        indent = line.split("u_cycle")[0]
        new_lines.append(indent + "u_cycle = current_cycle\n")
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done")
