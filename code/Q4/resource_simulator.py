# -*- coding: utf-8 -*-
"""
问题四：任务组独立执行资源配置仿真评估器
功能：
针对给定的服务区分组方案，核算各任务组在组间资源绝对隔离的前提下，
独立执行所需的各类装备峰值并发占用与库存缺口：
1. 运输无人机（A型、B型、C型实体机）
2. 共享电池（A型、B型、C型共享电池组，严格执行两阶段等效充电模型）
3. 中继无人机（R型实体机，周转时间 >= 300s）
4. 共享能源组件（MOD组件，两阶段充电模型）
"""
import os
import sys
import math
import numpy as np
import pandas as pd

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIR))
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code'))
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code', 'Q3'))

import data_loader as dl
import relay_physics as rp

sys.stdout.reconfigure(encoding='utf-8')

# 现有库存常数
EXISTING_INVENTORY = {
    'drones': {'A': 4, 'B': 2, 'C': 2, 'R': 2},
    'batteries': {'A': 6, 'B': 4, 'C': 4, 'R': 6} # R 的电池即为能源组件
}

def simulate_group_transport_resources(group_trips):
    """
    输入该任务组的运输架次列表，模拟该组独立执行所需的运输机和电池数量
    group_trips: list of dict, 每个 dict 包含：
      'm_type': 'A'/'B'/'C',
      't_start': float,
      't_back': float,
      'energy': float,
      'soc_end': float,
      'charge_time': float
    返回: 各机型所需实体机数、各机型所需电池组数、实体机时序、电池时序
    """
    if len(group_trips) == 0:
        return {'A': 0, 'B': 0, 'C': 0}, {'A': 0, 'B': 0, 'C': 0}
        
    needed_drones = {'A': 0, 'B': 0, 'C': 0}
    needed_batts = {'A': 0, 'B': 0, 'C': 0}
    
    for m in ['A', 'B', 'C']:
        m_trips = [t for t in group_trips if t['m_type'] == m]
        if len(m_trips) == 0:
            continue
            
        m_trips.sort(key=lambda x: x['t_start'])
        
        # 1. 计算实体机最少需求（基于时间区间图着色/贪心区间调度）
        drone_free_times = []
        for trip in m_trips:
            t_s = trip['t_start']
            t_e = trip['t_back']
            # 寻找最早可用的实体机
            assigned = False
            for idx in range(len(drone_free_times)):
                if drone_free_times[idx] <= t_s + 1e-4:
                    drone_free_times[idx] = t_e
                    assigned = True
                    break
            if not assigned:
                drone_free_times.append(t_e)
        needed_drones[m] = len(drone_free_times)
        
        # 2. 计算电池最少需求（返航后需充至 100% 并加 1s 换电缓冲方可给后续架次使用）
        batt_ready_times = []
        for trip in m_trips:
            t_s = trip['t_start']
            # 电池在返航后进行两阶段充电
            # 充电时间依据两阶段物理充电模型
            charge_dur = dl.compute_recharge_time(m, trip['soc_end'] / 100.0)
            t_ready = trip['t_back'] + charge_dur + 1.0
            
            assigned = False
            for idx in range(len(batt_ready_times)):
                if batt_ready_times[idx] <= t_s + 1e-4:
                    batt_ready_times[idx] = t_ready
                    assigned = True
                    break
            if not assigned:
                batt_ready_times.append(t_ready)
        needed_batts[m] = len(batt_ready_times)
        
    return needed_drones, needed_batts

def simulate_group_relay_resources(group_relay_sorties):
    """
    输入该任务组分配的中继架次列表，计算该组独立执行所需的中继机和能源组件数量
    group_relay_sorties: list of dict, 每个 dict 包含：
      't_start': float,
      't_back': float,
      'soc_end': float
    """
    if len(group_relay_sorties) == 0:
        return 0, 0
        
    sorties = sorted(group_relay_sorties, key=lambda x: x['t_start'])
    
    # 实体中继机需求（需满足周转 >= 300s）
    relay_free_times = []
    for s in sorties:
        t_s = s['t_start']
        t_ready = s['t_back'] + 300.0 # 实体机需 300s 周转
        assigned = False
        for idx in range(len(relay_free_times)):
            if relay_free_times[idx] <= t_s + 1e-4:
                relay_free_times[idx] = t_ready
                assigned = True
                break
        if not assigned:
            relay_free_times.append(t_ready)
            
    # 能源组件需求（两阶段充电后就绪）
    mod_ready_times = []
    for s in sorties:
        t_s = s['t_start']
        charge_dur = dl.compute_recharge_time('R', s['soc_end'] / 100.0)
        t_mod_ready = s['t_back'] + charge_dur + 1.0
        assigned = False
        for idx in range(len(mod_ready_times)):
            if mod_ready_times[idx] <= t_s + 1e-4:
                mod_ready_times[idx] = t_mod_ready
                assigned = True
                break
        if not assigned:
            mod_ready_times.append(t_mod_ready)
            
    return len(relay_free_times), len(mod_ready_times)

if __name__ == '__main__':
    print("资源仿真核算模块加载成功！")
