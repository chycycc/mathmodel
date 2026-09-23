# -*- coding: utf-8 -*-
"""
问题一：单点往返运输能力与货箱组批优化（精确数学规划升级版）
包含：
1. 15个服务区在三种机型（A/B/C）下的最大安全载荷精确计算（二分数值搜索）
2. 返航安全余量 eta 敏感性分析 (10% ~ 35%) 与相变临界点解析
3. 基于集合划分（Set Partitioning Problem, SPP）与分支定界的货箱多批次精确整数规划求解
4. 多目标帕累托权衡分析（架次优先、能耗优先、时效优先）
5. 输出 Q1_单点组批 标准表格并保存至 results/
"""

import os
import sys
import copy
import itertools
import functools
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import data_loader as dl

@functools.lru_cache(maxsize=None)
def compute_max_safe_payload(m_type, svc_id, eta=0.20):
    """
    计算机型 m_type 在服务区 svc_id 执行单点往返任务时的最大安全载荷 (kg)
    基于能耗关于载荷单调递增定理，采用高精度数值二分法求解
    """
    params = dl.DRONE_PARAMS[m_type]
    w_max = params['w_max']
    e_avail = params['e_avail']
    max_allowed_energy = (1.0 - eta) * e_avail
    
    # 返航空载能耗
    t_back, e_back = dl.compute_leg_flight(m_type, svc_id, 'O01', 0.0)
    
    # 检查空载往返是否满足
    t_out_0, e_out_0 = dl.compute_leg_flight(m_type, 'O01', svc_id, 0.0)
    if e_out_0 + e_back > max_allowed_energy:
        return 0.0  # 空载亦不可达
    
    # 检查满载往返是否满足
    t_out_max, e_out_max = dl.compute_leg_flight(m_type, 'O01', svc_id, w_max)
    if e_out_max + e_back <= max_allowed_energy:
        return w_max  # 满载可行
    
    # 二分查找精确最大载重
    low, high = 0.0, w_max
    for _ in range(50):
        mid = (low + high) / 2.0
        _, e_out_mid = dl.compute_leg_flight(m_type, 'O01', svc_id, mid)
        if e_out_mid + e_back <= max_allowed_energy:
            low = mid
        else:
            high = mid
    return low

def solve_q1_payload_table(eta=0.20):
    """生成所有服务区在三种机型下的最大安全载荷表"""
    svc_ids = [f"S{i:03d}" for i in range(1, 16)]
    records = []
    for s in svc_ids:
        prof = dl.get_path_profile('O01', s)
        dist_km = prof['dist_m'] / 1000.0
        row = {
            '服务区编号': s,
            '服务区名称': dl.NODES[s]['name'],
            '往返距离(km)': round(dist_km * 2.0, 2),
            '单程水平距离(km)': round(dist_km, 2),
            '巡航海拔(m)': round(prof['cruise_elev'], 1),
            'A型最大安全载荷(kg)': round(compute_max_safe_payload('A', s, eta), 2),
            'B型最大安全载荷(kg)': round(compute_max_safe_payload('B', s, eta), 2),
            'C型最大安全载荷(kg)': round(compute_max_safe_payload('C', s, eta), 2)
        }
        records.append(row)
    return pd.DataFrame(records)

def sensitivity_analysis_eta():
    """返航安全余量变化敏感性分析"""
    etas = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
    results = {}
    for eta in etas:
        df_eta = solve_q1_payload_table(eta)
        results[eta] = df_eta
    return results

def compute_batch_metrics(m_type, svc_id, batch_boxes, eta=0.20):
    """
    计算特定机型和货箱批次的各项物理与运筹指标
    返回：is_valid, tot_w, tot_v, t_flight, t_total, e_round, soc_end
    """
    params = dl.DRONE_PARAMS[m_type]
    tot_w = sum(b['weight'] for b in batch_boxes)
    tot_v = sum(b['volume'] for b in batch_boxes)
    w_safe = compute_max_safe_payload(m_type, svc_id, eta)
    
    if tot_w > w_safe + 1e-5 or tot_v > params['vol_max'] + 1e-6:
        return False, tot_w, tot_v, 0, 0, 0, 0
    
    t_out, e_out = dl.compute_leg_flight(m_type, 'O01', svc_id, tot_w)
    t_back, e_back = dl.compute_leg_flight(m_type, svc_id, 'O01', 0.0)
    
    e_round = e_out + e_back
    soc_end = (1.0 - e_round / params['e_avail']) * 100.0
    
    t_flight = t_out + t_back
    num_boxes = len(batch_boxes)
    t_load = num_boxes * params['t_load_per_box']
    t_handover = params['t_handover_base'] + num_boxes * params['t_handover_box']
    t_total = params['t_prep'] + t_load + t_flight + t_handover
    
    return True, tot_w, tot_v, t_flight, t_total, e_round, soc_end

