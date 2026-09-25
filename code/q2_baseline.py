# -*- coding: utf-8 -*-
"""
Q2 基线方案深度解析与四维时空航段轨迹提取模块
功能：
1. 读取 results/Q2_运输架次.csv 与 results/Q2_逐箱交付.csv；
2. 逐架次、逐航段分解爬升、巡航、下降、物资交接与装载工序；
3. 核验返回时刻与能耗是否 100% 与 Q2 基线一致；
4. 返回供问题三（通信判定）与问题四（资源核算）使用的结构化时空数据。
"""
import os
import sys
import pandas as pd
import numpy as np

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)
sys.path.insert(0, _CURRENT_DIR)

import data_loader as dl

def parse_and_verify_q2(results_dir=None):
    """
    解析并验证 Q2 基线结果，返回验证通过的架次时空轨迹列表
    """
    if results_dir is None:
        results_dir = os.path.join(_WORKSPACE_ROOT, 'results')
        
    fp_trips = os.path.join(results_dir, 'Q2', 'Q2_运输架次.csv')
    if not os.path.exists(fp_trips):
        fp_trips = os.path.join(results_dir, 'Q2_运输架次.csv')
        
    fp_boxes = os.path.join(results_dir, 'Q2', 'Q2_逐箱交付.csv')
    if not os.path.exists(fp_boxes):
        fp_boxes = os.path.join(results_dir, 'Q2_逐箱交付.csv')
        
    if not os.path.exists(fp_trips) or not os.path.exists(fp_boxes):
        raise FileNotFoundError(f"未找到 Q2 结果文件: {fp_trips} 或 {fp_boxes}")
        
    df_trips = pd.read_csv(fp_trips)
    df_boxes = pd.read_csv(fp_boxes)
    
    # 建立货箱字典
    box_map = {b['box_id']: b for b in dl.CARGO_BOXES}
    
    # 统计每个架次分配的货箱
    trip_boxes = {}
    for _, row in df_boxes.iterrows():
        tid = row['架次编号']
        bid = row['货箱编号']
        sid = row['服务区编号']
        t_deliv = float(row['交付完成时刻（s）'])
        trip_boxes.setdefault(tid, []).append((bid, sid, t_deliv))
        
    verified_trips = []
    
    for idx, row in df_trips.iterrows():
        tid = row['架次编号']
        drone_id = row['无人机编号']
        m_type = row['机型编号']
        bat_id = row['电池编号']
        t_start = float(row['开始时刻（s）'])
        route_str = row['访问服务区顺序']
        t_back_reported = float(row['返回O01时刻（s）'])
        e_reported = float(row['架次能耗（kWh）'])
        
        route = [s.strip() for s in route_str.split('->')]
        nodes = ['O01'] + route + ['O01']
        
        boxes = trip_boxes[tid]
        boxes_at_node = {}
        for bid, sid, t_deliv in boxes:
            boxes_at_node.setdefault(sid, []).append((bid, t_deliv))
            
        # 航段递推
        params = dl.DRONE_PARAMS[m_type]
        t_prep_total = params['t_prep'] + len(boxes) * params['t_load_per_box']
        
        total_w = sum(box_map[b[0]]['weight'] for b in boxes)
        cur_w = total_w
        cur_t = t_start + t_prep_total # 准备装载结束即实际起飞时刻
        phases = []
        
        phases.append({
            'trip_id': tid,
            'phase': '工位准备与装载',
            'from_node': 'O01',
            'to_node': 'O01',
            't_start': t_start,
            't_end': cur_t,
            'start_coord': (dl.NODES['O01']['lon'], dl.NODES['O01']['lat'], dl.NODES['O01']['elev']),
            'end_coord': (dl.NODES['O01']['lon'], dl.NODES['O01']['lat'], dl.NODES['O01']['elev'])
        })
        
        calc_energy = 0.0
        
        for leg_idx in range(len(nodes) - 1):
            u = nodes[leg_idx]
            v = nodes[leg_idx + 1]
            prof = dl.get_path_profile(u, v)
            
            # 航段耗时分解
            t_climb = prof['climb_h'] / params['v_climb']
            t_cruise = prof['dist_m'] / params['v_cruise']
            t_desc = prof['desc_h'] / params['v_desc']
            
            # 航段能耗
            w_ratio = cur_w / params['w_max']
            r_w = params['r_empty'] - (w_ratio ** 1.5) * (params['r_empty'] - params['r_full'])
            e_cruise = (prof['dist_m'] / r_w) * params['e_avail']
            m_total = params['m_empty'] + cur_w
            e_climb = (m_total * 9.80665 * prof['climb_h']) / (params['eta_climb'] * 3.6e6)
            calc_energy += (e_cruise + e_climb)
            
            # 1. 爬升
            p_climb_start = cur_t
            p_climb_end = cur_t + t_climb
            phases.append({
                'trip_id': tid,
                'phase': f'{u}->{v} 爬升',
                'from_node': u,
                'to_node': v,
                't_start': p_climb_start,
                't_end': p_climb_end,
                'start_coord': (dl.NODES[u]['lon'], dl.NODES[u]['lat'], prof['z_start']),
                'end_coord': (dl.NODES[u]['lon'], dl.NODES[u]['lat'], prof['cruise_elev'])
            })
            
            # 2. 巡航
            p_cruise_start = p_climb_end
            p_cruise_end = p_cruise_start + t_cruise
            phases.append({
                'trip_id': tid,
                'phase': f'{u}->{v} 巡航',
                'from_node': u,
                'to_node': v,
                't_start': p_cruise_start,
                't_end': p_cruise_end,
                'start_coord': (dl.NODES[u]['lon'], dl.NODES[u]['lat'], prof['cruise_elev']),
                'end_coord': (dl.NODES[v]['lon'], dl.NODES[v]['lat'], prof['cruise_elev'])
            })
            
            # 3. 下降
            p_desc_start = p_cruise_end
            p_desc_end = p_desc_start + t_desc
            phases.append({
                'trip_id': tid,
                'phase': f'{u}->{v} 下降',
                'from_node': u,
                'to_node': v,
                't_start': p_desc_start,
                't_end': p_desc_end,
                'start_coord': (dl.NODES[v]['lon'], dl.NODES[v]['lat'], prof['cruise_elev']),
                'end_coord': (dl.NODES[v]['lon'], dl.NODES[v]['lat'], prof['z_end'])
            })
            
            cur_t = p_desc_end
            
            # 若不是最后回到 O01，则有物资交接
            if v != 'O01':
                n_b = len(boxes_at_node[v])
                t_handover = params['t_handover_base'] + n_b * params['t_handover_box']
                phases.append({
                    'trip_id': tid,
                    'phase': f'{v} 物资交接',
                    'from_node': v,
                    'to_node': v,
                    't_start': cur_t,
                    't_end': cur_t + t_handover,
                    'start_coord': (dl.NODES[v]['lon'], dl.NODES[v]['lat'], prof['z_end']),
                    'end_coord': (dl.NODES[v]['lon'], dl.NODES[v]['lat'], prof['z_end'])
                })
                cur_t += t_handover
                # 校验交付时刻
                for bid, t_deliv in boxes_at_node[v]:
                    diff_deliv = abs(cur_t - t_deliv)
                    assert diff_deliv < 0.1, f"架次 {tid} 货箱 {bid} 交付时刻不一致: 计算={cur_t:.1f}, 记录={t_deliv:.1f}"
                # 扣除卸下载荷
                cur_w -= sum(box_map[b[0]]['weight'] for b in boxes_at_node[v])
                
        diff_back = abs(cur_t - t_back_reported)
        diff_e = abs(calc_energy - e_reported)
        assert diff_back < 0.1, f"架次 {tid} 返回时刻不一致: 计算={cur_t:.1f}, 记录={t_back_reported:.1f}"
        assert diff_e < 1e-4, f"架次 {tid} 能耗不一致: 计算={calc_energy:.6f}, 记录={e_reported:.6f}"
        
        verified_trips.append({
            'trip_id': tid,
            'drone_id': drone_id,
            'm_type': m_type,
            'bat_id': bat_id,
            't_start': t_start,
            't_back': cur_t,
            'energy': calc_energy,
            'phases': phases
        })
        
    return verified_trips

if __name__ == '__main__':
    trips = parse_and_verify_q2()
    print(f"成功解析并验证全部 {len(trips)} 个 Q2 运输架次！")
