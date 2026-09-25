# -*- coding: utf-8 -*-
"""
figures4papers  全套 14 张顶刊图表一键批量生成主调度脚本
严格遵循数据客观真实性公理，全面统一顶刊极简脊柱排版与语义调色板。
输出目录：figures/ (包含 300DPI 矢量 PDF、高清 PNG 与色盲灰度图)
"""

import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from plot_terrain_and_roadmap import plot_fig1, plot_fig2
from plot_q1_figures import plot_fig3, plot_fig4, plot_fig5
from plot_q2_figures import plot_fig6, plot_fig7, plot_fig8, plot_fig9
from plot_q3_figures import plot_fig10, plot_fig11, plot_fig12
from plot_q4_figures import plot_fig13, plot_fig14


def generate_all():
    print("=" * 70)
    print(">>> 启动 figures4papers  顶刊级全套学术图表渲染流水线...")
    print("=" * 70)
    t0 = time.time()
    
    tasks = [
        ("图 1 (地形救援态势图)", plot_fig1),
        ("图 2 (全景求解技术路线图)", plot_fig2),
        ("图 3 (货箱需求与属性分布图)", plot_fig3),
        ("图 4 (安全物理载荷上界图)", plot_fig4),
        ("图 5 (eta 敏感性与相变图)", plot_fig5),
        ("图 6 (ALNS真实收敛与算子演进图)", plot_fig6),
        ("图 7 (实体机时空调度甘特图)", plot_fig7),
        ("图 8 (共享电池两阶段流水线图)", plot_fig8),
        ("图 9 (24航次四分屏飞行拓扑图)", plot_fig9),
        ("图 10 (DEM射线追踪与中继剖面图)", plot_fig10),
        ("图 11 (中继甘特与全域通信保障图)", plot_fig11),
        ("图 12 (中继方案A/B性能雷达图)", plot_fig12),
        ("图 13 (图论连通分支与任务分区图)", plot_fig13),
        ("图 14 (隔离执行资源缺口大盘图)", plot_fig14),
    ]
    
    for name, func in tasks:
        t_start = time.time()
        print(f">> 正在渲染: {name} ...", end="", flush=True)
        func()
        print(f" 完成! ({time.time() - t_start:.2f}s)")
        
    print("=" * 70)
    print(f">>>  全套 14 张图表渲染全部成功! 总耗时: {time.time() - t0:.2f}s")
    print(f">>> 成果存放目录: figures/")
    print("=" * 70)


if __name__ == '__main__':
    generate_all()
