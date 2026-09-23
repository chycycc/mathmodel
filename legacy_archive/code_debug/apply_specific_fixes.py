# -*- coding: utf-8 -*-
"""
精细修复 Typst 4个文件中的特定语法细节
"""

# 1. 修复 4_symbols.typ 中的错误独立公式包裹
with open('paper/sections/4_symbols.typ', 'r', encoding='utf-8') as f:
    c4 = f.read()
c4 = c4.replace("$\n[$W_(\"safe\")^(max)(m, S_i)$], [机型 $m$ 在服务区 $S_i$ 单点往返的最大安全载荷], [$\"kg\"$],\n$", "    [$W_(\"safe\")^(max)(m, S_i)$], [机型 $m$ 在服务区 $S_i$ 单点往返的最大安全载荷], [$\"kg\"$],")
with open('paper/sections/4_symbols.typ', 'w', encoding='utf-8') as f:
    f.write(c4)

# 2. 修复 5_problem1.typ 中的双美元符号与花括号
with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    c5 = f.read()
c5 = c5.replace("$\n$\n(diff", "$\n(diff")
c5 = c5.replace("W_(\"safe\")^(max)(m, S_i) = min { W_(\"max\")(m), arg max_w { E_(\"round\")(m, w, S_i) <= 0.80 E_(\"avail\")(m) } }",
                'W_("safe")^(max)(m, S_i) = min( W_("max")(m), arg max_w { E_("round")(m, w, S_i) <= 0.80 E_("avail")(m) } )')
with open('paper/sections/5_problem1.typ', 'w', encoding='utf-8') as f:
    f.write(c5)

# 3. 修复 6_problem2.typ 中的 cases 语法
with open('paper/sections/6_problem2.typ', 'r', encoding='utf-8') as f:
    c6 = f.read()
cases_old = """    Delta t_("charge") = cases(
     ((0.90 - "SOC") / 0.90 times 0.65 + 0.35) T_("full")(m)\\, & "SOC" < 0.90,
     ((1.00 - "SOC") / 0.10 times 0.35) T_("full")(m)\\, & "SOC" >= 0.90
   )"""
cases_new = """    Delta t_("charge") = cases(
      ((0.90 - "SOC") / 0.90 times 0.65 + 0.35) T_("full")(m) quad "if SOC" < 0.90,
      ((1.00 - "SOC") / 0.10 times 0.35) T_("full")(m) quad "if SOC" >= 0.90,
    )"""
c6 = c6.replace(cases_old, cases_new)
with open('paper/sections/6_problem2.typ', 'w', encoding='utf-8') as f:
    f.write(c6)

# 4. 修复 7_problem3.typ 中的 mathbf
with open('paper/sections/7_problem3.typ', 'r', encoding='utf-8') as f:
    c7 = f.read()
c7 = c7.replace("mathbf(", "bold(")
with open('paper/sections/7_problem3.typ', 'w', encoding='utf-8') as f:
    f.write(c7)

print("精细修复完成！")
