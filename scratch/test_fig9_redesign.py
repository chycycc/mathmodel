# -*- coding: utf-8 -*-
"""生成 2x2 图 9 重绘方案预览图"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as patches

# 引入项目环境
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import NODES

SKILL_DIR = r"C:\Users\chy\.gemini\config\skills\scipilot-figure-skill\scripts"
sys.path.insert(0, SKILL_DIR)
from setup_style import setup_style
from export_figure import export_figure

setup_style(journal='general', lang='zh')

csv_path = os.path.join(WORKSPACE_ROOT, "results", "Q2", "Q2_运输架次.csv")
df = pd.read_csv(csv_path)

o_lon = NODES['O01']['lon']
o_lat = NODES['O01']['lat']

fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
(ax1, ax2), (ax3, ax4) = axes

# 通用底图绘制函数
def draw_base(ax, title):
    for nid, node in NODES.items():
        if nid == 'O01':
            continue
        ax.scatter(node['lon'], node['lat'], s=45, color='#334155', edgecolors='white', linewidth=0.6, zorder=5)
        ax.text(node['lon'] + 0.002, node['lat'] + 0.0015, nid[1:], fontsize=5.8, weight='bold', color='#1E293B', zorder=6)
    ax.scatter(o_lon, o_lat, s=120, color='#DC2626', marker='*', edgecolors='black', linewidth=0.6, zorder=7)
    ax.text(o_lon, o_lat - 0.006, 'O01', fontsize=6.2, weight='bold', color='#DC2626', ha='center', zorder=7)
    ax.set_title(title, fontsize=7.6, weight='bold', pad=5)
    ax.set_xlim(109.16, 109.295)
    ax.set_ylim(23.00, 23.088)
    ax.grid(True, linestyle='--', alpha=0.25)
    ax.tick_params(labelsize=5.8)

# Panel 1: 单点直达 (11 架次)
draw_base(ax1, '(a) 单点重载直达专线网 (11 架次)')
s_counts = {}
for _, row in df.iterrows():
    stops = row['访问服务区顺序'].split(" -> ")
    if len(stops) == 1:
        s = stops[0]
        s_counts[s] = s_counts.get(s, 0) + 1

for s, cnt in s_counts.items():
    lw = 1.0 + cnt * 0.8
    ax1.plot([o_lon, NODES[s]['lon']], [o_lat, NODES[s]['lat']],
             color='#2563EB', linestyle='--', linewidth=lw, alpha=0.75, zorder=3)
    # 标注直达频次
    mid_lon = (o_lon + NODES[s]['lon']) / 2
    mid_lat = (o_lat + NODES[s]['lat']) / 2
    if cnt > 1:
        ax1.text(mid_lon, mid_lat, f"{cnt}次", fontsize=5.5, color='#1E40AF', weight='bold',
                 bbox=dict(boxstyle='circle,pad=0.15', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=0.4))

# Panel 2: 双点闭环巡回 (10 架次)
draw_base(ax2, '(b) 双点闭环节约巡回航线 (10 架次)')
double_routes = []
for _, row in df.iterrows():
    stops = row['访问服务区顺序'].split(" -> ")
    if len(stops) == 2:
        double_routes.append(stops)

for s1, s2 in double_routes:
    # 闭环折线: O01 -> s1 -> s2 -> O01
    lons = [o_lon, NODES[s1]['lon'], NODES[s2]['lon'], o_lon]
    lats = [o_lat, NODES[s1]['lat'], NODES[s2]['lat'], o_lat]
    # O01出发返程用浅线
    ax2.plot([o_lon, NODES[s1]['lon']], [o_lat, NODES[s1]['lat']], color='#10B981', linestyle=':', linewidth=0.8, alpha=0.5, zorder=2)
    ax2.plot([NODES[s2]['lon'], o_lon], [NODES[s2]['lat'], o_lat], color='#10B981', linestyle=':', linewidth=0.8, alpha=0.5, zorder=2)
    # 核心跨点巡回用加粗实线 + 箭头
    ax2.annotate('', xy=(NODES[s2]['lon'], NODES[s2]['lat']), xytext=(NODES[s1]['lon'], NODES[s1]['lat']),
                 arrowprops=dict(arrowstyle="->", color='#059669', lw=1.3, shrinkA=4, shrinkB=4), zorder=4)

# Panel 3: 三点集约深度巡回 (3 架次)
draw_base(ax3, '(c) 三点集约深度巡回航线 (3 架次)')
triple_colors = ['#8B5CF6', '#EC4899', '#D97706']
t_idx = 0
for _, row in df.iterrows():
    stops = row['访问服务区顺序'].split(" -> ")
    if len(stops) == 3:
        c = triple_colors[t_idx % len(triple_colors)]
        t_id = row['架次编号']
        # 路径
        full = ['O01'] + stops + ['O01']
        for i in range(len(full) - 1):
            u, v = full[i], full[i+1]
            p_u = (o_lon, o_lat) if u == 'O01' else (NODES[u]['lon'], NODES[u]['lat'])
            p_v = (o_lon, o_lat) if v == 'O01' else (NODES[v]['lon'], NODES[v]['lat'])
            ls = ':' if (u == 'O01' or v == 'O01') else '-'
            lw = 0.9 if ls == ':' else 1.6
            ax3.plot([p_u[0], p_v[0]], [p_u[1], p_v[1]], color=c, linestyle=ls, linewidth=lw, alpha=0.85, zorder=3)
        # 标注架次标签
        p_mid = NODES[stops[1]]
        ax3.text(p_mid['lon'] - 0.005, p_mid['lat'] + 0.004, t_id, fontsize=5.8, color=c, weight='bold')
        t_idx += 1

# Panel 4: 全局航段通行流量密度与骨干空域走廊
draw_base(ax4, '(d) 24航次全网航段通行流量密度 (骨干走廊)')
segment_counts = {}
for _, row in df.iterrows():
    stops = row['访问服务区顺序'].split(" -> ")
    full = ['O01'] + stops + ['O01']
    for i in range(len(full) - 1):
        edge = tuple(sorted([full[i], full[i+1]]))
        segment_counts[edge] = segment_counts.get(edge, 0) + 1

for (u, v), cnt in segment_counts.items():
    p_u = (o_lon, o_lat) if u == 'O01' else (NODES[u]['lon'], NODES[u]['lat'])
    p_v = (o_lon, o_lat) if v == 'O01' else (NODES[v]['lon'], NODES[v]['lat'])
    if cnt >= 4:
        c, lw, alpha, z = '#DC2626', 2.8, 0.9, 4  # 极高频骨干走廊
    elif cnt >= 2:
        c, lw, alpha, z = '#F59E0B', 1.6, 0.8, 3  # 次级干线
    else:
        c, lw, alpha, z = '#94A3B8', 0.8, 0.5, 2  # 支线
    ax4.plot([p_u[0], p_v[0]], [p_u[1], p_v[1]], color=c, linewidth=lw, alpha=alpha, zorder=z)

# 统一坐标轴标签
for ax in [ax3, ax4]:
    ax.set_xlabel('经度 (°E)', fontsize=6.8)
for ax in [ax1, ax3]:
    ax.set_ylabel('纬度 (°N)', fontsize=6.8)

plt.tight_layout()
preview_path = os.path.join(WORKSPACE_ROOT, "figures", "fig9_preview_2x2.png")
fig.savefig(preview_path, dpi=300)
plt.close(fig)
print(f"2x2 预览图生成成功: {preview_path}")
