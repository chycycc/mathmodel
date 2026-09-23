# -*- coding: utf-8 -*-
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code'))
import data_loader as dl

df_s = pd.read_csv('results/Q2_运输架次.csv')
df_b = pd.read_csv('results/Q2_逐箱交付.csv')

print('=== 运输架次基本数据 ===')
print('总架次:', len(df_s))
print('机型分布:\n', df_s['机型编号'].value_counts())
print('总能耗:', round(df_s['架次能耗（kWh）'].sum(), 3))
ms = df_s['返回O01时刻（s）'].max()
print('Makespan (s):', ms, f'({ms/3600:.2f}h, {ms/3600:.4f}h)')

print('\n=== 各机型能耗统计 ===')
for m, grp in df_s.groupby('机型编号'):
    print(f'机型 {m}: 架次={len(grp)}, 能耗={grp["架次能耗（kWh）"].sum():.3f}kWh')

print('\n=== 电池使用分布 (共14组) ===')
print(df_s['电池编号'].value_counts())
print('实际使用电池种类数:', df_s['电池编号'].nunique())

print('\n=== 无人机使用分布 (共8架) ===')
print(df_s['无人机编号'].value_counts())
print('实际使用实体机数:', df_s['无人机编号'].nunique())

print('\n=== 逐箱交付与时限检查 ===')
print('总交付箱数:', len(df_b))
box_map = {b['box_id']: b for b in dl.CARGO_BOXES}
df_b['是否首批'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['is_first_batch'])
df_b['首批时限'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['first_deadline'])
df_b['期望时限'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['expect_time'])
df_b['货物类型'] = df_b['货箱编号'].apply(lambda bid: box_map[bid]['type'])

hard_viols = 0
soft_delay_sec = 0.0
for _, r in df_b.iterrows():
    deliv = r['交付完成时刻（s）']
    exp_t = r['期望时限']
    if r['是否首批'] or r['货物类型'] == '医疗物资':
        dl_val = r['首批时限'] if pd.notna(r['首批时限']) else r['期望时限']
        if deliv > dl_val + 1e-4:
            hard_viols += 1
    if deliv > exp_t:
        soft_delay_sec += (deliv - exp_t)

print('硬时限违约数:', hard_viols)
print('软时限累计延迟 (s):', round(soft_delay_sec, 1))

# 检查所有架次返航 SOC
print('\n=== 返航 SOC 安全检查 ===')
min_soc = 100.0
for _, r in df_s.iterrows():
    m = r['机型编号']
    e = r['架次能耗（kWh）']
    soc = (1.0 - e / dl.DRONE_PARAMS[m]['e_avail']) * 100.0
    if soc < min_soc:
        min_soc = soc
print('最低返航 SOC:', f'{min_soc:.2f}%', '(要求 >= 20.0%)')
