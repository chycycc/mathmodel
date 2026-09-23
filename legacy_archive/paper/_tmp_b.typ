= 问题一的模型建立与求解

== 单点往返物理能耗模型与最大安全载荷推导

=== 航段飞行能耗理论建模
设机型为 $m$，目标受灾服务区为 $S_i$。单点往返飞行任务由去程重载航段 $("O01" -> S_i)$ 与返程空载航段 $(S_i -> "O01")$ 构成。
两点间球面水平大圆距离 $d("O01", S_i)$ 采用 Haversine 公式计算：
$
d = 2 R_("earth") arcsin(sqrt((sin((Delta phi)/2))^2 + cos(phi_1) cos(phi_2) (sin((Delta lambda)/2))^2))
$
其中 $R_("earth") = 6371.0"km"$。沿航线根据 30m DEM 栅格插值提取沿线最高地表海拔 $H_("max")$，确定巡航平飞海拔为 $H_("cruise") = H_("max") + 50"m"$。
起点 $"O01"$ 的作业高度为地表海拔 $Z("O01") = 127.7"m"$，受灾服务区 $S_i$ 的作业高度为悬停作业高程 $Z(S_i) = "Elev"(S_i) + 30"m"$。
去程垂直爬升高度为 $Delta h_1 = H_("cruise") - Z("O01")$，返程空载垂直爬升高度为 $Delta h_2 = H_("cruise") - Z(S_i)$。

设去程有效装载质量为 $w$。去程阶段水平巡航等效航程 $R(m, w)$ 随有效载荷线性递减：
$
R(m, w) = R_0(m) - w / (W_("max")(m)) (R_0(m) - R_("full")(m))
$
去程总能耗包含水平巡航耗电与重力势能爬升耗电：
$
E_("out")(m, w) = d / (R(m, w)) E_("avail")(m) + ((M_0(m) + w) g Delta h_1) / (eta_("climb") dot 3.6 times 10^6) quad ("kWh")
$
返程时货物已全额卸载，装载质量 $w = 0$，空载返航能耗为：
$
E_("back")(m) = d / (R_0(m)) E_("avail")(m) + (M_0(m) g Delta h_2) / (eta_("climb") dot 3.6 times 10^6) quad ("kWh")
$
单点往返累计总飞行能耗为两阶段之和：
$
E_("round")(m, w, S_i) = E_("out")(m, w) + E_("back")(m)
$

=== 能耗单调性与最大安全载荷判定
$
对往返总能耗函数 $E_("round")(m, w, S_i)$ 关于有效载荷 $w$ 求一阶偏导数：
$
(diff E_("round")) / (diff w) = (d dot E_("avail")(m)) / (R^2(m, w)) dot (R_0(m) - R_("full")(m)) / (W_("max")(m)) + (g Delta h_1) / (eta_("climb") dot 3.6 times 10^6)
$
因基准空载航程 $R_0(m) > R_("full")(m)$，且爬升高度 $Delta h_1 >= 0$、机械电能转换效率 $eta_("climb") > 0$，导数恒满足：
$
(diff E_("round")) / (diff w) > 0
$
该数学性质严格证明了*单点往返总能耗关于有效装载质量严格单调递增*。
根据题目防范风险的安全余量规则，无人机返航降落 $"O01"$ 时的剩余电量荷电状态（SOC）不得低于 $eta = 20\%$，即：
$
E_("round")(m, w, S_i) <= (1 - eta) E_("avail")(m) = 0.80 E_("avail")(m)
$
结合机体结构标称载重上限 $W_("max")(m)$，各机型在服务区 $S_i$ 的最大安全有效载荷可由下式唯一确定：
$
W_("safe")^(max)(m, S_i) = min( W_("max")(m), arg max_w { E_("round")(m, w, S_i) <= 0.80 E_("avail")(m) } )
$
鉴于函数的单调连续性，采用高精度二分搜索算法（计算收敛判据 $|E - 0.80 E_("avail")| < 10^(-5)"kWh"$）求解。