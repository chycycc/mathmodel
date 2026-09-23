# -*- coding: utf-8 -*-
"""
问题二：异构无人机多点多架次时空协同调度模型（升级版 ALNS 算法）
核心技术架构：
1. 物理动力学与能耗积分器（compute_multistop_physics）：
   - 基于 30m DEM 栅格三维剖面，自适应积分巡航、爬升与交接卸载能耗；
   - 动态载荷逐段递减与 3/2 次方诱导气动阻力模型，严格校验返航 SOC >= 20%。
2. Clarke-Wright 航程节约多点回路挖掘器（_init_savings）：
   - 纯空间几何距离公式自动发掘多服务区回路候选，避免人工经验干预。
3. 扩展算子库的 ALNS 自适应大规模邻域搜索引擎（ALNS_VRPTW_Solver）：
   - 破坏算子：Random Removal（随机破坏）、Shaw Removal（时空相关性破坏）、Worst Removal（最坏边际代价破坏）；
   - 修复算子：Regret-2 Insertion（两阶段遗憾值插入）；
   - 局部搜索：双点回路邻接自适应合并（_merge_adjacent_sorties）；
   - 轮盘赌自适应权重调整与模拟退火 Metropolis 接受准则。
4. 事件驱动实体机与共享电池动态流水线评估器（simulate_pipeline）：
   - 严格维护 8 架实体机（A:4, B:2, C:2）与 14 组共享电池（A:6, B:4, C:4）双时间轴状态机；
   - 严格执行官方两阶段非线性等效充电模型（SOC < 0.90 占 65% 时间，SOC >= 0.90 占 35% 时间）；
   - 车电分离、异步解耦流水线周转，确保实体机与电池时间轴绝对无重叠冲突。
5. 标准结果持久化导出：
   - 生成符合竞赛组委会要求的 results/Q2_运输架次.csv 与 results/Q2_逐箱交付.csv。
"""

import os
import sys
import copy
import math
import random
import numpy as np
import pandas as pd

# 自适应工程工作区根路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code'))
import data_loader as dl

def get_box_deadline(b):
    """获取货箱的严格有效时限"""
    if b['is_first_batch'] and not pd.isna(b.get('first_deadline', np.nan)):
        return float(b['first_deadline'])
    return float(b.get('expect_time', 7200.0))

def compute_multistop_physics(m_type, visit_seq, box_allocations):
    """
    自适应计算多点回路的飞行时序与动态能耗
    visit_seq: 如 ['S015', 'S007'] 或 ['S001']
    box_allocations: {'S015': [boxes...], 'S007': [boxes...]}
    返回: (is_valid, total_flight_time, total_energy, soc_end, delivery_offsets)
    """
    params = dl.DRONE_PARAMS[m_type]
    all_boxes = []
    for s in visit_seq:
        all_boxes.extend(box_allocations.get(s, []))
        
    tot_w = sum(b['weight'] for b in all_boxes)
    tot_v = sum(b['volume'] for b in all_boxes)
    
    # 严格校验起飞质量与容积硬约束
    if tot_w > params['w_max'] + 1e-5 or tot_v > params['vol_max'] + 1e-6:
        return False, 0.0, 0.0, 0.0, {}
        
    cur_node = 'O01'
    cur_w = tot_w
    elapsed_flight = 0.0
    total_energy = 0.0
    delivery_offsets = {}
    
    for next_node in visit_seq:
        t_leg, e_leg = dl.compute_leg_flight(m_type, cur_node, next_node, cur_w)
        total_energy += e_leg
        elapsed_flight += t_leg
        
        # 卸载当前服务区的物资并结算交接时间
        s_boxes = box_allocations.get(next_node, [])
        n_box = len(s_boxes)
        t_handover = params['t_handover_base'] + n_box * params['t_handover_box']
        deliv_t = elapsed_flight + t_handover
        for b in s_boxes:
            delivery_offsets[b['box_id']] = deliv_t
            
        cur_w -= sum(b['weight'] for b in s_boxes)
        cur_node = next_node
        
    # 返航 O01 (空载返航，载荷为0)
    t_back, e_back = dl.compute_leg_flight(m_type, cur_node, 'O01', 0.0)
    total_energy += e_back
    elapsed_flight += t_back
    
    soc_end = (1.0 - total_energy / params['e_avail']) * 100.0
    # 校验返航电量安全余量下限 (SOC >= 20%)
    if soc_end < 20.0 - 1e-4:
        return False, 0.0, 0.0, 0.0, {}
        
    return True, elapsed_flight, total_energy, soc_end, delivery_offsets

