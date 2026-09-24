# -*- coding: utf-8 -*-
"""
问题三：中继无人机动力学、能耗与通信物理接口模块
包含：
1. 中继无人机（机型 R）航段时序与能耗精确计算
2. 中继悬停点回传链路（G01）与接入链路（UAV）通视及损耗判定
3. 能源组件两阶段非线性等效充电模型
4. 中继架次物理状态机校验（周转时间、返航电量安全余量、库存占用）
"""
import os
import sys
import math
import numpy as np

# 加入上级 code 路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIR))
sys.path.insert(0, os.path.join(_WORKSPACE_ROOT, 'code'))
import data_loader as dl

# 中继悬停候选制高点定义
RELAY_POS_WEST = {
    'name': '西区制高点',
    'lon': 109.20214,
    'lat': 23.03643,
    'ground_elev': 431.6,
    'hover_z': 731.6  # 地面海拔 + 300m 悬停高度
}

RELAY_POS_EAST_SOUTH = {
    'name': '东区南部制高点',
    'lon': 109.27857,
    'lat': 23.03643,
    'ground_elev': 387.3,
    'hover_z': 687.3  # 地面海拔 + 300m 悬停高度
}

RELAY_POS_EAST_NORTH = {
    'name': '东区北部制高点',
    'lon': 109.27500,
    'lat': 23.04786,
    'ground_elev': 376.9,
    'hover_z': 676.9  # 地面海拔 + 300m 悬停高度
}

def get_relay_transit_info(relay_pos_dict):
    """
    计算中继无人机从 O01 出发到达指定悬停位置，以及从悬停位置返回 O01 的航段时序与能耗
    """
    r_params = dl.DRONE_PARAMS['R']
    pos_o01 = dl.NODES['O01']
    
    lon1, lat1, z_o01 = pos_o01['lon'], pos_o01['lat'], pos_o01['elev']
    lon2, lat2, z_hover = relay_pos_dict['lon'], relay_pos_dict['lat'], relay_pos_dict['hover_z']
    
    dist_m = dl.haversine_distance(lon1, lat1, lon2, lat2)
    
    # 航段采样计算最高地面海拔与巡航海拔（题面附录2：最高地面高程以上 50m）
    num_steps = max(20, int(dist_m / 30.0))
    lons = np.linspace(lon1, lon2, num_steps)
    lats = np.linspace(lat1, lat2, num_steps)
    elevs = [dl.get_dem_elevation(lo, la) for lo, la in zip(lons, lats)]
    max_ground = max(elevs)
    cruise_elev = max(max_ground + 50.0, z_hover) # 巡航海拔不低于最高地面+50m且不低于悬停高度
    
    # 去程：从 O01 地面爬升至巡航高度，巡航后下降至悬停高度
    climb_out = max(0.0, cruise_elev - z_o01)
    desc_out = max(0.0, cruise_elev - z_hover)
    t_climb_out = climb_out / r_params['v_climb']
    t_desc_out = desc_out / r_params['v_desc']
    t_cruise_out = dist_m / r_params['v_cruise']
    t_flight_out = t_climb_out + t_cruise_out + t_desc_out
    
    # 能耗计算：中继机起飞总质量 23.5kg，巡航功率 1.15kW，爬升效率 0.72，下降效率 0
    e_cruise_out = (dist_m / r_params['v_cruise']) * (r_params['p_cruise'] / 3600.0)
    e_climb_out = (r_params['m_takeoff'] * 9.80665 * climb_out) / (r_params['eta_climb'] * 3.6e6)
    e_flight_out = e_cruise_out + e_climb_out
    
    # 返程：从悬停高度爬升至巡航高度，巡航后下降至 O01 地面
    climb_back = max(0.0, cruise_elev - z_hover)
    desc_back = max(0.0, cruise_elev - z_o01)
    t_climb_back = climb_back / r_params['v_climb']
    t_desc_back = desc_back / r_params['v_desc']
    t_cruise_back = dist_m / r_params['v_cruise']
    t_flight_back = t_climb_back + t_cruise_back + t_desc_back
    
    e_cruise_back = (dist_m / r_params['v_cruise']) * (r_params['p_cruise'] / 3600.0)
    e_climb_back = (r_params['m_takeoff'] * 9.80665 * climb_back) / (r_params['eta_climb'] * 3.6e6)
    e_flight_back = e_cruise_back + e_climb_back
    
    return {
        'dist_m': dist_m,
        'cruise_elev': cruise_elev,
        't_out': t_flight_out,
        'e_out': e_flight_out,
        't_back': t_flight_back,
        'e_back': e_flight_back
    }

