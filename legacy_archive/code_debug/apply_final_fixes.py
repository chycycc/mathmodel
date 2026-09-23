# -*- coding: utf-8 -*-

# 1. 修复 5_problem1.typ
with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    c5 = f.read()
# 移除 block 5 中误加的 $
c5 = c5.replace("== 能耗单调性与最大安全载荷判定\n$\n对往返总能耗函数", "== 能耗单调性与最大安全载荷判定\n对往返总能耗函数")
c5 = c5.replace("关于有效载荷 $w$ 求一阶偏导数：\n$\n(diff E_(\"round\"))", "关于有效载荷 $w$ 求一阶偏导数：\n$\n(diff E_(\"round\"))")
# 替换 arg max 内部花括号
c5 = c5.replace("W_(\"safe\")^(max)(m, S_i) = min( W_(\"max\")(m), arg max_w { E_(\"round\")(m, w, S_i) <= 0.80 E_(\"avail\")(m) } )",
                "W_(\"safe\")^(max)(m, S_i) = min( W_(\"max\")(m), arg max_w ( E_(\"round\")(m, w, S_i) <= 0.80 E_(\"avail\")(m) ) )")
with open('paper/sections/5_problem1.typ', 'w', encoding='utf-8') as f:
    f.write(c5)

# 2. 修复 6_problem2.typ
with open('paper/sections/6_problem2.typ', 'r', encoding='utf-8') as f:
    c6 = f.read()
c6 = c6.replace("=== 动态剩余载荷递减能耗积分模型\n$\n当无人机沿航路", "=== 动态剩余载荷递减能耗积分模型\n当无人机沿航路")
c6 = c6.replace("设架次 $p$ 起飞时的初始总载质量为 $w_(p, 0) = sum_(k in cal(K)_p) w_k$。\n$\n对于航路中的", "设架次 $p$ 起飞时的初始总载质量为 $w_(p, 0) = sum_(k in cal(K)_p) w_k$。\n对于航路中的")
with open('paper/sections/6_problem2.typ', 'w', encoding='utf-8') as f:
    f.write(c6)

# 3. 修复 7_problem3.typ
with open('paper/sections/7_problem3.typ', 'r', encoding='utf-8') as f:
    c7 = f.read()
c7 = c7.replace("lon(alpha_j)", "\"lon\"(alpha_j)")
c7 = c7.replace("lat(alpha_j)", "\"lat\"(alpha_j)")
with open('paper/sections/7_problem3.typ', 'w', encoding='utf-8') as f:
    f.write(c7)

print("最终语法细节精确修复完成！")
