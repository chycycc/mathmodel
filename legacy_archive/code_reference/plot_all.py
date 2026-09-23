# -*- coding: utf-8 -*-
"""
学术级高质量矢量图表生成脚本
输出全部 5 幅高清矢量 PDF 图表至 figures/ 目录：
1. fig1_3d_terrain_and_nodes.pdf: 镇龙乡三维高程地形、节点分布与中继阵位
2. fig2_max_payload_and_energy.pdf: 各机型最大安全载重对比与Q1单点组批能耗
3. fig3_flight_and_charging_gantt.pdf: 实体无人机与共享电池两阶段时空协同甘特图
4. fig4_coverage_and_relay_profile.pdf: 视距遮挡纵剖面与全航程通信保障时序
5. fig5_task_partitioning_topology.pdf: 任务空间分区拓扑与分散资源配置开销对比
"""

import sys
import os
sys.path.insert(0, 'code')
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D
import data_loader as dl

# 设置科研论文制图全局样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.5

FIGURES_DIR = 'figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

# 调色板定义 (Nature / Science 经典学术配色)
COLOR_BLUE = '#1f77b4'
COLOR_ORANGE = '#ff7f0e'
COLOR_GREEN = '#2ca02c'
COLOR_RED = '#d62728'
COLOR_PURPLE = '#9467bd'
COLOR_CYAN = '#17becf'
COLOR_GRAY = '#7f7f7f'

def plot_fig1_3d_terrain():
    """图 1: 3D 地形起伏、服务区节点与中继机悬停阵位"""
    print("正在绘制图 1: 3D 地形与空间节点网络...")
    fig = plt.figure(figsize=(10, 7.5))
    ax = fig.add_subplot(111, projection='3d')
    
    # 降采样 DEM 用于平滑快速渲染
    step = 8
    dem_sub = dl.DEM_GRID[::step, ::step]
    lons_sub = dl.DEM_LONS[::step]
    lats_sub = dl.DEM_LATS[::step]
    LON_M, LAT_M = np.meshgrid(lons_sub, lats_sub)
    
    # 绘制地形曲面
    surf = ax.plot_surface(LON_M, LAT_M, dem_sub, cmap='gist_earth', alpha=0.65,
                           linewidth=0, antialiased=True, rstride=1, cstride=1)
    
    # 标注 O01 调度中心
    o01 = dl.NODES['O01']
    ax.scatter([o01['lon']], [o01['lat']], [o01['elev']], color='red', s=180, marker='*',
               edgecolors='black', linewidth=1.2, label='O01 调度中心', zorder=10)
    ax.text(o01['lon'], o01['lat'] - 0.005, o01['elev'] + 80, 'O01 (调度中心)', color='darkred',
            fontweight='bold', fontsize=10, zorder=11)
    
    # 标注 15 个服务区
    s_lons = [dl.NODES[k]['lon'] for k in dl.NODES if k.startswith('S')]
    s_lats = [dl.NODES[k]['lat'] for k in dl.NODES if k.startswith('S')]
    s_elevs = [dl.NODES[k]['elev'] for k in dl.NODES if k.startswith('S')]
    ax.scatter(s_lons, s_lats, s_elevs, color='orange', s=60, marker='o',
               edgecolors='black', linewidth=0.8, label='受灾服务区 (S001~S015)', zorder=9)
    
    for k in dl.NODES:
        if k.startswith('S'):
            node = dl.NODES[k]
            ax.text(node['lon'], node['lat'], node['elev'] + 45, k, fontsize=8, color='black')
            
    # 标注两个中继机悬停阵位
    from problem3 import RELAY_POS_WEST, RELAY_POS_EAST
    ax.scatter([RELAY_POS_WEST['lon']], [RELAY_POS_WEST['lat']], [RELAY_POS_WEST['hover_z']],
               color='magenta', s=140, marker='^', edgecolors='black', linewidth=1.2,
               label='西部中继悬停阵位 (H=686m)', zorder=12)
    ax.scatter([RELAY_POS_EAST['lon']], [RELAY_POS_EAST['lat']], [RELAY_POS_EAST['hover_z']],
               color='cyan', s=140, marker='^', edgecolors='black', linewidth=1.2,
               label='东部中继悬停阵位 (H=691m)', zorder=12)
    
    # 绘制中继到 G01 的回传链路虚线
    ax.plot([o01['lon'], RELAY_POS_WEST['lon']], [o01['lat'], RELAY_POS_WEST['lat']],
            [o01['elev']+20, RELAY_POS_WEST['hover_z']], color='magenta', linestyle='--', linewidth=1.5)
    ax.plot([o01['lon'], RELAY_POS_EAST['lon']], [o01['lat'], RELAY_POS_EAST['lat']],
            [o01['elev']+20, RELAY_POS_EAST['hover_z']], color='cyan', linestyle='--', linewidth=1.5)

    ax.set_xlabel('经度 (°)', labelpad=10)
    ax.set_ylabel('纬度 (°)', labelpad=10)
    ax.set_zlabel('海拔高程 (m)', labelpad=10)
    ax.view_init(elev=32, azim=-62)
    ax.legend(loc='upper left', frameon=True, framealpha=0.85)
    
    cbar = fig.colorbar(surf, ax=ax, shrink=0.55, aspect=15, pad=0.08)
    cbar.set_label('地面海拔 (m)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig1_3d_terrain_and_nodes.pdf'), dpi=300)
    plt.close()
    print("图 1 导出成功: fig1_3d_terrain_and_nodes.pdf")

