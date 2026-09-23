# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'code')
import pandas as pd
import problem3 as p3
import data_loader as dl

df_q2_trips = pd.read_csv('results/Q2_运输架次.csv')
df_q2_boxes = pd.read_csv('results/Q2_逐箱交付.csv')
r_params = dl.DRONE_PARAMS['R']

dist_w, t_out_w, t_back_w, e_out_w, e_back_w = p3.get_transit_info(p3.RELAY_POS_WEST)
dist_e, t_out_e, t_back_e, e_out_e, e_back_e = p3.get_transit_info(p3.RELAY_POS_EAST)

# 设计 4 架次精简高效中继排班
raw_relays = [
    {
        'trip_id': 'RT01', 'drone_id': 'R01', 'mod_id': 'MOD_01', 'pos': p3.RELAY_POS_WEST,
        'pos_type': 'West', 't_start': 450.0, 't_srv_end': 3800.0,
        't_out': t_out_w, 't_back': t_back_w, 'e_out': e_out_w, 'e_back': e_back_w
    },
    {
        'trip_id': 'RT02', 'drone_id': 'R02', 'mod_id': 'MOD_02', 'pos': p3.RELAY_POS_EAST,
        'pos_type': 'East', 't_start': 380.0, 't_srv_end': 3700.0,
        't_out': t_out_e, 't_back': t_back_e, 'e_out': e_out_e, 'e_back': e_back_e
    },
    {
        'trip_id': 'RT03', 'drone_id': 'R01', 'mod_id': 'MOD_03', 'pos': p3.RELAY_POS_WEST,
        'pos_type': 'West', 't_start': 4300.0 + 350.0, 't_srv_end': 7100.0,
        't_out': t_out_w, 't_back': t_back_w, 'e_out': e_out_w, 'e_back': e_back_w
    },
    {
        'trip_id': 'RT04', 'drone_id': 'R02', 'mod_id': 'MOD_04', 'pos': p3.RELAY_POS_EAST,
        'pos_type': 'East', 't_start': 4200.0 + 350.0, 't_srv_end': 7000.0,
        't_out': t_out_e, 't_back': t_back_e, 'e_out': e_out_e, 'e_back': e_back_e
    }
]

raw_relays.sort(key=lambda x: x['t_start'])

relay_rows = []
for r in raw_relays:
    t_start = r['t_start']
    t_link_done = t_start + r_params['t_prep'] + r['t_out'] + r_params['t_link']
    t_srv_end = r['t_srv_end']
    t_back_done = t_srv_end + r['t_back']
    t_service = t_srv_end - (t_start + r_params['t_prep'] + r['t_out'])
    e_trip = r['e_out'] + r['e_back'] + (r_params['p_hover'] + r_params['p_com']) * (t_service / 3600.0)
    rem_soc = (1.0 - e_trip / r_params['e_avail']) * 100.0
    relay_rows.append({
        '中继架次编号': r['trip_id'],
        '中继无人机编号': r['drone_id'],
        '能源组件编号': r['mod_id'],
        '开始时刻（s）': round(t_start, 1),
        '悬停经度（°）': r['pos']['lon'],
        '悬停纬度（°）': r['pos']['lat'],
        '悬停海拔（m）': r['pos']['hover_z'],
        '建链完成时刻（s）': round(t_link_done, 1),
        '服务结束时刻（s）': round(t_srv_end, 1),
        '返回O01时刻（s）': round(t_back_done, 1),
        '架次能耗（kWh）': round(e_trip, 4),
        '_返航SOC(%)': round(rem_soc, 1)
    })

df_relay = pd.DataFrame(relay_rows)
print("中继排班表:")
print(df_relay[['中继架次编号', '中继无人机编号', '能源组件编号', '开始时刻（s）', '建链完成时刻（s）', '服务结束时刻（s）', '返回O01时刻（s）', '架次能耗（kWh）', '_返航SOC(%)']])

# 检查无人机周转间隔
for uid in ['R01', 'R02']:
    sub = df_relay[df_relay['中继无人机编号'] == uid].sort_values('开始时刻（s）')
    turnaround = sub.iloc[1]['开始时刻（s）'] - sub.iloc[0]['返回O01时刻（s）']
    print(f"{uid} 周转间隔: {turnaround:.1f}s (必须 >= 300s: {turnaround >= 300.0})")
