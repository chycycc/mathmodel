import sympy as sp

# 定义符号
w = sp.Symbol('w', positive=True) # 载荷
d = sp.Symbol('d', positive=True) # 单程水平距离
E_avail = sp.Symbol('E_avail', positive=True) # 电池可用能量
R_0 = sp.Symbol('R_0', positive=True) # 空载标准航程
R_full = sp.Symbol('R_full', positive=True) # 满载标准航程
W_max = sp.Symbol('W_max', positive=True) # 最大载重量
M_0 = sp.Symbol('M_0', positive=True) # 空机质量
g = sp.Symbol('g', positive=True) # 重力加速度
Delta_h1 = sp.Symbol('Delta_h1', positive=True) # 去程爬升高度
eta_climb = sp.Symbol('eta_climb', positive=True) # 爬升效率

# 等效航程函数 R(w) = R_0 - (R_0 - R_full) * (w / W_max)**(3/2)
R_w = R_0 - (R_0 - R_full) * (w / W_max)**(sp.Rational(3, 2))

# 水平巡航能耗 E_cruise = (d / R_w) * E_avail
E_cruise = (d / R_w) * E_avail

# 爬升附加能耗 E_climb = (M_0 + w) * g * Delta_h1 / (eta_climb * 3.6e6)
# 常数 C_climb = g * Delta_h1 / (eta_climb * 3600000)
C_climb = sp.Symbol('C_climb', positive=True)
E_climb = (M_0 + w) * C_climb

# 去程总能耗 E_out(w) = E_cruise + E_climb
E_out = E_cruise + E_climb

# 返程为 0 载荷，为常数，导数为 0
# 求关于 w 的一阶偏导数
dE_dw = sp.diff(E_out, w)

print("=== 一阶偏导 dE/dw ===")
sp.pprint(dE_dw)

print("\n=== LaTeX/Typst 表达式 ===")
print("LaTeX:", sp.latex(dE_dw))
