# -*- coding: utf-8 -*-
with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    c = f.read()

# 替换 Haversine 公式
c = c.replace("sin^2((Delta phi)/2)", "(sin((Delta phi)/2))^2")
c = c.replace("sin^2((Delta lambda)/2)", "(sin((Delta lambda)/2))^2")
c = c.replace("cos phi_1 cos phi_2", "cos(phi_1) cos(phi_2)")

with open('paper/sections/5_problem1.typ', 'w', encoding='utf-8') as f:
    f.write(c)

print("5_problem1.typ 替换完成！")
