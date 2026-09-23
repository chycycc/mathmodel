# -*- coding: utf-8 -*-
"""
问题二最优调度综合评估与网格搜索
测试不同架次合并与串联策略的全局指标表现
"""
import sys
import copy
import pandas as pd
import numpy as np

sys.path.append('code')
import data_loader as dl
from problem2 import compute_multistop_route

def run_simulation(planned_sorties):
    drones = {
        'U01': {'type': 'A', 'avail_time': 0.0},
        'U02': {'type': 'A', 'avail_time': 0.0},
        'U03': {'type': 'A', 'avail_time': 0.0},
        'U04': {'type': 'A', 'avail_time': 0.0},
        'U05': {'type': 'B', 'avail_time': 0.0},
        'U06': {'type': 'B', 'avail_time': 0.0},
        'U07': {'type': 'C', 'avail_time': 0.0},
        'U08': {'type': 'C', 'avail_time': 0.0},
    }
    
    batteries = {}
    for i in range(1, 7):
        batteries[f"BAT_A_{i:02d}"] = {'type': 'A', 'avail_time': 0.0, 'soc': 100.0}
    for i in range(1, 5):
        batteries[f"BAT_B_{i:02d}"] = {'type': 'B', 'avail_time': 0.0, 'soc': 100.0}
    for i in range(1, 5):
        batteries[f"BAT_C_{i:02d}"] = {'type': 'C', 'avail_time': 0.0, 'soc': 100.0}

    final_sorties = []
    final_deliveries = []
    sortie_idx = 1
    
    remaining_tasks = copy.deepcopy(planned_sorties)
    
    while remaining_tasks:
        best_candidate_idx = None
        best_earliest_start = 1e9
        best_u = None
        best_b = None
        best_chosen_m = None
        best_route_res = None
        actual_start_time = None
        
        for idx, task in enumerate(remaining_tasks):
            seq = task['visit_seq']
            b_list = task['boxes']
            alloc = {s: [b for b in b_list if b['service_id'] == s] for s in seq}
            preferred_m = task['m_type']
            m_candidates = [preferred_m] + [m for m in ['A', 'B', 'C'] if m != preferred_m]
            
            chosen_m = None
            route_res = None
            for m in m_candidates:
                val, t_flight_total, e_trip, soc_end, deliv_offsets = compute_multistop_route(m, seq, alloc)
                if val:
                    chosen_m = m
                    route_res = (t_flight_total, e_trip, soc_end, deliv_offsets)
                    break
                    
            if chosen_m is None:
                raise RuntimeError(f"任务 {seq} 货箱无法容纳")
                
            t_prep = dl.DRONE_PARAMS[chosen_m]['t_prep']
            t_load = len(b_list) * dl.DRONE_PARAMS[chosen_m]['t_load_per_box']
            min_req = task.get('min_start', 0.0)
            
            avail_u_list = [uid for uid, u in drones.items() if u['type'] == chosen_m]
            avail_b_list = [bid for bid, b in batteries.items() if b['type'] == chosen_m]
            
            t_cand_start = 1e9
            cand_u = None
            cand_b = None
            for uid in avail_u_list:
                u_ready = drones[uid]['avail_time']
                for bid in avail_b_list:
                    b_ready = batteries[bid]['avail_time']
                    act_start = max(min_req, u_ready + t_prep + t_load, b_ready)
                    if act_start < t_cand_start:
                        t_cand_start = act_start
                        cand_u = uid
                        cand_b = bid
                        
            # 首批紧急保障物资具备最高优先级
            has_first = any(b.get('is_first_batch', False) or b.get('type') == '医疗物资' for b in b_list)
            is_3600 = any(b.get('first_deadline') == 3600.0 for b in b_list)
            
            # 首批任务绝对优先保证在第一波全部起飞
            effective_start = t_cand_start - (300000.0 if is_3600 else (150000.0 if has_first else 0.0))
            
            if effective_start < best_earliest_start:
                best_earliest_start = effective_start
                best_candidate_idx = idx
                best_u = cand_u
                best_b = cand_b
                best_chosen_m = chosen_m
                best_route_res = route_res
                actual_start_time = t_cand_start

        task = remaining_tasks.pop(best_candidate_idx)
        t_flight_total, e_trip, soc_end, deliv_offsets = best_route_res
        
        t_start = actual_start_time
        t_return = t_start + t_flight_total
        
        drones[best_u]['avail_time'] = t_return
        t_charge = dl.compute_recharge_time(best_chosen_m, soc_end / 100.0)
        batteries[best_b]['avail_time'] = t_return + t_charge
        batteries[best_b]['soc'] = soc_end
        
        s_name = f"T{sortie_idx:03d}"
        sortie_idx += 1
        
        final_sorties.append({
            '架次编号': s_name,
            '无人机编号': best_u,
            '机型编号': best_chosen_m,
            '电池编号': best_b,
            '开始时刻（s）': round(t_start, 1),
            '访问服务区顺序': "->".join(task['visit_seq']),
            '返回O01时刻（s）': round(t_return, 1),
            '架次能耗（kWh）': round(e_trip, 4),
            '_返航SOC': round(soc_end, 2),
            '_包含箱数': len(task['boxes'])
        })
        
        for b in task['boxes']:
            d_time = t_start + deliv_offsets[b['box_id']]
            final_deliveries.append({
                '货箱编号': b['box_id'],
                '架次编号': s_name,
                '服务区编号': b['service_id'],
                '交付完成时刻（s）': round(d_time, 1),
                '_期望送达': b['expect_time'],
                '_首批时限': b['first_deadline'],
                '_类型': b['type'],
                '_延迟秒数': round(max(0.0, d_time - b['expect_time']), 1)
            })

    df_s = pd.DataFrame(final_sorties)
    df_d = pd.DataFrame(final_deliveries)
    return df_s, df_d

