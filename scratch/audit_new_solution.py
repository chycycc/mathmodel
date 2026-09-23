# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code'))
import data_loader as dl
from test_q2_alns_upgrade import Upgraded_ALNS_VRPTW_Solver, simulate_pipeline

solver = Upgraded_ALNS_VRPTW_Solver(seed=42)
best_sol, sr, br = solver.solve(max_iter=50)

df_s = pd.DataFrame(sr)
df_b = pd.DataFrame(br)

print("\n" + "="*50)
print("=== 新解详尽物理审查与审计 ===")
print("="*50)
print("总架次数:", len(df_s))
print("机型分布:\n", df_s['机型编号'].value_counts())
print("总能耗 (kWh):", round(df_s['架次能耗（kWh）'].sum(), 3))
print("完工时间 Makespan (s):", df_s['返回O01时刻（s）'].max(), f"({df_s['返回O01时刻（s）'].max()/3600:.3f} h)")

# 1. 实体机无冲突审计
drone_conflicts = 0
for uid, grp in df_s.groupby('无人机编号'):
    grp = grp.sort_values('开始时刻（s）')
    prev_end = -1
    for _, r in grp.iterrows():
        st = r['开始时刻（s）']
        ed = r['返回O01时刻（s）']
        if st < prev_end - 1e-4:
            print(f"实体机冲突! {uid}: 上次结束 {prev_end}, 本次开始 {st}")
            drone_conflicts += 1
        prev_end = ed
print("实体机冲突数:", drone_conflicts)

# 2. 共享电池充放电无冲突审计
batt_conflicts = 0
for bid, grp in df_s.groupby('电池编号'):
    grp = grp.sort_values('开始时刻（s）')
    prev_ready = -1
    for _, r in grp.iterrows():
        st = r['开始时刻（s）']
        rdy = r['电池就绪时刻（s）']
        chg = r['充电耗时（s）']
        if st < prev_ready - 1e-4:
            print(f"电池充放电冲突! {bid}: 上次就绪 {prev_ready}, 本次开始 {st}, 违背充电等待!")
            batt_conflicts += 1
        prev_ready = rdy
print("电池充放电冲突数:", batt_conflicts)

# 3. 返航 SOC 审计
min_soc = df_s['返航SOC（%）'].min()
print("最低返航 SOC (%):", min_soc, "(硬约束 >= 20.0%)")

# 4. 80箱全覆盖与不可拆分审计
delivered_boxes = set(df_b['货箱编号'])
print("总交付箱数:", len(df_b), "唯一箱数:", len(delivered_boxes), "(期望 80)")

# 5. 医疗与首批硬时限审计
hard_viols = 0
for _, r in df_b.iterrows():
    deliv = r['交付完成时刻（s）']
    if r['是否首批'] or r['货物类型'] == 'MED':
        dl_val = r['截止时限（s）']
        if deliv > dl_val + 1e-4:
            print(f"硬时限违约! 货箱 {r['货箱编号']}, 送达 {deliv}, 时限 {dl_val}")
            hard_viols += 1
print("硬约束违约箱数:", hard_viols)

# 6. 电池池各编号使用频次
print("\n各电池使用架次统计:")
print(df_s['电池编号'].value_counts())
