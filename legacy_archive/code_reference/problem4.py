# -*- coding: utf-8 -*-
"""
问题四：救援任务分区与独立资源配置优化方案
核心内容：
1. 以问题三联合调度方案为基础，设计 K=2 和 K=3 的任务分区；
2. 保证多点串联航线（S002 与 S004）归入同一任务组，满足硬约束；
3. 基于时域并发扫描法，精确核算各分区独立执行时的资源需求：
   - 运输无人机峰值并发数（A型、B型、C型）
   - 共享电池组周转峰值需求（含两阶段充电占用，A型、B型、C型）
   - 中继无人机与能源组件峰值需求
4. 综合对比 K=2 与 K=3 的资源配置规模、冗余度、组间均衡性及现有库存缺口；
5. 生成 results/Q4_分区配置.csv 并输出详尽的量化对比报告。
"""

import sys
import os
sys.path.insert(0, 'code')
import math
import numpy as np
import pandas as pd
import data_loader as dl

# 1. 定义分区方案
# K=2 方案
PARTITIONS_K2 = {
    'G1': ['S001', 'S003', 'S006', 'S007', 'S011', 'S015'],
    'G2': ['S002', 'S004', 'S005', 'S008', 'S009', 'S010', 'S012', 'S013', 'S014']
}

# K=3 方案
PARTITIONS_K3 = {
    'G1': ['S003', 'S006', 'S007', 'S015'],
    'G2': ['S001', 'S002', 'S004', 'S005', 'S008', 'S011'],
    'G3': ['S009', 'S010', 'S012', 'S013', 'S014']
}

def analyze_group_resources(group_svcs, df_q2_trips, df_q3_relays, df_q3_comm):
    """
    计算分配给指定服务区列表的任务子集，在独立执行时所需的各类硬件资源峰值。
    """
    # 1. 筛选属于该任务组的运输架次
    group_trips = []
    for idx, r in df_q2_trips.iterrows():
        svcs = r['访问服务区顺序'].split('->')
        # 只要航线访问了该组的服务区，就归入该组（由于 S002 & S004 必须同组，不存在跨组分裂）
        if any(s in group_svcs for s in svcs):
            group_trips.append(r)
    df_gt = pd.DataFrame(group_trips)
    
    if len(df_gt) == 0:
        return {
            'n_A': 0, 'n_B': 0, 'n_C': 0,
            'b_A': 0, 'b_B': 0, 'b_C': 0,
            'n_R': 0, 'b_MOD': 0,
            'trips_count': 0
        }
        
    # 2. 统计运输无人机峰值并发数（起飞准备至返回O01）
    # 每个架次的时间区间: [开始时刻, 返回O01时刻]
    def get_max_concurrent(intervals):
        if not intervals:
            return 0
        events = []
        for t_start, t_end in intervals:
            events.append((t_start, 1))
            events.append((t_end, -1))
        events.sort(key=lambda x: (x[0], x[1]))  # 结束优先或开始优先
        cur = 0
        max_c = 0
        for t, val in events:
            cur += val
            max_c = max(max_c, cur)
        return max_c

    # 分机型统计无人机并发
    drone_demands = {'A': 0, 'B': 0, 'C': 0}
    for m in ['A', 'B', 'C']:
        sub = df_gt[df_gt['机型编号'] == m]
        intervals = list(zip(sub['开始时刻（s）'], sub['返回O01时刻（s）']))
        drone_demands[m] = get_max_concurrent(intervals)
        
    # 3. 统计电池组峰值并发数（飞行时间 + 两阶段充电时间）
    # 电池被占用区间: [开始时刻, 返回O01时刻 + 充电时间]
    battery_demands = {'A': 0, 'B': 0, 'C': 0}
    for m in ['A', 'B', 'C']:
        sub = df_gt[df_gt['机型编号'] == m]
        intervals = []
        for _, r in sub.iterrows():
            t_start = r['开始时刻（s）']
            t_end = r['返回O01时刻（s）']
            e_trip = r['架次能耗（kWh）']
            e_avail = dl.DRONE_PARAMS[m]['e_avail']
            rem_soc = 1.0 - e_trip / e_avail
            t_charge = dl.compute_recharge_time(m, rem_soc)
            t_bat_free = t_end + t_charge
            intervals.append((t_start, t_bat_free))
        battery_demands[m] = get_max_concurrent(intervals)
        
    # 4. 统计中继无人机与能源组件并发
    # 找到为该组运输架次提供中继保障的中继架次
    trip_ids = set(df_gt['架次编号'])
    comm_sub = df_q3_comm[df_q3_comm['运输架次编号'].isin(trip_ids)]
    relay_ids = set(comm_sub[comm_sub['保障方式'] == '中继']['中继架次编号'].dropna().unique())
    
    # 筛选对应的中继架次
    relay_sub = df_q3_relays[df_q3_relays['中继架次编号'].isin(relay_ids)]
    
    # 中继无人机并发
    r_intervals = list(zip(relay_sub['开始时刻（s）'], relay_sub['返回O01时刻（s）']))
    n_relay_drones = get_max_concurrent(r_intervals)
    
    # 中继能源组件并发（含充电时间）
    mod_intervals = []
    for _, r in relay_sub.iterrows():
        t_start = r['开始时刻（s）']
        t_end = r['返回O01时刻（s）']
        e_trip = r['架次能耗（kWh）']
        rem_soc = 1.0 - e_trip / dl.DRONE_PARAMS['R']['e_avail']
        t_charge = dl.compute_recharge_time('R', rem_soc)
        mod_intervals.append((t_start, t_end + t_charge))
    n_mod_components = get_max_concurrent(mod_intervals)
    
    return {
        'n_A': drone_demands['A'],
        'n_B': drone_demands['B'],
        'n_C': drone_demands['C'],
        'b_A': battery_demands['A'],
        'b_B': battery_demands['B'],
        'b_C': battery_demands['C'],
        'n_R': n_relay_drones,
        'b_MOD': n_mod_components,
        'trips_count': len(df_gt),
        'relay_trips': list(relay_ids)
    }

