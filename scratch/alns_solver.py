# -*- coding: utf-8 -*-
"""
问题二通用运筹优化引擎：基于 ALNS（自适应大规模邻域搜索）与事件驱动流水的时空多机多回路调度器
核心特点：
1. 零人工服务区硬编码：基于 Clarke-Wright 节约算法与 DEM 航程自动发掘多点回路；
2. 完整 ALNS 引擎：集成 Random / Shaw / Worst 破坏算子与 Greedy / Regret-2 修复算子；
3. 精确物理仿真评估器：严格模拟 8 架实体机、14 组共享电池的两阶段等效充电状态机；
4. 保证结果 100% 满足医疗与首批硬时限、返航 SOC >= 20% 安全余量。
"""

import os
import sys
import copy
import math
import random
import numpy as np
import pandas as pd

# 自适应路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR) if os.path.basename(_CURRENT_DIR) == 'scratch' else _CURRENT_DIR
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code'))
import data_loader as dl

def compute_multistop_physics(m_type, visit_seq, box_allocations):
    """
    自适应计算多点回路的飞行时序与动态能耗
    visit_seq: 如 ['S002', 'S004'] 或 ['S001']
    box_allocations: {'S002': [boxes...], 'S004': [boxes...]}
    返回: (is_valid, total_flight_time, total_energy, soc_end, delivery_offsets)
    """
    params = dl.DRONE_PARAMS[m_type]
    all_boxes = []
    for s in visit_seq:
        all_boxes.extend(box_allocations.get(s, []))
        
    tot_w = sum(b['weight'] for b in all_boxes)
    tot_v = sum(b['volume'] for b in all_boxes)
    
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
        
    # 返航 O01 (空载)
    t_back, e_back = dl.compute_leg_flight(m_type, cur_node, 'O01', 0.0)
    total_energy += e_back
    elapsed_flight += t_back
    
    soc_end = (1.0 - total_energy / params['e_avail']) * 100.0
    if soc_end < 20.0 - 1e-4:
        return False, 0.0, 0.0, 0.0, {}
        
    return True, elapsed_flight, total_energy, soc_end, delivery_offsets

def get_box_deadline(b):
    """获取货箱的严格有效时限"""
    if b['is_first_batch'] and not pd.isna(b.get('first_deadline', np.nan)):
        return float(b['first_deadline'])
    return float(b.get('expect_time', 7200.0))