def build_plan_v2():
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

    # 11. S006 & S007 串联协同 (B型机: S006送1水 + S007送1食, 22kg, 0.055m3)
    b_s6_w = get_boxes('S006', 'WAT', count=1)
    b_s7_f = get_boxes('S007', 'FOD', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S006', 'S007'], 'boxes': b_s6_w + b_s7_f})

    # S006 剩余：1水 + 1卫 (20kg, 0.062m3 由 B型机运送)
    b_s6_rem = get_boxes('S006', 'WAT', count=1) + get_boxes('S006', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S006'], 'boxes': b_s6_rem})
    
    # S006 剩余：1食 (8kg 由 A型机直达)
    b_s6_f = get_boxes('S006', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S006'], 'boxes': b_s6_f})

    # S007 剩余：1水 + 1卫 (20kg, 0.062m3 由 B型机运送)
    b_s7_rem = get_boxes('S007', 'WAT', count=1) + get_boxes('S007', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S007'], 'boxes': b_s7_rem})

    # 12. S004 剩余 4 箱：
    b_s4_rem1 = get_boxes('S004', 'WAT', count=1) + get_boxes('S004', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S004'], 'boxes': b_s4_rem1})
    b_s4_rem2 = get_boxes('S004', 'WAT', count=1) + get_boxes('S004', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S004'], 'boxes': b_s4_rem2})

    # 13. S002 剩余 6 箱：
    b_s2_rem1 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S002'], 'boxes': b_s2_rem1})
    b_s2_rem2 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S002'], 'boxes': b_s2_rem2})
    b_s2_rem3 = get_boxes('S002', 'WAT', count=1) + get_boxes('S002', 'HYG', count=1)
    sorties.append({'m_type': 'B', 'visit_seq': ['S002'], 'boxes': b_s2_rem3})

    # 14. S010 & S013 串联回路 (A型机: S010送1食 + S013送1食, 16kg, 0.056m3)
    b_s10_f = get_boxes('S010', 'FOD', count=1)
    b_s13_f = get_boxes('S013', 'FOD', count=1)
    sorties.append({'m_type': 'A', 'visit_seq': ['S010', 'S013'], 'boxes': b_s10_f + b_s13_f})

    # 15. S012 与 S014 剩余食品 (各 1 箱，由 A 型机直达)
    for sid in ['S012', 'S014']:
        b_rem = get_boxes(sid)
        if b_rem:
            sorties.append({'m_type': 'A', 'visit_seq': [sid], 'boxes': b_rem})

    print(f"规划总架次数: {len(sorties)}, 覆盖货箱: {len(allocated_ids)} / {len(boxes)}")
    assert len(allocated_ids) == len(boxes), "货箱未全额覆盖！"
    return sorties

if __name__ == '__main__':
    planned = build_plan_v2()
    df_s, df_d = run_simulation(planned)
    print("\n================ 方案 V2 仿真结果 ================")
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