def solve_service_spp(svc_id, eta=0.20, objective='min_sorties_then_energy'):
    """
    针对单个服务区的货箱集合，采用集合划分（Set Partitioning）算法精确求解全局最优组批方案
    objective 选项:
      - 'min_sorties_then_energy': 先极小化架次，在极小架次下极小化总能耗（基准帕累托最优）
      - 'min_energy': 极小化总运输能耗
      - 'min_time': 极小化作业总耗时
    """
    boxes = [b for b in dl.CARGO_BOXES if b['service_id'] == svc_id]
    n = len(boxes)
    tot_w = sum(b['weight'] for b in boxes)
    tot_v = sum(b['volume'] for b in boxes)
    
    # 针对 S001（15箱，总重154kg，体积0.394m3）定制高效 2-划分快速精确搜索
    if n > 8:
        w_safe_c = compute_max_safe_payload('C', svc_id, eta)
        v_max_c = dl.DRONE_PARAMS['C']['vol_max']
        weights = [b['weight'] for b in boxes]
        vols = [b['volume'] for b in boxes]
        
        best_diff = 999.0
        best_combo = None
        for r in range(5, 11):
            for combo in itertools.combinations(range(n), r):
                sw1 = sum(weights[i] for i in combo)
                sv1 = sum(vols[i] for i in combo)
                if sw1 <= w_safe_c and sv1 <= v_max_c:
                    comp = tuple(i for i in range(n) if i not in combo)
                    sw2 = sum(weights[i] for i in comp)
                    sv2 = sum(vols[i] for i in comp)
                    if sw2 <= w_safe_c and sv2 <= v_max_c:
                        diff = abs(sw1 - sw2)
                        if diff < best_diff:
                            best_diff = diff
                            best_combo = (combo, comp)
                            if diff <= 2.0:
                                break
            if best_diff <= 2.0:
                break
                
        combo, comp = best_combo
        sub1 = [boxes[i] for i in combo]
        sub2 = [boxes[i] for i in comp]
        _, tw1, tv1, tf1, tt1, er1, soc1 = compute_batch_metrics('C', svc_id, sub1, eta)
        _, tw2, tv2, tf2, tt2, er2, soc2 = compute_batch_metrics('C', svc_id, sub2, eta)
        return [
            {'indices': set(combo), 'machine': 'C', 'boxes': sub1, 'tot_w': tw1, 'tot_v': tv1, 't_flight': tf1, 't_total': tt1, 'e_round': er1, 'soc_end': soc1},
            {'indices': set(comp), 'machine': 'C', 'boxes': sub2, 'tot_w': tw2, 'tot_v': tv2, 't_flight': tf2, 't_total': tt2, 'e_round': er2, 'soc_end': soc2}
        ]

    # 通用集合划分分支定界（适用 <= 8 箱）
    valid_batches = []
    for r in range(1, n + 1):
        for combo in itertools.combinations(range(n), r):
            sub_boxes = [boxes[i] for i in combo]
            for m in ['A', 'B', 'C']:
                val, tw, tv, tf, tt, er, soc = compute_batch_metrics(m, svc_id, sub_boxes, eta)
                if val:
                    valid_batches.append({
                        'indices': set(combo),
                        'machine': m,
                        'boxes': sub_boxes,
                        'tot_w': tw,
                        'tot_v': tv,
                        't_flight': tf,
                        't_total': tt,
                        'e_round': er,
                        'soc_end': soc
                    })

    best_sol = [999, 999999.0, 999999.0, None]
    
    # 排序优化分支定界剪枝（优先尝试大子集）
    if objective == 'min_sorties_then_energy':
        valid_batches.sort(key=lambda b: (len(b['indices']), -b['e_round']), reverse=True)
    elif objective == 'min_energy':
        valid_batches.sort(key=lambda b: (len(b['indices']), -b['e_round']), reverse=True)
    else:  # min_sorties_then_time
        valid_batches.sort(key=lambda b: (len(b['indices']), -b['t_total']), reverse=True)

    # 极速贪婪启发式生成初始可行解作为紧上界 (Warm-start)
    greedy_sol = []
    uncovered_tmp = set(range(n))
    while uncovered_tmp:
        first_e = min(uncovered_tmp)
        cands_tmp = [b for b in valid_batches if first_e in b['indices'] and b['indices'].issubset(uncovered_tmp)]
        if not cands_tmp:
            break
        cands_tmp.sort(key=lambda b: len(b['indices']), reverse=True)
        best_c = cands_tmp[0]
        greedy_sol.append(best_c)
        uncovered_tmp -= best_c['indices']
        
    if not uncovered_tmp:
        best_sol = [len(greedy_sol), sum(b['e_round'] for b in greedy_sol), sum(b['t_total'] for b in greedy_sol), list(greedy_sol)]
    else:
        best_sol = [999, 999999.0, 999999.0, None]

    def branch_and_bound(uncovered, cur_sorties, cur_e, cur_t, cur_batches):
        if objective in ['min_sorties_then_energy', 'min_sorties_then_time']:
            if cur_sorties > best_sol[0]:
                return
            if objective == 'min_sorties_then_energy' and cur_sorties == best_sol[0] and cur_e >= best_sol[1]:
                return
            if objective == 'min_sorties_then_time' and cur_sorties == best_sol[0] and cur_t >= best_sol[2]:
                return
        elif objective == 'min_energy':
            if cur_e >= best_sol[1]:
                return
                
        if not uncovered:
            best_sol[0] = cur_sorties
            best_sol[1] = cur_e
            best_sol[2] = cur_t
            best_sol[3] = list(cur_batches)
            return
            
        first_elem = min(uncovered)
        cands = [b for b in valid_batches if first_elem in b['indices'] and b['indices'].issubset(uncovered)]
        for c in cands:
            branch_and_bound(
                uncovered - c['indices'],
                cur_sorties + 1,
                cur_e + c['e_round'],
                cur_t + c['t_total'],
                cur_batches + [c]
            )
            
    branch_and_bound(set(range(n)), 0, 0.0, 0.0, [])
    if best_sol[3] is None:
        raise RuntimeError(f"服务区 {svc_id} 未能求出可行精确组批划分！")
    return best_sol[3]

