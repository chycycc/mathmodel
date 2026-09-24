# -*- coding: utf-8 -*-
"""
问题三：联合调度优化求解器
搜索全覆盖、零冲突的最优中继调度方案（比较不同中继架次配置方案）
"""
import os
import sys
sys.path.insert(0, os.path.abspath('code'))
sys.path.insert(0, os.path.abspath('code/Q3'))
import math
import pandas as pd
import numpy as np
import data_loader as dl
import relay_physics as rp
from milp_relay_scheduler import evaluate_schedule_feasibility

sys.stdout.reconfigure(encoding='utf-8')

def test_scheme_4sorties():
    """
    方案 A: 4 架次轮转中继方案
    RT01: R01 执飞西区前段 [800s ~ 3400s]
    RT02: R02 执飞东区前段 [740s ~ 2500s] (覆盖 S014, S002, S012 等)
    RT03: R02 执飞东区后段 [2850s ~ 5250s] (周转后换 MOD_03，覆盖 S004, S010, S013 等)
    RT04: R01 执飞西区后段 [3750s ~ 7260s] (周转后换 MOD_04，覆盖西区后段)
    让我们测算时间轴与覆盖率！
    """
    trans_w = rp.get_relay_transit_info(rp.RELAY_POS_WEST)
    trans_es = rp.get_relay_transit_info(rp.RELAY_POS_EAST_SOUTH)
    trans_en = rp.get_relay_transit_info(rp.RELAY_POS_EAST_NORTH)
    
    # RT01: 西区前段
    # 要求 t_link_done <= 816.2
    t_start_1 = 810.0 - 180.0 - trans_w['t_out'] - 30.0
    t_end_1 = 3400.0 # 服务至 3400s
    t_back_1 = t_end_1 + trans_w['t_back']
    
    # RT02: 东区前段 (悬停 EAST_SOUTH，必须覆盖 S014)
    # 要求 t_link_done <= 750.3
    t_start_2 = 740.0 - 180.0 - trans_es['t_out'] - 30.0
    t_end_2 = 2500.0 # 覆盖至 2500s (T001在2143s结束)
    t_back_2 = t_end_2 + trans_es['t_back']
    
    # RT03: 东区后段 (由 R02 执飞，悬停 EAST_NORTH，覆盖 S004 及东区后部)
    # R02 周转 >= 300s
    t_start_3 = math.ceil(t_back_2) + 301.0
    t_end_3 = 5250.0
    
    # RT04: 西区后段 (由 R01 执飞，悬停 WEST)
    # R01 周转 >= 300s
    t_start_4 = math.ceil(t_back_1) + 301.0
    t_end_4 = 7260.0
    
    sorties = [
        {
            'sortie_id': 'RT01', 'drone_id': 'R01', 'mod_id': 'MOD_01',
            'pos_key': 'WEST', 't_start': round(t_start_1, 1), 't_srv_end': round(t_end_1, 1)
        },
        {
            'sortie_id': 'RT02', 'drone_id': 'R02', 'mod_id': 'MOD_02',
            'pos_key': 'EAST_SOUTH', 't_start': round(t_start_2, 1), 't_srv_end': round(t_end_2, 1)
        },
        {
            'sortie_id': 'RT03', 'drone_id': 'R02', 'mod_id': 'MOD_03',
            'pos_key': 'EAST_NORTH', 't_start': round(t_start_3, 1), 't_srv_end': round(t_end_3, 1)
        },
        {
            'sortie_id': 'RT04', 'drone_id': 'R01', 'mod_id': 'MOD_04',
            'pos_key': 'WEST', 't_start': round(t_start_4, 1), 't_srv_end': round(t_end_4, 1)
        }
    ]
    
    ok, msg, metrics = evaluate_schedule_feasibility(sorties)
    print("=== 方案 A 测试结果 ===")
    print("可行性:", ok)
    print("说明:", msg)
    if ok:
        print(f"总架次: {metrics['total_sorties']}, 总能耗: {metrics['total_energy']:.4f} kWh, 完工时间: {metrics['latest_return']:.1f} s")
        for s in metrics['sorties_detail']:
            print(f"  {s['sortie_id']} ({s['drone_id']}-{s['mod_id']}-{s['pos_key']}): 开始={s['t_start']:.1f}, 离地={s['t_depart']:.1f}, 建链={s['t_link_done']:.1f}, 结束={s['t_srv_end']:.1f}, 返回={s['t_back_done']:.1f}, 能耗={s['total_energy']:.4f}kWh, SOC={s['soc_end']:.1f}%")
    return ok, metrics

if __name__ == '__main__':
    test_scheme_4sorties()