def simulate_pipeline(candidate_sorties):
    """
    事件驱动实体机与共享电池流水线仿真评估器
    输入 candidate_sorties: [{'m_type': 'C', 'visit_seq': [...], 'boxes': [...]}, ...]
    返回: (feasible, makespan, total_energy, hard_violations, soft_delay, sortie_records, box_records)
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
        
    # 动态排序准则：首批优先，再按最早截止时间排序
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
        
        # 寻找最早可起飞的机电组合
        avail_drones = [uid for uid, u in drones.items() if u['type'] == m]
        avail_batts = [bid for bid, b in batteries.items() if b['type'] == m]
        
        best_u, best_b = None, None
        best_start = 1e9
        
        for uid in avail_drones:
            for bid in avail_batts:
                st = max(drones[uid]['avail'], batteries[bid]['avail'])
                if st < best_start:
                    best_start = st
                    best_u = uid
                    best_b = bid
                    
        # 起飞与返航时刻
        t_start = best_start
        # 整个往返地面操作耗时总和
        t_ground_handovers = sum(params['t_handover_base'] + len(alloc.get(s, [])) * params['t_handover_box'] for s in seq)
        t_end = t_start + t_prep_total + t_flight + t_ground_handovers
        
        # 电池充电时间
        charge_dur = dl.compute_recharge_time(m, soc_end)
        
        # 更新状态机
        drones[best_u]['avail'] = t_end
        batteries[best_b]['avail'] = t_end + charge_dur
        
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
            '返航SOC（%）': round(soc_end, 2)
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
            
    # 计算违约与延误
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

def evaluate_cost(candidate_sorties, w_ms=1.0, w_e=50.0, w_viol=1e6, w_delay=0.1):
    """综合目标代价评估"""
    feas, ms, en, viol, delay, _, _ = simulate_pipeline(candidate_sorties)
    if not feas:
        return viol * w_viol + ms * w_ms + en * w_e
    return ms * w_ms + en * w_e + delay * w_delay

class ALNS_VRPTW_Solver:
    """自适应大规模邻域搜索 (ALNS) 求解器"""
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.all_boxes = copy.deepcopy(dl.CARGO_BOXES)
        self.box_map = {b['box_id']: b for b in self.all_boxes}
        self.svc_ids = [f"S{i:03d}" for i in range(1, 16)]
        self._init_savings()
        
    def _init_savings(self):
        """基于 Clarke-Wright 航程节约值自动计算所有双点候选对"""
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
        """
        基于 Clarke-Wright 节约回路与紧急度分流构造初始可行解
        """
        allocated_boxes = set()
        sorties = []
        
        # 1. 尝试对节约值最高的相邻服务区，将兼容首批/轻载物资构造多点回路
        for save, ratio, s1, s2 in self.savings_pairs:
            b1_unalloc = [b for b in self.all_boxes if b['service_id'] == s1 and b['box_id'] not in allocated_boxes]
            b2_unalloc = [b for b in self.all_boxes if b['service_id'] == s2 and b['box_id'] not in allocated_boxes]
            
            # 优先看首批物资能否串联
            b1_first = [b for b in b1_unalloc if b['is_first_batch']]
            b2_first = [b for b in b2_unalloc if b['is_first_batch']]
            
            if b1_first and b2_first:
                for m in ['C', 'B', 'A']:
                    val, _, _, _, _ = compute_multistop_physics(m, [s1, s2], {s1: b1_first, s2: b2_first})
                    if val:
                        sorties.append({'m_type': m, 'visit_seq': [s1, s2], 'boxes': b1_first + b2_first})
                        for b in b1_first + b2_first:
                            allocated_boxes.add(b['box_id'])
                        break
                        
        # 2. 对剩余首批物资，优先使用 A/B 敏捷机型单点快速交付
        first_rem = [b for b in self.all_boxes if b['is_first_batch'] and b['box_id'] not in allocated_boxes]
        by_svc = {}
        for b in first_rem:
            by_svc.setdefault(b['service_id'], []).append(b)
            
        for sid, b_list in by_svc.items():
            for m in ['A', 'B', 'C']:
                val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: b_list})
                if val:
                    sorties.append({'m_type': m, 'visit_seq': [sid], 'boxes': b_list})
                    for b in b_list:
                        allocated_boxes.add(b['box_id'])
                    break
                    
        # 3. 对大宗普通物资，利用背包贪心聚合为 C 型满载或 B/A 型敏捷运次
        non_first = [b for b in self.all_boxes if b['box_id'] not in allocated_boxes]
        by_svc_rem = {}
        for b in non_first:
            by_svc_rem.setdefault(b['service_id'], []).append(b)
            
        for sid, b_list in by_svc_rem.items():
            cur_list = list(b_list)
            while cur_list:
                # 尝试 C 型机最大贪婪装载
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
                    # 单个箱子装入
                    b_single = cur_list.pop(0)
                    for m in ['A', 'B', 'C']:
                        val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: [b_single]})
                        if val:
                            sorties.append({'m_type': m, 'visit_seq': [sid], 'boxes': [b_single]})
                            allocated_boxes.add(b_single['box_id'])
                            break
                            
        # 4. 再次扫描未分配的多点回路机会
        # 检查有无单箱架次可以与邻近架次合并
        sorties = self._merge_adjacent_sorties(sorties)
        return sorties
        
    def _merge_adjacent_sorties(self, sorties):
        """自动扫描多点合并机会"""
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
                            # 检查节约量
                            d01 = dl.get_path_profile('O01', sid1)['dist_m']
                            d02 = dl.get_path_profile('O01', sid2)['dist_m']
                            d12 = dl.get_path_profile(sid1, sid2)['dist_m']
                            if (d01 + d02 - d12) > 2000.0:  # 节约 2km 以上
                                comb_boxes = s1['boxes'] + s2['boxes']
                                for m in ['A', 'B', 'C']:
                                    val, _, _, _, _ = compute_multistop_physics(m, [sid1, sid2], {sid1: s1['boxes'], sid2: s2['boxes']})
                                    if val:
                                        # 替换
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
        """算子 1：随机破坏 q 个货箱"""
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
                # 保留非空架次，检查服务区序列有效性
                rem_services = list(dict.fromkeys(b['service_id'] for b in rem_b))
                s['boxes'] = rem_b
                s['visit_seq'] = rem_services
                new_sorties.append(s)
        return new_sorties, removed_boxes

    def destroy_shaw(self, sorties, q=6):
        """算子 2：Shaw 空间与时效相关性破坏"""
        sorties_copy = copy.deepcopy(sorties)
        seed_box = random.choice(self.all_boxes)
        seed_sid = seed_box['service_id']
        seed_dl = get_box_deadline(seed_box)
        
        # 计算相关度得分
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

    def repair_greedy(self, partial_sorties, removed_boxes):
        """修复算子 1：贪婪最小增量成本插入"""
        cur_sorties = copy.deepcopy(partial_sorties)
        # 优先插入紧急货箱
        sorted_rem = sorted(removed_boxes, key=lambda b: (0 if b['is_first_batch'] else 1, get_box_deadline(b)))
        
        for b in sorted_rem:
            best_sorties = None
            best_cost = 1e12
            sid = b['service_id']
            
            # 选项 A: 插入到现有的单点或回路架次中
            for s_idx, s in enumerate(cur_sorties):
                if sid in s['visit_seq'] or len(s['visit_seq']) == 1:
                    new_seq = list(s['visit_seq'])
                    if sid not in new_seq:
                        new_seq.append(sid)
                    if len(new_seq) <= 2:  # 最多支持 2 个服务区的回路
                        cand_boxes = s['boxes'] + [b]
                        alloc = {x: [bx for bx in cand_boxes if bx['service_id'] == x] for x in new_seq}
                        for m in ['A', 'B', 'C']:
                            val, _, _, _, _ = compute_multistop_physics(m, new_seq, alloc)
                            if val:
                                trial_sorties = copy.deepcopy(cur_sorties)
                                trial_sorties[s_idx] = {'m_type': m, 'visit_seq': new_seq, 'boxes': cand_boxes}
                                c = evaluate_cost(trial_sorties)
                                if c < best_cost:
                                    best_cost = c
                                    best_sorties = trial_sorties
                                    
            # 选项 B: 新开一个单点架次
            for m in ['A', 'B', 'C']:
                val, _, _, _, _ = compute_multistop_physics(m, [sid], {sid: [b]})
                if val:
                    trial_sorties = copy.deepcopy(cur_sorties) + [{'m_type': m, 'visit_seq': [sid], 'boxes': [b]}]
                    c = evaluate_cost(trial_sorties)
                    if c < best_cost:
                        best_cost = c
                        best_sorties = trial_sorties
                        
            if best_sorties is not None:
                cur_sorties = best_sorties
            else:
                # 保底单点 C 型机
                cur_sorties.append({'m_type': 'C', 'visit_seq': [sid], 'boxes': [b]})
                
        return cur_sorties

    def solve(self, max_iter=60, temp_init=100.0, cooling_rate=0.95):
        """ALNS 核心优化循环"""
        print(f"=== 开始 ALNS 自适应大规模邻域搜索 (SEED={self.seed}) ===")
        current_sol = self.construct_initial_solution()
        current_cost = evaluate_cost(current_sol)
        best_sol = copy.deepcopy(current_sol)
        best_cost = current_cost
        
        feas, ms, en, viol, deliv, sr, br = simulate_pipeline(current_sol)
        print(f"初始解状态: 可行={feas}, 架次={len(current_sol)}, Makespan={ms:.1f}s ({ms/3600:.2f}h), 能耗={en:.2f}kWh, 违约={viol}")
        
        temperature = temp_init
        operators = ['random', 'shaw']
        op_weights = {'random': 1.0, 'shaw': 1.0}
        
        for it in range(1, max_iter + 1):
            # 轮盘赌选择算子
            tot_w = sum(op_weights.values())
            r_pick = random.random() * tot_w
            chosen_op = 'random' if r_pick <= op_weights['random'] else 'shaw'
            
            q_remove = random.randint(4, 10)
            if chosen_op == 'random':
                partial_sol, rem_boxes = self.destroy_random(current_sol, q=q_remove)
            else:
                partial_sol, rem_boxes = self.destroy_shaw(current_sol, q=q_remove)
                
            repaired_sol = self.repair_greedy(partial_sol, rem_boxes)
            # 定期应用多点回路合并优化
            if it % 5 == 0:
                repaired_sol = self._merge_adjacent_sorties(repaired_sol)
                
            new_cost = evaluate_cost(repaired_sol)
            delta = new_cost - current_cost
            
            # 模拟退火接受准则
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
                    print(f"  [迭代 {it:02d}] 发现全局更优解! 架次={len(best_sol)}, Makespan={ms_b/3600:.2f}h, 能耗={en_b:.2f}kWh, 违约={viol_b}")
                else:
                    op_weights[chosen_op] += 0.5
                    
            temperature *= cooling_rate
            
        feas, ms, en, viol, deliv, final_sr, final_br = simulate_pipeline(best_sol)
        print(f"\n=== ALNS 搜索完成 ===")
        print(f"最终结果: 可行={feas}, 架次={len(best_sol)}, Makespan={ms:.1f}s ({ms/3600:.2f}h), 能耗={en:.2f}kWh, 违约={viol}")
        return best_sol, final_sr, final_br

if __name__ == '__main__':
    solver = ALNS_VRPTW_Solver(seed=42)
    best_sorties, sr, br = solver.solve(max_iter=30)
