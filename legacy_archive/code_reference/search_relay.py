# -*- coding: utf-8 -*-
"""
中继无人机最优三维悬停坐标网格搜索脚本
目标：
1. 满足与 G01 的回传链路可用（损耗 <= 126 dB，优先视距通视）；
2. 满足离地净空 <= 300 米；
3. 最大化对目标服务区（作业点及航段）的接入链路覆盖度；
4. 探索是否可以采用 1 个或 2 个专用悬停点覆盖全部航迹。
"""

import sys
sys.path.insert(0, 'code')
import math
import numpy as np
import data_loader as dl

def main():
    g01_pos = (dl.NODES['O01']['lon'], dl.NODES['O01']['lat'], dl.NODES['O01']['elev'] + dl.COM_PARAMS['G01']['hG'])
    
    lons = [dl.NODES[k]['lon'] for k in dl.NODES]
    lats = [dl.NODES[k]['lat'] for k in dl.NODES]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    # 细化网格
    grid_lons = np.linspace(min_lon, max_lon, 35)
    grid_lats = np.linspace(min_lat, max_lat, 35)
    
    candidates = []
    for lo in grid_lons:
        for la in grid_lats:
            ground_z = dl.get_dem_elevation(lo, la)
            # 悬停在地面上方 280 米 (<= 300m 约束)
            hover_z = ground_z + 280.0
            relay_pos = (lo, la, hover_z)
            
            # 1. 检查中继机与 G01 的回传链路
            b_avail, b_loss, _ = dl.is_link_available(relay_pos, 'Relay_backhaul', g01_pos, 'G01')
            if not b_avail:
                continue
            
            b_los = dl.check_line_of_sight(relay_pos, g01_pos)
            
            # 2. 检查对 15 个服务区作业高度 (elev + 30) 的接入覆盖
            covered_services = []
            for s_id in sorted([k for k in dl.NODES if k.startswith('S')]):
                pos_s = (dl.NODES[s_id]['lon'], dl.NODES[s_id]['lat'], dl.NODES[s_id]['elev'] + 30.0)
                a_avail, a_loss, _ = dl.is_link_available(relay_pos, 'Relay_access', pos_s, 'UAV')
                if a_avail:
                    covered_services.append(s_id)
            
            candidates.append({
                'lon': float(lo),
                'lat': float(la),
                'ground_z': float(ground_z),
                'hover_z': float(hover_z),
                'cov_count': len(covered_services),
                'services': covered_services,
                'b_loss': float(b_loss),
                'b_los': b_los
            })
            
    print(f"找到与 G01 具备有效回传的候选悬停点数量: {len(candidates)}")
    candidates.sort(key=lambda x: (x['cov_count'], x['b_los'], -x['b_loss']), reverse=True)
    
    print("\n--- 覆盖服务区数量最多的前 5 个西部/中心悬停点 ---")
    for i, c in enumerate(candidates[:5]):
        print(f"Top {i+1}: 经度 {c['lon']:.5f}°, 纬度 {c['lat']:.5f}°, 地面高 {c['ground_z']:.1f}m, 悬停高 {c['hover_z']:.1f}m")
        print(f"       覆盖数: {c['cov_count']}/15, 回传损耗: {c['b_loss']:.1f}dB, 回传LOS: {c['b_los']}")
        print(f"       覆盖服务区: {', '.join(c['services'])}")

    # 专门针对东部服务区 [S002, S004, S010, S012, S013, S014] 搜索
    east_targets = ['S002', 'S004', 'S010', 'S012', 'S013', 'S014']
    east_cands = []
    grid_lons_e = np.linspace(109.23, 109.28, 20)
    grid_lats_e = np.linspace(23.01, 23.08, 20)
    for lo in grid_lons_e:
        for la in grid_lats_e:
            gz = dl.get_dem_elevation(lo, la)
            hz = gz + 280.0
            pos_r = (lo, la, hz)
            b_avail, b_loss, _ = dl.is_link_available(pos_r, 'Relay_backhaul', g01_pos, 'G01')
            if not b_avail:
                continue
            cov = [tid for tid in east_targets if dl.is_link_available(pos_r, 'Relay_access', (dl.NODES[tid]['lon'], dl.NODES[tid]['lat'], dl.NODES[tid]['elev'] + 30.0), 'UAV')[0]]
            east_cands.append({'lon': lo, 'lat': la, 'gz': gz, 'hz': hz, 'cov': cov, 'b_loss': b_loss})
    east_cands.sort(key=lambda x: len(x['cov']), reverse=True)
    print("\n--- 覆盖东部服务区最多的前 5 个悬停点 ---")
    for i, c in enumerate(east_cands[:5]):
        print(f"East Top {i+1}: 经度 {c['lon']:.5f}°, 纬度 {c['lat']:.5f}°, 地面 {c['gz']:.1f}m, 悬停 {c['hz']:.1f}m, 回传 {c['b_loss']:.1f}dB")
        print(f"          覆盖目标: {', '.join(c['cov'])}")

if __name__ == '__main__':
    main()
