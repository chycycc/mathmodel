# -*- coding: utf-8 -*-
"""
问题一：单点往返运输能力与货箱组批优化（精确数学规划升级版）
包含：
1. 15个服务区在三种机型（A/B/C）下的最大安全载荷精确计算（二分数值搜索）
2. 返航安全余量 eta 敏感性分析 (10% ~ 35%)，每个 eta 重新求解组批
3. 基于集合划分（Set Partitioning Problem, SPP）与位掩码动态规划的精确组批求解
4. 多目标词典序对比（架次优先、能耗优先、时间优先）
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
    """返航安全余量敏感性分析，并重新求解每个 eta 下的完整组批方案。

    返回值保留每个 eta 的最大安全载荷表、完整组批表和汇总指标；
    这避免只改变载荷表而不重新验证全网架次和能耗。
    """
    etas = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
    details = {}
    summary_rows = []
    payload_rows = []
    for eta in etas:
        payload_df = solve_q1_payload_table(eta)
        batch_df = solve_q1_all_batches(eta, objective='min_sorties_then_energy')
        details[eta] = {
            'payload_table': payload_df,
            'batch_table': batch_df,
        }
        summary_rows.append({
            '安全余量eta': eta,
            '总架次': int(len(batch_df)),
            '总能耗(kWh)': float(batch_df['架次能耗（kWh）'].sum()),
            '累计作业时间(s)': float(batch_df['_累计作业时间(s)'].sum()),
            'A型架次': int((batch_df['机型编号'] == 'A').sum()),
            'B型架次': int((batch_df['机型编号'] == 'B').sum()),
            'C型架次': int((batch_df['机型编号'] == 'C').sum()),
        })
        payload_rows.extend(payload_df.assign(安全余量eta=eta).to_dict('records'))

    result = {
        'summary': pd.DataFrame(summary_rows),
        'details': details,
        'payload_table': pd.DataFrame(payload_rows),
    }
    return result

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
    针对单个服务区的货箱集合，采用集合划分（Set Partitioning）位掩码动态规划精确求解组批方案。
    对 S001 等货箱较多的服务区不再使用提前停止的启发式两批分支。
    objective 选项:
      - 'min_sorties_then_energy': (架次, 能耗, 时间) 词典序
      - 'min_energy': (能耗, 架次, 时间) 词典序
      - 'min_time': (时间, 架次, 能耗) 词典序
      - 'min_sorties_then_time': (架次, 时间, 能耗) 词典序
    """
    boxes = [b for b in dl.CARGO_BOXES if b['service_id'] == svc_id]
    n = len(boxes)

    if objective not in {'min_sorties_then_energy', 'min_energy', 'min_time', 'min_sorties_then_time'}:
        raise ValueError(f'不支持的目标: {objective}')

    # 枚举所有非空货箱子集和三种机型，形成集合划分候选列。
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

    # 用位掩码表示货箱集合。n=15 时状态数最多 2^15，避免启发式提前停止。
    candidate_masks = []
    by_first_bit = [[] for _ in range(n)]
    for batch in valid_batches:
        mask = 0
        for i in batch['indices']:
            mask |= 1 << i
        batch['_mask'] = mask
        idx = len(candidate_masks)
        candidate_masks.append(batch)
        for i in batch['indices']:
            by_first_bit[i].append(idx)

    def objective_key(raw):
        count, energy, total_time = raw
        if objective == 'min_sorties_then_energy':
            return (count, energy, total_time)
        if objective == 'min_energy':
            return (energy, count, total_time)
        if objective == 'min_time':
            return (total_time, count, energy)
        return (count, total_time, energy)

    @functools.lru_cache(maxsize=None)
    def solve_mask(mask):
        if mask == 0:
            return (0, 0.0, 0.0), ()
        first_bit = (mask & -mask).bit_length() - 1
        best_raw = None
        best_choice = None
        for candidate_idx in by_first_bit[first_bit]:
            candidate = candidate_masks[candidate_idx]
            candidate_mask = candidate['_mask']
            if candidate_mask & mask != candidate_mask:
                continue
            sub_raw, sub_choice = solve_mask(mask ^ candidate_mask)
            raw = (sub_raw[0] + 1,
                   sub_raw[1] + candidate['e_round'],
                   sub_raw[2] + candidate['t_total'])
            if best_raw is None or objective_key(raw) < objective_key(best_raw):
                best_raw = raw
                best_choice = (candidate_idx,) + sub_choice
        if best_raw is None:
            raise RuntimeError(f"服务区 {svc_id} 未能求出可行精确组批划分！")
        return best_raw, best_choice

    _, choice = solve_mask((1 << n) - 1)
    return [{k: v for k, v in candidate_masks[i].items() if k != '_mask'} for i in choice]

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
    
    # 导出基准词典序方案
    df_final = solve_q1_all_batches(eta=0.20, objective='min_sorties_then_energy')
    os.makedirs('results', exist_ok=True)
    df_final.to_csv('results/Q1_单点组批方案.csv', index=False, encoding='utf-8-sig')
    sensitivity = sensitivity_analysis_eta()
    sensitivity['summary'].to_csv('results/Q1_敏感性_eta_汇总.csv', index=False, encoding='utf-8-sig')
    sensitivity['payload_table'].to_csv('results/Q1_敏感性_eta_安全载荷.csv', index=False, encoding='utf-8-sig')
    print(f"\n已将精确优化后的问题一基准组批方案导出至 results/Q1_单点组批方案.csv (共 {len(df_final)} 架次, 总能耗 {df_final['架次能耗（kWh）'].sum():.3f} kWh)")
    print("已将每个 eta 重新求解后的敏感性结果导出至 results/Q1_敏感性_eta_汇总.csv 和 results/Q1_敏感性_eta_安全载荷.csv")
