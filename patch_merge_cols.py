import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_ub = False
for i, line in enumerate(lines):
    if 'col_ub1, col_ub2 = st.columns(2)' in line:
        in_ub = True
        continue
    if in_ub:
        if 'with col_ub1:' in line:
            new_lines.append('                    st.markdown("<br>", unsafe_allow_html=True)\n')
        elif 'with col_ub2:' in line:
            new_lines.append('                    st.markdown("<br>", unsafe_allow_html=True)\n')
        elif 'btn_save, btn_del = st.columns([3, 2])' in line:
            in_ub = False
            new_lines.append(line)
        else:
            # We need to change the indent level because we are removing `with col_ub1:` and `with col_ub2:`
            # Wait, no, we are moving them under `col_u2` which has the SAME indent level as `col_ub1`!
            # `col_ub1` block is indented 16 spaces.
            # The content inside `with col_ub1:` is indented 20 spaces.
            # We want to dedent it by 4 spaces.
            if line.startswith('                    '):
                new_lines.append(line[4:])
            elif line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append(line)
    else:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Merged col_ub into col_u2")
