# -*- coding: utf-8 -*-
import sys
import os
import copy
import math
import random
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code'))
import data_loader as dl

def get_box_deadline(b):
    if b['is_first_batch'] and not pd.isna(b.get('first_deadline', np.nan)):
        return float(b['first_deadline'])
    return float(b.get('expect_time', 7200.0))

def compute_multistop_physics(m_type, visit_seq, box_allocations):
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
        
        s_boxes = box_allocations.get(next_node, [])
        n_box = len(s_boxes)
        t_handover = params['t_handover_base'] + n_box * params['t_handover_box']
        deliv_t = elapsed_flight + t_handover
        for b in s_boxes:
            delivery_offsets[b['box_id']] = deliv_t
            
        cur_w -= sum(b['weight'] for b in s_boxes)
        cur_node = next_node
        
    t_back, e_back = dl.compute_leg_flight(m_type, cur_node, 'O01', 0.0)
    total_energy += e_back
    elapsed_flight += t_back
    
    soc_end = (1.0 - total_energy / params['e_avail']) * 100.0
    if soc_end < 20.0 - 1e-4:
        return False, 0.0, 0.0, 0.0, {}
        
    return True, elapsed_flight, total_energy, soc_end, delivery_offsets

def simulate_pipeline(candidate_sorties):
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
        
        for uid in avail_drones:
            for bid in avail_batts:
                st = max(drones[uid]['avail'], batteries[bid]['avail'])
                if st < best_start:
                    best_start = st
                    best_u = uid
                    best_b = bid
                    
        t_start = best_start
        t_ground_handovers = sum(params['t_handover_base'] + len(alloc.get(s, [])) * params['t_handover_box'] for s in seq)
        t_end = t_start + t_prep_total + t_flight + t_ground_handovers
        
        # 严格真实两阶段等效充电
        charge_dur = dl.compute_recharge_time(m, soc_end / 100.0)
        
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
    feas, ms, en, viol, delay, _, _ = simulate_pipeline(candidate_sorties)
    if not feas:
        return viol * w_viol + ms * w_ms + en * w_e
    return ms * w_ms + en * w_e + delay * w_delay

class Upgraded_ALNS_VRPTW_Solver:
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.all_boxes = copy.deepcopy(dl.CARGO_BOXES)
        self.box_map = {b['box_id']: b for b in self.all_boxes}
        self.svc_ids = [f"S{i:03d}" for i in range(1, 16)]
        self._init_savings()
        
    def _init_savings(self):
        self.savings_pairs = []
        for i in range(len(self.svc_ids)):
            for j in range(i + 1, len(self.svc_ids)):
                s1, s2 = self.svc_ids[i], self.svc_ids[j]
                d01 = dl.get_path_profile('O01', s1)['dist_m']
                d02 = dl.get_path_profile('O01', s2)['dist_m']
                d12 = dl.get_path_profile(s1, s2)['dist_m']
                save = d01 + d02 - d12
                ratio = save / (d01 + d02)
                if save > 1000.0:
                    self.savings_pairs.append((save, ratio, s1, s2))
        self.savings_pairs.sort(key=lambda x: x[0], reverse=True)
        
    def construct_initial_solution(self):
        allocated_boxes = set()
        sorties = []
        
        # 1. 优先对首批物资进行配对或单点快速保障
        first_boxes = [b for b in self.all_boxes if b['is_first_batch']]
        by_svc_first = {}
        for b in first_boxes:
            by_svc_first.setdefault(b['service_id'], []).append(b)
            
        # 尝试将相邻服务区的首批物资合并
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
                        
        # 剩余首批物资单点直达
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
                            if (d01 + d02 - d12) > 1500.0:
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
        """破坏算子 3：最坏边际能耗与延误破坏 (Worst Removal)"""
        sorties_copy = copy.deepcopy(sorties)
        box_scores = []
        for s_idx, s in enumerate(sorties_copy):
            m = s['m_type']
            boxes = s['boxes']
            base_e = sum(b['weight'] for b in boxes)
            for b in boxes:
                # 评估货箱的单箱重与时限紧迫度
                score = b['weight'] / dl.DRONE_PARAMS[m]['w_max'] + (1.0 if b['is_first_batch'] else 0.0) * 2.0
                box_scores.append((score, b['box_id']))
                
        box_scores.sort(key=lambda x: x[0], reverse=True)
        # 加权随机选取
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

    def solve(self, max_iter=60, temp_init=150.0, cooling_rate=0.96):
        print(f"=== 启动升级版 ALNS (真实两阶段物理充电 + Worst Removal) ===")
        current_sol = self.construct_initial_solution()
        current_cost = evaluate_cost(current_sol)
        best_sol = copy.deepcopy(current_sol)
        best_cost = current_cost
        
        feas, ms, en, viol, deliv, sr, br = simulate_pipeline(current_sol)
        print(f"初始解: 可行={feas}, 架次={len(current_sol)}, Makespan={ms:.1f}s ({ms/3600:.2f}h), 能耗={en:.2f}kWh, 违约={viol}")
        
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
        print(f"\n=== ALNS 优化完成 ===")
        print(f"最终性能: 可行={feas}, 总架次={len(best_sol)}, Makespan={ms:.1f}s ({ms/3600:.2f}h), 能耗={en:.2f}kWh, 违约={viol}")
        return best_sol, final_sr, final_br

if __name__ == '__main__':
    solver = Upgraded_ALNS_VRPTW_Solver(seed=42)
    best_sol, sr, br = solver.solve(max_iter=50)
