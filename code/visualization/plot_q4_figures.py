# -*- coding: utf-8 -*-
"""
问题四关键学术图表升级脚本 (figures4papers 顶刊美学规范版)
严格保持计算数据 100% 真实客观，全面升维结构排版与学术配色体系。
包含：
- fig13_q4_graph_connectivity_partitions.pdf: 服务区强绑定网络拓扑图论连通分支与 K=2,3 任务分区图 (彻底无遮挡版)
- fig14_q4_resource_demand_shortage.pdf: 各任务组隔离执行下的装备资源并发需求与库存缺口对比图 (figures4papers 原位标注)
"""

import os
import sys
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import matplotlib.patheffects as pe

# 引入项目基础路径与数据模块
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import NODES

from f4p_style import apply_f4p_style, export_f4p_figure, F4P_PALETTE

FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")
RESULTS_Q2_DIR = os.path.join(WORKSPACE_ROOT, "results", "Q2")
RESULTS_Q4_DIR = os.path.join(WORKSPACE_ROOT, "results", "Q4")
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_fig13():
    """图13：服务区强绑定网络拓扑图论连通分支与任务分区映射 (figures4papers 版)"""
    apply_f4p_style(font_size=7.2)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 4.0))
    
    csv_q2 = os.path.join(RESULTS_Q2_DIR, "Q2_运输架次.csv")
    df_q2 = pd.read_csv(csv_q2)
    
    # 1. 图论拓扑构建
    G = nx.Graph()
    svc_all = [f'S{i:03d}' for i in range(1, 16)]
    G.add_nodes_from(svc_all)
    
    for _, row in df_q2.iterrows():
        stops = row['访问服务区顺序'].split(" -> ")
        if len(stops) > 1:
            for i in range(len(stops)):
                for j in range(i + 1, len(stops)):
                    G.add_edge(stops[i], stops[j])
                    
    pos = nx.spring_layout(G, seed=42, k=0.55)
    pos['S010'] = np.array([0.88, 0.35])
    pos['S014'] = np.array([0.88, -0.35])
    
    group1_nodes = [s for s in svc_all if s not in ['S010', 'S014']]
    
    # (a) 拓扑与连通分支证明
    c_g1 = F4P_PALETTE['blue_main']
    c_g2 = F4P_PALETTE['highlight_gold']
    c_g3 = F4P_PALETTE['green_3']
    
    nx.draw_networkx_edges(G, pos, ax=ax1, edge_color=F4P_PALETTE['neutral_gray'], width=1.3, alpha=0.7)
    nx.draw_networkx_nodes(G, pos, nodelist=group1_nodes, ax=ax1,
                          node_color=c_g1, node_size=240, edgecolors='white', linewidths=1.2)
    nx.draw_networkx_nodes(G, pos, nodelist=['S010'], ax=ax1,
                          node_color=c_g2, node_size=260, edgecolors='white', linewidths=1.2)
    nx.draw_networkx_nodes(G, pos, nodelist=['S014'], ax=ax1,
                          node_color=c_g3, node_size=260, edgecolors='white', linewidths=1.2)
                          
    labels = {s: s[1:] for s in svc_all}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax1, font_size=6.6, font_color='white', font_weight='bold')
    
    ax1.set_xlim(-1.18, 1.55)
    ax1.set_ylim(-1.05, 1.05)
    
    ax1.text(0.04, 0.15, "连通分支 C1 (13个互锁服务区)\n跨区航次物理不可拆分", 
             transform=ax1.transAxes, fontsize=6.2, color=c_g1, weight='bold',
             bbox=dict(boxstyle='round,pad=0.25', facecolor='#EFF6FF', edgecolor='#BFDBFE', lw=0.6))
             
    ax1.text(1.02, 0.35, "孤立点 C2: {S010}\n(单点直达T011)", ha='left', va='center', fontsize=6.0, color=c_g2, weight='bold')
    ax1.text(1.02, -0.35, "孤立点 C3: {S014}\n(单点直达T005)", ha='left', va='center', fontsize=6.0, color=c_g3, weight='bold')
    
    ax1.set_title('(a) 服务区多点航次回路强绑定图论连通分支', weight='bold', pad=12)
    ax1.axis('off')
    
    # (b) 地理空间任务分区映射
    ax2.set_xlim(109.155, 109.308)
    ax2.set_ylim(22.985, 23.125)
    ax2.set_xticks([109.16, 109.20, 109.24, 109.28])
    ax2.set_xticklabels(['109.16°E', '109.20°E', '109.24°E', '109.28°E'], fontsize=6.6)
    ax2.set_yticks([23.00, 23.04, 23.08, 23.12])
    ax2.set_yticklabels(['23.00°N', '23.04°N', '23.08°N', '23.12°N'], fontsize=6.6)
    
    white_halo = [pe.withStroke(linewidth=2.2, foreground='white')]
    
    for s in group1_nodes:
        lon, lat = NODES[s]['lon'], NODES[s]['lat']
        ax2.scatter(lon, lat, s=85, color=c_g1, edgecolors='white', linewidth=1.0, zorder=3)
        dx, dy = 0.003, 0.002
        if s in ['S008', 'S004', 'S002']:
            dy = 0.003
        elif s in ['S006', 'S011', 'S007']:
            dy = -0.004
            dx = 0.001
        elif s == 'S015':
            dx = 0.003
            dy = 0.001
        ax2.text(lon + dx, lat + dy, s[1:], fontsize=6.2, weight='bold', color=c_g1, zorder=4, path_effects=white_halo)
        
    ax2.scatter(NODES['S010']['lon'], NODES['S010']['lat'], s=110, color=c_g2, edgecolors='white', linewidth=1.0, zorder=3)
    ax2.text(NODES['S010']['lon'] + 0.003, NODES['S010']['lat'] + 0.001, 'S010', fontsize=6.5, weight='bold', color=c_g2, zorder=4, path_effects=white_halo)
    
    ax2.scatter(NODES['S014']['lon'], NODES['S014']['lat'], s=110, color=c_g3, edgecolors='white', linewidth=1.0, zorder=3)
    ax2.text(NODES['S014']['lon'] + 0.003, NODES['S014']['lat'] - 0.004, 'S014', fontsize=6.5, weight='bold', color=c_g3, zorder=4, path_effects=white_halo)
    
    o_lon, o_lat = NODES['O01']['lon'], NODES['O01']['lat']
    c_alert = F4P_PALETTE['red_strong']
    ax2.scatter(o_lon, o_lat, s=160, color=c_alert, marker='*', edgecolors='black', linewidth=0.8, zorder=5)
    ax2.text(o_lon, o_lat + 0.005, 'O01 基地', ha='center', va='bottom', fontsize=6.5, weight='bold', color=c_alert, zorder=5, path_effects=white_halo)
    
    rect1 = patches.FancyBboxPatch((109.162, 23.018), 0.112, 0.088,
                                  boxstyle="round,pad=0.008,rounding_size=0.025",
                                  facecolor=c_g1, edgecolor=c_g1,
                                  linewidth=1.2, linestyle='--', alpha=0.10, zorder=1)
    ax2.add_patch(rect1)
    ax2.text(109.162, 23.106, "任务组 1 (主战区: 13服务区, 22架次)", fontsize=6.2, color=c_g1, weight='bold', path_effects=white_halo)
    
    rect2 = patches.FancyBboxPatch((109.266, 22.998), 0.026, 0.030,
                                  boxstyle="round,pad=0.006,rounding_size=0.015",
                                  facecolor=c_g2, edgecolor=c_g2,
                                  linewidth=1.0, linestyle=':', alpha=0.16, zorder=1)
    ax2.add_patch(rect2)
    ax2.text(109.248, 22.990, "任务组 2 (K=2) / 组2+3 (K=3)", fontsize=6.0, color=c_g2, weight='bold', path_effects=white_halo)
    
    ax2.set_title('(b) 地理空间任务分区方案映射 (K=2 与 K=3)', weight='bold', pad=12)
    ax2.set_xlabel('经度')
    ax2.set_ylabel('纬度')
    ax2.grid(True)
    
    # 顶部外部图例
    handles = [
        patches.Patch(facecolor=c_g1, label='任务组 1 (主战区 13服务区, 22架次)'),
        patches.Patch(facecolor=c_g2, label='任务组 2 (K=2: S010+S014; K=3: S010)'),
        patches.Patch(facecolor=c_g3, label='任务组 3 (K=3: 独立S014, 1架次)'),
        mlines.Line2D([], [], marker='*', color='w', markerfacecolor=c_alert, markeredgecolor='k', markersize=8, label='O01 基地')
    ]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.02), ncol=4, fontsize=6.0, frameon=False)
    
    plt.subplots_adjust(left=0.06, right=0.96, bottom=0.18, top=0.88, wspace=0.28)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig13_q4_graph_connectivity_partitions"), size_inches=(7.8, 4.0))
    plt.close(fig)


