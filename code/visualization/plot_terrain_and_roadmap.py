# -*- coding: utf-8 -*-
"""
宏观场景与技术路线图升级脚本 (figures4papers 顶刊美学规范版)
严格保持计算数据 100% 真实客观，全面升维结构排版与学术配色体系。
包含：
- fig1_terrain_rescue_network.pdf: 山区地形真实山体光照阴影晕渲(Hillshade)与无人机救援网络拓扑图 (带标准地学物理比例尺)
- fig2_overall_methodology_roadmap.pdf: 整体研究框架与空地协同求解系统闭环架构流 (顶刊三层闭环架构全景图)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
from matplotlib.colors import LightSource, Normalize
from matplotlib.cm import ScalarMappable

# 引入项目基础路径与数据模块
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import DEM_GRID, DEM_LONS, DEM_LATS, NODES

from f4p_style import apply_f4p_style, export_f4p_figure, F4P_PALETTE

FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_fig1():
    """图1：山区真实地形阴影晕渲(Hillshade)与无人机救援网络拓扑图 (带标准物理比例尺)"""
    apply_f4p_style(font_size=7.5)
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    
    step = 2  # 高分辨率平滑采样
    lons_sub = DEM_LONS[::step]
    lats_sub = DEM_LATS[::step]
    dem_sub = DEM_GRID[::step, ::step]
    
    # 1. 真实山体阴影晕渲 (Hillshade) 计算，呈现 Google Earth 级真实三维地貌起伏
    ls = LightSource(azdeg=315, altdeg=45)
    rgb_shaded = ls.shade(dem_sub, cmap=plt.cm.gist_earth, blend_mode='overlay', 
                          vert_exag=1.8, dx=30, dy=30, vmin=dem_sub.min(), vmax=dem_sub.max())
    
    # 渲染带阴影晕渲的地形底图
    extent = [DEM_LONS.min(), DEM_LONS.max(), DEM_LATS.min(), DEM_LATS.max()]
    ax.imshow(rgb_shaded, extent=extent, origin='lower', aspect='auto', zorder=1)
    
    # 叠加极细等高线辅助线，提供精确海拔参考
    levels = np.linspace(dem_sub.min(), dem_sub.max(), 32)
    ax.contour(lons_sub, lats_sub, dem_sub, levels=levels[::4], colors='black', alpha=0.15, linewidths=0.45, zorder=2)
    
    # 配套标准高程渐变色条
    norm = Normalize(vmin=dem_sub.min(), vmax=dem_sub.max())
    sm = ScalarMappable(norm=norm, cmap=plt.cm.gist_earth)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label('地表高程 / 海拔 (m)')
    cbar.ax.tick_params(labelsize=6.8)
    
    o_lon = NODES['O01']['lon']
    o_lat = NODES['O01']['lat']
    
    # 辐射辅助连接线
    for nid, node in NODES.items():
        if nid == 'O01':
            continue
        ax.plot([o_lon, node['lon']], [o_lat, node['lat']], 
                color=F4P_PALETTE['neutral_dark'], linestyle=':', linewidth=0.6, alpha=0.45, zorder=2)
                
    pops = [node['pop'] for nid, node in NODES.items() if nid != 'O01']
    min_pop, max_pop = min(pops), max(pops)
    
    c_node = F4P_PALETTE['blue_main']
    for nid, node in NODES.items():
        if nid == 'O01':
            continue
        pop = node['pop']
        # 散点面积与人口对应 (40 ~ 180)
        size = 40 + (pop - min_pop) / (max_pop - min_pop) * 140
        ax.scatter(node['lon'], node['lat'], s=size, color=c_node, edgecolors='white', 
                   linewidth=0.9, alpha=0.92, zorder=4)
                   
        offset_x, offset_y = 0.003, 0.002
        if nid in ['S001', 'S005', 'S011']:
            offset_y = -0.006
        elif nid in ['S004', 'S008', 'S002']:
            offset_y = 0.004
        elif nid == 'S006':
            offset_y = 0.004
            offset_x = 0.002
        elif nid == 'S003':
            # S003 为网络最西侧节点，标签置于右上方，彻底杜绝超出画布左侧坐标轴
            offset_x = 0.003
            offset_y = 0.003
        elif nid in ['S007', 'S015']:
            offset_x = -0.016
            
        label_text = f"{nid}\n({node['elev']:.0f}m)"
        ax.text(node['lon'] + offset_x, node['lat'] + offset_y, label_text, 
                fontsize=6.2, color=F4P_PALETTE['neutral_dark'], weight='bold', zorder=5,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.88, edgecolor='none'))

    # O01 调度中心
    c_base = F4P_PALETTE['red_strong']
    ax.scatter(o_lon, o_lat, s=240, color=c_base, marker='*', edgecolors='black', 
               linewidth=1.0, zorder=6)
    ax.text(o_lon + 0.004, o_lat - 0.005, 'O01 调度中心\n(基地/固定网关G01)', 
            fontsize=7.2, color=c_base, weight='bold', zorder=6,
            bbox=dict(boxstyle='square,pad=0.25', facecolor='#FEF2F2', edgecolor=c_base, linewidth=0.8))

    ax.set_title('图 1  广西横州镇龙乡高精度 30m DEM 地貌阴影晕渲与应急救援网络拓扑', weight='bold', pad=12)
    ax.set_xlabel('经度 (°E)')
    ax.set_ylabel('纬度 (°N)')
    
    margin_lon = 0.015
    margin_lat = 0.012
    all_lons = [n['lon'] for n in NODES.values()]
    all_lats = [n['lat'] for n in NODES.values()]
    ax.set_xlim(min(all_lons) - margin_lon, max(all_lons) + margin_lon)
    ax.set_ylim(min(all_lats) - margin_lat, max(all_lats) + margin_lat)
    
    # 指北针 (带标准极简学术罗盘标)
    ax.annotate('N', xy=(0.04, 0.94), xytext=(0.04, 0.86),
                xycoords='axes fraction', ha='center', va='bottom',
                arrowprops=dict(facecolor=F4P_PALETTE['neutral_dark'], width=1.5, headwidth=5),
                fontsize=7.8, weight='bold')
                
    # ---------------- 地学标准黑白物理比例尺 (Scale Bar: 0 - 2 - 4 km) ----------------
    # 当地纬度约 23.04°N, 经度 1° 对应地表物理距离约 102.32 km -> 1 km 约 0.009773° 经度
    deg_per_km = 0.009773
    sb_len_km = 4.0
    sb_len_deg = sb_len_km * deg_per_km  # 约 0.03909°
    sb_half_deg = 2.0 * deg_per_km        # 约 0.01955°
    
    sb_x0 = 109.245
    sb_y0 = 22.9945
    sb_h = 0.0016
    
    # 比例尺半透明保护底衬
    sb_bg = patches.FancyBboxPatch((sb_x0 - 0.004, sb_y0 - 0.0035), sb_len_deg + 0.012, 0.0085,
                                   boxstyle="round,pad=0.001,rounding_size=0.002",
                                   facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.7, alpha=0.92, zorder=6)
    ax.add_patch(sb_bg)
    
    # 0 ~ 2 km: 黑色段块
    rect_b = patches.Rectangle((sb_x0, sb_y0), sb_half_deg, sb_h, facecolor=F4P_PALETTE['neutral_dark'], edgecolor='black', lw=0.6, zorder=7)
    # 2 ~ 4 km: 白色段块
    rect_w = patches.Rectangle((sb_x0 + sb_half_deg, sb_y0), sb_half_deg, sb_h, facecolor='#FFFFFF', edgecolor='black', lw=0.6, zorder=7)
    ax.add_patch(rect_b)
    ax.add_patch(rect_w)
    
    # 比例尺刻度文字 (0, 2, 4 km)
    ax.text(sb_x0, sb_y0 + sb_h + 0.0010, '0', ha='center', va='bottom', fontsize=5.8, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=8)
    ax.text(sb_x0 + sb_half_deg, sb_y0 + sb_h + 0.0010, '2', ha='center', va='bottom', fontsize=5.8, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=8)
    ax.text(sb_x0 + sb_len_deg, sb_y0 + sb_h + 0.0010, '4 km', ha='center', va='bottom', fontsize=5.8, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=8)
                
    # ---------------- 顶刊级专业图例卡片 (彻底解决气泡上下垂直覆盖) ----------------
    sample_pops = [10, 100, 1000, 2100]
    legend_handles = [
        mlines.Line2D([], [], marker='*', color='w', markerfacecolor=c_base, markeredgecolor='k', markersize=10.5, label='O01 凤丹村调度基地 (127.7m)')
    ]
    for sp in sample_pops:
        s_size = 40 + (sp - min_pop) / (max_pop - min_pop) * 140
        legend_handles.append(
            mlines.Line2D([], [], marker='o', color='w', markerfacecolor=c_node, markeredgecolor='white',
                          markersize=np.sqrt(s_size)*0.85, label=f'{sp} 人')
        )
    leg = ax.legend(handles=legend_handles, loc='lower left', frameon=True, framealpha=0.92, facecolor='white',
                    edgecolor='#CBD5E1', fontsize=6.2, title='受灾人口规模与基地',
                    labelspacing=1.65, handletextpad=1.2, borderpad=0.8)
    leg.get_title().set_fontsize(6.8)
    leg.get_title().set_weight('bold')

    plt.subplots_adjust(left=0.08, right=0.95, bottom=0.10, top=0.92)
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig1_terrain_rescue_network"), size_inches=(7.8, 5.4))
    plt.close(fig)


def plot_fig2():
    """图2：山区无人机应急救援协同优化系统闭环架构与技术路线图 (顶刊三层闭环流重构版)"""
    apply_f4p_style(font_size=7.5)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.axis('off')
    
    # 主标题栏
    ax.text(0.5, 0.970, "图 2  山区洪涝灾害无人机应急运输与通信协同优化技术路线与系统架构图", 
            ha='center', va='center', fontsize=9.6, weight='bold', color=F4P_PALETTE['neutral_dark'])
    
    # ========================== Layer 1: 输入与物理环境解析层 ==========================
    layer1_y = 0.785
    layer1_h = 0.150
    
    bg_l1 = patches.FancyBboxPatch((0.02, layer1_y), 0.96, layer1_h,
                                   boxstyle="round,pad=0.005,rounding_size=0.015",
                                   facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1.0, linestyle='--', zorder=1)
    ax.add_patch(bg_l1)
    ax.text(0.035, 0.920, "【输入层】物理环境与多源多维约束解析 (Physical & Environmental Inputs)", 
            ha='left', va='center', fontsize=6.8, weight='bold', color=F4P_PALETTE['blue_main'], zorder=3)
    
    # 三个子输入卡片
    inputs = [
        {
            "x": 0.035, "w": 0.285, "title": "1. 真实三维地形空间",
            "lines": ["• 30m 高精度 DEM 栅格高程矩阵", "• 净空安全巡航走廊与坡度约束", "• 3/2 次方航程动力学能耗衰减"]
        },
        {
            "x": 0.355, "w": 0.290, "title": "2. 80件急救物资多维需求",
            "lines": ["• 急救包/食品/饮水/棉被 4大类", "• 货箱单件质量与体积几何限制", "• 首批必保物资 100% 紧急交付"]
        },
        {
            "x": 0.680, "w": 0.285, "title": "3. 异构装备与通信物理规范",
            "lines": ["• A/B/C 三型无人机最大安全载重", "• 14组车电分离共享电池周转", "• 1.4GHz 无线射频传播损耗预算"]
        }
    ]
    card1_h = 0.088
    card1_y = layer1_y + 0.010
    for inp in inputs:
        c_patch = patches.FancyBboxPatch((inp["x"], card1_y), inp["w"], card1_h,
                                         boxstyle="round,pad=0.003,rounding_size=0.010",
                                         facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=0.7, zorder=2)
        ax.add_patch(c_patch)
        ax.text(inp["x"] + 0.010, card1_y + card1_h - 0.016, inp["title"], 
                ha='left', va='center', fontsize=6.2, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=3)
        
        ly = card1_y + card1_h - 0.036
        for l_txt in inp["lines"]:
            ax.text(inp["x"] + 0.010, ly, l_txt, ha='left', va='center', fontsize=5.1, color=F4P_PALETTE['neutral_mid'], zorder=3)
            ly -= 0.020

    # 下行数据流指示箭头
    for ax_arrow in [0.175, 0.50, 0.825]:
        ax.annotate("", xy=(ax_arrow, 0.752), xytext=(ax_arrow, 0.780),
                    arrowprops=dict(arrowstyle="->", color=F4P_PALETTE['blue_secondary'], lw=1.2), zorder=4)

    # ========================== Layer 2: 四阶段核心建模与协同求解引擎 ==========================
    layer2_y = 0.250
    layer2_h = 0.495
    
    bg_l2 = patches.FancyBboxPatch((0.02, layer2_y), 0.96, layer2_h,
                                   boxstyle="round,pad=0.005,rounding_size=0.015",
                                   facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.1, zorder=1)
    ax.add_patch(bg_l2)
    ax.text(0.035, layer2_y + layer2_h - 0.025, "【求解核】四阶段递进建模与协同优化求解引擎 (Four-Stage Optimization Engines)", 
            fontsize=6.8, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=3)
            
    stages_l2 = [
        {
            "tag": "阶段 01",
            "title": "问题一：精确装载组批",
            "border": F4P_PALETTE['green_3'],
            "bg": "#F0FDF4",
            "x": 0.035, "w": 0.21,
            "steps": [
                "二分搜索有效载荷物理上界",
                "80箱物资属性与容积预检",
                "0-1 集合划分模型 (SPP)",
                "位掩码状态压缩动态规划求解",
                "基准 18 架次与 η 敏感性相变"
            ]
        },
        {
            "tag": "阶段 02",
            "title": "问题二：多机时空调度",
            "border": F4P_PALETTE['blue_main'],
            "bg": "#EFF6FF",
            "x": 0.275, "w": 0.21,
            "steps": [
                "异构车电分离多回路时空网络",
                "自适应大邻域搜索 (ALNS) 算子族",
                "多目标模拟退火 Pareto 优化",
                "8机14电双流水线仿真推进",
                "24架次极优排程 (0硬约束违约)"
            ]
        },
        {
            "tag": "阶段 03",
            "title": "问题三：中继通信协同",
            "border": F4P_PALETTE['violet'],
            "bg": "#F5F3FF",
            "x": 0.515, "w": 0.21,
            "steps": [
                "325 航段视距 (LOS) 射线追踪",
                "41.85% 阴影衰落盲区精确定位",
                "西区/东南/东北 3 制高点悬停",
                "双中继机接力无缝轮换时序",
                "方案A: 100% 连续双向通信保障"
            ]
        },
        {
            "tag": "阶段 04",
            "title": "问题四：网络分区与缺口",
            "border": F4P_PALETTE['red_strong'],
            "bg": "#FEF2F2",
            "x": 0.755, "w": 0.21,
            "steps": [
                "跨区回路强绑定不可拆分约束",
                "代数图论连通分支封闭划分",
                "K=2 与 K=3 唯一解剖结构证明",
                "战区隔离执行并发需求峰值",
                "时分复用切断之刚性缺口量化"
            ]
        }
    ]
    
    card_h2 = 0.41
    card_y2 = layer2_y + 0.025
    
    for s_idx, st in enumerate(stages_l2):
        c_patch = patches.FancyBboxPatch((st["x"], card_y2), st["w"], card_h2,
                                         boxstyle="round,pad=0.004,rounding_size=0.012",
                                         facecolor=st["bg"], edgecolor=st["border"], linewidth=1.1, zorder=2)
        ax.add_patch(c_patch)
        
        tag_patch = patches.FancyBboxPatch((st["x"] + 0.012, card_y2 + card_h2 - 0.048), st["w"] - 0.024, 0.038,
                                           boxstyle="round,pad=0.003,rounding_size=0.008",
                                           facecolor=st["border"], edgecolor='none', zorder=3)
        ax.add_patch(tag_patch)
        ax.text(st["x"] + st["w"]/2, card_y2 + card_h2 - 0.029, st["tag"], ha='center', va='center',
                fontsize=6.5, color='white', weight='bold', zorder=4)
                
        ax.text(st["x"] + st["w"]/2, card_y2 + card_h2 - 0.075, st["title"], ha='center', va='center',
                fontsize=6.8, weight='bold', color=F4P_PALETTE['neutral_dark'], zorder=4)
                
        ax.plot([st["x"] + 0.015, st["x"] + st["w"] - 0.015], [card_y2 + card_h2 - 0.10, card_y2 + card_h2 - 0.10],
                color=st["border"], linewidth=0.7, alpha=0.4, zorder=3)
                
        t_y = card_y2 + card_h2 - 0.130
        for item_txt in st["steps"]:
            ax.scatter(st["x"] + 0.012, t_y - 0.004, s=8, color=st["border"], zorder=4)
            ax.text(st["x"] + 0.022, t_y, item_txt, ha='left', va='top', fontsize=5.6, color=F4P_PALETTE['neutral_dark'], zorder=4)
            t_y -= 0.058
            
    # 阶段间极简递进连接箭头 (仅在卡片之间的净空缝隙中绘制，无文字胶囊遮挡，不侵占卡片内容)
    for idx in range(3):
        st_from = stages_l2[idx]
        st_to = stages_l2[idx + 1]
        mid_y = card_y2 + card_h2 / 2
        ax.annotate("", xy=(st_to["x"] - 0.004, mid_y), xytext=(st_from["x"] + st_from["w"] + 0.004, mid_y),
                    arrowprops=dict(arrowstyle="-|>", color=st_from["border"], lw=1.5, mutation_scale=10), zorder=4)

    # ========================== Layer 3: 综合决策评估与工程指标闭环 ==========================
    layer3_y = 0.03
    layer3_h = 0.185
    
    bg_l3 = patches.FancyBboxPatch((0.02, layer3_y), 0.96, layer3_h,
                                   boxstyle="round,pad=0.005,rounding_size=0.015",
                                   facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1.0, zorder=1)
    ax.add_patch(bg_l3)
    ax.text(0.035, layer3_y + layer3_h - 0.023, "【产出层】综合决策评估与工程指标看板 (Global Decision Support & Metrics)", 
            fontsize=6.8, weight='bold', color=F4P_PALETTE['green_3'], zorder=3)

    metrics = [
        {"x": 0.035, "w": 0.21, "title": "时效最优指标", "val": "Makespan 7730.5s (2.15h)", "sub": "首批必保物资 100% 紧急达标"},
        {"x": 0.275, "w": 0.21, "title": "能效卓越指标", "val": "总航行能耗 78.27 kWh", "sub": "14组电池车电分离 0冲突周转"},
        {"x": 0.515, "w": 0.21, "title": "通信坚韧指标", "val": "100% 连续无缝链路", "sub": "325 航段全覆盖，无孤岛死角"},
        {"x": 0.755, "w": 0.21, "title": "管理学缺口预警", "val": "刚性短缺量化核算", "sub": "B机缺1~2架/B电缺2组/中继缺1架"}
    ]
    
    for m in metrics:
        m_patch = patches.FancyBboxPatch((m["x"], layer3_y + 0.014), m["w"], 0.115,
                                         boxstyle="round,pad=0.004,rounding_size=0.010",
                                         facecolor='#FFFFFF', edgecolor='#E2E8F0', linewidth=0.8, zorder=2)
        ax.add_patch(m_patch)
        ax.text(m["x"] + 0.010, layer3_y + 0.100, m["title"], fontsize=5.8, weight='bold', color=F4P_PALETTE['neutral_mid'], zorder=3)
        ax.text(m["x"] + 0.010, layer3_y + 0.066, m["val"], fontsize=6.3, weight='bold', color=F4P_PALETTE['blue_main'], zorder=3)
        ax.text(m["x"] + 0.010, layer3_y + 0.035, m["sub"], fontsize=5.2, color=F4P_PALETTE['neutral_dark'], zorder=3)

    # 求解核到底部看板的连接引导线
    for c_arrow in [0.14, 0.38, 0.62, 0.86]:
        ax.annotate("", xy=(c_arrow, layer3_y + layer3_h), xytext=(c_arrow, layer2_y),
                    arrowprops=dict(arrowstyle="->", color='#94A3B8', lw=0.9, linestyle=':'), zorder=4)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    
    export_f4p_figure(fig, os.path.join(FIGURES_DIR, "fig2_overall_methodology_roadmap"), size_inches=(8.5, 5.5))
    plt.close(fig)


if __name__ == '__main__':
    plot_fig1()
    plot_fig2()