def compute_relay_sortie_metrics(relay_pos_dict, t_start, t_srv_end):
    """
    计算单个中继架次的完整物理时序、总能耗与返航 SOC
    t_start: 任务开始时刻（开始工位准备）
    t_srv_end: 服务结束时刻（准备返回 O01）
    """
    r_params = dl.DRONE_PARAMS['R']
    transit = get_relay_transit_info(relay_pos_dict)
    
    # 工位准备 180s
    t_prep = r_params['t_prep']
    t_depart = t_start + t_prep
    t_arrive = t_depart + transit['t_out']
    
    # 建链 30s
    t_link = r_params['t_link']
    t_link_done = t_arrive + t_link
    
    assert t_srv_end >= t_link_done, f"服务结束时刻 {t_srv_end} 必须不早于建链完成时刻 {t_link_done}"
    
    # 返程
    t_back_done = t_srv_end + transit['t_back']
    
    # 悬停与服务时间
    # 悬停时间 = 从到达时刻至服务结束时刻
    t_hover_total = t_srv_end - t_arrive
    t_service = t_srv_end - t_link_done
    
    # 悬停基础功率 1.05 kW，通信附加功率 0.05 kW (服务期间)
    e_hover = (r_params['p_hover'] * t_link + (r_params['p_hover'] + r_params['p_com']) * t_service) / 3600.0
    
    # 架次总能耗
    total_energy = transit['e_out'] + e_hover + transit['e_back']
    soc_end = (1.0 - total_energy / r_params['e_avail']) * 100.0
    
    # 能源组件两阶段充电时间 (全充时间 1800s)
    # 输入为剩余 SOC (0.0~1.0)
    recharge_time = dl.compute_recharge_time('R', soc_end / 100.0)
    battery_ready = t_back_done + recharge_time + 1.0 # 加 1s 缓冲
    
    return {
        't_start': t_start,
        't_depart': t_depart,
        't_arrive': t_arrive,
        't_link_done': t_link_done,
        't_srv_end': t_srv_end,
        't_back_done': t_back_done,
        't_service': t_service,
        'total_energy': total_energy,
        'soc_end': soc_end,
        'recharge_time': recharge_time,
        'battery_ready': battery_ready
    }

def verify_relay_link(relay_pos_dict, uav_pos):
    """
    验证中继与网关 G01 的回传链路、以及中继与运输无人机接入链路是否双向同时可用
    返回 (is_valid, backhaul_loss, access_loss)
    """
    pos_g01 = (dl.NODES['O01']['lon'], dl.NODES['O01']['lat'], dl.NODES['O01']['elev'] + dl.COM_PARAMS['G01']['hG'])
    r_pos = (relay_pos_dict['lon'], relay_pos_dict['lat'], relay_pos_dict['hover_z'])
    
    back_ok, back_loss, _ = dl.is_link_available(r_pos, 'Relay_backhaul', pos_g01, 'G01')
    if not back_ok:
        return False, back_loss, 999.0
        
    access_ok, access_loss, _ = dl.is_link_available(r_pos, 'Relay_access', uav_pos, 'UAV')
    return access_ok, back_loss, access_loss
