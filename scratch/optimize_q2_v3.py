# -*- coding: utf-8 -*-
import sys
import copy
import pandas as pd
import numpy as np

sys.path.append('.')
sys.path.append('code')
import data_loader as dl
from problem2 import compute_multistop_route
from scratch.optimize_q2_sim import run_simulation

def build_plan_v3():
    boxes = copy.deepcopy(dl.CARGO_BOXES)
    allocated_ids = set()
    sorties = []
    
    def get_boxes(sid, cat=None, is_first=None, count=None):
        res = []
        for b in boxes:
            if b['box_id'] in allocated_ids:
                continue
            if b['service_id'] != sid:
                continue
            b_cat = b['box_id'].split('-')[1]
            if cat is not None and b_cat != cat:
                continue
            if is_first is not None and b['is_first_batch'] != is_first:
                continue
            res.append(b)
            if count is not None and len(res) == count:
                break
        for b in res:
            allocated_ids.add(b['box_id'])
        return res

    # 1. S001 第一批（C型机 满载 78kg，0.188m3）：
    b_s1_p1 = get_boxes('S001', 'MED') + get_boxes('S001', 'WAT', count=4) + get_boxes('S001', 'FOD', count=2)
    sorties.append({'m_type': 'C', 'visit_seq': ['S001'], 'boxes': b_s1_p1})

    # 2. S002 & S004 首批多点串联回路（C型机，34kg，0.078m3）：
    b_s2_first = get_boxes('S002', is_first=True)
    b_s4_first = get_boxes('S004', is_first=True)
    sorties.append({'m_type': 'C', 'visit_seq': ['S002', 'S004'], 'boxes': b_s2_first + b_s4_first})

    # 3. 剩余 6 个 3600s 紧急点的首批保障物资：
    sorties.append({'m_type': 'A', 'visit_seq': ['S006'], 'boxes': get_boxes('S006', is_first=True)})
    sorties.append({'m_type': 'A', 'visit_seq': ['S007'], 'boxes': get_boxes('S007', is_first=True)})
    sorties.append({'m_type': 'A', 'visit_seq': ['S010'], 'boxes': get_boxes('S010', is_first=True)})
    sorties.append({'m_type': 'A', 'visit_seq': ['S013'], 'boxes': get_boxes('S013', is_first=True)})
    sorties.append({'m_type': 'B', 'visit_seq': ['S014'], 'boxes': get_boxes('S014', is_first=True)})
    sorties.append({'m_type': 'B', 'visit_seq': ['S012'], 'boxes': get_boxes('S012', is_first=True)})

    # 4. S001 第二批（C型机 满载 76kg，0.206m3）：
    b_s1_p2 = get_boxes('S001', 'WAT', count=4) + get_boxes('S001', 'FOD', count=1) + get_boxes('S001', 'HYG', count=2)
    sorties.append({'m_type': 'C', 'visit_seq': ['S001'], 'boxes': b_s1_p2})

    # 5. S003 (西北 7200s，拆为2批)：
    b_s3_p1 = get_boxes('S003', is_first=True) + get_boxes('S003', 'WAT', count=2)
    sorties.append({'m_type': 'C', 'visit_seq': ['S003'], 'boxes': b_s3_p1})
    b_s3_p2 = get_boxes('S003', 'WAT', count=1) + get_boxes('S003', 'FOD', count=2) + get_boxes('S003', 'HYG', count=1)
    sorties.append({'m_type': 'C', 'visit_seq': ['S003'], 'boxes': b_s3_p2})

    # 6. S008 全部 5 箱（45kg，0.129m3）由 C型机一趟完成
    b_s8 = get_boxes('S008')
    sorties.append({'m_type': 'C', 'visit_seq': ['S008'], 'boxes': b_s8})

    # 7. S005 全部 6 箱（59kg，0.156m3）由 C型机一趟完成
    b_s5 = get_boxes('S005')
    sorties.append({'m_type': 'C', 'visit_seq': ['S005'], 'boxes': b_s5})

    # 8. S015 全部 3 箱（25kg，0.067m3）由 B型机直达
    b_s15 = get_boxes('S015')
    sorties.append({'m_type': 'B', 'visit_seq': ['S015'], 'boxes': b_s15})

    # 9. S009 全部 3 箱（25kg，0.067m3）由 B型机直达
    b_s9 = get_boxes('S009')
    sorties.append({'m_type': 'B', 'visit_seq': ['S009'], 'boxes': b_s9})

    # 10. S011 全部 3 箱（25kg，0.067m3）由 B型机直达
    b_s11 = get_boxes('S011')
    sorties.append({'m_type': 'B', 'visit_seq': ['S011'], 'boxes': b_s11})

    # 11. S006 剩余 4 箱：
    b_s6_rem1 = get_boxes('S006', 'WAT', count=1) + get_boxes('S006', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S006'], 'boxes': b_s6_rem1})
    b_s6_rem2 = get_boxes('S006', 'WAT', count=1) + get_boxes('S006', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S006'], 'boxes': b_s6_rem2})

    # 12. S007 剩余 3 箱：
    b_s7_rem1 = get_boxes('S007', 'WAT', count=1) + get_boxes('S007', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S007'], 'boxes': b_s7_rem1})
    b_s7_rem2 = get_boxes('S007', 'HYG', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S007'], 'boxes': b_s7_rem2})

    # 13. S004 剩余 4 箱：
    b_s4_rem1 = get_boxes('S004', 'WAT', count=1) + get_boxes('S004', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S004'], 'boxes': b_s4_rem1})
    b_s4_rem2 = get_boxes('S004', 'WAT', count=1) + get_boxes('S004', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S004'], 'boxes': b_s4_rem2})

    # 14. S002 剩余 6 箱：
    b_s2_rem1 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S002'], 'boxes': b_s2_rem1})
    b_s2_rem2 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S002'], 'boxes': b_s2_rem2})
    b_s2_rem3 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S002'], 'boxes': b_s2_rem3})

    # 15. S010 & S013 串联回路 (由 A 型机运送两箱食品, 16kg, 0.056m3)
    b_s10_f = get_boxes('S010', 'FOD', count=1)
    b_s13_f = get_boxes('S013', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S010', 'S013'], 'boxes': b_s10_f + b_s13_f})

    # 16. S012 与 S014 剩余食品 (各 1 箱，由 A 型机直达)
    for sid in ['S012', 'S014']:
        b_rem = get_boxes(sid)
        if b_rem:
            sorties.append({'m_type': 'A', 'visit_seq': [sid], 'boxes': b_rem})

    print(f"规划总架次数: {len(sorties)}, 覆盖货箱: {len(allocated_ids)} / {len(boxes)}")
    assert len(allocated_ids) == len(boxes), "货箱未全额覆盖！"
    return sorties

if __name__ == '__main__':
    planned = build_plan_v3()
    df_s, df_d = run_simulation(planned)
    print("\n================ 方案 V3 仿真结果 ================")
    print(f"总架次数: {len(df_s)}")
    mspan = df_s['返回O01时刻（s）'].max()
    print(f"Makespan: {mspan:.1f} s ({mspan/3600.0:.2f} 小时)")
    tot_e = df_s['架次能耗（kWh）'].sum()
    print(f"总能耗: {tot_e:.3f} kWh")
    
    first_viol = df_d[(df_d['_首批时限'].notnull()) & (df_d['交付完成时刻（s）'] > df_d['_首批时限'])]
    print(f"首批违约箱数: {len(first_viol)}")
    
    exp_viol = df_d[df_d['交付完成时刻（s）'] > df_d['_期望送达']]
    print(f"期望时限违约箱数: {len(exp_viol)}")
    
    print("\n各机型出动统计:")
    print(df_s['机型编号'].value_counts())
    print("\n各无人机出动与完工时刻:")
    for uid in sorted(df_s['无人机编号'].unique()):
        u_s = df_s[df_s['无人机编号'] == uid]
        print(f"{uid} ({u_s.iloc[0]['机型编号']}): 出动 {len(u_s)} 架次, 最终返回时刻 {u_s['返回O01时刻（s）'].max():.1f} s ({u_s['返回O01时刻（s）'].max()/3600.0:.2f}h), 总能耗 {u_s['架次能耗（kWh）'].sum():.2f} kWh")
