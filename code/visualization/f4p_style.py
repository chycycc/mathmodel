# -*- coding: utf-8 -*-
"""
figures4papers (ChenLiu-1996) 顶刊绘图样式系统适配模块
整合 Yale CS 顶刊规范 (NeurIPS/ICML/Nature MI):
1. 经典语义调色板 PALETTE (学术蓝、渐进绿、对照红/粉、中性灰、点睛青/紫)
2. 极简高对比坐标轴 (移除 top/right 脊柱，优雅轴线与字体排版)
3. 导出规范 (300 DPI 矢量 PDF、高清 PNG、双通道支持)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. figures4papers 核心官方语义调色板
F4P_PALETTE = {
    "blue_main": "#0F4D92",       # 核心锚点蓝 (正式提案/采纳方案)
    "blue_secondary": "#3775BA",  # 次级蓝 (关键通道/对比项)
    "blue_light": "#B9D4F2",      # 极浅蓝 (微底衬)
    
    "green_1": "#DDF3DE",        # 浅绿
    "green_2": "#AADCA9",        # 中绿
    "green_3": "#2E7D32",        # 深绿 / 充裕 / 节约
    "green_accent": "#059669",   # 翡翠绿
    
    "red_1": "#F6CFCB",          # 极浅粉红 (警告背景)
    "red_2": "#E9A6A1",          # 中粉红
    "red_strong": "#B64342",     # 经典学术深红 / 紧迫 / 违约 / 基准
    "red_alert": "#DC2626",      # 高亮警示红
    
    "neutral_light": "#F8FAFC",  # 超浅中性灰
    "neutral_gray": "#CFCECE",   # 浅灰
    "neutral_mid": "#767676",    # 中灰
    "neutral_dark": "#272727",   # 极深炭灰 (文字/坐标)
    
    "highlight_gold": "#D97706", # 琥珀金 (突出对比)
    "teal": "#0D9488",           # 青绿
    "violet": "#7C3AED",         # 紫罗兰 (三点/复杂多变量)
}

def apply_f4p_style(font_size=8.0, axes_linewidth=1.0, lang='zh'):
    """
    配置全局 matplotlib rcParams，符合 figures4papers 顶级期刊美学标准
    """
    plt.rcParams.clear()
    
    # 字体降级族 (Windows 环境兼容中文与 Times/Helvetica)
    if lang == 'zh':
        font_families = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'sans-serif']
    else:
        font_families = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
        
    plt.rcParams['font.family'] = font_families
    plt.rcParams['font.sans-serif'] = font_families
    plt.rcParams['axes.unicode_minus'] = False
    
    # 基础字号与线宽阶梯
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.labelsize'] = font_size
    plt.rcParams['axes.titlesize'] = font_size + 1.2
    plt.rcParams['xtick.labelsize'] = font_size - 1.0
    plt.rcParams['ytick.labelsize'] = font_size - 1.0
    plt.rcParams['legend.fontsize'] = font_size - 1.2
    plt.rcParams['figure.titlesize'] = font_size + 2.0
    
    # 极简坐标轴 (移除 top 与 right)
    plt.rcParams['axes.linewidth'] = axes_linewidth
    plt.rcParams['axes.edgecolor'] = F4P_PALETTE['neutral_dark']
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    
    # 刻度线规范
    plt.rcParams['xtick.major.size'] = 3.5
    plt.rcParams['xtick.major.width'] = axes_linewidth * 0.8
    plt.rcParams['ytick.major.size'] = 3.5
    plt.rcParams['ytick.major.width'] = axes_linewidth * 0.8
    plt.rcParams['xtick.direction'] = 'out'
    plt.rcParams['ytick.direction'] = 'out'
    plt.rcParams['xtick.color'] = F4P_PALETTE['neutral_dark']
    plt.rcParams['ytick.color'] = F4P_PALETTE['neutral_dark']
    
    # 网格线规范 (极简淡灰辅助线)
    plt.rcParams['grid.color'] = F4P_PALETTE['neutral_gray']
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.alpha'] = 0.45
    
    # 图例无框轻量化
    plt.rcParams['legend.frameon'] = False
    plt.rcParams['legend.handlelength'] = 1.4
    plt.rcParams['legend.handletextpad'] = 0.5
    plt.rcParams['legend.borderaxespad'] = 0.4
    
    # 输出与渲染
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['savefig.bbox'] = 'tight'
    plt.rcParams['savefig.pad_inches'] = 0.05
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

def export_f4p_figure(fig, basename, size_inches=(7.2, 4.0), dpi=300):
    """
    统一导出为 PDF 与 PNG，严格遵循出版规范
    """
    fig.set_size_inches(size_inches)
    pdf_path = f"{basename}.pdf"
    png_path = f"{basename}.png"
    gray_path = f"{basename}_grayscale.png"
    
    os.makedirs(os.path.dirname(os.path.abspath(basename)), exist_ok=True)
    
    # 1. 导出矢量 PDF
    fig.savefig(pdf_path, dpi=dpi, bbox_inches='tight', pad_inches=0.04)
    # 2. 导出高清 PNG
    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', pad_inches=0.04)
    
    # 3. 导出色盲灰度预览
    from PIL import Image
    im = Image.open(png_path).convert('L')
    im.save(gray_path)
    
    print(f"[figures4papers] 成功导出: {pdf_path} (PDF & PNG & 灰度图)")
