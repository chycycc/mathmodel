# -*- coding: utf-8 -*-
import typst

with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 逐行测试单个公式
in_math = False
cur_math = []
math_start = 0

for idx, line in enumerate(lines, 1):
    if line.strip() == '$':
        if not in_math:
            in_math = True
            cur_math = []
            math_start = idx
        else:
            in_math = False
            formula = '\n'.join(cur_math)
            test_content = f"$ {formula} $\n"
            with open('paper/_tmp_m.typ', 'w', encoding='utf-8') as fp:
                fp.write(test_content)
            try:
                typst.compile('paper/_tmp_m.typ', output='paper/_tmp_m.pdf')
            except Exception as e:
                print(f"Error in formula at lines {math_start}-{idx}: {e}")
                print(f"Content:\n{formula}\n")

import os
if os.path.exists('paper/_tmp_m.typ'): os.remove('paper/_tmp_m.typ')
if os.path.exists('paper/_tmp_m.pdf'): os.remove('paper/_tmp_m.pdf')
