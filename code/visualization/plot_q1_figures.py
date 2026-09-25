# -*- coding: utf-8 -*-
"""
figures4papers 风格升级：问题一关键图表
- 图 3: fig3_q1_cargo_demand_profile (服务区分类需求与80箱物理属性分布)
- 图 4: fig4_q1_safe_payload_boundary (三类机型15个服务区最大安全物理载荷上界)
- 图 5: fig5_q1_eta_sensitivity (返航安全电量余量 eta 敏感性全景分析)
输出目录: figures/
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import CARGO_BOXES, NODES

from f4p_style import apply_f4p_style, export_f4p_figure, F4P_PALETTE

FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")
RESULTS_Q1_DIR = os.path.join(WORKSPACE_ROOT, "results", "Q1")
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_fig3():
    """图3：80箱物资物理属性与各服务区需求分布 (figures4papers 典雅学术版)"""
    apply_f4p_style(font_size=7.8)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.8))
    
    svc_ids = [f'S{i:03d}' for i in range(1, 16)]
    med_counts, life_counts = [], []
    pops = [NODES[s]['pop'] for s in svc_ids]
    
    for s in svc_ids:
        s_boxes = [b for b in CARGO_BOXES if b['service_id'] == s]
        med = sum(1 for b in s_boxes if '医疗' in b['type'])
        life = sum(1 for b in s_boxes if '生活' in b['type'])
        med_counts.append(med)
        life_counts.append(life)
        
    x = np.arange(len(svc_ids))
    width = 0.60
    
    # Panel (a): 堆叠柱状图与人口规模 (严格还原 0~18 真实尺度)
    c_med = F4P_PALETTE['red_strong']   # 学术深红 #B64342
    c_life = F4P_PALETTE['blue_main']   # 核心锚点蓝 #0F4D92
    c_pop = F4P_PALETTE['highlight_gold'] # 琥珀金 #D97706
    
    ax1.bar(x, med_counts, width, label='急救医疗物资 (箱)', color=c_med, edgecolor='white', linewidth=0.7)
    ax1.bar(x, life_counts, width, bottom=med_counts, label='生活保障物资 (箱)', color=c_life, edgecolor='white', linewidth=0.7)
    
    ax1.set_xlabel('受灾服务区编号')
    ax1.set_ylabel('需求货箱数量 (箱)')
    ax1.set_title('(a) 15 个受灾服务区应急物资分类需求分布', weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([s[1:] for s in svc_ids], fontsize=6.5, rotation=45)
    ax1.set_ylim(0, 18)
    ax1.grid(axis='y')
    ax1.legend(loc='upper right', fontsize=6.8)
    
    # 右轴人口
    ax1_twin = ax1.twinx()
    ax1_twin.plot(x, pops, color=c_pop, marker='o', markersize=3.2, linewidth=1.2, linestyle='--', label='受灾人口')
    ax1_twin.set_ylabel('受灾人口规模 (人)', color=c_pop)
    ax1_twin.tick_params(axis='y', labelcolor=c_pop)
    ax1_twin.set_yscale('log')
    ax1_twin.spines['top'].set_visible(False)
    ax1_twin.spines['left'].set_visible(False)
    
    # Panel (b): 气泡散点图
    box_specs = [
        {'name': '急救医疗包', 'w': 3.0, 'v': 12.0, 'color': c_med, 'total': 16, 'first': 15},
        {'name': '防寒棉被褥', 'w': 6.0, 'v': 35.0, 'color': c_life, 'total': 9, 'first': 0},
        {'name': '应急干粮食品', 'w': 8.0, 'v': 28.0, 'color': c_life, 'total': 19, 'first': 0},
        {'name': '瓶装饮用水', 'w': 14.0, 'v': 27.0, 'color': c_life, 'total': 36, 'first': 15},
    ]
    
    for item in box_specs:
        s_size = item['total'] * 16.0 + 90.0
        ax2.scatter(item['w'], item['v'], s=s_size, color=item['color'], alpha=0.88,
                    edgecolors=F4P_PALETTE['neutral_dark'], linewidth=0.8, zorder=4)
        if item['first'] > 0:
            ax2.scatter(item['w'], item['v'], s=50, marker='^', color='white',
                        edgecolors=F4P_PALETTE['neutral_dark'], linewidth=0.7, zorder=5)
            
    # 原位微注记
    ax2.annotate('急救医疗包\n16箱 (首批15箱)', xy=(3.0, 12.0), xytext=(5.0, 12.0),
                 arrowprops=dict(arrowstyle="->", color=F4P_PALETTE['neutral_mid'], lw=0.6),
                 fontsize=6.2, color=F4P_PALETTE['neutral_dark'], weight='bold', va='center')
    ax2.annotate('防寒棉被褥\n9箱', xy=(6.0, 35.0), xytext=(8.0, 35.8),
                 arrowprops=dict(arrowstyle="->", color=F4P_PALETTE['neutral_mid'], lw=0.6),
                 fontsize=6.2, color=F4P_PALETTE['neutral_dark'], weight='bold', va='center')
    ax2.annotate('应急干粮食品\n19箱', xy=(8.0, 28.0), xytext=(9.8, 31.2),
                 arrowprops=dict(arrowstyle="->", color=F4P_PALETTE['neutral_mid'], lw=0.6),
                 fontsize=6.2, color=F4P_PALETTE['neutral_dark'], weight='bold', va='center')
    ax2.annotate('瓶装饮用水\n36箱 (首批15箱)', xy=(14.0, 27.0), xytext=(16.8, 27.0),
                 arrowprops=dict(arrowstyle="->", color=F4P_PALETTE['neutral_mid'], lw=0.6),
                 fontsize=6.2, color=F4P_PALETTE['neutral_dark'], weight='bold', va='center')
    
    # 载重上限线与徽章标头
    ax2.axvline(25, color=F4P_PALETTE['green_3'], linestyle='--', linewidth=1.1, alpha=0.85)
    ax2.axvline(30, color=F4P_PALETTE['highlight_gold'], linestyle='--', linewidth=1.1, alpha=0.85)
    
    ax2.text(25, 37.2, 'A机上限\n25 kg', ha='center', va='center', fontsize=6.0, color=F4P_PALETTE['green_3'], weight='bold',
             bbox=dict(boxstyle='round,pad=0.25', facecolor=F4P_PALETTE['green_1'], edgecolor=F4P_PALETTE['green_2'], lw=0.6))
    ax2.text(30, 37.2, 'B机上限\n30 kg', ha='center', va='center', fontsize=6.0, color=F4P_PALETTE['highlight_gold'], weight='bold',
             bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFBEB', edgecolor='#FDE68A', lw=0.6))
             
    # 物理特性小卡片
    insight_text = (
        "物理特性与运载洞察:\n"
        "- 单件货箱最大质量为 14kg\n"
        "  远低于单机载重上限 (25/30kg)\n"
        "- 单机单件绝不超载\n"
        "- 装载瓶颈在于容积配载与架次权衡"
    )
    ax2.text(21.5, 14.5, insight_text, fontsize=5.8, color=F4P_PALETTE['neutral_dark'], linespacing=1.35,
             bbox=dict(boxstyle='round,pad=0.4', facecolor=F4P_PALETTE['neutral_light'], edgecolor=F4P_PALETTE['neutral_gray'], lw=0.5))
             
    ax2.set_xlabel('货箱单件质量 (kg)')
    ax2.set_ylabel('货箱单件容积 (L)')
    ax2.set_title('(b) 80 件应急救援货箱物理属性与载重余量分布', weight='bold', pad=18)
    ax2.set_xlim(1.0, 33.5)
    ax2.set_ylim(8.0, 40.0)
    ax2.grid(True)
    
    # 外部顶部无框图例
    scatter_handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c_med, markeredgecolor=F4P_PALETTE['neutral_dark'], markersize=6.0, label='急救医疗物资'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c_life, markeredgecolor=F4P_PALETTE['neutral_dark'], markersize=6.0, label='生活保障物资'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='white', markeredgecolor=F4P_PALETTE['neutral_dark'], markersize=5.5, label='含首批必保要求')
    ]
    ax2.legend(handles=scatter_handles, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=3, fontsize=6.2, frameon=False)
    
    # 调整子图间距，彻底防止 (a) 轴右侧 twinx 标签与 (b) 轴左侧 ylabel 重叠
    plt.subplots_adjust(left=0.08, right=0.92, bottom=0.15, top=0.86, wspace=0.35)
    
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig3_q1_cargo_demand_profile"), size_inches=(8.2, 3.8))
    plt.close(fig)


def plot_fig4():
    """图4：三类机型在15个服务区的最大安全物理载荷上界 (figures4papers 分组柱状标杆版)"""
    apply_f4p_style(font_size=7.8)
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    
    csv_path = os.path.join(RESULTS_Q1_DIR, "Q1_敏感性_eta_安全载荷.csv")
    df = pd.read_csv(csv_path)
    df_base = df[df['安全余量eta'] == 0.2].copy()
    
    svc_labels = [s for s in df_base['服务区编号']]
    x = np.arange(len(svc_labels))
    width = 0.26
    
    # figures4papers 核心三元色：次级蓝、深墨绿、优雅紫
    c_A = F4P_PALETTE['blue_secondary']  # #3775BA
    c_B = F4P_PALETTE['green_3']         # #2E7D32
    c_C = F4P_PALETTE['violet']          # #7C3AED
    c_alert = F4P_PALETTE['red_strong']  # #B64342
    
    ax.bar(x - width, df_base['A型最大安全载荷(kg)'], width, label='A型机 (额定 25kg)', color=c_A, edgecolor='white', linewidth=0.6)
    ax.bar(x, df_base['B型最大安全载荷(kg)'], width, label='B型机 (额定 30kg)', color=c_B, edgecolor='white', linewidth=0.6)
    ax.bar(x + width, df_base['C型最大安全载荷(kg)'], width, label='C型机 (额定 80kg)', color=c_C, edgecolor='white', linewidth=0.6)
    
    # 理论参考线
    ax.axhline(25, color=c_A, linestyle=':', linewidth=0.8, alpha=0.7)
    ax.axhline(30, color=c_B, linestyle=':', linewidth=0.8, alpha=0.7)
    ax.axhline(80, color=c_C, linestyle=':', linewidth=0.8, alpha=0.7)
    
    # 突出标注降额点 (In-Place Annotation 柱顶学术注记)
    for idx, row in df_base.iterrows():
        c_val = row['C型最大安全载荷(kg)']
        if c_val < 79.9:
            svc_idx = svc_labels.index(row['服务区编号'])
            ax.annotate(f"{c_val:.1f}kg",
                        xy=(svc_idx + width, c_val),
                        xytext=(svc_idx + width - 0.25, c_val + 5.0),
                        arrowprops=dict(arrowstyle="->", color=c_alert, lw=0.8),
                        fontsize=6.2, color=c_alert, weight='bold')
                        
    ax.set_title('图 4  基准返航余量 (η=0.20) 下三类机型在 15 个受灾服务区的最大安全物理载荷上界', weight='bold', pad=18)
    ax.set_xlabel('受灾服务区编号')
    ax.set_ylabel('最大安全物理载荷上限 (kg)')
    ax.set_xticks(x)
    ax.set_xticklabels(svc_labels, fontsize=6.8, rotation=30)
    ax.set_ylim(0, 95)
    ax.grid(axis='y')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=3, fontsize=6.8)
    
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig4_q1_safe_payload_boundary"), size_inches=(6.8, 3.8))
    plt.close(fig)


def plot_fig5():
    """图5：返航安全电量余量 eta 敏感性多指标全景分析图 (figures4papers 典雅版)"""
    apply_f4p_style(font_size=7.8)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.6))
    
    csv_path = os.path.join(RESULTS_Q1_DIR, "Q1_敏感性_eta_汇总.csv")
    df = pd.read_csv(csv_path)
    
    etas = df['安全余量eta'].values
    etas_str = [f"{e*100:.0f}%" for e in etas]
    x = np.arange(len(etas))
    
    # Panel (a): 堆叠柱状图
    width = 0.50
    b_trips = df['B型架次'].values
    c_trips = df['C型架次'].values
    
    c_B = F4P_PALETTE['green_3']
    c_C = F4P_PALETTE['violet']
    
    ax1.bar(x, b_trips, width, label='B型机架次 (30kg)', color=c_B, edgecolor='white', linewidth=0.7)
    ax1.bar(x, c_trips, width, bottom=b_trips, label='C型机架次 (80kg)', color=c_C, edgecolor='white', linewidth=0.7)
    
    for i, total in enumerate(df['总架次'].values):
        ax1.text(x[i], total + 0.4, f"{total}架", ha='center', va='bottom', fontsize=6.5, weight='bold', color=F4P_PALETTE['neutral_dark'])
        
    ax1.set_title('(a) 安全电量余量 η 对总架次及机型构成的影响', weight='bold')
    ax1.set_xlabel('返航最低安全电量余量 η')
    ax1.set_ylabel('优化所需运输总架次 (次)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(etas_str)
    ax1.set_ylim(0, 30)
    ax1.grid(axis='y')
    ax1.legend(loc='upper left', fontsize=6.5)
    
    # 高亮基准点 eta=0.20
    base_idx = np.where(np.isclose(etas, 0.20))[0][0]
    ax1.get_children()[base_idx].set_edgecolor(F4P_PALETTE['red_alert'])
    ax1.get_children()[base_idx].set_linewidth(1.4)
    
    # Panel (b): 双轴趋势线
    energy = df['总能耗(kWh)'].values
    time_h = df['累计作业时间(s)'].values / 3600.0
    
    c_e = F4P_PALETTE['blue_main']
    c_t = F4P_PALETTE['highlight_gold']
    
    ax2.plot(x, energy, marker='o', markersize=4.5, linewidth=1.5, color=c_e, label='总飞行能耗 (kWh)')
    ax2.set_xlabel('返航最低安全电量余量 η')
    ax2.set_ylabel('总飞行能耗 (kWh)', color=c_e)
    ax2.tick_params(axis='y', labelcolor=c_e)
    ax2.set_xticks(x)
    ax2.set_xticklabels(etas_str)
    ax2.set_ylim(50, 90)
    ax2.grid(True)
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x, time_h, marker='s', markersize=4.5, linewidth=1.5, linestyle='--', color=c_t, label='累计作业时间 (h)')
    ax2_twin.set_ylabel('累计作业时间 (h)', color=c_t)
    ax2_twin.tick_params(axis='y', labelcolor=c_t)
    ax2_twin.set_ylim(8.0, 14.0)
    ax2_twin.spines['top'].set_visible(False)
    ax2_twin.spines['left'].set_visible(False)
    
    # 基准垂直指示线与高亮圈
    ax2.axvline(base_idx, color=F4P_PALETTE['red_alert'], linestyle=':', linewidth=1.0, alpha=0.75)
    ax2.scatter(base_idx, energy[base_idx], s=40, facecolors='none', edgecolors=F4P_PALETTE['red_alert'], linewidth=1.2, zorder=5)
    ax2_twin.scatter(base_idx, time_h[base_idx], s=40, facecolors='none', edgecolors=F4P_PALETTE['red_alert'], linewidth=1.2, zorder=5)
    
    # 拐点标注
    ax2.annotate('基准最优平衡点 (η=0.20)\n能耗 59.20kWh, 耗时 9.08h',
                 xy=(base_idx, energy[base_idx]), xytext=(0.15, 78.0),
                 arrowprops=dict(facecolor=F4P_PALETTE['red_alert'], arrowstyle='->', lw=0.9),
                 fontsize=6.2, color=F4P_PALETTE['red_alert'], weight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#FEF2F2', edgecolor=F4P_PALETTE['red_alert'], lw=0.6))
                 
    ax2.set_title('(b) 能耗与耗时随电量余量剧增的临界相变', weight='bold')
    
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig5_q1_eta_sensitivity"), size_inches=(7.5, 3.6))
    plt.close(fig)


if __name__ == '__main__':
    plot_fig3()
    plot_fig4()
    plot_fig5()
