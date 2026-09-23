# -*- coding: utf-8 -*-
import typst

with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    content = f.read()

# 尝试编译整个文件
try:
    with open('paper/_tmp_full.typ', 'w', encoding='utf-8') as fp:
        fp.write(content)
    typst.compile('paper/_tmp_full.typ', output='paper/_tmp_full.pdf')
    print("Full file compiles OK!")
except Exception as e:
    print("Full file Error:", e)
