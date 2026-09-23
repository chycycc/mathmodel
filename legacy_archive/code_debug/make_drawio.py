# -*- coding: utf-8 -*-
"""
生成标准 DrawIO (.drawio) XML 源文件
包含：
1. figures/fig_roadmap.drawio (整体求解技术路线图)
2. figures/fig_flow_q2.drawio (问题二 ALNS 与充电周转算法流程图)
3. figures/fig_flow_q3.drawio (问题三 DEM 视距通视与中继空地协同决策图)
"""

import os

FIGURES_DIR = 'figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

def generate_roadmap_drawio():
    content = """<mxfile host="Electron" modified="2026-09-23T10:00:00.000Z" agent="Mozilla/5.0" version="21.6.8" type="device">
  <diagram id="diagram_roadmap" name="全篇整体研究技术路线图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- 阶段 0: 输入层 -->
        <mxCell id="in_title" value="输入层：基础多源异构救援数据与环境感知" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#0288d1;fontStyle=1;fontSize=14;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="60" y="40" width="1020" height="40" as="geometry"/>
        </mxCell>
        <mxCell id="in_dem" value="30m DEM 数字高程模型&#xa;(1309×1486 矩阵, 地形起伏 41.7~1132.9m)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="80" y="95" width="220" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="in_cargo" value="受灾需求与货箱清单&#xa;(15个服务区, 80不可拆箱, 758kg, 紧迫时限)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="340" y="95" width="230" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="in_drones" value="无人机与能源系统&#xa;(A/B/C型运输机, R型中继机, 两阶段等效充电)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="610" y="95" width="230" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="in_comm" value="无线射频与空间信道&#xa;(2.4GHz, 链路损耗门限, 10dB山体阻断衰减)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="880" y="95" width="180" height="50" as="geometry"/>
        </mxCell>
        
        <!-- 阶段 1: 问题一 -->
        <mxCell id="q1_box" value="问题一：单点往返载荷计算与多批次组批优化&#xa;• 能耗单调性证明与二分法搜索最大安全载重 W_safe&#xa;• C型重载机能量敏感性衰减分析 (80kg -> 50.26kg)&#xa;• 0-1 整数线性规划 (ILP) 货箱不可拆分多批次组批" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="60" y="180" width="1020" height="75" as="geometry"/>
        </mxCell>
        
        <!-- 阶段 2: 问题二 -->
        <mxCell id="q2_box" value="问题二：异构多点多架次时空协同调度模型 (VRPTW + 充电池周转)&#xa;• 8 架实体无人机 (4 A, 2 B, 2 C) 时域无冲突调度与飞行推进&#xa;• 14 组共享电池动态两阶段充电状态机 (恒流快充 65% + 恒压慢充 35%)&#xa;• 动态剩余载重积分能耗模型与医疗物资 100% 准时交付保障 (Makespan = 3.46h)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f5e9;strokeColor=#388e3c;fontSize=12;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="60" y="290" width="1020" height="85" as="geometry"/>
        </mxCell>
        
        <!-- 阶段 3: 问题三 -->
        <mxCell id="q3_box" value="问题三：30m DEM 视距遮挡分析与空地中继通信协同优化&#xa;• 3D 光线追踪空间通视判别算法 (Ray-Casting LOS) 沿途采样&#xa;• 固定网关 G01 直连断开区域识别 (12个深山服务区直连中断)&#xa;• 西部/东部双悬停点三维位姿优化与 6 个中继架次零空隙空地接力 (100% 连续通信保障)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontSize=12;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="60" y="410" width="1020" height="85" as="geometry"/>
        </mxCell>
        
        <!-- 阶段 4: 问题四 -->
        <mxCell id="q4_box" value="问题四：救援任务分区与独立资源配置优化&#xa;• 基于航线强绑定 (T002: S002-S004) 的空间拓扑聚类划分 (K=2, K=3)&#xa;• 区间并发扫描法精确核算各组独立运作所需的无人机、电池与中继硬件资产&#xa;• 集中池化协同 (Pooling Effect) 与分散独立配置开销 (Decentralization Overhead) 权衡" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fbe9e7;strokeColor=#d84315;fontSize=12;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="60" y="530" width="1020" height="85" as="geometry"/>
        </mxCell>
        
        <!-- 阶段 5: 决策成果 -->
        <mxCell id="out_box" value="决策成果输出：官方结果提交模板.xlsx (6个Sheet) + 5幅高精度学术矢量图表 (figures/*.pdf) + 应急抢险调度方案报告" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#eceff1;strokeColor=#455a64;fontStyle=1;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="60" y="650" width="1020" height="50" as="geometry"/>
        </mxCell>
        
        <!-- 流程连接箭头 -->
        <mxCell id="e0" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#0288d1;" edge="1" parent="1" source="in_title" target="q1_box">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#7b1fa2;" edge="1" parent="1" source="q1_box" target="q2_box">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#388e3c;" edge="1" parent="1" source="q2_box" target="q3_box">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#f57c00;" edge="1" parent="1" source="q3_box" target="q4_box">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#d84315;" edge="1" parent="1" source="q4_box" target="out_box">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    with open(os.path.join(FIGURES_DIR, 'fig_roadmap.drawio'), 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print("成功生成: figures/fig_roadmap.drawio")

def generate_flow_q2_drawio():
    content = """<mxfile host="Electron" modified="2026-09-23T10:00:00.000Z" agent="Mozilla/5.0" version="21.6.8" type="device">
  <diagram id="diagram_flow_q2" name="问题二时空调度与充电周转算法流程图">
    <mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <mxCell id="n_start" value="开始：80箱物资清单、8架实体机、14组电池与首批时限" style="ellipse;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#0288d1;fontStyle=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="250" y="30" width="320" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_sort" value="物资优先级排序：医疗物资 &amp; 首批时限物资置顶，按截止时间升序构建候选池" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="240" y="110" width="340" height="45" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_init" value="初始调度构造：基于就近聚类与首批时限贪婪插入，分配实体机与初始满电电池" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="240" y="185" width="340" height="45" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_alns" value="自适应大邻域搜索 (ALNS) 迭代：&#xa;• 随机破坏 / 空间关联破坏 (Shaw Removal)&#xa;• 遗憾值插入 (Regret-2 / Regret-3) 重新组配航段" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="240" y="260" width="340" height="55" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_sim" value="时序推进与状态机检查：&#xa;1. 动态载荷结算航段能耗，校验返航 SOC >= 20%&#xa;2. 实体机周转间隔 >= 300s + 装箱时间&#xa;3. 电池两阶段等效充电推进 (快速65% + 慢速35%)，校验可用时刻" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f5e9;strokeColor=#388e3c;fontSize=11;align=left;spacingLeft=10;" vertex="1" parent="1">
          <mxGeometry x="210" y="345" width="400" height="75" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_check" value="是否存在时效违约&#xa;或物理冲突？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="310" y="450" width="200" height="70" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_repair" value="时空冲突修复算子：&#xa;延后冲突架次出发时刻，重新指派空闲电池" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffebee;strokeColor=#c62828;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="580" y="460" width="190" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_eval" value="解质量评估：计算全任务 Makespan 与总运输能耗，更新全局最优解" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#388e3c;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="240" y="555" width="340" height="45" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_stop" value="满足终止条件&#xa;(达最大迭代步数)？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="310" y="630" width="200" height="70" as="geometry"/>
        </mxCell>
        
        <mxCell id="n_end" value="输出最优调度方案：Q2_运输架次表 (27架次) 与 Q2_逐箱交付表 (80箱)" style="ellipse;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#0288d1;fontStyle=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="240" y="735" width="340" height="50" as="geometry"/>
        </mxCell>
        
        <!-- 连接线 -->
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_start" target="n_sort"/>
        <mxCell id="c2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_sort" target="n_init"/>
        <mxCell id="c3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_init" target="n_alns"/>
        <mxCell id="c4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_alns" target="n_sim"/>
        <mxCell id="c5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_sim" target="n_check"/>
        <mxCell id="c6" value="是" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#c62828;" edge="1" parent="1" source="n_check" target="n_repair"/>
        <mxCell id="c7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#c62828;" edge="1" parent="1" source="n_repair" target="n_sim">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="675" y="380"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="c8" value="否" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#2e7d32;" edge="1" parent="1" source="n_check" target="n_eval"/>
        <mxCell id="c9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_eval" target="n_stop"/>
        <mxCell id="c10" value="否" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="n_stop" target="n_alns">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="160" y="665"/>
              <mxPoint x="160" y="287"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="c11" value="是" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#2e7d32;" edge="1" parent="1" source="n_stop" target="n_end"/>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    with open(os.path.join(FIGURES_DIR, 'fig_flow_q2.drawio'), 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print("成功生成: figures/fig_flow_q2.drawio")

