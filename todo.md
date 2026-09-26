# 任务清单

## 阶段一：问题一至问题四建模与算法求解（已完成）
- [x] **问题一：单点往返运输与货箱组批**
  - [x] 基于 30m DEM 栅格剖面计算爬升/巡航/下降动力学耗时与能耗
  - [x] 二分法精确求解返航安全余量 $\eta$ 下各机型在 15 个服务区的最大安全载荷
  - [x] SPP 位掩码集合划分求解 18 架次单点组批方案（总能耗 59.2034 kWh）
  - [x] 完成 $\eta \in [0.10, 0.35]$ 全工况敏感性分析
  - [x] 导出 `results/Q1/Q1_单点组批方案.csv` 与敏感性分析结果
- [x] **问题二：异构无人机多点多架次运输调度**
  - [x] 基于 Clarke-Wright 航程节约发掘多元回路
  - [x] 改进 ALNS（自适应大邻域搜索，Shaw破坏/Regret-2修复/模拟退火接受）
  - [x] 8 架实体机与 14 组共享电池双时间轴离散事件仿真（两阶段等效充电模型）
  - [x] 求解出 24 架次最优基准调度方案（完工 7730.5s，总能耗 78.2654 kWh，硬时限 0 违约，流水线 0 冲突）
  - [x] 导出 `results/Q2/Q2_运输架次.csv` 与 `results/Q2/Q2_逐箱交付.csv`
- [x] **问题三：通信约束下的运输与中继联合调度**
  - [x] 基于 30m DEM 射线追踪精确判定 24 个运输航次的视距遮挡（136 个遮挡区间）
  - [x] 全域 224 个制高点搜索，确定西区（731.6m）、东南（687.3m）、东北（676.9m）三制高点
  - [x] 方案 A（精简分解）规划 3 个中继长悬停架次（仅需 2 架实体机，地面周转 302.7s $\ge$ 300s）
  - [x] 325 个通信微时段 100% 连续无缝覆盖，中继总能耗 3.7309 kWh，系统完工 7746.3s，联合能耗 81.9963 kWh
  - [x] 导出 `results/Q3/Q3_中继架次.csv` 与 `results/Q3/Q3_通信保障.csv`
- [x] **问题四：救援任务分区与资源配置**
  - [x] 证明航次多服务区强绑定拓扑下，13 个服务区构成不可分超大分支，S010 与 S014 为独立单点分支
  - [x] 确立 K=2 与 K=3 唯一数学确定性分组方案
  - [x] 严格按“执行期间不得跨组调配”核算各组峰值并发需求与 8 类资源缺口
  - [x] 导出 `results/Q4/Q4_分区配置.csv`
- [x] **官方结果提交文件生成**
  - [x] 编写并运行 `code/export/export_full_submission.py`
  - [x] 生成包含全部 6 个标准 Sheet 的 `results/结果提交_最终完整版.xlsx`

---

## 阶段二：工程重构、规范化归类与全要素独立审计门禁（已完成）
- [x] **工程结构规范化（方案 A）**
  - [x] 清理根目录废弃代码与冗余文件
  - [x] 代码模块化解耦为 `code/Q1`、`code/Q2`、`code/Q3`、`code/Q4`、`code/export`
  - [x] 结果分类归档至 `results/Q1`~`results/Q4`
  - [x] 彻底排查并消除所有外部机器绝对路径硬编码
- [x] **自动化独立审计系统搭建**
  - [x] 开发 `audit/Q1_audit.py`（7项全通，输出 `audit/Q1_audit.md`）
  - [x] 开发 `audit/Q2_audit.py`（8项全通，输出 `audit/Q2_audit.md`）
  - [x] 运行 `audit/Q3_audit.py`（8项全通，输出 `audit/Q3_audit.md`）
  - [x] 运行 `audit/Q4_audit.py`（6项全通，输出 `audit/Q4_audit.md`）
  - [x] 开发一键自动化综合验证入口 `audit/verify_all.py`（29 项指标 100% 全绿，退出码 0）
- [x] **报告资产体系升级**
  - [x] 全面升级 4 份跨题综合总纲（`ANALYSIS_MODELING_REPORT.md`、`RESULTS_REPORT.md`、`INTEGRATED_AUDIT.md`、`VERIFY_REPORT.md`）
  - [x] 规范重命名 4 份子题目专项报告（`Q1_REPORT.md`~`Q4_REPORT.md`）
- [x] **Git 版本库提交与远端同步**
  - [x] 提交至分支 `feature/q3-q4-tasks`（Commit: `8f1d8a3`）并成功推送至远程仓库

---

