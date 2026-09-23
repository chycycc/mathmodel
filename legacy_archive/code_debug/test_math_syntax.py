# -*- coding: utf-8 -*-
import typst

# 测试三行公式 vs 单行公式
s1 = """
$
d = 2 R_("earth")
$
"""

s2 = """
$ d = 2 R_("earth") $
"""

with open('paper/_s1.typ', 'w', encoding='utf-8') as f: f.write(s1)
try:
    typst.compile('paper/_s1.typ', output='paper/_s1.pdf')
    print("s1 (three lines) OK!")
except Exception as e:
    print("s1 Error:", e)

with open('paper/_s2.typ', 'w', encoding='utf-8') as f: f.write(s2)
try:
    typst.compile('paper/_s2.typ', output='paper/_s2.pdf')
    print("s2 (single line) OK!")
except Exception as e:
    print("s2 Error:", e)
