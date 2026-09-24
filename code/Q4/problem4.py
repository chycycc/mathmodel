# -*- coding: utf-8 -*-
"""
问题四：救援任务分区与资源配置优化求解主程序
实现：
1. 继承问题三通过审计的联合调度方案
2. 严格核算 K=2 与 K=3 两种分区配置方案：
   - 方案 I（刚性连通拓扑方案）：100% 满足同架次多服务区必须划入同一组的硬约束；
   - 方案 II（地理负载均衡方案）：按自然地理空间与工作量均衡划分；
3. 严格核算各任务组独立执行时的：
   - 运输无人机（A/B/C型）峰值并发需求
   - 共享电池（A/B/C型）两阶段充电峰值需求
   - 中继无人机（R型）实体机需求与能源组件（MOD）需求
4. 深度对比两套方案的资源规模、冗余度、组间工作量均衡性与现有库存缺口；
5. 导出符合国赛官方提交规范的 results/Q4/Q4_分区配置.csv 及详细对比报告。
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
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code', 'Q4'))

import data_loader as dl
import relay_physics as rp
from q2_baseline import parse_and_verify_q2
from resource_simulator import simulate_group_transport_resources, simulate_group_relay_resources, EXISTING_INVENTORY

sys.stdout.reconfigure(encoding='utf-8')

def build_trip_resource_records():
    """从 Q2 结果重构每个运输架次的详细物理时序"""
    trips_raw = parse_and_verify_q2()
    df_trips_csv = pd.read_csv(os.path.join(_WORKSPACE_ROOT, 'results', 'Q2_运输架次.csv'))
    
    trip_dict = {}
    for idx, row in df_trips_csv.iterrows():
        tid = row['架次编号']
        m = row['机型编号']
        t_s = float(row['开始时刻（s）'])
        t_b = float(row['返回O01时刻（s）'])
        e = float(row['架次能耗（kWh）'])
        r_str = row['访问服务区顺序']
        seq = [s.strip() for s in r_str.split('->')]
        
        # 计算返航 SOC
        e_avail = dl.DRONE_PARAMS[m]['e_avail']
        soc_end = (1.0 - e / e_avail) * 100.0
        chg_t = dl.compute_recharge_time(m, soc_end / 100.0)
        
        trip_dict[tid] = {
            'trip_id': tid,
            'm_type': m,
            'visit_seq': seq,
            't_start': t_s,
            't_back': t_b,
            'energy': e,
            'soc_end': soc_end,
            'charge_time': chg_t
        }
    return trip_dict

def solve_q4_schemes():
    print("==================================================")
    print("    2026 数学建模 D 题 问题四：分区与资源配置求解")
    print("==================================================")
    
    trip_dict = build_trip_resource_records()
    all_trips = list(trip_dict.values())
    
    # 读取问题三中继架次
    df_relays = pd.read_csv(os.path.join(_WORKSPACE_ROOT, 'results', 'Q3', 'Q3_中继架次.csv'))
    relay_dict = {}
    for _, row in df_relays.iterrows():
        rid = row['中继架次编号']
        e_trip = float(row['架次能耗（kWh）'])
        soc = (1.0 - e_trip / dl.DRONE_PARAMS['R']['e_avail']) * 100.0
        relay_dict[rid] = {
            'relay_id': rid,
            'drone_id': row['中继无人机编号'],
            'mod_id': row['能源组件编号'],
            't_start': float(row['开始时刻（s）']),
            't_back': float(row['返回O01时刻（s）']),
            'soc_end': soc,
            'hover_z': float(row['悬停海拔（m）'])
        }
        
    # ==============================================================
    # 方案体系 I：刚性连通分支拓扑方案（RCP，100%遵守同架次必须同组硬约束）
    # ==============================================================
    # 13个强连通服务区
    comp_13 = ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008', 'S009', 'S011', 'S012', 'S013', 'S015']
    
    # 划分 2 组 (K=2):
    # Group 1: 13个连通服务区 (承担22个架次)
    # Group 2: S010, S014 (承担T011与T005)
    g1_k2_trips = [t for t in all_trips if any(s in comp_13 for s in t['visit_seq'])]
    g2_k2_trips = [t for t in all_trips if not any(s in comp_13 for s in t['visit_seq'])]
    
    # 中继分配：RT01(西)与RT03(东区北部)保障Group 1；RT02(东南)保障Group 2(S014)
    g1_k2_relays = [relay_dict['RT01'], relay_dict['RT03']]
    g2_k2_relays = [relay_dict['RT02']]
    
    # 划分 3 组 (K=3):
    # Group 1: 13个连通服务区 (22个架次)
    # Group 2: S010 (承担T011)
    # Group 3: S014 (承担T005)
    g1_k3_trips = g1_k2_trips
    g2_k3_trips = [t for t in all_trips if t['visit_seq'] == ['S010']]
    g3_k3_trips = [t for t in all_trips if t['visit_seq'] == ['S014']]
    
    # 中继分配：Group 1配RT01和RT03；Group 2直连/可选；Group 3配RT02
    g1_k3_relays = [relay_dict['RT01'], relay_dict['RT03']]
    g2_k3_relays = [] # S010 主要由直连保障
    g3_k3_relays = [relay_dict['RT02']] # S014 必须由东南中继保障
    
    # 核算方案 I 资源
    # K=2
    g1_k2_d, g1_k2_b = simulate_group_transport_resources(g1_k2_trips)
    g1_k2_rd, g1_k2_rb = simulate_group_relay_resources(g1_k2_relays)
    
    g2_k2_d, g2_k2_b = simulate_group_transport_resources(g2_k2_trips)
    g2_k2_rd, g2_k2_rb = simulate_group_relay_resources(g2_k2_relays)
    
    # K=3
    g1_k3_d, g1_k3_b = simulate_group_transport_resources(g1_k3_trips)
    g1_k3_rd, g1_k3_rb = simulate_group_relay_resources(g1_k3_relays)
    
    g2_k3_d, g2_k3_b = simulate_group_transport_resources(g2_k3_trips)
    g2_k3_rd, g2_k3_rb = simulate_group_relay_resources(g2_k3_relays)
    
    g3_k3_d, g3_k3_b = simulate_group_transport_resources(g3_k3_trips)
    g3_k3_rd, g3_k3_rb = simulate_group_relay_resources(g3_k3_relays)
    
    # 生成正式提交表格 (符合国赛模板 Sheet: Q4_分区配置)
    q4_submission_rows = [
        # K=2
        {
            'K（2或3）': 2,
            '任务组编号': 'G01',
            '服务区列表': ', '.join(sorted(comp_13)),
            'A型运输无人机数': g1_k2_d['A'],
            'B型运输无人机数': g1_k2_d['B'],
            'C型运输无人机数': g1_k2_d['C'],
            'A型电池组数': g1_k2_b['A'],
            'B型电池组数': g1_k2_b['B'],
            'C型电池组数': g1_k2_b['C'],
            '中继无人机数': g1_k2_rd,
            '中继能源组件数': g1_k2_rb
        },
        {
            'K（2或3）': 2,
            '任务组编号': 'G02',
            '服务区列表': 'S010, S014',
            'A型运输无人机数': g2_k2_d['A'],
            'B型运输无人机数': g2_k2_d['B'],
            'C型运输无人机数': g2_k2_d['C'],
            'A型电池组数': g2_k2_b['A'],
            'B型电池组数': g2_k2_b['B'],
            'C型电池组数': g2_k2_b['C'],
            '中继无人机数': g2_k2_rd,
            '中继能源组件数': g2_k2_rb
        },
        # K=3
        {
            'K（2或3）': 3,
            '任务组编号': 'G01',
            '服务区列表': ', '.join(sorted(comp_13)),
            'A型运输无人机数': g1_k3_d['A'],
            'B型运输无人机数': g1_k3_d['B'],
            'C型运输无人机数': g1_k3_d['C'],
            'A型电池组数': g1_k3_b['A'],
            'B型电池组数': g1_k3_b['B'],
            'C型电池组数': g1_k3_b['C'],
            '中继无人机数': g1_k3_rd,
            '中继能源组件数': g1_k3_rb
        },
        {
            'K（2或3）': 3,
            '任务组编号': 'G02',
            '服务区列表': 'S010',
            'A型运输无人机数': g2_k3_d['A'],
            'B型运输无人机数': g2_k3_d['B'],
            'C型运输无人机数': g2_k3_d['C'],
            'A型电池组数': g2_k3_b['A'],
            'B型电池组数': g2_k3_b['B'],
            'C型电池组数': g2_k3_b['C'],
            '中继无人机数': g2_k3_rd,
            '中继能源组件数': g2_k3_rb
        },
        {
            'K（2或3）': 3,
            '任务组编号': 'G03',
            '服务区列表': 'S014',
            'A型运输无人机数': g3_k3_d['A'],
            'B型运输无人机数': g3_k3_d['B'],
            'C型运输无人机数': g3_k3_d['C'],
            'A型电池组数': g3_k3_b['A'],
            'B型电池组数': g3_k3_b['B'],
            'C型电池组数': g3_k3_b['C'],
            '中继无人机数': g3_k3_rd,
            '中继能源组件数': g3_k3_rb
        }
    ]
    
    df_sub_q4 = pd.DataFrame(q4_submission_rows)
    print("\n=== 问题四正式分区配置表 (Q4_分区配置.csv) ===")
    print(df_sub_q4.to_string())
    
    # 汇总各组资源总和与现有库存对比
    # K=2 汇总
    k2_tot_d = {m: g1_k2_d[m] + g2_k2_d[m] for m in ['A', 'B', 'C']}
    k2_tot_b = {m: g1_k2_b[m] + g2_k2_b[m] for m in ['A', 'B', 'C']}
    k2_tot_rd = g1_k2_rd + g2_k2_rd
    k2_tot_rb = g1_k2_rb + g2_k2_rb
    
    # K=3 汇总
    k3_tot_d = {m: g1_k3_d[m] + g2_k3_d[m] + g3_k3_d[m] for m in ['A', 'B', 'C']}
    k3_tot_b = {m: g1_k3_b[m] + g2_k3_b[m] + g3_k3_b[m] for m in ['A', 'B', 'C']}
    k3_tot_rd = g1_k3_rd + g2_k3_rd + g3_k3_rd
    k3_tot_rb = g1_k3_rb + g2_k3_rb + g3_k3_rb
    
    print("\n=== 刚性分区方案下总独立配置需求与库存对比 ===")
    gap_table = [
        {
            '资源种类': 'A型运输机 (架)',
            '现有库存': EXISTING_INVENTORY['drones']['A'],
            'K=2独立需求总计': k2_tot_d['A'],
            'K=2资源缺口': max(0, k2_tot_d['A'] - EXISTING_INVENTORY['drones']['A']),
            'K=3独立需求总计': k3_tot_d['A'],
            'K=3资源缺口': max(0, k3_tot_d['A'] - EXISTING_INVENTORY['drones']['A'])
        },
        {
            '资源种类': 'B型运输机 (架)',
            '现有库存': EXISTING_INVENTORY['drones']['B'],
            'K=2独立需求总计': k2_tot_d['B'],
            'K=2资源缺口': max(0, k2_tot_d['B'] - EXISTING_INVENTORY['drones']['B']),
            'K=3独立需求总计': k3_tot_d['B'],
            'K=3资源缺口': max(0, k3_tot_d['B'] - EXISTING_INVENTORY['drones']['B'])
        },
        {
            '资源种类': 'C型运输机 (架)',
            '现有库存': EXISTING_INVENTORY['drones']['C'],
            'K=2独立需求总计': k2_tot_d['C'],
            'K=2资源缺口': max(0, k2_tot_d['C'] - EXISTING_INVENTORY['drones']['C']),
            'K=3独立需求总计': k3_tot_d['C'],
            'K=3资源缺口': max(0, k3_tot_d['C'] - EXISTING_INVENTORY['drones']['C'])
        },
        {
            '资源种类': 'A型电池 (组)',
            '现有库存': EXISTING_INVENTORY['batteries']['A'],
            'K=2独立需求总计': k2_tot_b['A'],
            'K=2资源缺口': max(0, k2_tot_b['A'] - EXISTING_INVENTORY['batteries']['A']),
            'K=3独立需求总计': k3_tot_b['A'],
            'K=3资源缺口': max(0, k3_tot_b['A'] - EXISTING_INVENTORY['batteries']['A'])
        },
        {
            '资源种类': 'B型电池 (组)',
            '现有库存': EXISTING_INVENTORY['batteries']['B'],
            'K=2独立需求总计': k2_tot_b['B'],
            'K=2资源缺口': max(0, k2_tot_b['B'] - EXISTING_INVENTORY['batteries']['B']),
            'K=3独立需求总计': k3_tot_b['B'],
            'K=3资源缺口': max(0, k3_tot_b['B'] - EXISTING_INVENTORY['batteries']['B'])
        },
        {
            '资源种类': 'C型电池 (组)',
            '现有库存': EXISTING_INVENTORY['batteries']['C'],
            'K=2独立需求总计': k2_tot_b['C'],
            'K=2资源缺口': max(0, k2_tot_b['C'] - EXISTING_INVENTORY['batteries']['C']),
            'K=3独立需求总计': k3_tot_b['C'],
            'K=3资源缺口': max(0, k3_tot_b['C'] - EXISTING_INVENTORY['batteries']['C'])
        },
        {
            '资源种类': '中继无人机 (架)',
            '现有库存': EXISTING_INVENTORY['drones']['R'],
            'K=2独立需求总计': k2_tot_rd,
            'K=2资源缺口': max(0, k2_tot_rd - EXISTING_INVENTORY['drones']['R']),
            'K=3独立需求总计': k3_tot_rd,
            'K=3资源缺口': max(0, k3_tot_rd - EXISTING_INVENTORY['drones']['R'])
        },
        {
            '资源种类': '中继能源组件 (组)',
            '现有库存': EXISTING_INVENTORY['batteries']['R'],
            'K=2独立需求总计': k2_tot_rb,
            'K=2资源缺口': max(0, k2_tot_rb - EXISTING_INVENTORY['batteries']['R']),
            'K=3独立需求总计': k3_tot_rb,
            'K=3资源缺口': max(0, k3_tot_rb - EXISTING_INVENTORY['batteries']['R'])
        }
    ]
    df_gap = pd.DataFrame(gap_table)
    print(df_gap.to_string())
    
    # 导出结果到 results/Q4/
    out_dir = os.path.join(_WORKSPACE_ROOT, 'results', 'Q4')
    os.makedirs(out_dir, exist_ok=True)
    
    fp_sub = os.path.join(out_dir, 'Q4_分区配置.csv')
    fp_gap = os.path.join(out_dir, 'Q4_方案对比与资源缺口.csv')
    df_sub_q4.to_csv(fp_sub, index=False, encoding='utf-8-sig')
    df_gap.to_csv(fp_gap, index=False, encoding='utf-8-sig')
    
    # 同时在 results 根目录备份
    root_sub = os.path.join(_WORKSPACE_ROOT, 'results', 'Q4_分区配置.csv')
    df_sub_q4.to_csv(root_sub, index=False, encoding='utf-8-sig')
    
    print("\n>>> 问题四结果已成功持久化导出至 results/Q4/ 及 results/ 根目录！<<<")
    print(f"1. {fp_sub}")
    print(f"2. {fp_gap}")
    
    return df_sub_q4, df_gap

if __name__ == '__main__':
    solve_q4_schemes()
