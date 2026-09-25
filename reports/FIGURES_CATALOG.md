# 2026年中国研究生数学建模竞赛 D 题全套学术级图表名录与论文引用指南 (顶刊规范版)

> **设计系统**：全局导入耶鲁大学开源顶刊图表标准库 **`figures4papers`** (ChenLiu-1996)，全面确立学术蓝、生态绿、点睛金、警示红和中性灰的统一样式系统（Design System）。  
> **质量规范**：严格执行 **`scipilot-figure-skill`** 闭环自检标准（机器合规 `check_figure.py` 100% 通过，0 FAIL）。  
> **存放路径**：[figures/](file:///d:/dev-java/math_model/figures)（全套 14 组共 42 个文件，每图均配备高精度矢量 `.pdf`、300 DPI 高清预览 `.png` 以及无障碍灰度校核图 `_grayscale.png`）。  
> **版本归档说明**：全套图表已全面升级至顶刊规范标准；历史初版图表与代码已分别打包归档至 `archive/figures_v1.zip` 与 `archive/visualization_v1.zip`，并在 `.gitignore` 中配置本地忽略，防止被 git 跟踪提交。  
> **一键批处理复现脚本**：[code/visualization/generate_all_figures.py](file:///d:/dev-java/math_model/code/visualization/generate_all_figures.py)。

---

## 全套 14 张图表名录与论文章节映射一览表

| 图号 | 文件名前缀 | 推荐论文图题（中英双语） | 对应章节 | 推荐排版宽度 | 核心科学结论、物理机制与升级要点 |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **图 1** | `fig1_terrain_rescue_network` | **山区地形高程等高线与应急救援网络拓扑图**<br>*3D Terrain Elevation Contours and Drone Rescue Network Topology* | 第 1 章 / 第 2 章 背景与假设 | 双栏 (7.2 in) | **【维度一升级】** 引入 `LightSource(315°, 45°)` 真实山体阴影晕渲（Hillshade），叠加 `gist_earth` 色带呈现 Google Earth 级三维起伏；右下角增设 $0-2-4\text{ km}$ 地学标准黑白比例尺；调度中心 O01（127.7m）与 15 个受灾点人口气泡、S003 标签经纬度安全解耦。 |
| **图 2** | `fig2_overall_methodology_roadmap` | **山区洪涝灾害无人机应急运输与通信协同优化技术路线与系统架构图**<br>*Overall Methodology and Algorithmic Roadmap for Air-Ground Collaborative Optimization* | 第 2 章 总体建模思路 | 双栏 (7.2 in) | **【维度二升级】** 升维为三层层次架构流：【输入层】物理环境多维解析 $\to$ 【求解核】四阶段递进建模与协同优化求解引擎 $\to$ 【产出层】综合决策评估看板；各卡片间保留极简阶段递进指示箭头，版面开阔无压盖。 |
| **图 3** | `fig3_q1_cargo_demand_profile` | **15 个服务区物资需求构成与 80 件货箱物理属性分布**<br>*Spatial Demand Composition of Service Areas and Physical Profiles of Cargo Boxes* | 第 3 章 问题一建模与求解 | 双栏 (7.2 in) | Panel (a) 堆叠柱状图揭示急救医疗（16箱）与生活保障物资（64箱）的空间异构性与人口对数关联；Panel (b) 气泡图展示 4 类货箱质量-容积分布及首批必保物资要求（15箱医疗+15箱水）。 |
| **图 4** | `fig4_q1_safe_payload_boundary` | **三类机型在 15 个受灾服务区的最大安全物理载荷上界**<br>*Maximum Safe Physical Payloads for Heterogeneous Drones across Service Areas* | 第 3 章 问题一安全载荷分析 | 单栏偏宽 (6.5 in) | 基准返航余量 $\eta=0.20$ 下三类机型物理安全载荷分析。原位红小箭头精准标注 5 处受航程与爬升能耗制约的关键降额点：S008（C机 58.53kg, B机 28.69kg）、S004（C机 63.23kg）、S012（C机 68.02kg）、S003（C机 68.33kg）、S002（C机 68.56kg）。 |
| **图 5** | `fig5_q1_eta_sensitivity` | **返航安全电量余量 $\eta$ 敏感性多指标全景分析图**<br>*Multi-objective Sensitivity Analysis of Reserve Power Margin $\eta$* | 第 3 章 问题一敏感性分析 | 双栏 (7.2 in) | Panel (a) 揭示架次构成随 $\eta$ 的阶梯变化（$\eta \le 0.20$ 稳定在 18 架次）；Panel (b) 揭示 $\eta > 0.20$ 后总能耗与作业时间呈现指数级恶化的相变膨胀，论证 $\eta=0.20$ 为黄金最优平衡点。 |
| **图 6** | `fig6_q2_alns_convergence_comparison` | **ALNS 启发式求解收敛轨迹与邻域算子自适应演化**<br>*ALNS Convergence Trajectory and Adaptive Operator Weight Evolution* | 第 4 章 问题二算法设计 | 双栏 (7.2 in) | Panel (a) 呈现 Seed 42, 43, 44 真实日志收敛过程，Seed 42 在第 56 代锁定最优代价值 538.25（24架次，78.27 kWh）；探索解散点严守下包络线公理；Panel (b) 展示 6 大破坏-修复算子从 16.7% 均等初始权重自适应动态演进。 |
| **图 7** | `fig7_q2_drone_schedule_gantt` | **8 架实体无人机执飞 24 架次任务时空调度甘特图**<br>*Spatiotemporal Scheduling Gantt Chart for 8 Heterogeneous Drones* | 第 4 章 问题二方案展示 | 双栏 (7.2 in) | **【维度四升级】** 8 架实体机（U01~U08）时空调度推进全景；各甘特条内自适应嵌入航线与真实物理载重利用率徽标（如 `T003: S01-S09 [78kg, 98%]`），直接证明运力装载饱和度；联合完工时刻 Makespan = 7730.5s (2.15h) 标注于底部安全开阔区。 |
| **图 8** | `fig8_q2_battery_recharge_pipeline` | **14 组共享电池车电分离两阶段等效充放电流水线图**<br>*Two-Stage Equal-Charging and Discharging Pipeline for 14 Shared Batteries* | 第 4 章 问题二电池调度 | 双栏 (7.2 in) | 严格刻画 14 组电池执飞放电段、恒流快充段（0~90%）、涓流段（90~100%）与冷云灰待命状态，直观论证车电分离架构下全周期 0 冲突无缝周转。 |
| **图 9** | `fig9_q2_flight_routes_network` | **24 个运输航次多层级空间飞行拓扑与全网空域流量走廊**<br>*Multilevel Flight Route Network Topologies and Airspace Corridor Traffic Density* | 第 4 章 问题二路径拓扑 | 双栏 (7.2 in) | 2x2 四分屏深度解构：(a) 11架次单点直达专线网；(b) 10架次双点航程节约闭环回路（带箭头巡航航向）；(c) 3架次三点深度集约巡航回路（T009/T012/T017）；(d) 24架次全网航段通行流量密度（红/橙/灰标示核心骨干走廊与支线），彻底解决线条交叉重叠问题。 |
| **图 10** | `fig10_q3_los_dem_profile_blockage` | **30m DEM 山区复杂地形视距遮挡 (LOS) 射线追踪与第一菲涅尔区保活几何机制**<br>*3D Terrain Ray-Casting for LOS Blockage and 1st Fresnel Zone Preservation* | 第 5 章 问题三信道建模 | 双栏 (7.2 in) | **【维度三升级】** 引入 $f=1.4\text{ GHz}$ 第一菲涅尔区（$F_1$）空间信道半透明椭球透视带，直观揭示 O01 $\to$ S003 沿线最高山脊（高程 423.8m）刺入第一菲涅尔区深达 150m+ 造成的严重深衰落阻断，严密证明高空中继机 RT01（悬停 731.6m）架设的物理必然性。 |
| **图 11** | `fig11_q3_relay_schedule_timeline` | **通信中继无人机调度全景时序与 100% 连续通信保障**<br>*Relay Drone Scheduling Timeline and 100% Continuous Communication Guarantee* | 第 5 章 问题三方案展示 | 双栏 (7.2 in) | Panel (a) 展示 RT01/02/03 架次起降、悬停与 R02 地面维护换电 $302.7\text{s} \ge 300\text{s}$ 安全窗口；Panel (b) 展现 325 处微时段通信链路（直连58.15%, 中继41.85%）100% 连续无断连。 |
| **图 12** | `fig12_q3_scheme_pareto_radar` | **中继协同调度方案 A 与方案 B 综合性能雷达图**<br>*Radar Evaluation of Communication Relay Scheme A vs. Scheme B* | 第 5 章 问题三对比与权衡 | 单栏 (4.8 in) | **【维度五升级】** 7 个决策维度轴线顶点直接标明方案 A 与方案 B 的真实物理工程绝对实测值（中继能耗 A:3.73kWh vs B:3.55kWh、最低返航SOC A:30.5% vs B:64.5%、维护时间 A:302.7s vs B:充裕等），叠加顶刊实心圆点与方块标记，杜绝主观评分嫌疑。 |
| **图 13** | `fig13_q4_graph_connectivity_partitions` | **服务区强绑定网络拓扑图论连通分支与任务分区图**<br>*Graph-Theoretic Connected Components and Task Partition Mapping* | 第 6 章 问题四图论模型 | 双栏 (7.2 in) | Panel (a) 严格证明跨区多点航次将 13 个服务区互锁成不可分大分支 $C_1$，S010 与 S014 为独立孤立点；Panel (b) 地理投影直观解释 K=2 唯一划分为组1+组2，K=3 唯一划分为组1+组2+组3 的代数拓扑解。 |
| **图 14** | `fig14_q4_resource_demand_shortage` | **任务分区隔离执行下的装备并发需求峰值与短缺缺口图**<br>*Peak Concurrency Demands and Inventory Deficits under Partition Isolation* | 第 6 章 问题四资源缺口 | 双栏 (7.2 in) | 分组柱状图对比现有库存、K=2 与 K=3 独立总需求，原位标出 B 型机（缺1~2架）、B 型电池（缺2组）与中继机（缺1架），左上角嵌入提示框揭示战区隔离切断时分复用的管理学机制。 |

---

## 论文排版嵌入代码示例 (直接引用 figures/)

### 1. Typst 论文引擎插入示例：
```typst
#figure(
  image("figures/fig7_q2_drone_schedule_gantt.pdf", width: 95%),
  caption: [8 架实体无人机执飞 24 架次任务时空调度甘特图 (ALNS 优化全局排程)],
) <fig_q2_gantt>

#figure(
  image("figures/fig10_q3_los_dem_profile_blockage.pdf", width: 95%),
  caption: [30m DEM 山区复杂地形视距遮挡 (LOS) 射线追踪与第一菲涅尔区保活几何机制],
) <fig_q3_fresnel>

#figure(
  image("figures/fig11_q3_relay_schedule_timeline.pdf", width: 95%),
  caption: [通信中继无人机调度全景时序与 100% 连续通信保障剖面],
) <fig_q3_timeline>
```

### 2. LaTeX 论文引擎插入示例：
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/fig7_q2_drone_schedule_gantt.pdf}
  \caption{8 架实体无人机执飞 24 架次任务时空调度甘特图 (ALNS 优化全局排程)}
  \label{fig:q2_gantt}
\end{figure}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/fig10_q3_los_dem_profile_blockage.pdf}
  \caption{30m DEM 山区复杂地形视距遮挡 (LOS) 射线追踪与第一菲涅尔区保活几何机制}
  \label{fig:q3_fresnel}
\end{figure}
```