def simulate_pipeline(candidate_sorties):
    """
    事件驱动实体机与共享电池流水线仿真评估器（ASAP-EDF Pipeline）
    严格执行两阶段非线性物理充电模型，实现实体机与共享电池无冲突周转
    """
    drones = {
        'U01': {'type': 'A', 'avail': 0.0},
        'U02': {'type': 'A', 'avail': 0.0},
        'U03': {'type': 'A', 'avail': 0.0},
        'U04': {'type': 'A', 'avail': 0.0},
        'U05': {'type': 'B', 'avail': 0.0},
        'U06': {'type': 'B', 'avail': 0.0},
        'U07': {'type': 'C', 'avail': 0.0},
        'U08': {'type': 'C', 'avail': 0.0},
    }
    
    batteries = {}
    for i in range(1, 7):
        batteries[f"BAT_A_{i:02d}"] = {'type': 'A', 'avail': 0.0}
    for i in range(1, 5):
        batteries[f"BAT_B_{i:02d}"] = {'type': 'B', 'avail': 0.0}
    for i in range(1, 5):
        batteries[f"BAT_C_{i:02d}"] = {'type': 'C', 'avail': 0.0}
        
    # 动态优先级排序：首批优先，再按最早有效截止时间排序（EDF）
    tasks = copy.deepcopy(candidate_sorties)
    def task_priority_key(t):
        boxes = t['boxes']
        has_first = any(b['is_first_batch'] for b in boxes)
        min_deadline = min(get_box_deadline(b) for b in boxes)
        return (0 if has_first else 1, min_deadline)
        
    tasks.sort(key=task_priority_key)
    
    sortie_records = []
    box_records = []
    
    for s_idx, task in enumerate(tasks, start=1):
        m = task['m_type']
        seq = task['visit_seq']
        b_list = task['boxes']
        alloc = {s: [b for b in b_list if b['service_id'] == s] for s in seq}
        
        val, t_flight, e_trip, soc_end, deliv_offsets = compute_multistop_physics(m, seq, alloc)
        if not val:
            return False, 1e9, 1e9, 999, 1e9, [], []
            
        params = dl.DRONE_PARAMS[m]
        n_box = len(b_list)
        t_prep_total = params['t_prep'] + n_box * params['t_load_per_box']
        
        avail_drones = [uid for uid, u in drones.items() if u['type'] == m]
        avail_batts = [bid for bid, b in batteries.items() if b['type'] == m]
        
        best_u, best_b = None, None
        best_start = 1e9
        
        # 寻找能够最早起飞的机电组合（ASAP策略）
        for uid in avail_drones:
            for bid in avail_batts:
                st = max(drones[uid]['avail'], batteries[bid]['avail'])
                if st < best_start:
                    best_start = st
                    best_u = uid
                    best_b = bid
                    
        # 向上取整至 0.1 秒，杜绝由于浮点数四舍五入引发的显示精度假冲突
        t_start = math.ceil(best_start * 10.0) / 10.0
        t_ground_handovers = sum(params['t_handover_base'] + len(alloc.get(s, [])) * params['t_handover_box'] for s in seq)
        t_end = math.ceil((t_start + t_prep_total + t_flight + t_ground_handovers) * 10.0) / 10.0
        
        # 核心修正：严格按照 0.0~1.0 小数量纲调用两阶段等效充电模型
        charge_dur = dl.compute_recharge_time(m, soc_end / 100.0)
        
        # 推进物理状态机：实体机返航后换电可再次起飞；卸下的电池进入充电桩（增加 1 秒换电与精度安全裕量）
        drones[best_u]['avail'] = t_end
        batteries[best_b]['avail'] = math.ceil((t_end + charge_dur) * 10.0) / 10.0 + 1.0
        
        seq_str = " -> ".join(seq)
        sortie_records.append({
            '架次编号': f"T{s_idx:03d}",
            '无人机编号': best_u,
            '机型编号': m,
            '电池编号': best_b,
            '开始时刻（s）': round(t_start, 1),
            '访问服务区顺序': seq_str,
            '返回O01时刻（s）': round(t_end, 1),
            '架次能耗（kWh）': round(e_trip, 3),
            '返航SOC（%）': round(soc_end, 2),
            '充电耗时（s）': round(charge_dur, 1),
            '电池就绪时刻（s）': round(t_end + charge_dur, 1)
        })
        
        for b in b_list:
            deliv_time = t_start + t_prep_total + deliv_offsets[b['box_id']]
            dl_val = get_box_deadline(b)
            exp_val = float(b.get('expect_time', 7200.0))
            box_records.append({
                '货箱编号': b['box_id'],
                '架次编号': f"T{s_idx:03d}",
                '服务区编号': b['service_id'],
                '交付完成时刻（s）': round(deliv_time, 1),
                '截止时限（s）': dl_val,
                '期望时限（s）': exp_val,
                '是否首批': b['is_first_batch'],
                '货物类型': b['box_id'].split('-')[1]
            })
            
    # 计算硬时限违约与软时限延误
    hard_violations = 0
    soft_delay = 0.0
    for br in box_records:
        t_deliv = br['交付完成时刻（s）']
        if br['是否首批'] or br['货物类型'] == 'MED':
            if t_deliv > br['截止时限（s）'] + 1e-4:
                hard_violations += 1
        if t_deliv > br['期望时限（s）']:
            soft_delay += (t_deliv - br['期望时限（s）'])
            
    makespan = max(sr['返回O01时刻（s）'] for sr in sortie_records)
    total_energy = sum(sr['架次能耗（kWh）'] for sr in sortie_records)
    feasible = (hard_violations == 0)
    
    return feasible, makespan, total_energy, hard_violations, soft_delay, sortie_records, box_records

