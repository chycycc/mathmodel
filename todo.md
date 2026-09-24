# 任务清单

## 阶段一：问题一与问题二方案求解与比对（已完成）
- [x] 基于纯算法求解问题一（集合划分分支定界，18架次，59.20kWh）
- [x] 开发并运行真正的 ALNS 自适应大规模邻域搜索算法求解问题二（最新落地基准：29架次，2.26h (8143.7s)，88.73kWh，0违约，14组电池全员激活周转，0冲突）
- [x] 将 36 架次对比方案（对应 `stage1_race/computer_C/q12_solver.py`）归档至 `stage1_race/computer_D/`（作为后续多目标对比素材）
- [x] 绘制问题二全套学术级矢量图表（收敛曲线、8机甘特图、14电池流水线、Pareto权衡图，存于 `figures/*.pdf`）
- [x] 撰写权威特等奖级问题二专门建模与算法设计报告（`reports/Q2_ANALYSIS_MODELING.md`）

---

## 目录与文件整理（已完成）
- [x] 将历史生成的 `paper/`、旧结果及旧报告移入 `legacy_archive/`
- [x] 将旧版 `problem3.py`、`problem4.py`、`search_relay.py`、`plot_all.py`、`verify_all.py` 移入 `legacy_archive/code_reference/`
- [x] 主目录 `results/` 保存真实算法求解基准数据：
  - `Q1_单点组批方案.csv`（18架次，59.203 kWh）
  - `Q2_运输架次.csv`（29架次升级基准，8143.7s，88.729 kWh）
  - `Q2_逐箱交付.csv`（80箱，0硬违约）
- [x] 主目录 `code/` 保留纯算法基座文件：
  - `data_loader.py`（数据与地理空间加载器，自适应路径）
  - `problem1.py`（问题一集合划分精确求解器）
  - `problem2.py`（问题二完整 ALNS 自适应求解器）
  - `export_excel.py`（官方结果回填导出工具）
- [x] 同步胜出方案至 `stage1_race/computer_A/`（包含最新 Q1/Q2 代码、CSV 结果与简报）
- [x] 更新 `reports/ANALYSIS_MODELING_REPORT.md` 与 `reports/Q2_ANALYSIS_MODELING.md`，使数学模型、算子定义与真实代码 100% 对应

---

## 阶段二：问题三与问题四求解（待后续执行）
- [x] **问题三：通信中继联合调度**
  - [x] 读取 30m DEM 矩阵，计算当前24个运输架次的三维空间航迹
  - [x] 计算与 G01 的视距遮挡（LOS）及双向链路通断情况
  - [x] 搜索R01/R02候选悬停位置与服务时序（当前基线无需启用中继）
  - [x] 导出 `results/Q3/Q3_中继任务.csv` 与 `results/Q3/Q3_通信保障.csv`
- [x] **问题四：任务分区与资源配置**
  - [x] 施加跨服务区多点航次不可拆分约束
  - [x] 完成15个服务区在K=2与K=3时的任务组划分
  - [x] 统计各组运输机、电池及中继资源最大并发需求
  - [x] 导出 `results/Q4/Q4_分区配置.csv`
- [ ] **导出 Excel 提交文件**
  - [ ] 运行 `code/export_excel.py`，生成完整的 `results/结果提交模板.xlsx`
- [ ] **生成计算结果报告**
  - [ ] 汇总 Q1~Q4 完整数据，编写 `reports/RESULTS_REPORT.md`

---

## 阶段三：图表、论文与验收（待阶段二完成后执行）
- [ ] **生成图表**
  - [ ] 绘制数据分析图（保存至 `figures/*.pdf`）
  - [ ] 绘制技术路线图与系统架构图（保存至 `figures/*.drawio` / `figures/*.pdf`）
- [ ] **论文撰写**
  - [ ] 基于 Typst 模板撰写论文正文（`paper/main.typ`）
  - [ ] 插入图表与表格，填入最终计算数据
- [ ] **最终验收检查**
  - [ ] 检查约束条件、数值一致性、格式规范
  - [ ] 编写 `reports/VERIFY_REPORT.md`


## 阶段二补充说明
- [x] Q3/Q4结果、报告和审计已生成。
- [ ] DrawIO/PDF与论文编译：当前环境未安装drawio、typst或xelatex；已保留SVG和.drawio源文件。
- [!] 版本冲突：plan.md为29架次历史基线，当前Q2 CSV/Q2报告为24架次；切换版本前需重新运行Q3/Q4。