def main():
    print("==========================================================")
    print("开始执行问题四：任务分区与独立资源配置优化")
    print("==========================================================")
    
    df_q2_trips = pd.read_csv('results/Q2_运输架次.csv')
    df_q3_relays = pd.read_csv('results/Q3_中继架次.csv')
    df_q3_comm = pd.read_csv('results/Q3_通信保障.csv')
    
    out_rows = []
    
    # 1. 评估 K=2
    print("\n--- 评估 K=2 分区方案 ---")
    for g_id, svcs in PARTITIONS_K2.items():
        res = analyze_group_resources(svcs, df_q2_trips, df_q3_relays, df_q3_comm)
        svc_str = ','.join(svcs)
        out_rows.append({
            'K（2或3）': 2,
            '任务组编号': g_id,
            '服务区列表': svc_str,
            'A型运输无人机数': res['n_A'],
            'B型运输无人机数': res['n_B'],
            'C型运输无人机数': res['n_C'],
            'A型电池组数': res['b_A'],
            'B型电池组数': res['b_B'],
            'C型电池组数': res['b_C'],
            '中继无人机数': res['n_R'],
            '中继能源组件数': res['b_MOD']
        })
        print(f"任务组 {g_id} ({svc_str}):")
        print(f"  运输架次: {res['trips_count']}, 中继架次: {res['relay_trips']}")
        print(f"  无人机需求: A={res['n_A']}, B={res['n_B']}, C={res['n_C']} (合计 {res['n_A']+res['n_B']+res['n_C']})")
        print(f"  电池组需求: A={res['b_A']}, B={res['b_B']}, C={res['b_C']} (合计 {res['b_A']+res['b_B']+res['b_C']})")
        print(f"  中继资源: 中继机={res['n_R']}, 能源组件={res['b_MOD']}")

    # 2. 评估 K=3
    print("\n--- 评估 K=3 分区方案 ---")
    for g_id, svcs in PARTITIONS_K3.items():
        res = analyze_group_resources(svcs, df_q2_trips, df_q3_relays, df_q3_comm)
        svc_str = ','.join(svcs)
        out_rows.append({
            'K（2或3）': 3,
            '任务组编号': g_id,
            '服务区列表': svc_str,
            'A型运输无人机数': res['n_A'],
            'B型运输无人机数': res['n_B'],
            'C型运输无人机数': res['n_C'],
            'A型电池组数': res['b_A'],
            'B型电池组数': res['b_B'],
            'C型电池组数': res['b_C'],
            '中继无人机数': res['n_R'],
            '中继能源组件数': res['b_MOD']
        })
        print(f"任务组 {g_id} ({svc_str}):")
        print(f"  运输架次: {res['trips_count']}, 中继架次: {res['relay_trips']}")
        print(f"  无人机需求: A={res['n_A']}, B={res['n_B']}, C={res['n_C']} (合计 {res['n_A']+res['n_B']+res['n_C']})")
        print(f"  电池组需求: A={res['b_A']}, B={res['b_B']}, C={res['b_C']} (合计 {res['b_A']+res['b_B']+res['b_C']})")
        print(f"  中继资源: 中继机={res['n_R']}, 能源组件={res['b_MOD']}")

    df_out = pd.DataFrame(out_rows)
    df_out.to_csv('results/Q4_分区配置.csv', index=False, encoding='utf-8-sig')
    print("\n成功输出: results/Q4_分区配置.csv")
    
    # 3. 汇总对比与库存缺口分析
    print("\n==========================================================")
    print("资源配置与现有库存缺口对比分析")
    print("==========================================================")
    
    stock = {
        'A_drone': 4, 'B_drone': 2, 'C_drone': 2,
        'A_bat': 6, 'B_bat': 4, 'C_bat': 4,
        'R_drone': 2, 'MOD': 6
    }
    
    for k in [2, 3]:
        sub = df_out[df_out['K（2或3）'] == k]
        tot_nA = sub['A型运输无人机数'].sum()
        tot_nB = sub['B型运输无人机数'].sum()
        tot_nC = sub['C型运输无人机数'].sum()
        tot_bA = sub['A型电池组数'].sum()
        tot_bB = sub['B型电池组数'].sum()
        tot_bC = sub['C型电池组数'].sum()
        tot_nR = sub['中继无人机数'].sum()
        tot_bMOD = sub['中继能源组件数'].sum()
        
        print(f"\n[分区 K={k} 总体资源配置汇总]")
        print(f"  无人机总需求: A={tot_nA} (库存{stock['A_drone']}, 缺口{max(0, tot_nA-stock['A_drone'])}), "
              f"B={tot_nB} (库存{stock['B_drone']}, 缺口{max(0, tot_nB-stock['B_drone'])}), "
              f"C={tot_nC} (库存{stock['C_drone']}, 缺口{max(0, tot_nC-stock['C_drone'])})")
        print(f"  电池组总需求: A={tot_bA} (库存{stock['A_bat']}, 缺口{max(0, tot_bA-stock['A_bat'])}), "
              f"B={tot_bB} (库存{stock['B_bat']}, 缺口{max(0, tot_bB-stock['B_bat'])}), "
              f"C={tot_bC} (库存{stock['C_bat']}, 缺口{max(0, tot_bC-stock['C_bat'])})")
        print(f"  中继机总需求: R={tot_nR} (库存{stock['R_drone']}, 缺口{max(0, tot_nR-stock['R_drone'])}), "
              f"组件={tot_bMOD} (库存{stock['MOD']}, 缺口{max(0, tot_bMOD-stock['MOD'])})")

if __name__ == '__main__':
    main()