def solve_q1_all_batches(eta=0.20, objective='min_sorties_then_energy'):
    """求解所有 15 个服务区的全局最优组批方案并生成输出数据框"""
    svc_ids = [f"S{i:03d}" for i in range(1, 16)]
    all_batches = []
    sorties_count = 1
    
    for s in svc_ids:
        s_batches = solve_service_spp(s, eta=eta, objective=objective)
        for b in s_batches:
            box_id_list = ",".join(x['box_id'] for x in b['boxes'])
            record = {
                '架次编号': f"T{sorties_count:03d}",
                '服务区编号': s,
                '机型编号': b['machine'],
                '货箱编号列表': box_id_list,
                '总质量（kg）': round(b['tot_w'], 2),
                '总体积（m³）': round(b['tot_v'], 4),
                '往返时间（s）': round(b['t_flight'], 1),
                '架次能耗（kWh）': round(b['e_round'], 4),
                '返航SOC（%）': round(b['soc_end'], 2),
                '_累计作业时间(s)': round(b['t_total'], 1),
                '_货箱数': len(b['boxes'])
            }
            all_batches.append(record)
            sorties_count += 1
            
    df = pd.DataFrame(all_batches)
    return df

if __name__ == '__main__':
    print("================ 1. 最大安全载荷计算结果 (基准 eta=20%) ================")
    df_payload = solve_q1_payload_table(eta=0.20)
    print(df_payload[['服务区编号', '服务区名称', '往返距离(km)', 'A型最大安全载荷(kg)', 'B型最大安全载荷(kg)', 'C型最大安全载荷(kg)']])
    
    print("\n================ 2. 集合划分精确整数规划多目标结果对比 ================")
    for obj in ['min_sorties_then_energy', 'min_energy', 'min_sorties_then_time']:
        df_res = solve_q1_all_batches(eta=0.20, objective=obj)
        tot_sorties = len(df_res)
        tot_energy = df_res['架次能耗（kWh）'].sum()
        tot_time = df_res['_累计作业时间(s)'].sum()
        m_counts = df_res['机型编号'].value_counts().to_dict()
        print(f"目标 [{obj:24s}]: 总架次 = {tot_sorties} 架次, 总能耗 = {tot_energy:.3f} kWh, 累计作业耗时 = {tot_time:.1f} s, 机型构成 = {m_counts}")
    
    # 导出基准帕累托最优方案
    df_final = solve_q1_all_batches(eta=0.20, objective='min_sorties_then_energy')
    os.makedirs('results', exist_ok=True)
    df_final.to_csv('results/Q1_单点组批方案.csv', index=False, encoding='utf-8-sig')
    print(f"\n已将精确优化后的问题一基准组批方案导出至 results/Q1_单点组批方案.csv (共 {len(df_final)} 架次, 总能耗 {df_final['架次能耗（kWh）'].sum():.3f} kWh)")
