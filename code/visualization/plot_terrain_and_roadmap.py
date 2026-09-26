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
from matplotlib.colors import LightSource, Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

# 引入项目基础路径与数据模块
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "code"))
from data_loader import DEM_GRID, DEM_LONS, DEM_LATS, NODES

from f4p_style import apply_f4p_style, export_f4p_figure, F4P_PALETTE

FIGURES_DIR = os.path.join(WORKSPACE_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_fig1():
    """图1：高精度 2D GIS 矢量等高线测绘与应急救援网络拓扑图 (全矢量锐利无模糊，带标准物理比例尺与分级生命线)"""
    apply_f4p_style(font_size=7.5)
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    
    # 1. 提取局部高精度 ROI (全分辨率 30m 真实网格，拒绝全局粗采样与平滑模糊)
    margin_lon = 0.016
    margin_lat = 0.014
    all_lons = [n['lon'] for n in NODES.values()]
    all_lats = [n['lat'] for n in NODES.values()]
    min_lon, max_lon = min(all_lons) - margin_lon, max(all_lons) + margin_lon
    min_lat, max_lat = min(all_lats) - margin_lat, max(all_lats) + margin_lat

    lon_mask = (DEM_LONS >= min_lon) & (DEM_LONS <= max_lon)
    lat_mask = (DEM_LATS >= min_lat) & (DEM_LATS <= max_lat)

    sub_lons = DEM_LONS[lon_mask]
    sub_lats = DEM_LATS[lat_mask]
    sub_dem = DEM_GRID[np.ix_(lat_mask, lon_mask)].copy()

    LON_2D, LAT_2D = np.meshgrid(sub_lons, sub_lats)

    # 2. 地理测绘标准等高线色阶与分层设色 (通透清爽、大地植被自然色阶)
    levels = np.arange(100, 780, 40)
    topo_palette = [
        '#F4F8F3', '#E5EFE2', '#D3E5CF', '#BFDCB9', '#ACD2A4', 
        '#E6DDAE', '#DEC98E', '#D1B170', '#C29858', '#AE7E47', 
        '#99673C', '#835334', '#6D402C', '#583025'
    ]
    cmap_clean = LinearSegmentedColormap.from_list('clean_topo', topo_palette, N=len(levels)-1)

    # 纯矢量分层设色底图
    cf = ax.contourf(LON_2D, LAT_2D, sub_dem, levels=levels, cmap=cmap_clean, alpha=0.90, zorder=1)

    # 锐利等高线轮廓 (首曲线 0.45pt，计曲线 0.85pt 并注记高程)
    c_lines = ax.contour(LON_2D, LAT_2D, sub_dem, levels=levels, colors='#64748B', linewidths=0.45, alpha=0.55, zorder=2)
    c_index = ax.contour(LON_2D, LAT_2D, sub_dem, levels=levels[::3], colors='#334155', linewidths=0.85, alpha=0.75, zorder=2)
    ax.clabel(c_index, inline=True, fmt='%1.0fm', fontsize=5.2, colors='#334155')

    # 高程渐变色条
    cbar = fig.colorbar(cf, ax=ax, fraction=0.035, pad=0.02, ticks=levels[::2])
    cbar.set_label('地表高程 / 海拔 (m)', weight='bold')
    cbar.ax.tick_params(labelsize=6.8)

    o_lon = NODES['O01']['lon']
    o_lat = NODES['O01']['lat']

    # 人口等级函数 (四级感知阶梯，双重冗余编码)
    def get_pop_tier(pop):
        if pop < 50:
            return {'tier': 'I', 'size': 45, 'color': '#0284C7', 'label': '微型聚落 (<50人)'}
        elif pop <= 150:
            return {'tier': 'II', 'size': 95, 'color': '#D97706', 'label': '小型村落 (50-150人)'}
        elif pop <= 400:
            return {'tier': 'III', 'size': 180, 'color': '#EA580C', 'label': '中型村落 (150-400人)'}
        else:
            return {'tier': 'IV', 'size': 380, 'color': '#DC2626', 'label': '特大聚集区 (2100人)'}

    # 3. 救援拓扑连接线渲染 (彻底解决共线重叠，确保 15 条生命线皆清晰独立)
    for nid, node in NODES.items():
        if nid == 'O01':
            continue
        
        # 针对特大核心 S001 (2100人)：专属一级核心主通道（加粗白底 + 强对比高亮实线，直抵红心）
        if nid == 'S001':
            ax.plot([o_lon, node['lon']], [o_lat, node['lat']], color='#FFFFFF', lw=3.8, zorder=4)
            ax.plot([o_lon, node['lon']], [o_lat, node['lat']], color='#1E40AF', lw=2.0, linestyle='-', zorder=5)
        elif nid == 'S009':
            # S009 (45人) 恰好与 S001 处于同一直线，为空域安全与视觉区分，航线经由东侧山谷通道略作分流
            mid_lon = (o_lon + node['lon']) / 2.0 + 0.0062
            mid_lat = (o_lat + node['lat']) / 2.0 - 0.0030
            t = np.linspace(0, 1, 30)
            curve_lon = (1 - t)**2 * o_lon + 2 * (1 - t) * t * mid_lon + t**2 * node['lon']
            curve_lat = (1 - t)**2 * o_lat + 2 * (1 - t) * t * mid_lat + t**2 * node['lat']
            
            ax.plot(curve_lon, curve_lat, color='#FFFFFF', lw=2.4, zorder=3)
            ax.plot(curve_lon, curve_lat, color='#1D4ED8', lw=1.2, linestyle='--', dashes=(4, 2.5), zorder=4)
        else:
            # 其他 13 个常规辐射分支
            ax.plot([o_lon, node['lon']], [o_lat, node['lat']], color='#FFFFFF', lw=2.4, zorder=3)
            ax.plot([o_lon, node['lon']], [o_lat, node['lat']], color='#1D4ED8', lw=1.2, linestyle='--', dashes=(4, 2.5), zorder=4)

    # 4. 受灾节点散点与智能标签排布
    for nid, node in NODES.items():
        if nid == 'O01':
            continue
        tier = get_pop_tier(node['pop'])
        ax.scatter(node['lon'], node['lat'], s=tier['size'], color=tier['color'], 
                   edgecolors='#FFFFFF', linewidth=1.2, zorder=6)
        
        offset_x, offset_y = 0.003, 0.002
        if nid == 'S001':
            offset_x = 0.004
            offset_y = -0.004
        elif nid in ['S005', 'S011']:
            offset_y = -0.006
        elif nid in ['S004', 'S008', 'S002']:
            offset_y = 0.004
        elif nid == 'S006':
            offset_y = 0.004
            offset_x = 0.002
        elif nid == 'S003':
            offset_x = 0.003
            offset_y = 0.003
        elif nid in ['S007', 'S015']:
            offset_x = -0.016
            
        label_text = f"{nid} ({node['pop']}人)\n{node['elev']:.0f}m"
        ax.text(node['lon'] + offset_x, node['lat'] + offset_y, label_text, 
                fontsize=5.8, color='#0F172A', weight='bold', zorder=7,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', alpha=0.92, edgecolor='#94A3B8', linewidth=0.5))

    # O01 调度基地 (指挥网关)
    c_base = '#DC2626'
    ax.scatter(o_lon, o_lat, s=260, color=c_base, marker='*', edgecolors='#000000', linewidth=0.8, zorder=8)
    ax.text(o_lon - 0.004, o_lat - 0.0055, 'O01 凤丹村调度基地\n(指挥中心/固定网关G01)', 
            fontsize=6.8, color='#991B1B', weight='bold', zorder=8, ha='right',
            bbox=dict(boxstyle='square,pad=0.25', facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.8))

    ax.set_title('图 1  高精度 2D GIS 矢量等高线测绘与应急救援网络拓扑图', weight='bold', pad=12)
    ax.set_xlabel('经度 (°E)')
    ax.set_ylabel('纬度 (°N)')
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # 罗盘指北针
    ax.annotate('N', xy=(0.04, 0.94), xytext=(0.04, 0.86), xycoords='axes fraction', ha='center', va='bottom',
                arrowprops=dict(facecolor='#0F172A', width=1.5, headwidth=5), fontsize=7.8, weight='bold')

    # 标准地学黑白物理比例尺 (0 - 2 - 4 km)
    deg_per_km = 0.009773
    sb_len_km = 4.0
    sb_len_deg = sb_len_km * deg_per_km
    sb_half_deg = 2.0 * deg_per_km

    sb_x0 = 109.245
    sb_y0 = 22.9945
    sb_h = 0.0016

    sb_bg = patches.FancyBboxPatch((sb_x0 - 0.004, sb_y0 - 0.0035), sb_len_deg + 0.012, 0.0085,
                                   boxstyle="round,pad=0.001,rounding_size=0.002",
                                   facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.7, alpha=0.94, zorder=6)
    ax.add_patch(sb_bg)

    rect_b = patches.Rectangle((sb_x0, sb_y0), sb_half_deg, sb_h, facecolor='#0F172A', edgecolor='black', lw=0.6, zorder=7)
    rect_w = patches.Rectangle((sb_x0 + sb_half_deg, sb_y0), sb_half_deg, sb_h, facecolor='#FFFFFF', edgecolor='black', lw=0.6, zorder=7)
    ax.add_patch(rect_b)
    ax.add_patch(rect_w)

    ax.text(sb_x0, sb_y0 + sb_h + 0.0010, '0', ha='center', va='bottom', fontsize=5.8, weight='bold', color='#0F172A', zorder=8)
    ax.text(sb_x0 + sb_half_deg, sb_y0 + sb_h + 0.0010, '2', ha='center', va='bottom', fontsize=5.8, weight='bold', color='#0F172A', zorder=8)
    ax.text(sb_x0 + sb_len_deg, sb_y0 + sb_h + 0.0010, '4 km', ha='center', va='bottom', fontsize=5.8, weight='bold', color='#0F172A', zorder=8)

    # 专属学术图例
    legend_handles = [
        mlines.Line2D([], [], marker='*', color='w', markerfacecolor=c_base, markeredgecolor='k', markersize=11.0, label='O01 调度中心 (指挥基站)'),
        mlines.Line2D([], [], color='#1E40AF', linestyle='-', linewidth=2.0, label='S001 特大聚落核心主干航路'),
        mlines.Line2D([], [], color='#1D4ED8', linestyle='--', dashes=(3, 2), linewidth=1.5, label='常规应急生命线连接通道'),
        mlines.Line2D([], [], marker='o', color='w', markerfacecolor='#0284C7', markeredgecolor='white', markersize=6.0, label='微型聚落 (<50人)'),
        mlines.Line2D([], [], marker='o', color='w', markerfacecolor='#D97706', markeredgecolor='white', markersize=8.5, label='小型村落 (50-150人)'),
        mlines.Line2D([], [], marker='o', color='w', markerfacecolor='#EA580C', markeredgecolor='white', markersize=11.0, label='中型村落 (150-400人)'),
        mlines.Line2D([], [], marker='o', color='w', markerfacecolor='#DC2626', markeredgecolor='white', markersize=14.5, label='特大聚集区 (2100人)'),
    ]
    leg = ax.legend(handles=legend_handles, loc='lower left', frameon=True, framealpha=0.94, facecolor='white',
                    edgecolor='#CBD5E1', fontsize=5.9, title='基地、航线与受灾人口等级',
                    labelspacing=1.30, handletextpad=1.0, borderpad=0.7)
    leg.get_title().set_fontsize(6.5)
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
            "lines": ["• A/B/C 三型无人机最大安全载重", "• 14组车电分离共享电池周转", "• 2.4GHz 无线射频传播损耗预算"]
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