def generate_flow_q3_drawio():
    content = """<mxfile host="Electron" modified="2026-09-23T10:00:00.000Z" agent="Mozilla/5.0" version="21.6.8" type="device">
  <diagram id="diagram_flow_q3" name="问题三空间通视与空地中继决策流">
    <mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <mxCell id="s_start" value="输入：时刻 t 运输无人机三维坐标 (lon, lat, alt)" style="ellipse;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#0288d1;fontStyle=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="260" y="30" width="300" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_los" value="三维光线追踪 (Ray-Casting)：&#xa;沿直连视线与沿途 30m DEM 地面双线性插值高程比较" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="250" y="110" width="320" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_check_los" value="视线是否穿透山体&#xa;(存在 z &lt;= H_DEM)？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="310" y="190" width="200" height="70" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_calc_direct" value="计算自由空间衰减 + 附加损耗 (若遮挡 +10dB)&#xa;计算双向链路最大允许门限 L_max = 122.0 dB" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#0288d1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="250" y="290" width="320" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_check_avail" value="直连损耗 &lt;= 122.0 dB？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="310" y="370" width="200" height="65" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_direct_ok" value="记录当前时刻为【直连】保障状态&#xa;(由固定网关 G01 维持通信)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f5e9;strokeColor=#388e3c;fontStyle=1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="80" y="375" width="180" height="55" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_search_relay" value="直连不可用：检索空中处于就绪服务态的中继无人机&#xa;(核验建链时刻 t_link_done &lt;= t &lt;= t_srv_end)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="250" y="470" width="320" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_check_relay_link" value="核验双向中继链路：&#xa;1. 回传链路 (Relay-G01) 损耗 &lt;= 126.0 dB&#xa;2. 接入链路 (Relay-UAV) 损耗 &lt;= 116.0 dB" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#7b1fa2;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="250" y="550" width="320" height="55" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_relay_ok" value="记录当前时刻为【中继】保障状态&#xa;(匹配对应中继架次编号 RT01~RT06)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff3e0;strokeColor=#f57c00;fontStyle=1;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="285" y="635" width="250" height="50" as="geometry"/>
        </mxCell>
        
        <mxCell id="s_end" value="输出：全时域 100% 连续通信保障，无盲区中断" style="ellipse;whiteSpace=wrap;html=1;fillColor=#e1f5fe;strokeColor=#0288d1;fontStyle=1;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="260" y="715" width="300" height="45" as="geometry"/>
        </mxCell>
        
        <!-- 连线 -->
        <mxCell id="d1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_start" target="s_los"/>
        <mxCell id="d2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_los" target="s_check_los"/>
        <mxCell id="d3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_check_los" target="s_calc_direct"/>
        <mxCell id="d4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_calc_direct" target="s_check_avail"/>
        <mxCell id="d5" value="是" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#2e7d32;" edge="1" parent="1" source="s_check_avail" target="s_direct_ok"/>
        <mxCell id="d6" value="否" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;strokeColor=#c62828;" edge="1" parent="1" source="s_check_avail" target="s_search_relay"/>
        <mxCell id="d7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_search_relay" target="s_check_relay_link"/>
        <mxCell id="d8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_check_relay_link" target="s_relay_ok"/>
        <mxCell id="d9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_direct_ok" target="s_end">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="170" y="738"/>
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="d10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;" edge="1" parent="1" source="s_relay_ok" target="s_end"/>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    with open(os.path.join(FIGURES_DIR, 'fig_flow_q3.drawio'), 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print("成功生成: figures/fig_flow_q3.drawio")

if __name__ == '__main__':
    generate_roadmap_drawio()
    generate_flow_q2_drawio()
    generate_flow_q3_drawio()
