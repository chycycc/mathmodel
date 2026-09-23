# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code'))
import data_loader as dl
import pandas as pd
import numpy as np

print("=== 基础参数核对 ===")
for m in ['A', 'B', 'C']:
    p = dl.DRONE_PARAMS[m]
    print(f"机型 {m}: 空载质量={p['m_empty']}kg, 最大载重={p['w_max']}kg, 最大容积={p['vol_max']}m^3, 速度={p['v_cruise']}m/s, 电池能量={p['e_avail']}kWh, 充电耗时={p['full_charge_time']}s, 电池库存={p['total_batteries']}")

df_s = pd.read_csv('results/Q2_运输架次.csv')
df_b = pd.read_csv('results/Q2_逐箱交付.csv')

print("\n=== 架次数据概览 ===")
print("总架次:", len(df_s))
print("机型分布:\n", df_s['机型编号'].value_counts())
print("总能耗:", df_s['架次能耗（kWh）'].sum())
print("最大完工时间 (s):", df_s['返回O01时刻（s）'].max(), f"({df_s['返回O01时刻（s）'].max()/3600:.2f} h)")

# 逐箱时限核验
print("\n=== 逐箱时限核验 ===")
box_map = {b['box_id']: b for b in dl.CARGO_BOXES}
df_b['是否首批'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['is_first_batch'])
df_b['首批时限'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['first_deadline'])
df_b['期望时限'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['expect_time'])
df_b['货物类型'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['type'])

hard_viols = 0
for _, row in df_b.iterrows():
    deliv = row['交付完成时刻（s）']
    if row['是否首批'] or row['货物类型'] == '医疗物资':
        deadline = row['首批时限'] if pd.notna(row['首批时限']) else row['期望时限']
        if deliv > deadline + 1e-4:
            print(f"违约: 货箱 {row['货箱编号']}, 送达 {deliv}, 时限 {deadline}")
            hard_viols += 1

print("硬约束违约箱数:", hard_viols)

# 实体机和电池时间线排查
print("\n=== 实体机使用重叠检查 ===")
for uid, grp in df_s.groupby('无人机编号'):
    grp = grp.sort_values('开始时刻（s）')
    prev_end = -1
    for _, r in grp.iterrows():
        st = r['开始时刻（s）']
        ed = r['返回O01时刻（s）']
        if st < prev_end - 1e-4:
            print(f"实体机冲突: {uid}, 上次结束 {prev_end}, 本次开始 {st}")
        prev_end = ed
print("实体机无重叠冲突检查完毕。")

print("\n=== 电池使用与充电间隔检查 ===")
for bid, grp in df_s.groupby('电池编号'):
    grp = grp.sort_values('开始时刻（s）')
    prev_end = None
    prev_m = None
    prev_e = None
    for _, r in grp.iterrows():
        st = r['开始时刻（s）']
        ed = r['返回O01时刻（s）']
        m = r['机型编号']
        e = r['架次能耗（kWh）']
        if prev_end is not None:
            soc_end = 1.0 - prev_e / dl.DRONE_PARAMS[prev_m]['e_avail']
            chg_time = dl.compute_recharge_time(prev_m, soc_end)
            ready_time = prev_end + chg_time
            gap = st - prev_end
            is_overlap = (st < ready_time - 1e-4)
            print(f"电池 {bid} (机型 {m}): 上次结束={prev_end:.1f}s, 能耗={prev_e:.2f}kWh, SOC={soc_end*100:.1f}%, 充饱需={chg_time:.1f}s, 本次开始={st:.1f}s, 间隔={gap:.1f}s, 理论就绪={ready_time:.1f}s, 是否早于充饱={is_overlap}")
        prev_end = ed
        prev_m = m
        prev_e = e