def plot_fig2_payload_and_energy():
    """图 2: 三种机型最大安全载重对比与 Q1 单点组批架次能耗"""
    print("正在绘制图 2: 最大安全载重与组批能耗分析...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
    
    # 读取问题 1 计算的最大安全载荷
    from problem1 import compute_max_safe_payload
    s_ids = sorted([k for k in dl.NODES if k.startswith('S')])
    
    payloads_A = [compute_max_safe_payload('A', s) for s in s_ids]
    payloads_B = [compute_max_safe_payload('B', s) for s in s_ids]
    payloads_C = [compute_max_safe_payload('C', s) for s in s_ids]
    
    x = np.arange(len(s_ids))
    width = 0.26
    
    rects1 = ax1.bar(x - width, payloads_A, width, label='A 型机 (额定 25kg)', color=COLOR_BLUE, alpha=0.85)
    rects2 = ax1.bar(x, payloads_B, width, label='B 型机 (额定 30kg)', color=COLOR_ORANGE, alpha=0.85)
    rects3 = ax1.bar(x + width, payloads_C, width, label='C 型机 (额定 80kg)', color=COLOR_GREEN, alpha=0.85)
    
    # 标示 C 型机物理上限与安全衰减
    ax1.axhline(y=80, color='darkgreen', linestyle=':', linewidth=1.2, alpha=0.7, label='C 型物理上限 (80kg)')
    ax1.set_xlabel('受灾服务区编号')
    ax1.set_ylabel('单点往返最大安全载荷 (kg)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(s_ids, rotation=45)
    ax1.set_ylim(0, 95)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', frameon=True)
    ax1.set_title('(a) 各机型在各服务区单点往返最大安全载载量', fontsize=11, pad=8)
    
    # 右图：Q1 组批方案 19 个架次的载重与能耗
    df_q1 = pd.read_csv('results/Q1_单点组批方案.csv')
    trips = df_q1['架次编号']
    weights = df_q1['总质量（kg）']
    energies = df_q1['架次能耗（kWh）']
    socs = df_q1['返航SOC（%）']
    
    x2 = np.arange(len(trips))
    ax2_twin = ax2.twinx()
    
    p1 = ax2.bar(x2 - 0.18, weights, width=0.36, color='#34495e', alpha=0.8, label='装载质量 (kg)')
    p2 = ax2_twin.plot(x2 + 0.18, energies, color='#e74c3c', marker='o', linewidth=1.8, markersize=5, label='架次能耗 (kWh)')
    p3 = ax2_twin.plot(x2 + 0.18, socs / 20.0, color='#27ae60', marker='s', linestyle='--', linewidth=1.5, markersize=4, label='返航 SOC (按20归一)')
    
    ax2.set_xlabel('Q1 组批架次编号')
    ax2.set_ylabel('实际装载质量 (kg)')
    ax2_twin.set_ylabel('架次实际能耗 (kWh) / 归一化 SOC')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(trips, rotation=50)
    ax2.set_ylim(0, 90)
    ax2_twin.set_ylim(0, 7.5)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    # 合并双轴图例
    lines = [p1, p2[0], p3[0]]
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left', frameon=True)
    ax2.set_title('(b) Q1 单点往返 19 架次载货量与能耗分布', fontsize=11, pad=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig2_max_payload_and_energy.pdf'), dpi=300)
    plt.close()
    print("图 2 导出成功: fig2_max_payload_and_energy.pdf")

def plot_fig3_gantt_chart():
    """图 3: 8 架实体无人机与 14 组共享电池两阶段时空协同甘特图"""
    print("正在绘制图 3: 实体机与电池时空调度甘特图...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8.5), sharex=True)
    
    df_trips = pd.read_csv('results/Q2_运输架次.csv')
    df_boxes = pd.read_csv('results/Q2_逐箱交付.csv')
    
    # 实体机映射
    drones = ['U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07', 'U08']
    d_colors = {'A': '#2980b9', 'B': '#e67e22', 'C': '#27ae60'}
    
    # 绘制无人机时间线
    for idx, d_id in enumerate(drones):
        sub = df_trips[df_trips['无人机编号'] == d_id]
        for _, r in sub.iterrows():
            t_start = r['开始时刻（s）']
            t_end = r['返回O01时刻（s）']
            dur = t_end - t_start
            m_type = r['机型编号']
            t_id = r['架次编号']
            
            # 绘制任务条
            ax1.barh(idx, dur, left=t_start, height=0.55, color=d_colors[m_type], edgecolor='black', alpha=0.88)
            ax1.text(t_start + dur / 2.0, idx, f"{t_id}\n({r['访问服务区顺序']})",
                     ha='center', va='center', color='white', fontsize=7.5, fontweight='bold')
            
    ax1.set_yticks(range(len(drones)))
    ax1.set_yticklabels([f"{d} ({dl.DRONE_PARAMS['A' if d in ['U01','U02','U03','U04'] else ('B' if d in ['U05','U06'] else 'C')]['name'][:4]})" for d in drones])
    ax1.set_ylabel('实体无人机编号')
    ax1.grid(axis='x', linestyle='--', alpha=0.6)
    mspan_h = df_trips['返回O01时刻（s）'].max() / 3600.0
    ax1.set_title(f'(a) 8 架异构实体运输无人机任务执行时间轴 (Makespan = {mspan_h:.2f}h, 均衡流水线)', fontsize=11, pad=8)
    
    # 绘制电池时间线 (14 组电池)
    bats = [f"BAT_A_0{i}" for i in range(1, 7)] + [f"BAT_B_0{i}" for i in range(1, 5)] + [f"BAT_C_0{i}" for i in range(1, 5)]
    
    for idx, b_id in enumerate(bats):
        sub = df_trips[df_trips['电池编号'] == b_id]
        m_type = b_id.split('_')[1]
        for _, r in sub.iterrows():
            t_start = r['开始时刻（s）']
            t_end = r['返回O01时刻（s）']
            dur_flight = t_end - t_start
            
            # 飞行阶段
            ax2.barh(idx, dur_flight, left=t_start, height=0.55, color='#34495e', edgecolor='black', alpha=0.9)
            
            # 计算两阶段充电时间
            e_trip = r['架次能耗（kWh）']
            e_avail = dl.DRONE_PARAMS[m_type]['e_avail']
            rem_soc = 1.0 - e_trip / e_avail
            t_full = dl.DRONE_PARAMS[m_type]['full_charge_time']
            
            # 区分快速阶段与慢速阶段
            if rem_soc < 0.90:
                t_fast = ((0.90 - rem_soc) / 0.90) * 0.65 * t_full
                t_slow = 0.35 * t_full
            else:
                t_fast = 0.0
                t_slow = ((1.0 - rem_soc) / 0.10) * 0.35 * t_full
                
            # 绘制快速充电条
            if t_fast > 0:
                ax2.barh(idx, t_fast, left=t_end, height=0.55, color='#e74c3c', edgecolor='black', alpha=0.85)
            # 绘制慢速充电条
            if t_slow > 0:
                ax2.barh(idx, t_slow, left=t_end + t_fast, height=0.55, color='#f1c40f', edgecolor='black', alpha=0.85)
                
    ax2.set_yticks(range(len(bats)))
    ax2.set_yticklabels(bats)
    ax2.set_ylabel('共享电池编号')
    ax2.set_xlabel('任务推进时间 t (s)')
    ax2.grid(axis='x', linestyle='--', alpha=0.6)
    
    # 模拟图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#34495e', edgecolor='black', label='飞行任务中 (放电)'),
        Patch(facecolor='#e74c3c', edgecolor='black', label='恒流快速充电 (<90% SOC)'),
        Patch(facecolor='#f1c40f', edgecolor='black', label='恒压慢速涓流 (90%~100% SOC)'),
        Patch(facecolor='#27ae60', edgecolor='black', label='满电待命 (空闲可用)')
    ]
    ax2.legend(handles=legend_elements, loc='upper right', frameon=True, ncol=4)
    ax2.set_title('(b) 14 组共享电池周转与两阶段等效充电状态演进图', fontsize=11, pad=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig3_flight_and_charging_gantt.pdf'), dpi=300)
    plt.close()
    print("图 3 导出成功: fig3_flight_and_charging_gantt.pdf")

def plot_fig4_coverage_and_relay():
    """图 4: 视距遮挡地形剖面与全航程连续通信保障示意图"""
    print("正在绘制图 4: 通信地形遮挡与中继覆盖分析...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8.0))
    
    # 上图: O01 到远距目标点 S008 的航迹地形纵剖面与视线阻断
    p_o01 = dl.NODES['O01']
    p_s08 = dl.NODES['S008']
    prof = dl.get_path_profile('O01', 'S008')
    dist_m = prof['dist_m']
    
    steps = 200
    lons = np.linspace(p_o01['lon'], p_s08['lon'], steps)
    lats = np.linspace(p_o01['lat'], p_s08['lat'], steps)
    dists_km = np.linspace(0, dist_m / 1000.0, steps)
    elevs = [dl.get_dem_elevation(lo, la) for lo, la in zip(lons, lats)]
    
    ax1.fill_between(dists_km, 0, elevs, color='#95a5a6', alpha=0.6, label='DEM 地表高程剖面')
    ax1.plot(dists_km, elevs, color='#7f8c8d', linewidth=1.5)
    
    # 绘制 G01 天线位置与运输机巡航航线
    z_g01 = p_o01['elev'] + 20.0
    ax1.scatter([0], [z_g01], color='red', s=100, marker='^', label='G01 网关天线 (H=147.7m)', zorder=6)
    
    # 运输机在 S008 上空作业点 (H = 240.9 + 30 = 270.9m)
    z_uav = p_s08['elev'] + 30.0
    ax1.scatter([dists_km[-1]], [z_uav], color='blue', s=80, marker='o', label='S008 运输机作业点 (H=270.9m)', zorder=6)
    
    # G01 直连视线（被山峰遮挡）
    ax1.plot([0, dists_km[-1]], [z_g01, z_uav], color='red', linestyle=':', linewidth=2.0, label='G01 直连视线 (受山体严重遮挡, 损耗>128dB 阻断)')
    
    # 中继无人机高空阵位（西部悬停点，投影在横截面上）
    # 距离 O01 约 4.7km，悬停海拔 686.2m
    dist_relay = 4.75
    z_relay = 686.2
    ax1.scatter([dist_relay], [z_relay], color='magenta', s=140, marker='*', label='空中中继无人机 R01 (H=686.2m)', zorder=7)
    
    # 中继回传视线 (通视)
    ax1.plot([0, dist_relay], [z_g01, z_relay], color='green', linestyle='-', linewidth=2.0, label='回传视距链路 (LOS=True, 损耗113.6dB, 畅通)')
    # 中继接入视线 (俯视通视)
    ax1.plot([dist_relay, dists_km[-1]], [z_relay, z_uav], color='magenta', linestyle='--', linewidth=2.0, label='接入俯视链路 (LOS=True, 俯视完全通视)')

    ax1.set_xlabel('O01 到 S008 沿途水平距离 (km)')
    ax1.set_ylabel('海拔高程 (m)')
    ax1.set_ylim(0, 850)
    ax1.grid(linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
    ax1.set_title('(a) O01 至 S008 航线空间遮挡几何与空中中继视距通视机理剖面图', fontsize=11, pad=8)
    
    # 下图: Q3 全部 72 个通信阶段在 27 个运输架次中的直连 vs 中继时序
    df_comm = pd.read_csv('results/Q3_通信保障.csv')
    df_relays = pd.read_csv('results/Q3_中继架次.csv')
    
    trip_list = sorted(df_comm['运输架次编号'].unique())
    for t_idx, t_id in enumerate(trip_list):
        sub = df_comm[df_comm['运输架次编号'] == t_id]
        for _, r in sub.iterrows():
            st = r['开始时刻（s）']
            et = r['结束时刻（s）']
            method = r['保障方式']
            color = '#2ecc71' if method == '直连' else '#e74c3c'
            ax2.barh(t_idx, et - st, left=st, height=0.65, color=color, edgecolor='black', linewidth=0.5, alpha=0.85)
            
    ax2.set_yticks(range(len(trip_list)))
    ax2.set_yticklabels(trip_list, fontsize=8)
    ax2.set_xlabel('时间轴 t (s)')
    ax2.set_ylabel('运输架次')
    ax2.grid(axis='x', linestyle='--', alpha=0.5)
    
    # 标注中继架次的覆盖区间
    from matplotlib.patches import Patch
    n_direct = len(df_comm[df_comm['保障方式'] == '直连'])
    n_relay = len(df_comm[df_comm['保障方式'] == '中继'])
    comm_legends = [
        Patch(facecolor='#2ecc71', edgecolor='black', label=f'固定网关 G01 直连保障 ({n_direct}个阶段)'),
        Patch(facecolor='#e74c3c', edgecolor='black', label=f'空中中继无人机接力保障 ({n_relay}个阶段, 100%覆盖)')
    ]
    ax2.legend(handles=comm_legends, loc='upper right', frameon=True)
    ax2.set_title(f'(b) 全救援周期 {len(trip_list)} 个运输架次 100% 连续通信保障状态时序图', fontsize=11, pad=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig4_coverage_and_relay_profile.pdf'), dpi=300)
    plt.close()
    print("图 4 导出成功: fig4_coverage_and_relay_profile.pdf")

def plot_fig5_partitioning_and_overhead():
    """图 5: 服务区空间分区拓扑与分散独立配置资源开销对比"""
    print("正在绘制图 5: 任务空间分区与分散配置开销...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0))
    
    # 左图: 15 个服务区地理分布与 K=2 分区图示
    from problem4 import PARTITIONS_K2
    g1_svcs = PARTITIONS_K2['G1']
    g2_svcs = PARTITIONS_K2['G2']
    
    o01 = dl.NODES['O01']
    ax1.scatter([o01['lon']], [o01['lat']], color='red', s=200, marker='*', edgecolors='black', label='O01 调度中心', zorder=5)
    ax1.text(o01['lon'] + 0.002, o01['lat'] - 0.002, 'O01', fontweight='bold', color='darkred')
    
    # 绘制 G1 点
    g1_lons = [dl.NODES[s]['lon'] for s in g1_svcs]
    g1_lats = [dl.NODES[s]['lat'] for s in g1_svcs]
    ax1.scatter(g1_lons, g1_lats, color=COLOR_BLUE, s=100, marker='o', edgecolors='black', label='任务组 G1 (西区&中谷单元, 40箱/389kg)', zorder=4)
    for s in g1_svcs:
        ax1.text(dl.NODES[s]['lon'] + 0.002, dl.NODES[s]['lat'] + 0.002, s, fontsize=8.5, color='darkblue')
        
    # 绘制 G2 点
    g2_lons = [dl.NODES[s]['lon'] for s in g2_svcs]
    g2_lats = [dl.NODES[s]['lat'] for s in g2_svcs]
    ax1.scatter(g2_lons, g2_lats, color=COLOR_ORANGE, s=100, marker='s', edgecolors='black', label='任务组 G2 (北区&东深山单元, 40箱/369kg)', zorder=4)
    for s in g2_svcs:
        ax1.text(dl.NODES[s]['lon'] + 0.002, dl.NODES[s]['lat'] + 0.002, s, fontsize=8.5, color='darkred')
        
    # 绘制 S002 与 S004 的强绑定连线
    ax1.plot([dl.NODES['S002']['lon'], dl.NODES['S004']['lon']],
             [dl.NODES['S002']['lat'], dl.NODES['S004']['lat']],
             color='red', linestyle='--', linewidth=2.0, label='T002 串联强约束 (S002-S004同组)')

    ax1.set_xlabel('经度 (°)')
    ax1.set_ylabel('纬度 (°)')
    ax1.grid(linestyle='--', alpha=0.5)
    ax1.legend(loc='lower right', frameon=True, fontsize=8.5)
    ax1.set_title('(a) 服务区地理分布与 K=2 科学分区拓扑图', fontsize=11, pad=8)
    
    # 右图: 集中统筹 vs K=2 独立 vs K=3 独立 资源需求对比
    df_q4 = pd.read_csv('results/Q4_分区配置.csv')
    categories = ['A型无人机', 'B型无人机', 'C型无人机', 'A型电池', 'B型电池', 'C型电池', '中继无人机', '中继能源件']
    stock = [4, 2, 2, 6, 4, 4, 2, 6]
    
    sub_k2 = df_q4[df_q4['K（2或3）'] == 2]
    k2_needs = [
        int(sub_k2['A型运输无人机数'].sum()),
        int(sub_k2['B型运输无人机数'].sum()),
        int(sub_k2['C型运输无人机数'].sum()),
        int(sub_k2['A型电池组数'].sum()),
        int(sub_k2['B型电池组数'].sum()),
        int(sub_k2['C型电池组数'].sum()),
        int(sub_k2['中继无人机数'].sum()),
        int(sub_k2['中继能源组件数'].sum())
    ]
    
    sub_k3 = df_q4[df_q4['K（2或3）'] == 3]
    k3_needs = [
        int(sub_k3['A型运输无人机数'].sum()),
        int(sub_k3['B型运输无人机数'].sum()),
        int(sub_k3['C型运输无人机数'].sum()),
        int(sub_k3['A型电池组数'].sum()),
        int(sub_k3['B型电池组数'].sum()),
        int(sub_k3['C型电池组数'].sum()),
        int(sub_k3['中继无人机数'].sum()),
        int(sub_k3['中继能源组件数'].sum())
    ]
    
    x = np.arange(len(categories))
    width = 0.26
    
    r1 = ax2.bar(x - width, stock, width, label='现有库存基准 (集中统筹占用)', color='#27ae60', alpha=0.85)
    r2 = ax2.bar(x, k2_needs, width, label='K=2 独立执行需求', color='#f39c12', alpha=0.85)
    r3 = ax2.bar(x + width, k3_needs, width, label='K=3 独立执行需求', color='#c0392b', alpha=0.85)
    
    ax2.set_xlabel('救援装备资产类别')
    ax2.set_ylabel('所需独立配置数量')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=40, ha='right')
    ax2.set_ylim(0, max(max(k2_needs), max(k3_needs)) + 2)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', frameon=True)
    ax2.set_title('(b) 集中统筹 vs 分散独立配置资源开销对比', fontsize=11, pad=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig5_task_partitioning_topology.pdf'), dpi=300)
    plt.close()
    print("图 5 导出成功: fig5_task_partitioning_topology.pdf")

def main():
    print("==========================================================")
    print("开始生成全部 5 幅学术级高清矢量图表 (PDF 格式)")
    print("==========================================================")
    plot_fig1_3d_terrain()
    plot_fig2_payload_and_energy()
    plot_fig3_gantt_chart()
    plot_fig4_coverage_and_relay()
    plot_fig5_partitioning_and_overhead()
    print("\n全部图表生成完毕，已保存至 figures/ 目录！")

if __name__ == '__main__':
    main()
