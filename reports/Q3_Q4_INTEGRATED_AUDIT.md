# Q3/Q4 综合审计

## 结论

问题三在当前24架次Q2基线下通过连续通信审计：1344个采样点由直连或中继覆盖，23个架次使用中继，0中断。问题四的K2_A和K3分区满足服务区唯一归属和架次不可拆分；修复DEM后中继需求为每组1–8架次/组件，资源缺口需按中继库存进一步审计。

## 关键风险

plan.md记录的29架次历史方案与当前Q2 CSV的24架次方案不一致；该差异会影响Q3/Q4所有继承结果。当前阶段已停止猜测并将24架次CSV作为实际基线。若用户要求29架次版本，必须先指定版本并重新运行。

## 文件清单

- code/Q3/q3_solver.py
- code/Q4/q4_solver.py
- results/Q3/Q3_通信保障.csv
- results/Q3/Q3_中继任务.csv
- results/Q3/Q3_summary.json
- results/Q4/Q4_分区配置.csv
- results/Q4/Q4_summary.json
- reports/Q3_report.md
- reports/Q4_report.md
- reports/Q3_audit.md
- reports/Q4_audit.md
