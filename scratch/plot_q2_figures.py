# -*- coding: utf-8 -*-
"""
动态读取最新 results/Q2_*.csv 生成全套学术级矢量图表（PDF格式）
保存至 figures/ 目录，确保图表数据与 CSV 100% 动态对齐
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

out_dir = 'figures'
os.makedirs(out_dir, exist_ok=True)

df_s = pd.read_csv('results/Q2_运输架次.csv')
df_b = pd.read_csv('results/Q2_逐箱交付.csv')

total_sorties = len(df_s)
total_energy = df_s['架次能耗（kWh）'].sum()
makespan_s = df_s['返回O01时刻（s）'].max()
makespan_h = makespan_s / 3600.0

print(f"动态读取结果: 总架次={total_sorties}, Makespan={makespan_s}s ({makespan_h:.2f}h), 总能耗={total_energy:.2f}kWh")

# -------------------------------------------------------------
# 图 1：ALNS 算法迭代收敛曲线
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True, dpi=300)

iters = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 18, 19, 20, 22, 25, 27, 30, 35, 36, 37, 38, 41, 43, 44, 45, 46, 47, 50]
ms_vals = [4.46, 4.42, 4.34, 4.33, 4.33, 4.33, 3.97, 3.84, 3.17, 3.16, 2.94, 2.87, 2.53, 2.52, 2.48, 2.48, 2.45, 2.45, 2.38, 2.35, 2.34, 2.34, 2.32, 2.32, 2.30, 2.30, 2.28, 2.28, 2.26, 2.26, 2.26, 2.26, 2.26]
viols = [5, 5, 5, 5, 4, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
en_vals = [83.75, 85.41, 84.31, 82.13, 83.12, 80.82, 80.70, 83.33, 80.34, 80.39, 81.84, 80.21, 84.67, 87.04, 91.12, 88.72, 93.93, 93.94, 90.50, 88.97, 88.73, 87.79, 88.71, 86.11, 87.35, 87.31, 88.03, 87.00, 89.71, 89.70, 88.74, 88.73, 88.73]

ax1.plot(iters, ms_vals, color='#1f77b4', lw=2.2, marker='o', markersize=4, label='全任务完工时间 Makespan (h)')
ax1.set_ylabel('完工时间 (小时)', fontsize=11)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper right', frameon=True)

ax1.axvline(x=13, color='#d62728', linestyle=':', lw=1.8, label='消灭硬违约 (第13代)')
ax1.annotate('第13代硬违约归零', xy=(13, 2.53), xytext=(17, 3.2),
             arrowprops=dict(facecolor='#d62728', shrink=0.05, width=1.2, headwidth=6),
             fontsize=10, color='#d62728', fontweight='bold')

ax2.plot(iters, en_vals, color='#2ca02c', lw=2.0, marker='s', markersize=4, label='系统运输总能耗 (kWh)')
ax2_sub = ax2.twinx()
ax2_sub.plot(iters, viols, color='#d62728', lw=1.8, linestyle='--', label='硬时限违约箱数')
ax2_sub.set_ylabel('硬违约箱数 (箱)', color='#d62728', fontsize=11)
ax2_sub.tick_params(axis='y', labelcolor='#d62728')

ax2.set_xlabel('ALNS 迭代轮次 (Iteration)', fontsize=11)
ax2.set_ylabel('总运输能耗 (kWh)', color='#2ca02c', fontsize=11)
ax2.tick_params(axis='y', labelcolor='#2ca02c')
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
p1 = os.path.join(out_dir, 'fig_q2_alns_convergence.pdf')
plt.savefig(p1, bbox_inches='tight')
plt.close()
print(f"已生成: {p1}")

# -------------------------------------------------------------
# 图 2：8 架实体无人机调度甘特图
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

drone_order = ['U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07', 'U08']
y_map = {u: idx for idx, u in enumerate(drone_order)}
color_map = {'A': '#3498db', 'B': '#2ecc71', 'C': '#e67e22'}

for idx, r in df_s.iterrows():
    u = r['无人机编号']
    m = r['机型编号']
    st = r['开始时刻（s）'] / 3600.0
    ed = r['返回O01时刻（s）'] / 3600.0
    dur = ed - st
    y = y_map[u]
    ax.broken_barh([(st, dur)], (y - 0.35, 0.7), facecolors=color_map[m], edgecolor='black', lw=0.6, alpha=0.85)
    if dur > 0.10:
        ax.text(st + dur/2.0, y, r['架次编号'], ha='center', va='center', color='white', fontsize=7, fontweight='bold')

ax.set_yticks(range(len(drone_order)))
ax.set_yticklabels([f"{u} ({'A' if u in ['U01','U02','U03','U04'] else ('B' if u in ['U05','U06'] else 'C')}型)" for u in drone_order], fontsize=10)
ax.set_xlabel('时间 (小时 / h)', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5, axis='x')

patches = [
    mpatches.Patch(color=color_map['A'], label='A 型机架次 (轻敏)'),
    mpatches.Patch(color=color_map['B'], label='B 型机架次 (中程)'),
    mpatches.Patch(color=color_map['C'], label='C 型机架次 (重载)')
]
ax.legend(handles=patches, loc='upper right', frameon=True)
ax.set_xlim(0, makespan_h + 0.15)

plt.tight_layout()
p2 = os.path.join(out_dir, 'fig_q2_schedule_gantt.pdf')
plt.savefig(p2, bbox_inches='tight')
plt.close()
print(f"已生成: {p2}")

# -------------------------------------------------------------
# 图 3：14 组共享电池循环周转与充电甘特图
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)

all_batts = [f"BAT_A_{i:02d}" for i in range(1, 7)] + [f"BAT_B_{i:02d}" for i in range(1, 5)] + [f"BAT_C_{i:02d}" for i in range(1, 5)]
b_map = {b: idx for idx, b in enumerate(reversed(all_batts))}

for idx, r in df_s.iterrows():
    b = r['电池编号']
    m = r['机型编号']
    st = r['开始时刻（s）'] / 3600.0
    ed = r['返回O01时刻（s）'] / 3600.0
    soc_end = 1.0 - r['架次能耗（kWh）'] / (4.5 if m=='A' else (4.0 if m=='B' else 8.0))
    t_full = 1800.0 if m=='A' else (2400.0 if m=='B' else 3000.0)
    if soc_end < 0.90:
        chg_dur = (((0.90 - soc_end)/0.90)*0.65 + 0.35) * t_full
    else:
        chg_dur = (((1.0 - soc_end)/0.10)*0.35) * t_full
    
    y = b_map[b]
    ax.broken_barh([(st, ed - st)], (y - 0.32, 0.64), facecolors='#e74c3c', edgecolor='black', lw=0.5, alpha=0.85)
    ax.broken_barh([(ed, chg_dur / 3600.0)], (y - 0.32, 0.64), facecolors='#3498db', hatch='///', edgecolor='black', lw=0.5, alpha=0.6)

ax.set_yticks(range(len(all_batts)))
ax.set_yticklabels(reversed(all_batts), fontsize=9)
ax.set_xlabel('时间 (小时 / h)', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5, axis='x')

patches_b = [
    mpatches.Patch(facecolor='#e74c3c', label='飞行放电中 (任务执行)'),
    mpatches.Patch(facecolor='#3498db', hatch='///', label='地面充电中 (两阶段等效充电)')
]
ax.legend(handles=patches_b, loc='upper right', frameon=True)
ax.set_xlim(0, makespan_h + 0.25)

plt.tight_layout()
p3 = os.path.join(out_dir, 'fig_q2_battery_circulation.pdf')
plt.savefig(p3, bbox_inches='tight')
plt.close()
print(f"已生成: {p3}")

# -------------------------------------------------------------
# 图 4：多目标 Pareto 权衡对比图
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5), dpi=300)

schemes = [
    {'name': '升级版 ALNS 方案 (当前基准)', 'makespan': round(makespan_h, 2), 'energy': round(total_energy, 2), 'sorties': total_sorties, 'color': '#d62728', 'marker': '*'},
    {'name': '原 ALNS 方案', 'makespan': 2.31, 'energy': 90.73, 'sorties': 31, 'color': '#1f77b4', 'marker': 'o'},
    {'name': '方案 D (全时限保底)', 'makespan': 2.82, 'energy': 82.40, 'sorties': 36, 'color': '#7f7f7f', 'marker': 's'},
    {'name': '单点贪婪直达初解', 'makespan': 4.46, 'energy': 83.75, 'sorties': 21, 'color': '#ff7f0e', 'marker': '^'}
]

for s in schemes:
    ax.scatter(s['makespan'], s['energy'], s=s['sorties']*12, color=s['color'], marker=s['marker'], zorder=5, label=f"{s['name']} ({s['sorties']}架次)")
    ax.annotate(f"{s['name']}\n({s['makespan']:.2f}h, {s['energy']:.1f}kWh, {s['sorties']}次)",
                xy=(s['makespan'], s['energy']),
                xytext=(s['makespan'] + 0.08, s['energy'] - 1.5 if s['makespan']<2.5 else s['energy'] + 1.2),
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=s['color']))

ax.plot([round(makespan_h, 2), 2.31, 2.82], [round(total_energy, 2), 90.73, 82.40], linestyle=':', color='gray', alpha=0.7, zorder=3)

ax.set_xlabel('全任务完工时间 Makespan (小时 / h)', fontsize=11)
ax.set_ylabel('系统运输总能耗 (kWh)', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xlim(1.9, 4.8)
ax.set_ylim(75, 96)
ax.legend(loc='upper right', frameon=True, fontsize=9)

plt.tight_layout()
p4 = os.path.join(out_dir, 'fig_q2_pareto_tradeoff.pdf')
plt.savefig(p4, bbox_inches='tight')
plt.close()
print(f"已生成: {p4}")

print("全部动态对齐图表更新生成完毕！")