def evaluate_cost(candidate_sorties, w_ms=2.0, w_e=20.0, w_viol=1e6, w_delay=0.1):
    """多目标综合代价评估函数"""
    feas, ms, en, viol, delay, _, _ = simulate_pipeline(candidate_sorties)
    if not feas:
        return viol * w_viol + ms * w_ms + en * w_e
    return ms * w_ms + en * w_e + delay * w_delay

class ALNS_VRPTW_Solver:
    """自适应大规模邻域搜索 (ALNS) 升级版求解器"""
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.all_boxes = copy.deepcopy(dl.CARGO_BOXES)
        self.box_map = {b['box_id']: b for b in self.all_boxes}
        self.svc_ids = [f"S{i:03d}" for i in range(1, 16)]
        self._init_savings()
        
    def _init_savings(self):
        """基于 Clarke-Wright 航程节约算法自动计算双点回路候选"""
        self.savings_pairs = []
        for i in range(len(self.svc_ids)):
            for j in range(i + 1, len(self.svc_ids)):
                s1, s2 = self.svc_ids[i], self.svc_ids[j]
                d01 = dl.get_path_profile('O01', s1)['dist_m']
                d02 = dl.get_path_profile('O01', s2)['dist_m']
                d12 = dl.get_path_profile(s1, s2)['dist_m']
                save = d01 + d02 - d12
                ratio = save / (d01 + d02)
                if save > 1000.0:  # 节约大于 1km
                    self.savings_pairs.append((save, ratio, s1, s2))
        self.savings_pairs.sort(key=lambda x: x[0], reverse=True)
        
    def construct_initial_solution(self):
        """自适应构造初始可行解（节约回路 + 0-1 背包贪婪）"""
        allocated_boxes = set()
        sorties = []
        
        # 1. 优先对首批保障物资进行临近合并或单点快速直达
        first_boxes = [b for b in self.all_boxes if b['is_first_batch']]
        by_svc_first = {}
        for b in first_boxes:
            by_svc_first.setdefault(b['service_id'], []).append(b)
            
        for save, ratio, s1, s2 in self.savings_pairs:
            b1 = by_svc_first.get(s1, [])
            b2 = by_svc_first.get(s2, [])
            b1_un = [b for b in b1 if b['box_id'] not in allocated_boxes]
            b2_un = [b for b in b2 if b['box_id'] not in allocated_boxes]
            if b1_un and b2_un:
                for m in ['C', 'B', 'A']:
                    val, _, _, _, _ = compute_multistop_physics(m, [s1, s2], {s1: b1_un, s2: b2_un})
                    if val:
                        sorties.append({'m_type': m, 'visit_seq': [s1, s2], 'boxes': b1_un + b2_un})
                        for b in b1_un + b2_un:
                            allocated_boxes.add(b['box_id'])
                        break
                        
        for sid, b_list in by_svc_first.items():
            unalloc = [b for b in b_list if b['box_id'] not in allocated_boxes]
            if unalloc:
                for m in ['A', 'B', 'C']:
                    val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: unalloc})
                    if val:
                        sorties.append({'m_type': m, 'visit_seq': [sid], 'boxes': unalloc})
                        for b in unalloc:
                            allocated_boxes.add(b['box_id'])
                        break
                        
        # 2. 对普通物资进行贪婪组批与合并
        rem_boxes = [b for b in self.all_boxes if b['box_id'] not in allocated_boxes]
        by_svc_rem = {}
        for b in rem_boxes:
            by_svc_rem.setdefault(b['service_id'], []).append(b)
            
        for sid, b_list in by_svc_rem.items():
            cur_list = list(b_list)
            while cur_list:
                best_batch = None
                best_m = None
                for m in ['C', 'B', 'A']:
                    params = dl.DRONE_PARAMS[m]
                    pack = []
                    tw, tv = 0.0, 0.0
                    for b in cur_list:
                        if tw + b['weight'] <= params['w_max'] and tv + b['volume'] <= params['vol_max']:
                            pack.append(b)
                            tw += b['weight']
                            tv += b['volume']
                    if pack:
                        val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: pack})
                        if val:
                            best_batch = pack
                            best_m = m
                            if m == 'C' and len(pack) >= 4:
                                break
                                
                if best_batch:
                    sorties.append({'m_type': best_m, 'visit_seq': [sid], 'boxes': best_batch})
                    for b in best_batch:
                        allocated_boxes.add(b['box_id'])
                        cur_list.remove(b)
                else:
                    b_single = cur_list.pop(0)
                    for m in ['A', 'B', 'C']:
                        val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: [b_single]})
                        if val:
                            sorties.append({'m_type': m, 'visit_seq': [sid], 'boxes': [b_single]})
                            allocated_boxes.add(b_single['box_id'])
                            break
                            
        sorties = self._merge_adjacent_sorties(sorties)
        return sorties
        
    def _merge_adjacent_sorties(self, sorties):
        """局部搜索：自适应合并邻近单点架次为多点回路"""
        improved = True
        while improved:
            improved = False
            for i in range(len(sorties)):
                for j in range(i + 1, len(sorties)):
                    s1, s2 = sorties[i], sorties[j]
                    if len(s1['visit_seq']) == 1 and len(s2['visit_seq']) == 1:
                        sid1 = s1['visit_seq'][0]
                        sid2 = s2['visit_seq'][0]
                        if sid1 != sid2:
                            d01 = dl.get_path_profile('O01', sid1)['dist_m']
                            d02 = dl.get_path_profile('O01', sid2)['dist_m']
                            d12 = dl.get_path_profile(sid1, sid2)['dist_m']
                            if (d01 + d02 - d12) > 1500.0:  # 节约 1.5km 以上
                                comb_boxes = s1['boxes'] + s2['boxes']
                                for m in ['A', 'B', 'C']:
                                    val, _, _, _, _ = compute_multistop_physics(m, [sid1, sid2], {sid1: s1['boxes'], sid2: s2['boxes']})
                                    if val:
                                        merged = {'m_type': m, 'visit_seq': [sid1, sid2], 'boxes': comb_boxes}
                                        new_sorties = [s for idx, s in enumerate(sorties) if idx not in (i, j)] + [merged]
                                        cost_old = evaluate_cost(sorties)
                                        cost_new = evaluate_cost(new_sorties)
                                        if cost_new < cost_old:
                                            sorties = new_sorties
                                            improved = True
                                            break
                                if improved:
                                    break
                if improved:
                    break
        return sorties

    def destroy_random(self, sorties, q=6):
        """破坏算子 1：随机破坏 (Random Removal)"""
        sorties_copy = copy.deepcopy(sorties)
        all_box_ids = [b['box_id'] for s in sorties_copy for b in s['boxes']]
        if len(all_box_ids) <= q:
            return sorties_copy, []
        remove_ids = set(random.sample(all_box_ids, q))
        removed_boxes = [self.box_map[bid] for bid in remove_ids]
        
        new_sorties = []
        for s in sorties_copy:
            rem_b = [b for b in s['boxes'] if b['box_id'] not in remove_ids]
            if rem_b:
                rem_services = list(dict.fromkeys(b['service_id'] for b in rem_b))
                s['boxes'] = rem_b
                s['visit_seq'] = rem_services
                new_sorties.append(s)
        return new_sorties, removed_boxes

    def destroy_shaw(self, sorties, q=6):
        """破坏算子 2：Shaw 空间与时效相关性破坏 (Shaw Removal)"""
        sorties_copy = copy.deepcopy(sorties)
        seed_box = random.choice(self.all_boxes)
        seed_sid = seed_box['service_id']
        seed_dl = get_box_deadline(seed_box)
        
        def relatedness(b):
            d = dl.get_path_profile(seed_sid, b['service_id'])['dist_m']
            t_diff = abs(seed_dl - get_box_deadline(b))
            return d / 1000.0 + t_diff / 600.0
            
        sorted_boxes = sorted(self.all_boxes, key=relatedness)
        remove_ids = set(b['box_id'] for b in sorted_boxes[:q])
        removed_boxes = [self.box_map[bid] for bid in remove_ids]
        
        new_sorties = []
        for s in sorties_copy:
            rem_b = [b for b in s['boxes'] if b['box_id'] not in remove_ids]
            if rem_b:
                rem_services = list(dict.fromkeys(b['service_id'] for b in rem_b))
                s['boxes'] = rem_b
                s['visit_seq'] = rem_services
                new_sorties.append(s)
        return new_sorties, removed_boxes

    def destroy_worst(self, sorties, q=6):
        """破坏算子 3：最坏边际代价破坏 (Worst Removal)"""
        sorties_copy = copy.deepcopy(sorties)
        box_scores = []
        for s in sorties_copy:
            m = s['m_type']
            boxes = s['boxes']
            for b in boxes:
                score = b['weight'] / dl.DRONE_PARAMS[m]['w_max'] + (2.0 if b['is_first_batch'] else 0.0)
                box_scores.append((score, b['box_id']))
                
        box_scores.sort(key=lambda x: x[0], reverse=True)
        p_len = min(len(box_scores), q * 2)
        candidates = [x[1] for x in box_scores[:p_len]]
        remove_ids = set(random.sample(candidates, min(q, len(candidates))))
        removed_boxes = [self.box_map[bid] for bid in remove_ids]
        
        new_sorties = []
        for s in sorties_copy:
            rem_b = [b for b in s['boxes'] if b['box_id'] not in remove_ids]
            if rem_b:
                rem_services = list(dict.fromkeys(b['service_id'] for b in rem_b))
                s['boxes'] = rem_b
                s['visit_seq'] = rem_services
                new_sorties.append(s)
        return new_sorties, removed_boxes

    def repair_regret(self, partial_sorties, removed_boxes, k=2):
        """修复算子：遗憾值插入 (Regret-2 Insertion)"""
        cur_sorties = copy.deepcopy(partial_sorties)
        unassigned = list(removed_boxes)
        
        while unassigned:
            regret_list = []
            for b in unassigned:
                sid = b['service_id']
                cand_costs = []
                
                # 尝试插入现有架次
                for s_idx, s in enumerate(cur_sorties):
                    if sid in s['visit_seq'] or len(s['visit_seq']) == 1:
                        new_seq = list(s['visit_seq'])
                        if sid not in new_seq:
                            new_seq.append(sid)
                        if len(new_seq) <= 2:
                            cand_boxes = s['boxes'] + [b]
                            alloc = {x: [bx for bx in cand_boxes if bx['service_id'] == x] for x in new_seq}
                            for m in ['A', 'B', 'C']:
                                val, _, _, _, _ = compute_multistop_physics(m, new_seq, alloc)
                                if val:
                                    trial_sorties = copy.deepcopy(cur_sorties)
                                    trial_sorties[s_idx] = {'m_type': m, 'visit_seq': new_seq, 'boxes': cand_boxes}
                                    c = evaluate_cost(trial_sorties)
                                    cand_costs.append((c, trial_sorties))
                                    
                # 尝试新开单点架次
                for m in ['A', 'B', 'C']:
                    val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: [b]})
                    if val:
                        trial_sorties = copy.deepcopy(cur_sorties) + [{'m_type': m, 'visit_seq': [sid], 'boxes': [b]}]
                        c = evaluate_cost(trial_sorties)
                        cand_costs.append((c, trial_sorties))
                        
                cand_costs.sort(key=lambda x: x[0])
                if not cand_costs:
                    trial_sorties = copy.deepcopy(cur_sorties) + [{'m_type': 'C', 'visit_seq': [sid], 'boxes': [b]}]
                    c = evaluate_cost(trial_sorties)
                    cand_costs.append((c, trial_sorties))
                    
                best_c = cand_costs[0][0]
                second_c = cand_costs[1][0] if len(cand_costs) > 1 else best_c + 500.0
                regret_val = second_c - best_c
                regret_list.append((regret_val, b, cand_costs[0][1]))
                
            regret_list.sort(key=lambda x: x[0], reverse=True)
            _, best_b, best_next_sol = regret_list[0]
            cur_sorties = best_next_sol
            unassigned.remove(best_b)
            
        return cur_sorties

    def solve(self, max_iter=50, temp_init=150.0, cooling_rate=0.96):
        """ALNS 优化主循环"""
        print(f"==========================================================")
        print(f"启动升级版 ALNS 算法求解问题二 (SEED={self.seed})")
        print(f"物理约束状态：两阶段非线性物理充电时钟已完全激活 (SOC < 0.9 占65%, SOC >= 0.9 占35%)")
        print(f"==========================================================")
        current_sol = self.construct_initial_solution()
        current_cost = evaluate_cost(current_sol)
        best_sol = copy.deepcopy(current_sol)
        best_cost = current_cost
        
        feas, ms, en, viol, deliv, sr, br = simulate_pipeline(current_sol)
        print(f"初始解状态: 可行={feas}, 架次={len(current_sol)}, Makespan={ms:.1f}s ({ms/3600:.2f}h), 能耗={en:.2f}kWh, 违约={viol}")
        
        temperature = temp_init
        operators = ['random', 'shaw', 'worst']
        op_weights = {'random': 1.0, 'shaw': 1.0, 'worst': 1.0}
        
        for it in range(1, max_iter + 1):
            tot_w = sum(op_weights.values())
            r_pick = random.random() * tot_w
            acc = 0.0
            chosen_op = 'random'
            for op, w in op_weights.items():
                acc += w
                if r_pick <= acc:
                    chosen_op = op
                    break
                    
            q_remove = random.randint(4, 8)
            if chosen_op == 'random':
                partial_sol, rem_boxes = self.destroy_random(current_sol, q=q_remove)
            elif chosen_op == 'shaw':
                partial_sol, rem_boxes = self.destroy_shaw(current_sol, q=q_remove)
            else:
                partial_sol, rem_boxes = self.destroy_worst(current_sol, q=q_remove)
                
            repaired_sol = self.repair_regret(partial_sol, rem_boxes, k=2)
            if it % 5 == 0:
                repaired_sol = self._merge_adjacent_sorties(repaired_sol)
                
            new_cost = evaluate_cost(repaired_sol)
            delta = new_cost - current_cost
            
            accept = False
            if delta < 0:
                accept = True
            elif random.random() < math.exp(-delta / max(temperature, 1e-4)):
                accept = True
                
            if accept:
                current_sol = repaired_sol
                current_cost = new_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_sol = copy.deepcopy(current_sol)
                    op_weights[chosen_op] += 2.0
                    f_b, ms_b, en_b, viol_b, _, _, _ = simulate_pipeline(best_sol)
                    print(f"  [迭代 {it:02d} / {max_iter}] 发现全局更优解! 可行={f_b}, 架次={len(best_sol)}, Makespan={ms_b/3600:.2f}h ({ms_b:.1f}s), 能耗={en_b:.2f}kWh, 违约={viol_b}")
                else:
                    op_weights[chosen_op] += 0.5
                    
            temperature *= cooling_rate
            
        feas, ms, en, viol, deliv, final_sr, final_br = simulate_pipeline(best_sol)
        print(f"\n==========================================================")
        print(f"升级版 ALNS 搜索完成!")
        print(f"最终性能指标: 可行={feas}, 总架次={len(best_sol)}, 完工耗时={ms:.1f}s ({ms/3600:.2f}h), 总能耗={en:.2f}kWh, 硬违约={viol}")
        print(f"==========================================================")
        return best_sol, final_sr, final_br

