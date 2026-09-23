# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'code')
import data_loader as dl

print("=== 问题 1：最大安全载荷计算 ===")
svc_ids = [f"S{i:03d}" for i in range(1, 16)]
drone_types = ['A', 'B', 'C']

for s in svc_ids:
    line = f"{s} ({dl.NODES[s]['name']}): "
    prof = dl.get_path_profile('O01', s)
    dist_km = prof['dist_m'] / 1000.0
    line += f"距离={dist_km:.2f}km, 巡航海拔={prof['cruise_elev']:.1f}m | "
    for m in drone_types:
        w_max = dl.DRONE_PARAMS[m]['w_max']
        e_avail = dl.DRONE_PARAMS[m]['e_avail']
        t_out0, e_out0 = dl.compute_leg_flight(m, 'O01', s, 0.0)
        t_back0, e_back0 = dl.compute_leg_flight(m, s, 'O01', 0.0)
        e_round0 = e_out0 + e_back0
        if e_round0 > 0.8 * e_avail:
            w_safe = 0.0
        else:
            t_out_full, e_out_full = dl.compute_leg_flight(m, 'O01', s, w_max)
            e_round_full = e_out_full + e_back0
            if e_round_full <= 0.8 * e_avail:
                w_safe = w_max
            else:
                low, high = 0.0, w_max
                for _ in range(40):
                    mid = (low + high) / 2.0
                    _, eo = dl.compute_leg_flight(m, 'O01', s, mid)
                    if eo + e_back0 <= 0.8 * e_avail:
                        low = mid
                    else:
                        high = mid
                w_safe = low
        line += f"{m}:{w_safe:.1f}kg({w_safe/w_max*100:.0f}%) "
    print(line)