## 阶段三：论文级图表统一生成（已全部完成）
- [x] **数据驱动型高清矢量插图与架构图生成 (`figures/*.pdf`, `*.png`, `*_grayscale.png`)**
  - [x] **全局图表**：`fig1_terrain_rescue_network`（30m DEM 三维山地高程与救援网络拓扑图）
  - [x] **全局图表**：`fig2_overall_methodology_roadmap`（论文全流程五阶段技术路线图）
  - [x] **Q1 图表**：`fig3_q1_cargo_demand_profile`（80箱物资属性与15服务区需求空间分布）
  - [x] **Q1 图表**：`fig4_q1_safe_payload_boundary`（基准 $\eta=0.20$ 下三类机型最大安全物理载荷上界）
  - [x] **Q1 图表**：`fig5_q1_eta_sensitivity`（安全余量 $\eta \in [0.10, 0.35]$ 架次与能耗敏感性相变膨胀）
  - [x] **Q2 图表**：`fig6_q2_alns_convergence_comparison`（ALNS 算法多随机种子迭代收敛与自适应算子权重演化）
  - [x] **Q2 图表**：`fig7_q2_drone_schedule_gantt`（8 架实体机 24 架次时空调度甘特图，Makespan=7730.5s）
  - [x] **Q2 图表**：`fig8_q2_battery_recharge_pipeline`（14 组共享电池车电分离两阶段等效充电流水线图，0冲突）
  - [x] **Q2 图表**：`fig9_q2_flight_routes_network`（24 个运输航次空间多点回路飞行网络拓扑，单点11+双点10+三点3）
  - [x] **Q3 图表**：`fig10_q3_los_dem_profile_blockage`（30m DEM 视距遮挡 LOS 射线追踪与高空中继保活剖面）
  - [x] **Q3 图表**：`fig11_q3_relay_schedule_timeline`（中继架次甘特图与 325 处微时段 100% 连续链路全景图）
  - [x] **Q3 图表**：`fig12_q3_scheme_pareto_radar`（中继协同调度方案 A 与方案 B 综合性能 7 维雷达决策图）
  - [x] **Q4 图表**：`fig13_q4_graph_connectivity_partitions`（服务区强绑定网络拓扑图论连通分支与 K=2,3 任务分区图）
  - [x] **Q4 图表**：`fig14_q4_resource_demand_shortage`（各任务组隔离执行下 8 类装备峰值需求与库存缺口大盘图）
  - [x] **图表归档指南**：输出 `reports/FIGURES_CATALOG.md`，包含全部中英图题、排版尺寸与 LaTeX/Typst 嵌入示例代码

---

## 阶段四：竞赛论文初稿撰写与图文资产闭环（已完成初稿，等待审查）
- [x] **代码、文档、图片、结果全要素冲突排查与消除（100% 自洽）**
  - [x] 核查 Q1~Q4 基础物理参数、数据表与代码算法接口（全部吻合）
  - [x] 验证 29 项指标自动化质量门禁（`audit/verify_all.py` 退出码 0，全绿通过）
  - [x] 核对官方 6-Sheet Excel 成果与底表数据（完全一致）
  - [x] 补齐并固化图表形式层与视觉层闭环自检报告（`FIGURE_AUDIT_REPORT.md` 与 `FIGURE_AUDIT_REPORT_V2.md`）
- [x] **论文框架搭建与模板适配**
  - [x] 建立 `paper/` 目录并配置中国研究生数学建模竞赛“华为杯”官方标准 LaTeX 模板
  - [x] 完善 `paper/main.tex`，适配 Windows 中文字体、三线表宏、浮动体及相对图形路径 `\graphicspath{{../figures/}}`
- [x] **正文各章节详细撰写（LaTeX 源码体系）**
  - [x] 摘要与关键词撰写（核心模型、求解方法、量化指标提炼，无占位符）
  - [x] 一、问题重述与研究背景（`paper/sections/1_restatement.tex`）
  - [x] 二、问题分析与总体建模思路（`paper/sections/2_analysis.tex`，嵌入图 1、图 2）
  - [x] 三、模型基本假设与合理性说明（`paper/sections/3_assumptions.tex`）
  - [x] 四、主要符号与物理参数说明（`paper/sections/4_symbols.tex`，包含规范三线表）
  - [x] 五、问题一建模与求解（`paper/sections/5_problem1.tex`，嵌入图 3、图 4、图 5 及 2 个三线表）
  - [x] 六、问题二建模与求解（`paper/sections/6_problem2.tex`，嵌入图 6、图 7、图 8、图 9 及 2 个三线表）
  - [x] 七、问题三建模与求解（`paper/sections/7_problem3.tex`，嵌入图 10、图 11、图 12 及 2 个三线表）
  - [x] 八、问题四建模与求解（`paper/sections/8_problem4.tex`，嵌入图 13、图 14 及 2 个三线表）
  - [x] 九、系统鲁棒性与关键参数敏感性综合分析（`paper/sections/9_sensitivity.tex`）
  - [x] 十、模型的评价、改进方向与实际推广建议（`paper/sections/10_evaluation.tex`）
  - [x] 参考文献整理（`paper/references.tex`，收录 15 篇真实中英文权威学术期刊文献）
  - [x] 附录 A 核心求解算法代码（`paper/sections/A_code.tex`，包含 5 大核心模块实现）
- [x] **输出全景初稿审阅版（Markdown）**
  - [x] 生成 [paper/PAPER_DRAFT_REVIEW.md](file:///d:/dev-java/math_model/paper/PAPER_DRAFT_REVIEW.md)，供用户在当前 IDE 中图文并茂实时审查

---

## 阶段五：用户审查反馈与最终论文排版核验（待用户审查后执行）
- [ ] 收集并落实用户对论文初稿的修改审查意见
- [ ] 校验论文所有数值指标与 `results/` 及 `reports/RESULTS_REPORT.md` 绝对一致
- [ ] 核查论文所有图表引用、公式编号及参考文献引用有效性
- [ ] 检查最终交付 Excel 与代码包提交合规性