def plot_fig14():
    """图14：各任务组隔离执行下的装备资源需求与库存缺口对比图 (figures4papers 版)"""
    apply_f4p_style(font_size=7.5)
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    
    csv_path = os.path.join(RESULTS_Q4_DIR, "Q4_方案对比与资源缺口.csv")
    if not os.path.exists(csv_path):
        print(f"警告：未找到 {csv_path}")
        return
        
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    res_names = [r.replace(" (架)", "").replace(" (组)", "") for r in df.iloc[:, 0]]
    stock = df.iloc[:, 1].values
    req_k2 = df.iloc[:, 2].values
    gap_k2 = df.iloc[:, 3].values
    req_k3 = df.iloc[:, 4].values
    gap_k3 = df.iloc[:, 5].values
    
    x = np.arange(len(res_names))
    width = 0.26
    
    c_stock = F4P_PALETTE['neutral_mid']      # 现存库存中性灰
    c_k2 = F4P_PALETTE['blue_main']           # K=2 学术深蓝
    c_k3 = F4P_PALETTE['violet']              # K=3 紫罗兰
    c_alert = F4P_PALETTE['red_strong']       # 缺口警告深红
    c_pass = F4P_PALETTE['green_3']           # 达标墨绿
    
    ax.bar(x - width, stock, width, label='现存装备总库存', color=c_stock, alpha=0.75, edgecolor='white', linewidth=0.6)
    ax.bar(x, req_k2, width, label='K=2 隔离执行独立需求总计', color=c_k2, alpha=0.90, edgecolor='white', linewidth=0.6)
    ax.bar(x + width, req_k3, width, label='K=3 隔离执行独立需求总计', color=c_k3, alpha=0.90, edgecolor='white', linewidth=0.6)
    
    for i in range(len(res_names)):
        g2 = int(gap_k2[i])
        g3 = int(gap_k3[i])
        max_h = max(stock[i], req_k2[i], req_k3[i])
        
        if g2 > 0 or g3 > 0:
            if g2 == g3:
                txt = f"缺 {g2}"
            else:
                txt = f"缺 {g2} (K2)\n缺 {g3} (K3)"
                
            ax.annotate(txt,
                        xy=(x[i] + width/2, max_h),
                        xytext=(x[i] + width/2, max_h + 0.65),
                        ha='center', va='bottom',
                        fontsize=6.2, color=c_alert, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FEF2F2', edgecolor='#FECACA', lw=0.6))
        else:
            ax.text(x[i] + width/2, max_h + 0.15, "达标", ha='center', va='bottom', fontsize=5.8, color=c_pass, weight='bold')

    ax.set_title('图 14  应急救援任务分区隔离执行下的装备并发需求峰值与绝对短缺缺口大盘', weight='bold', pad=14)
    ax.set_xlabel('应急救援关键装备与共享资源类别')
    ax.set_ylabel('配置台套数量 (架 / 组)')
    ax.set_xticks(x)
    ax.set_xticklabels(res_names, fontsize=6.8, rotation=20)
    ax.set_ylim(0, 8.8)
    ax.grid(axis='y')
    
    # 管理学成因提示框
    insight_box = (
        "【管理学成因揭示】\n"
        "分战区独立包干切断了跨组在时间轴上的时分复用，导致并发需求叠加与碎片化闲置并存，\n"
        "使 B 型无人机 (缺1~2架)、B 型电池 (缺2组) 与中继机 (缺1架) 呈现刚性库存短缺。"
    )
    ax.text(0.03, 0.88, insight_box, transform=ax.transAxes, fontsize=6.2, color=F4P_PALETTE['neutral_dark'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor=F4P_PALETTE['neutral_light'], edgecolor=F4P_PALETTE['neutral_gray'], lw=0.6))
            
    ax.legend(loc='upper right', fontsize=6.5, framealpha=0.92)
    
    plt.subplots_adjust(left=0.08, right=0.96, bottom=0.15, top=0.90)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig14_q4_resource_demand_shortage"), size_inches=(7.6, 4.0))
    plt.close(fig)


if __name__ == '__main__':
    plot_fig13()
    plot_fig14()
