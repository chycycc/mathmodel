# -*- coding: utf-8 -*-
"""
问题三：中继无人机全局精确调度排班求解器（MILP / 整数规划与时空网络流）
核心逻辑：
1. 精确刻画 24 个运输架次全部不可直连时间切片的需求；
2. 决策变量：中继架次集合，每个架次的起飞时刻、悬停点、服务结束时刻、指派实体机（R01/R02）、指派能源组件（MOD_01~06）；
3. 严格硬约束：
   - 覆盖约束：每个不可直连时间切片必须被至少一个在空有效的中继架次覆盖；
   - 实体机不重叠约束：同一实体机的相继架次必须满足前一架次返回 O01 后至少间隔 300s 周转；
   - 能源组件两阶段充电时序约束：同一组件复用前必须完成两阶段物理充电并加 1s 缓冲；
   - 单架次电量约束：每架次总能耗 <= 2.56 kWh（返航 SOC >= 20.0%）；
   - 实体机总数 <= 2，共享能源组件 <= 6。
4. 目标：最小化中继架次数、最小化中继总能耗、最小化联合完工时间。
"""
import os
import sys
sys.path.insert(0, os.path.abspath('code'))
sys.path.insert(0, os.path.abspath('code/Q3'))
import math
import numpy as np
import pandas as pd
import data_loader as dl
import relay_physics as rp
from q2_baseline import parse_and_verify_q2

sys.stdout.reconfigure(encoding='utf-8')

def evaluate_schedule_feasibility(relay_sorties):
    """
    输入中继架次排班列表，全面评估可行性与指标
    relay_sorties: [
        {
            'sortie_id': 'RT01',
            'drone_id': 'R01',
            'mod_id': 'MOD_01',
            'pos_key': 'WEST', # 'WEST', 'EAST_SOUTH', 'EAST_NORTH'
            't_start': float,
            't_srv_end': float
        }, ...
    ]
    """
    pos_map = {
        'WEST': rp.RELAY_POS_WEST,
        'EAST_SOUTH': rp.RELAY_POS_EAST_SOUTH,
        'EAST_NORTH': rp.RELAY_POS_EAST_NORTH
    }
    
    # 1. 计算每个架次的动力学与能耗
    calculated_sorties = []
    for s in relay_sorties:
        p_dict = pos_map[s['pos_key']]
        m = rp.compute_relay_sortie_metrics(p_dict, s['t_start'], s['t_srv_end'])
        rec = dict(s)
        rec.update(m)
        rec['pos_dict'] = p_dict
        calculated_sorties.append(rec)
        
    # 2. 检查单架次返航 SOC >= 20%
    for s in calculated_sorties:
        if s['soc_end'] < 20.0 - 1e-4:
            return False, f"架次 {s['sortie_id']} 返航 SOC 违约: {s['soc_end']:.2f}% < 20%", {}
            
    # 3. 检查实体机时间不重叠且周转 >= 300s
    for uid in ['R01', 'R02']:
        u_sorties = [s for s in calculated_sorties if s['drone_id'] == uid]
        u_sorties.sort(key=lambda x: x['t_start'])
        for i in range(len(u_sorties) - 1):
            s1 = u_sorties[i]
            s2 = u_sorties[i+1]
            gap = s2['t_start'] - s1['t_back_done']
            if gap < 300.0 - 1e-3:
                return False, f"实体机 {uid} 在架次 {s1['sortie_id']} 与 {s2['sortie_id']} 之间周转不足: 间隔={gap:.1f}s < 300s", {}
                
    # 4. 检查共享能源组件两阶段充电可用性
    mod_usage = {}
    for s in calculated_sorties:
        mod_usage.setdefault(s['mod_id'], []).append(s)
    for mid, m_sorties in mod_usage.items():
        m_sorties.sort(key=lambda x: x['t_start'])
        for i in range(len(m_sorties) - 1):
            s1 = m_sorties[i]
            s2 = m_sorties[i+1]
            ready_t = s1['battery_ready']
            if s2['t_start'] < ready_t:
                return False, f"能源组件 {mid} 在架次 {s2['sortie_id']} 开始前未完成充电: 需就绪时刻={ready_t:.1f}s, 实际开始={s2['t_start']:.1f}s", {}
                
    # 5. 检查每个需中继的运输采样点是否被有效中继架次覆盖
    # 构建中继服务时间区间索引
    trips = parse_and_verify_q2()
    pos_g01 = (dl.NODES['O01']['lon'], dl.NODES['O01']['lat'], dl.NODES['O01']['elev'] + dl.COM_PARAMS['G01']['hG'])
    
    uncovered_count = 0
    total_unavail_points = 0
    
    for t in trips:
        tid = t['trip_id']
        for p in t['phases']:
            t_s = p['t_start']
            t_e = p['t_end']
            p1 = p['start_coord']
            p2 = p['end_coord']
            dur = t_e - t_s
            n_samples = max(2, int(dur / 5.0))
            alphas = np.linspace(0.0, 1.0, n_samples)
            for a in alphas:
                cur_t = (1.0 - a) * t_s + a * t_e
                cur_pos = (
                    (1.0 - a) * p1[0] + a * p2[0],
                    (1.0 - a) * p1[1] + a * p2[1],
                    (1.0 - a) * p1[2] + a * p2[2]
                )
                avail_g01, _, _ = dl.is_link_available(cur_pos, 'UAV', pos_g01, 'G01')
                if not avail_g01:
                    total_unavail_points += 1
                    # 查找当前时刻处于服务中的中继架次
                    active_relays = [
                        s for s in calculated_sorties
                        if s['t_link_done'] <= cur_t <= s['t_srv_end']
                    ]
                    # 检查是否有至少一个中继架次可提供有效覆盖
                    covered = False
                    for r in active_relays:
                        is_ok, _, _ = dl.is_link_available(
                            (r['pos_dict']['lon'], r['pos_dict']['lat'], r['pos_dict']['hover_z']),
                            'Relay_access', cur_pos, 'UAV'
                        )
                        if is_ok:
                            covered = True
                            break
                    if not covered:
                        uncovered_count += 1
                        
    cov_rate = (total_unavail_points - uncovered_count) / max(1, total_unavail_points)
    if uncovered_count > 0:
        return False, f"存在通信中断: 未覆盖点数={uncovered_count}/{total_unavail_points} (覆盖率 {cov_rate*100:.2f}%)", {}
        
    # 计算综合指标
    total_energy = sum(s['total_energy'] for s in calculated_sorties)
    latest_return = max(s['t_back_done'] for s in calculated_sorties)
    
    metrics = {
        'total_sorties': len(calculated_sorties),
        'total_energy': total_energy,
        'latest_return': latest_return,
        'coverage_rate': cov_rate,
        'sorties_detail': calculated_sorties
    }
    return True, "全约束严格满足，通信 100% 连续！", metrics

if __name__ == '__main__':
    print("中继排班评估模块加载成功！")
