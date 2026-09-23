# -*- coding: utf-8 -*-
import typst

with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1, len(lines) + 1):
    test_content = ''.join(lines[:i])
    with open('paper/_tmp_p.typ', 'w', encoding='utf-8') as fp:
        fp.write(test_content)
    try:
        typst.compile('paper/_tmp_p.typ', output='paper/_tmp_p.pdf')
    except Exception as e:
        if 'unclosed delimiter' in str(e):
            print(f"Error when adding line {i}: {lines[i-1].strip()}")
            break
