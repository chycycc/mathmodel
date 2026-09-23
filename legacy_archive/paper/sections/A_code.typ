#set text(font: ("SimSun", "Times New Roman"), size: 10pt)
#set par(first-line-indent: 0pt)

本文所有计算与图表均基于 Python 3.12 独立复现，核心算法源程序已归档于 `code/` 目录。现将关键模块源代码节选列示如下：

== 附录 A.1 空间光线追踪与 DEM 视距遮挡判别核心代码 (data_loader.py)

```python
# -*- coding: utf-8 -*-
import math
import numpy as np

def check_line_of_sight(pos1, pos2):
    """
    基于三维空间射线追踪 (Ray-Casting) 判定两通信端点间是否存在山体遮挡
    pos1: (lon, lat, alt_m) 发射天线端点三维坐标
    pos2: (lon, lat, alt_m) 接收天线端点三维坐标
    返回: True 为视距畅通 (LOS), False 为存在山体阻断 (NLOS)
    """
    lon1, lat1, z1 = pos1
    lon2, lat2, z2 = pos2
    # 计算两点间的水平球面距离
    horiz_dist = haversine_distance(lon1, lat1, lon2, lat2)
    # 按每 20 米一步进行离散空间射线步进采样
    steps = max(20, int(horiz_dist / 20.0))
    alphas = np.linspace(0.0, 1.0, steps)
    
    for a in alphas[1:-1]:  # 遍历中间路径采样点
        cur_lon = (1.0 - a) * lon1 + a * lon2
        cur_lat = (1.0 - a) * lat1 + a * lat2
        cur_z = (1.0 - a) * z1 + a * z2  # 视线高度
        dem_z = get_dem_elevation(cur_lon, cur_lat)  # 双线性插值查询 DEM 地表海拔
        if cur_z <= dem_z:
            return False  # 视线穿透山体，发生阻断
    return True
```

== 附录 A.2 两阶段电池充电时钟推进核心模型 (data_loader.py)

```python
def compute_recharge_time(m_type, remaining_soc):
    """
    两阶段动力电池物理等效充电时间计算
    m_type: 机型编号 ('A', 'B', 'C', 'R')
    remaining_soc: 返航剩余电量荷电状态 (0.2 ~ 1.0)
    返回: 充至 100% 满电所需的等效时间 (秒)
    """
    t_full = DRONE_PARAMS[m_type]['full_charge_time']
    if remaining_soc >= 1.0:
        return 0.0
    # 第一阶段：恒流快速充电阶段 ($SOC < 90%$，耗时占满充时间的 65%)
    if remaining_soc < 0.90:
        frac = ((0.90 - remaining_soc) / 0.90) * 0.65 + 0.35
    # 第二阶段：恒压慢速涓流阶段 (SOC >= 90%，耗时占满充时间的 35%)
    else:
        frac = ((1.0 - remaining_soc) / 0.10) * 0.35
    return frac * t_full
```

== 附录 A.3 问题二时空网络自适应大邻域搜索核心流程 (problem2.py)

```python
def solve_q2_alns():
    """
    考虑实体无人机周转与电池两阶段充电推进的自适应大邻域搜索算法
    """
    # 1. 优先级启发式初始化可行解
    current_solution = construct_priority_initial_solution()
    best_solution = copy.deepcopy(current_solution)
    
    # 2. ALNS 自适应主迭代循环
    for iteration in range(MAX_ITERATIONS):
        # 依据轮盘赌概率选择破坏算子 (Shaw 空间破坏 / 紧迫度破坏)
        destroyed_routes, removed_boxes = apply_destroy_operator(current_solution)
        # 采用多重遗憾值算子 (Regret-2 / Regret-3) 执行时空修复插入
        repaired_solution = apply_repair_operator(destroyed_routes, removed_boxes)
        
        # 3. 推进两阶段电池充电时钟与机体周转状态机
        feasible, makespan, energy = evaluate_physical_state_machine(repaired_solution)
        
        if feasible:
            if makespan < best_solution.makespan:
                best_solution = copy.deepcopy(repaired_solution)
                current_solution = copy.deepcopy(repaired_solution)
    return best_solution
```