# -*- coding: utf-8 -*-
# 1. 替换 5_problem1.typ 中的 diff 为 partial
with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    c5 = f.read()
c5 = c5.replace("diff", "partial")
with open('paper/sections/5_problem1.typ', 'w', encoding='utf-8') as f:
    f.write(c5)

# 2. 替换 7_problem3.typ 中的 implies 为 =>
with open('paper/sections/7_problem3.typ', 'r', encoding='utf-8') as f:
    c7 = f.read()
c7 = c7.replace("implies", "=>")
with open('paper/sections/7_problem3.typ', 'w', encoding='utf-8') as f:
    f.write(c7)

print("偏导与箭头符号替换完成！")
