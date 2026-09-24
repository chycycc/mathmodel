# 问题一、问题二计算结果报告

## 运行环境

- Python：`D:\Anaconda\python.exe`
- 代码：`D:\数学建模代码\code\problem1.py`、`problem2.py`、`data_loader.py`
- 数据：题目附件中的 Excel、CSV 和 30 m DEM

## 问题一

基准安全余量 η=0.20，采用全货箱子集枚举、可行性筛选和位掩码集合划分，目标为架次—能耗—时间词典序。结果为 18 架次，A/B/C=0/9/9，总能耗 59.2034 kWh，累计作业时间 32706.5 s，80 箱唯一覆盖。

敏感性结果已保存于 `Q1_敏感性_eta_汇总.csv`，每个 η 均重新求解完整组批。

## 问题二

采用 ALNS 和事件驱动实体机/共享电池流水线仿真。正式运行参数为随机种子 42、43、44，每个种子 100 次迭代。最佳 seed 42 方案为 24 架次、78.265387 kWh、完工时间 7730.5 s、硬时限违约 0；80 箱唯一覆盖；路线为单点 11、双点 10、三点 3。

## 一致性校验

`D:\数学建模2026\scratch\verify_q1_q2_current.py` 重新调用当前物理函数检查容量、服务区归属、能耗、交付时刻、实体机时间轴、电池时间轴和硬时限。当前两题均无错误，问题二硬时限违约为 0。

## 复现

```powershell
& 'D:\Anaconda\python.exe' 'D:\数学建模代码\code\problem1.py'
$env:Q2_SEEDS='42,43,44'
$env:Q2_MAX_ITER='100'
& 'D:\Anaconda\python.exe' 'D:\数学建模代码\code\problem2.py'
& 'D:\Anaconda\python.exe' 'D:\数学建模2026\scratch\verify_q1_q2_current.py'
```

