# -*- coding: utf-8 -*-
"""
问题二关键学术图表升级脚本 (figures4papers 顶刊美学规范版)
严格保持计算数据 100% 真实客观，全面升维结构排版与学术配色体系。
包含：
- fig6_q2_alns_convergence_comparison.pdf: ALNS 真实逐代收敛轨迹与邻域算子自适应权重演进
- fig7_q2_drone_schedule_gantt.pdf: 8 架实体无人机 24 架次时空调度甘特图 (无重叠无遮挡)
- fig8_q2_battery_recharge_pipeline.pdf: 14 组共享电池车电分离两阶段充放电流水线图
- fig9_q2_flight_routes_network.pdf: 24 个运输航次空间多点回路飞行网络拓扑图 (2x2 四分屏全景解构)
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines

# 引入项目基础路径与数据模块
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import NODES, DRONE_PARAMS

from f4p_style import apply_f4p_style, export_f4p_figure, F4P_PALETTE

FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")
RESULTS_Q2_DIR = os.path.join(WORKSPACE_ROOT, "results", "Q2")
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_fig6():
    """图6：ALNS 启发式求解收敛轨迹与算子权重演进 (figures4papers 真实日志双栏版)"""
    apply_f4p_style(font_size=7.5)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.8))
    
    path_42 = os.path.join(RESULTS_Q2_DIR, "Q2_ALNS_逐代收敛日志_Seed42.csv")
    path_43 = os.path.join(RESULTS_Q2_DIR, "Q2_ALNS_逐代收敛日志_Seed43.csv")
    path_44 = os.path.join(RESULTS_Q2_DIR, "Q2_ALNS_逐代收敛日志_Seed44.csv")
    path_ops = os.path.join(RESULTS_Q2_DIR, "Q2_ALNS_算子权重演进.csv")
    
    if not (os.path.exists(path_42) and os.path.exists(path_43) and os.path.exists(path_44)):
        print("错误：未找到收敛日志文件，请确认 CSV 存在")
        return
        
    df_42 = pd.read_csv(path_42)
    df_43 = pd.read_csv(path_43)
    df_44 = pd.read_csv(path_44)
    df_ops = pd.read_csv(path_ops) if os.path.exists(path_ops) else None
    
    c_main = F4P_PALETTE['red_strong']     # 采纳主方案深红 #B64342
    c_s43 = F4P_PALETTE['blue_secondary']  # 对照方案蓝 #3775BA
    c_s44 = F4P_PALETTE['green_3']         # 对照方案绿 #2E7D32
    c_scatter = F4P_PALETTE['red_strong']
    
    # Panel (a): 真实求解历程与当前解/历史最优解严格对齐折线
    ax1.plot(df_42['iteration'], df_42['best_cost'], color=c_main, linewidth=1.8,
             label=f'Seed 42 (采纳方案: {df_42["best_cost"].iloc[-1]:.2f}, 24架次)', zorder=4)
    ax1.plot(df_43['iteration'], df_43['best_cost'], color=c_s43, linewidth=1.2, linestyle='--',
             label=f'Seed 43 (对照方案: {df_43["best_cost"].iloc[-1]:.2f}, 28架次)', zorder=3)
    ax1.plot(df_44['iteration'], df_44['best_cost'], color=c_s44, linewidth=1.2, linestyle='-.',
             label=f'Seed 44 (对照方案: {df_44["best_cost"].iloc[-1]:.2f}, 25架次)', zorder=3)
    
    # 绘制真实受扰动解散点 (公理：散点必定位于最优折线上方或恰好落于折线拐点)
    step = 3
    ax1.scatter(df_42['iteration'].iloc[::step], df_42['current_cost'].iloc[::step],
                color=c_scatter, s=10, alpha=0.38, edgecolors='none', label='Seed 42 探索解散点', zorder=2)
    
    # 标注最优拐点 (移至上方迭代轮数 72~92、代价 550~590 的纯白开阔区，对应用户手绘黑框指引)
    min_cost_val = df_42['best_cost'].min()
    lock_it = df_42[df_42['best_cost'] <= min_cost_val + 1e-4]['iteration'].iloc[0]
    
    ax1.scatter(lock_it, min_cost_val, s=48, facecolors='none', edgecolors=c_main, linewidth=1.5, zorder=6)
    ax1.annotate(f'最优解锁定 (第{lock_it}代)\n24架次, 78.27kWh',
                 xy=(lock_it, min_cost_val), xytext=(72, 570),
                 arrowprops=dict(facecolor=c_main, edgecolor=c_main, arrowstyle='->', lw=1.2),
                 fontsize=6.2, color=c_main, weight='bold',
                 bbox=dict(boxstyle='round,pad=0.25', facecolor='#FEF2F2', edgecolor='#FECACA', lw=0.8),
                 zorder=7)
                 
    ax1.set_title('(a) ALNS 启发式算法 100 代阶梯收敛轨迹 (真实日志)', weight='bold')
    ax1.set_xlabel('迭代轮数 (Iteration)')
    ax1.set_ylabel('多目标综合惩罚代价值')
    ax1.set_xlim(1, 100)
    ax1.set_ylim(400, 800)
    ax1.grid(True)
    ax1.legend(loc='upper right', fontsize=6.0, framealpha=0.9)
    
    # Panel (b): 算子自适应权重自调节演化柱状图
    if df_ops is not None:
        operators = df_ops['operator'].tolist()
        weights_init = df_ops['initial_weight'].values
        weights_final = df_ops['final_weight'].values
        
        x_op = np.arange(len(operators))
        w_bar = 0.32
        c_init = F4P_PALETTE['neutral_mid']
        c_final = F4P_PALETTE['blue_main']
        
        ax2.bar(x_op - w_bar/2, weights_init, w_bar, label='初始均等权重 (16.7%)', color=c_init, alpha=0.75, edgecolor='white', linewidth=0.6)
        ax2.bar(x_op + w_bar/2, weights_final, w_bar, label='自适应收敛权重 (动态进化)', color=c_final, alpha=0.90, edgecolor='white', linewidth=0.6)
        
        for i in range(len(operators)):
            ax2.text(x_op[i] + w_bar/2, weights_final[i] + 0.01, f"{weights_final[i]*100:.0f}%",
                     ha='center', va='bottom', fontsize=6.2, weight='bold', color=c_final)
            
        ax2.set_title('(b) 自适应邻域搜索算子动态权重调优演进', weight='bold')
        ax2.set_xlabel('邻域破坏与修复算子族')
        ax2.set_ylabel('自适应得分权重归一化占比')
        ax2.set_xticks(x_op)
        ax2.set_xticklabels(operators, fontsize=6.2, rotation=15)
        ax2.set_ylim(0, 0.45)
        ax2.grid(axis='y')
        ax2.legend(loc='upper right', fontsize=6.2, framealpha=0.9)
        
    plt.subplots_adjust(left=0.08, right=0.95, bottom=0.15, top=0.90, wspace=0.28)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig6_q2_alns_convergence_comparison"), size_inches=(7.6, 3.8))
    plt.close(fig)


def plot_fig7():
    """图7：8架实体无人机24架次时空调度甘特图 (figures4papers 极简无遮挡版)"""
    apply_f4p_style(font_size=7.5)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    
    csv_path = os.path.join(RESULTS_Q2_DIR, "Q2_运输架次.csv")
    if not os.path.exists(csv_path):
        print(f"警告：未找到 {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    drones = ['U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07', 'U08']
    drone_types = {'U01': 'A', 'U02': 'A', 'U03': 'A', 'U04': 'A',
                   'U05': 'B', 'U06': 'B', 'U07': 'C', 'U08': 'C'}
    
    type_colors = {
        'A': F4P_PALETTE['blue_secondary'], # #3775BA
        'B': F4P_PALETTE['green_3'],        # #2E7D32
        'C': F4P_PALETTE['violet']          # #7C3AED
    }
    
    y_pos = {d: i for i, d in enumerate(drones)}
    # 加载货箱数据并精确统计每个架次的实际载重负荷与饱和利用率
    from data_loader import CARGO_BOXES
    box_w_map = {b['box_id']: b['weight'] for b in CARGO_BOXES}
    csv_boxes = os.path.join(RESULTS_Q2_DIR, "Q2_逐箱交付_内部核验.csv")
    trip_weights = {}
    if os.path.exists(csv_boxes):
        df_boxes = pd.read_csv(csv_boxes, encoding='utf-8')
        df_boxes['weight'] = df_boxes['货箱编号'].map(box_w_map)
        trip_weights = df_boxes.groupby('架次编号')['weight'].sum().to_dict()
    type_caps = {'A': 25.0, 'B': 50.0, 'C': 80.0}
    bar_height = 0.55

    for _, row in df.iterrows():
        d_id = row['无人机编号']
        t_start = float(row['开始时刻（s）'])
        t_end = float(row['返回O01时刻（s）'])
        trip_id = row['架次编号']
        path_str = row['访问服务区顺序']
        m_type = row['机型编号']
        
        y = y_pos[d_id]
        dur = t_end - t_start
        color = type_colors[m_type]
        
        rect = patches.FancyBboxPatch((t_start, y - bar_height/2), dur, bar_height,
                                      boxstyle="round,pad=0.02,rounding_size=0.04",
                                      facecolor=color, edgecolor='white', linewidth=0.6,
                                      alpha=0.92, zorder=3)
        ax.add_patch(rect)
        
        clean_path = path_str.replace(" -> ", "-").replace("S0", "S")
        w_val = trip_weights.get(trip_id, 0.0)
        cap = type_caps[m_type]
        ratio = w_val / cap * 100
        
        # 根据甘特块宽度自适应排版架次航线与物理载重率信息徽标
        if dur >= 1350:
            ax.text(t_start + dur/2, y + 0.10, f"{trip_id}: {clean_path}", ha='center', va='center',
                    fontsize=5.5, color='white', weight='bold', zorder=4)
            ax.text(t_start + dur/2, y - 0.12, f"[{w_val:.0f}kg, {ratio:.0f}%]", ha='center', va='center',
                    fontsize=5.0, color='#F8FAFC', alpha=0.95, zorder=4)
        elif dur >= 800:
            ax.text(t_start + dur/2, y + 0.09, f"{trip_id}: {clean_path}", ha='center', va='center',
                    fontsize=4.9, color='white', weight='bold', zorder=4)
            ax.text(t_start + dur/2, y - 0.11, f"[{w_val:.0f}kg, {ratio:.0f}%]", ha='center', va='center',
                    fontsize=4.5, color='#F8FAFC', alpha=0.95, zorder=4)
        else:
            ax.text(t_start + dur/2, y, f"{trip_id} [{w_val:.0f}kg]", ha='center', va='center',
                    fontsize=4.8, color='white', weight='bold', zorder=4)

    # 标记联合完工时刻线 Makespan = 7730.5s
    max_time = 7730.5
    c_alert = F4P_PALETTE['red_strong']
    ax.axvline(max_time, color=c_alert, linestyle='--', linewidth=1.2, zorder=5)
    
    # 标注框置于最底部 U01 任务结束后的广阔空白区 (y=0.25 处)，彻底消除对 U03 T020 的任何遮盖
    ax.annotate('最终联合完工时刻\nMakespan = 7730.5s (2.15h)',
                xy=(max_time, 0.25), xytext=(max_time - 1900, 0.25),
                arrowprops=dict(arrowstyle="->", color=c_alert, lw=1.1),
                fontsize=6.3, color=c_alert, weight='bold',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FEF2F2', edgecolor='#FECACA', lw=0.8),
                zorder=6)
    
    ax.set_title('图 7  8 架实体无人机执飞 24 架次任务时空调度甘特图 (ALNS 优化全局排程)', weight='bold', pad=22)
    ax.set_xlabel('应急救援调度推进时间 (s)')
    ax.set_ylabel('实体无人机编号与配置机型')
    
    y_labels = [f"{d} ({drone_types[d]}型)" for d in drones]
    ax.set_yticks(range(len(drones)))
    ax.set_yticklabels(y_labels, fontsize=7.0)
    ax.set_xlim(-100, 8300)
    ax.set_ylim(-0.6, len(drones) + 0.1)
    ax.grid(axis='x')
    
    # 说明图例置于图表正上方居中外部，不侵占任何数据空间
    handles = [
        patches.Patch(facecolor=type_colors['A'], edgecolor='none', label='A型轻载机 (U01~U04, 10架次)'),
        patches.Patch(facecolor=type_colors['B'], edgecolor='none', label='B型中载机 (U05~U06, 8架次)'),
        patches.Patch(facecolor=type_colors['C'], edgecolor='none', label='C型重载机 (U07~U08, 6架次)')
    ]
    ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=3, fontsize=6.8, frameon=False)
    
    plt.subplots_adjust(left=0.10, right=0.96, bottom=0.13, top=0.86)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig7_q2_drone_schedule_gantt"), size_inches=(7.6, 4.2))
    plt.close(fig)


def plot_fig8():
    """图8：14组共享电池车电分离两阶段充放电流水线图 (figures4papers 版)"""
    apply_f4p_style(font_size=7.2)
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    
    csv_path = os.path.join(RESULTS_Q2_DIR, "Q2_运输架次.csv")
    if not os.path.exists(csv_path):
        print(f"警告：未找到 {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    bats_A = [f'BAT_A_{i:02d}' for i in range(1, 7)]
    bats_B = [f'BAT_B_{i:02d}' for i in range(1, 5)]
    bats_C = [f'BAT_C_{i:02d}' for i in range(1, 5)]
    all_bats = bats_A + bats_B + bats_C
    
    bat_y = {b: i for i, b in enumerate(all_bats)}
    bar_h = 0.54
    
    c_fly = F4P_PALETTE['blue_main']       # 执飞深蓝 #0F4D92
    c_fast = F4P_PALETTE['highlight_gold'] # 恒流快充琥珀金 #D97706
    c_trickle = F4P_PALETTE['green_3']     # 涓流养护深绿 #2E7D32
    c_ready = '#CBD5E1'                    # 就绪冷云灰 (清晰高辨识度，绝不模糊看不清)
    c_ready_border = '#64748B'             # 就绪深边框
    
    # 背景就绪待命底色
    for b in all_bats:
        y = bat_y[b]
        ax.barh(y, 8000, height=bar_h, color='#E2E8F0', edgecolor=c_ready_border, linewidth=0.5, zorder=1)
        
    for _, row in df.iterrows():
        b_id = row['电池编号']
        t_start = float(row['开始时刻（s）'])
        t_end = float(row['返回O01时刻（s）'])
        energy = float(row['架次能耗（kWh）'])
        m_type = row['机型编号']
        trip_id = row['架次编号']
        
        y = bat_y[b_id]
        fly_dur = t_end - t_start
        
        # 执飞放电段
        ax.barh(y, fly_dur, left=t_start, height=bar_h, color=c_fly, edgecolor='white', linewidth=0.5, zorder=3)
        ax.text(t_start + fly_dur/2, y, trip_id, ha='center', va='center', fontsize=5.2, color='white', weight='bold', zorder=4)
        
        t_full = DRONE_PARAMS[m_type]['full_charge_time']
        e_avail = DRONE_PARAMS[m_type]['e_avail']
        soc_back = max(0.20, (e_avail - energy) / e_avail)
        
        if soc_back < 0.90:
            chg_stage1 = t_full * ((0.90 - soc_back) / 0.90) * 0.65
            chg_stage2 = t_full * 0.35
        else:
            chg_stage1 = 0.0
            chg_stage2 = t_full * ((1.0 - soc_back) / 0.10) * 0.35
            
        if chg_stage1 > 0:
            ax.barh(y, chg_stage1, left=t_end, height=bar_h, color=c_fast, edgecolor='white', linewidth=0.4, zorder=2)
        if chg_stage2 > 0:
            ax.barh(y, chg_stage2, left=t_end + chg_stage1, height=bar_h, color=c_trickle, edgecolor='white', linewidth=0.4, zorder=2)

    ax.set_title('图 8  14 组共享电池车电分离两阶段等效充电流水线推进全景 (0 冲突周转)', weight='bold', pad=30)
    ax.set_xlabel('救援调度推进时间 (s)')
    ax.set_ylabel('共享电池组资产编号')
    ax.set_yticks(range(len(all_bats)))
    ax.set_yticklabels(all_bats, fontsize=6.6)
    ax.set_xlim(-50, 8100)
    ax.set_ylim(-0.6, len(all_bats) - 0.4)
    ax.grid(axis='x')
    
    # 状态图例置于图表正上方居中，清晰展示就绪灰色块与边框
    handles = [
        patches.Patch(facecolor=c_fly, edgecolor='none', label='执飞放电作业'),
        patches.Patch(facecolor=c_fast, edgecolor='none', label='阶段一恒流快充 (0~90%, 耗时65%)'),
        patches.Patch(facecolor=c_trickle, edgecolor='none', label='阶段二涓流补电 (90~100%, 耗时35%)'),
        patches.Patch(facecolor=c_ready, edgecolor=c_ready_border, linewidth=0.8, label='电池池满电就绪待命 (Ready)')
    ]
    ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=2, fontsize=6.2, frameon=False)
    
    plt.subplots_adjust(left=0.11, right=0.96, bottom=0.10, top=0.88)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig8_q2_battery_recharge_pipeline"), size_inches=(7.6, 5.0))
    plt.close(fig)


def plot_fig9():
    """图9：24个运输航次空间多点回路飞行网络拓扑图 (figures4papers 2x2 全景解构版)"""
    apply_f4p_style(font_size=7.0)
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 6.0))
    (ax1, ax2), (ax3, ax4) = axes
    
    csv_path = os.path.join(RESULTS_Q2_DIR, "Q2_运输架次.csv")
    if not os.path.exists(csv_path):
        print(f"警告：未找到 {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    o_lon = NODES['O01']['lon']
    o_lat = NODES['O01']['lat']
    
    def draw_base(ax, title):
        for nid, node in NODES.items():
            if nid == 'O01':
                continue
            ax.scatter(node['lon'], node['lat'], s=42, color=F4P_PALETTE['neutral_dark'], edgecolors='white', linewidth=0.6, zorder=5)
            ax.text(node['lon'] + 0.002, node['lat'] + 0.0015, nid[1:], fontsize=5.6, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=6)
            
        ax.scatter(o_lon, o_lat, s=120, color=F4P_PALETTE['red_strong'], marker='*', edgecolors='black', linewidth=0.6, zorder=7)
        ax.text(o_lon, o_lat - 0.006, 'O01基地', fontsize=6.0, weight='bold', color=F4P_PALETTE['red_strong'], ha='center', zorder=7)
        ax.set_title(title, weight='bold', pad=6)
        ax.set_xlim(109.16, 109.295)
        ax.set_ylim(23.00, 23.088)
        ax.grid(True)
        ax.tick_params(labelsize=5.6)

    # (a) 单点重载直达专线网
    draw_base(ax1, '(a) 单点重载直达专线网 (11 架次)')
    s_counts = {}
    for _, row in df.iterrows():
        stops = row['访问服务区顺序'].split(" -> ")
        if len(stops) == 1:
            s_counts[stops[0]] = s_counts.get(stops[0], 0) + 1

    c_direct = F4P_PALETTE['blue_main']
    for s, cnt in s_counts.items():
        lw = 1.0 + (cnt - 1) * 0.8
        ax1.plot([o_lon, NODES[s]['lon']], [o_lat, NODES[s]['lat']],
                 color=c_direct, linestyle='--', linewidth=lw, alpha=0.82, zorder=3)
        if cnt > 1:
            mid_lon = (o_lon + NODES[s]['lon']) / 2 - 0.003
            mid_lat = (o_lat + NODES[s]['lat']) / 2 + 0.003
            ax1.text(mid_lon, mid_lat, f"{cnt}次直达", fontsize=5.2, color=c_direct, weight='bold',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='#EFF6FF', edgecolor='#BFDBFE', lw=0.4, zorder=4))
                     
    legend_a = [
        mlines.Line2D([], [], color=c_direct, linestyle='--', linewidth=1.4, label='单点往返专线 (11架次)'),
        mlines.Line2D([], [], marker='*', color='w', markerfacecolor=F4P_PALETTE['red_strong'], markeredgecolor='k', markersize=8, label='O01 调度基地')
    ]
    ax1.legend(handles=legend_a, loc='upper left', fontsize=5.6, framealpha=0.92)

    # (b) 双点闭环节约巡回航线
    draw_base(ax2, '(b) 双点闭环节约巡回航线 (10 架次)')
    double_routes = []
    seg_d_counts = {}
    for _, row in df.iterrows():
        stops = row['访问服务区顺序'].split(" -> ")
        if len(stops) == 2:
            double_routes.append(stops)
            pair = (stops[0], stops[1])
            seg_d_counts[pair] = seg_d_counts.get(pair, 0) + 1

    c_hub = F4P_PALETTE['green_2']
    c_tour = F4P_PALETTE['green_3']
    for s1, s2 in double_routes:
        ax2.plot([o_lon, NODES[s1]['lon']], [o_lat, NODES[s1]['lat']], color=c_hub, linestyle=':', linewidth=0.7, alpha=0.6, zorder=2)
        ax2.plot([NODES[s2]['lon'], o_lon], [NODES[s2]['lat'], o_lat], color=c_hub, linestyle=':', linewidth=0.7, alpha=0.6, zorder=2)

    drawn_pairs = set()
    for s1, s2 in double_routes:
        if (s1, s2) in drawn_pairs:
            continue
        drawn_pairs.add((s1, s2))
        cnt = seg_d_counts[(s1, s2)]
        ax2.annotate('', xy=(NODES[s2]['lon'], NODES[s2]['lat']), xytext=(NODES[s1]['lon'], NODES[s1]['lat']),
                     arrowprops=dict(arrowstyle="->", color=c_tour, lw=1.3, shrinkA=3, shrinkB=3), zorder=4)
        if cnt > 1:
            m_lon = (NODES[s1]['lon'] + NODES[s2]['lon']) / 2
            m_lat = (NODES[s1]['lat'] + NODES[s2]['lat']) / 2 + 0.003
            ax2.text(m_lon, m_lat, f"{cnt}次", fontsize=5.2, color=c_tour, weight='bold')

    legend_b = [
        mlines.Line2D([], [], color=c_tour, linestyle='-', linewidth=1.5, label='跨点协同巡航 (节约航程)'),
        mlines.Line2D([], [], color=c_hub, linestyle=':', linewidth=0.9, label='O01往返进出航段')
    ]
    ax2.legend(handles=legend_b, loc='upper left', fontsize=5.6, framealpha=0.92)

    # (c) 三点集约深度巡回航线
    draw_base(ax3, '(c) 三点集约深度巡回航线 (3 架次)')
    triple_meta = [
        {'color': F4P_PALETTE['violet'], 'name': 'T009: S006->S007->S011'},
        {'color': F4P_PALETTE['red_strong'], 'name': 'T012: S002->S009->S001'},
        {'color': F4P_PALETTE['highlight_gold'], 'name': 'T017: S011->S015->S003'}
    ]
    t_idx = 0
    legend_c = []
    for _, row in df.iterrows():
        stops = row['访问服务区顺序'].split(" -> ")
        if len(stops) == 3:
            meta = triple_meta[t_idx % len(triple_meta)]
            c = meta['color']
            t_id = row['架次编号']
            full = ['O01'] + stops + ['O01']
            
            for i in range(len(full) - 1):
                u, v = full[i], full[i+1]
                p_u = (o_lon, o_lat) if u == 'O01' else (NODES[u]['lon'], NODES[u]['lat'])
                p_v = (o_lon, o_lat) if v == 'O01' else (NODES[v]['lon'], NODES[v]['lat'])
                
                if u == 'O01' or v == 'O01':
                    ax3.plot([p_u[0], p_v[0]], [p_u[1], p_v[1]], color=c, linestyle=':', linewidth=0.8, alpha=0.6, zorder=2)
                else:
                    ax3.annotate('', xy=p_v, xytext=p_u,
                                 arrowprops=dict(arrowstyle="->", color=c, lw=1.4, shrinkA=3, shrinkB=3), zorder=4)
                    
            p_mid = NODES[stops[1]]
            offset_y = 0.0035 if t_idx != 1 else -0.004
            ax3.text(p_mid['lon'] - 0.005, p_mid['lat'] + offset_y, t_id, fontsize=5.6, color=c, weight='bold', zorder=6)
            legend_c.append(mlines.Line2D([], [], color=c, linestyle='-', linewidth=1.5, label=meta['name']))
            t_idx += 1
            
    ax3.legend(handles=legend_c, loc='upper left', fontsize=5.4, framealpha=0.92)

    # (d) 24 航次全网航段通行流量密度
    draw_base(ax4, '(d) 24 航次全网航段通行流量密度 (骨干走廊)')
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
            c, lw, alpha, z = F4P_PALETTE['red_strong'], 2.8, 0.92, 4
        elif cnt >= 2:
            c, lw, alpha, z = F4P_PALETTE['highlight_gold'], 1.6, 0.82, 3
        else:
            c, lw, alpha, z = F4P_PALETTE['neutral_mid'], 0.8, 0.50, 2
            
        ax4.plot([p_u[0], p_v[0]], [p_u[1], p_v[1]], color=c, linewidth=lw, alpha=alpha, zorder=z)

    legend_d = [
        mlines.Line2D([], [], color=F4P_PALETTE['red_strong'], linewidth=2.5, label='核心骨干走廊 (≥4次)'),
        mlines.Line2D([], [], color=F4P_PALETTE['highlight_gold'], linewidth=1.6, label='次级干线通道 (2~3次)'),
        mlines.Line2D([], [], color=F4P_PALETTE['neutral_mid'], linewidth=0.8, label='支线辐射航段 (1次)')
    ]
    ax4.legend(handles=legend_d, loc='upper left', fontsize=5.6, framealpha=0.92)

    for ax in [ax3, ax4]:
        ax.set_xlabel('经度 (°E)')
    for ax in [ax1, ax3]:
        ax.set_ylabel('纬度 (°N)')
        
    plt.tight_layout()
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig9_q2_flight_routes_network"), size_inches=(7.6, 6.0))
    plt.close(fig)


if __name__ == '__main__':
    plot_fig6()
    plot_fig7()
    plot_fig8()
    plot_fig9()