def run_solver_and_export():
    """执行求解并直接导出官方标准结果文件"""
    solver = ALNS_VRPTW_Solver(seed=42)
    best_sorties, sortie_records, box_records = solver.solve(max_iter=50)
    
    # 构造 DataFrame
    df_sorties = pd.DataFrame(sortie_records)
    df_boxes = pd.DataFrame(box_records)
    
    out_dir = os.path.join(_WORKSPACE_ROOT, 'results')
    os.makedirs(out_dir, exist_ok=True)
    
    p_sorties = os.path.join(out_dir, 'Q2_运输架次.csv')
    p_boxes = os.path.join(out_dir, 'Q2_逐箱交付.csv')
    
    # 严格按照官方提交模板字段导出
    cols_s = ['架次编号', '无人机编号', '机型编号', '电池编号', '开始时刻（s）', '访问服务区顺序', '返回O01时刻（s）', '架次能耗（kWh）']
    cols_b = ['货箱编号', '架次编号', '服务区编号', '交付完成时刻（s）']
    
    df_sorties[cols_s].to_csv(p_sorties, index=False, encoding='utf-8-sig')
    df_boxes[cols_b].to_csv(p_boxes, index=False, encoding='utf-8-sig')
    print(f"结果已成功导出至:\n  - {p_sorties}\n  - {p_boxes}")

if __name__ == '__main__':
    run_solver_and_export()
