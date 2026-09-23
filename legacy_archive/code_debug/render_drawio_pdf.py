# -*- coding: utf-8 -*-
"""
将非数据型图示（技术路线图、问题二流程图、问题三流程图）精确渲染导出为高质量矢量 PDF
确保 Typst 论文可直接无缝引用 figures/fig_roadmap.pdf, fig_flow_q2.pdf, fig_flow_q3.pdf
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

FIGURES_DIR = 'figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

def render_roadmap_pdf():
    fig, ax = plt.subplots(figsize=(11, 8.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # 标题块/说明
    # 阶段 0: 输入层
    rect0 = patches.FancyBboxPatch((4, 86), 92, 10, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#e1f5fe", edgecolor="#0288d1", linewidth=1.5)
    ax.add_patch(rect0)
    ax.text(6, 92, "输入层：基础多源异构救援数据与环境感知", fontsize=11, fontweight='bold', color='#01579b', va='center')
    ax.text(6, 88.5, "- 30m DEM 矩阵 (1309×1486)   - 15 个服务区 80 箱物资 (758kg)   - 8 架实体机与 14 组电池   - 2.4GHz 射频链路参数", fontsize=9, color='#0277bd', va='center')
    
    # 阶段 1: 问题一
    rect1 = patches.FancyBboxPatch((4, 69), 92, 13, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#f3e5f5", edgecolor="#7b1fa2", linewidth=1.5)
    ax.add_patch(rect1)
    ax.text(6, 78.5, "问题一：单点往返载荷计算与多批次组批优化", fontsize=11, fontweight='bold', color='#4a148c', va='center')
    ax.text(6, 74.5, "- 证明往返能耗关于载重单调递增性，采用高精度二分法求解各机型最大安全载荷 W_safe", fontsize=9, color='#311b92', va='center')
    ax.text(6, 71.2, "- 发现 C 型机受远距爬升安全余量约束上限衰减 (80kg -> 50.26kg)；构建 0-1 ILP 求解全局最优 19 架次单点方案", fontsize=9, color='#311b92', va='center')
    
    # 阶段 2: 问题二
    rect2 = patches.FancyBboxPatch((4, 50), 92, 15, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#e8f5e9", edgecolor="#388e3c", linewidth=1.5)
    ax.add_patch(rect2)
    ax.text(6, 61.5, "问题二：异构多点多架次时空协同调度模型 (VRPTW + 充电池周转)", fontsize=11, fontweight='bold', color='#1b5e20', va='center')
    ax.text(6, 57.5, "- 状态空间构建：8 架实体机 (4 A, 2 B, 2 C) 时域推进与 14 组共享电池两阶段等效充电状态机 (快充 65% + 慢充 35%)", fontsize=9, color='#2e7d32', va='center')
    ax.text(6, 54.0, "- 提出自适应大邻域搜索算法 (ALNS)，挖掘出 T002 (S002->S004) 串联回路，实现医疗物资 100% 达标准时送达", fontsize=9, color='#2e7d32', va='center')
    ax.text(6, 51.0, "- 求解得到 27 个运输架次最优排班，全任务 Makespan 为 12463.7s (3.46h)，总运输能耗 84.15 kWh", fontsize=9, color='#2e7d32', va='center')

    # 阶段 3: 问题三
    rect3 = patches.FancyBboxPatch((4, 31), 92, 15, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#fff3e0", edgecolor="#f57c00", linewidth=1.5)
    ax.add_patch(rect3)
    ax.text(6, 42.5, "问题三：30m DEM 视距遮挡分析与空地中继通信协同优化", fontsize=11, fontweight='bold', color='#e65100', va='center')
    ax.text(6, 38.5, "- 三维光线追踪 (Ray-Casting) 沿途 20m 采样判别山体阻断，发现 12 个深山服务区由于地形遮挡附加 10dB 损耗直连中断", fontsize=9, color='#ef6c00', va='center')
    ax.text(6, 35.0, "- 网格化空间通视搜索确定西部 (H=686m) 与东部 (H=691m) 双战略悬停阵位，均实现与 G01 视距通视与深谷俯视全覆盖", fontsize=9, color='#ef6c00', va='center')
    ax.text(6, 32.0, "- 编排 6 个中继架次零空隙空地接力，实现全周期 72 个通信阶段 100% 连续通信保障，通信盲区与中断时长均为 0 秒", fontsize=9, color='#ef6c00', va='center')

    # 阶段 4: 问题四
    rect4 = patches.FancyBboxPatch((4, 13), 92, 14, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#fbe9e7", edgecolor="#d84315", linewidth=1.5)
    ax.add_patch(rect4)
    ax.text(6, 23.5, "问题四：救援任务空间分区与独立资源配置优化", fontsize=11, fontweight='bold', color='#bf360c', va='center')
    ax.text(6, 19.8, "- 基于 T002 串联航线硬约束绑定 (S002-S004 强同组)，结合图谱聚类设计 K=2 (对半分区) 与 K=3 (三格联防) 方案", fontsize=9, color='#d84315', va='center')
    ax.text(6, 16.5, "- 采用区间并发扫描法核算各组独立运作所需的无人机、电池与中继资产峰值，定量揭示分散独立配置开销", fontsize=9, color='#d84315', va='center')
    ax.text(6, 13.8, "- 科学论证集中池化协同 (Pooling Effect) 的资源节约优势，针对独立分区方案给出精准的硬件扩充与库存缺口归因", fontsize=9, color='#d84315', va='center')

    # 底部输出
    rect5 = patches.FancyBboxPatch((4, 2), 92, 7.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   facecolor="#eceff1", edgecolor="#455a64", linewidth=1.5)
    ax.add_patch(rect5)
    ax.text(50, 5.7, "决策产出：官方结果提交模板.xlsx (6个Sheet) + 5幅高精度学术矢量图表 + 全套灾情应急调度方案",
            fontsize=10.5, fontweight='bold', color='#263238', ha='center', va='center')

    # 连接箭头
    arrow_props = dict(arrowstyle="->", color="#37474f", linewidth=2.0)
    ax.annotate("", xy=(50, 84), xytext=(50, 86), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 67), xytext=(50, 69), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 48), xytext=(50, 50), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 29), xytext=(50, 31), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 11), xytext=(50, 13), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig_roadmap.pdf'), dpi=300)
    plt.close()
    print("成功导出: figures/fig_roadmap.pdf")

def render_flow_q2_pdf():
    fig, ax = plt.subplots(figsize=(7.5, 9.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_box(x, y, w, h, text, fc='#ffffff', ec='#0288d1', fs=9, bold=False):
        p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.0",
                                   facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(p)
        ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center', fontsize=fs,
                fontweight='bold' if bold else 'normal', color='#212121')

    def draw_rhombus(x, y, w, h, text, fc='#fff3e0', ec='#f57c00', fs=8.5):
        verts = [(x + w/2.0, y + h), (x + w, y + h/2.0), (x + w/2.0, y), (x, y + h/2.0)]
        poly = patches.Polygon(verts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(poly)
        ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center', fontsize=fs, color='#212121')

    # 绘制流程节点
    draw_box(15, 92, 70, 5.5, "开始：输入 80 箱物资、8 架实体机与 14 组共享电池", fc='#e1f5fe', ec='#0288d1', fs=9.5, bold=True)
    draw_box(15, 82, 70, 6.0, "物资分级排序：医疗物资与高优先级首批物资置顶\n按期望送达时限截止时间升序构建候选池", fc='#ffffff', ec='#0288d1')
    draw_box(15, 71, 70, 6.5, "初始解构造：基于空间距离聚类与首批时限贪婪插入\n初次指派实体机编号 (U01~U08) 与初始满电电池", fc='#ffffff', ec='#0288d1')
    draw_box(15, 59, 70, 7.5, "自适应大邻域搜索 (ALNS) 迭代：\n- Shaw 空间关联破坏算子与随机移除算子\n- 遗憾值插入 (Regret-2 / Regret-3) 重新组配航段序列", fc='#f3e5f5', ec='#7b1fa2')
    draw_box(12, 44, 76, 10.5, "时序推进与物理状态机验证：\n1. 动态载荷结算航段能耗，校验返航安全余量 SOC >= 20%\n2. 实体机周转时间间隔 >= 300s + 装箱时间\n3. 共享电池两阶段等效充电推进 (快充65% + 慢充35%) 确定可用时刻", fc='#e8f5e9', ec='#388e3c', fs=8.5)

    draw_rhombus(25, 30, 50, 9.0, "是否存在时效违约\n或物理时空冲突？")
    draw_box(68, 31, 28, 7.0, "时空冲突修复：\n平移起飞时刻，重新指派电池", fc='#ffebee', ec='#c62828', fs=8)

    draw_box(15, 18, 70, 6.0, "解质量评价：计算完工时间 Makespan 与总运输能耗\n根据接受准则更新全局最优解", fc='#ffffff', ec='#388e3c')
    draw_rhombus(25, 6, 50, 8.0, "达到终止步数？")
    draw_box(15, -2.5, 70, 5.0, "输出最优调度：Q2_运输架次 (27架次) 与 Q2_逐箱交付 (80箱)", fc='#e1f5fe', ec='#0288d1', fs=9.5, bold=True)

    # 连线
    arr = dict(arrowstyle="->", color="#37474f", linewidth=1.5)
    ax.annotate("", xy=(50, 88), xytext=(50, 92), arrowprops=arr)
    ax.annotate("", xy=(50, 77.5), xytext=(50, 82), arrowprops=arr)
    ax.annotate("", xy=(50, 66.5), xytext=(50, 71), arrowprops=arr)
    ax.annotate("", xy=(50, 54.5), xytext=(50, 59), arrowprops=arr)
    ax.annotate("", xy=(50, 39), xytext=(50, 44), arrowprops=arr)

    # 判定分支
    ax.annotate("", xy=(68, 34.5), xytext=(65, 34.5), arrowprops=arr)
    ax.text(66, 36, "是", fontsize=8.5, color='#c62828', fontweight='bold')
    # 修复后回流
    ax.plot([82, 82, 50], [38, 49, 49], color='#c62828', linestyle='--', linewidth=1.2)

    ax.annotate("", xy=(50, 24), xytext=(50, 30), arrowprops=arr)
    ax.text(51.5, 27, "否", fontsize=8.5, color='#2e7d32', fontweight='bold')

    ax.annotate("", xy=(50, 14), xytext=(50, 18), arrowprops=arr)
    ax.annotate("", xy=(50, 2.5), xytext=(50, 6), arrowprops=arr)
    ax.text(51.5, 4.5, "是", fontsize=8.5, color='#2e7d32', fontweight='bold')

    # 未终止回流
    ax.plot([25, 6, 6, 15], [10, 10, 63, 63], color='#37474f', linestyle='--', linewidth=1.2)
    ax.text(18, 11, "否", fontsize=8.5, color='#37474f')

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig_flow_q2.pdf'), dpi=300)
    plt.close()
    print("成功导出: figures/fig_flow_q2.pdf")

def render_flow_q3_pdf():
    fig, ax = plt.subplots(figsize=(7.5, 9.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_box(x, y, w, h, text, fc='#ffffff', ec='#0288d1', fs=9, bold=False):
        p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.0",
                                   facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(p)
        ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center', fontsize=fs,
                fontweight='bold' if bold else 'normal', color='#212121')

    def draw_rhombus(x, y, w, h, text, fc='#fff3e0', ec='#f57c00', fs=8.5):
        verts = [(x + w/2.0, y + h), (x + w, y + h/2.0), (x + w/2.0, y), (x, y + h/2.0)]
        poly = patches.Polygon(verts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(poly)
        ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center', fontsize=fs, color='#212121')

    draw_box(15, 92, 70, 5.5, "输入：时刻 t 运输无人机三维坐标 (lon, lat, alt)", fc='#e1f5fe', ec='#0288d1', fs=9.5, bold=True)
    draw_box(15, 81, 70, 6.5, "三维光线追踪 (Ray-Casting)：\n沿直连视线逐点采样，双线性插值查询 DEM 地表海拔高程", fc='#ffffff', ec='#0288d1')
    draw_rhombus(25, 68, 50, 8.5, "视线是否发生山体阻断\n(存在采样点 z <= H_DEM)？")
    draw_box(15, 54, 70, 8.5, "计算自由空间衰减与附加遮挡衰减 (遮挡时叠加 10dB 附加损耗)\n计算双向链路损耗并与最大允许门限 (122.0 dB) 比对", fc='#ffffff', ec='#0288d1')
    draw_rhombus(25, 41, 50, 8.5, "直连损耗 <= 122.0 dB？")

    draw_box(68, 41.5, 28, 7.5, "记录为【直连】保障状态\n(由固定网关 G01 维持通信)", fc='#e8f5e9', ec='#388e3c', fs=8, bold=True)
    draw_box(15, 28, 70, 7.5, "直连不可用：检索空中已就绪的中继无人机架次\n核验时间窗：t_link_done <= t <= t_service_end", fc='#f3e5f5', ec='#7b1fa2')
    draw_rhombus(22, 15, 56, 8.5, "核验双向中继链路：\n回传 <= 126dB 且 接入 <= 116dB？")
    draw_box(15, 2, 70, 7.5, "记录为【中继】保障状态，匹配对应中继架次 (RT01~RT06)\n输出全周期 100% 连续通信保障，通信盲区中断 0 秒", fc='#fff3e0', ec='#f57c00', fs=8.5, bold=True)

    arr = dict(arrowstyle="->", color="#37474f", linewidth=1.5)
    ax.annotate("", xy=(50, 87.5), xytext=(50, 92), arrowprops=arr)
    ax.annotate("", xy=(50, 76.5), xytext=(50, 81), arrowprops=arr)
    ax.annotate("", xy=(50, 62.5), xytext=(50, 68), arrowprops=arr)
    ax.annotate("", xy=(50, 49.5), xytext=(50, 54), arrowprops=arr)

    # 直连判定
    ax.annotate("", xy=(68, 45.25), xytext=(65, 45.25), arrowprops=arr)
    ax.text(66, 46.5, "是", fontsize=8.5, color='#2e7d32', fontweight='bold')
    ax.annotate("", xy=(50, 35.5), xytext=(50, 41), arrowprops=arr)
    ax.text(51.5, 38, "否", fontsize=8.5, color='#c62828', fontweight='bold')

    ax.annotate("", xy=(50, 23.5), xytext=(50, 28), arrowprops=arr)
    ax.annotate("", xy=(50, 9.5), xytext=(50, 15), arrowprops=arr)
    ax.text(51.5, 12, "是", fontsize=8.5, color='#2e7d32', fontweight='bold')

    # 汇合至底端
    ax.plot([82, 82, 50], [41.5, -2, -2], color='#2e7d32', linestyle='--', linewidth=1.2)
    ax.annotate("", xy=(50, 2), xytext=(50, -2), arrowprops=arr)

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'fig_flow_q3.pdf'), dpi=300)
    plt.close()
    print("成功导出: figures/fig_flow_q3.pdf")

def main():
    print("==========================================================")
    print("开始精确渲染非数据型图示矢量 PDF")
    print("==========================================================")
    render_roadmap_pdf()
    render_flow_q2_pdf()
    render_flow_q3_pdf()
    print("\n全部非数据矢量 PDF 导出完成！")

if __name__ == '__main__':
    main()
