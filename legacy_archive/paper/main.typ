#set document(title: "山区洪涝灾害下无人机运输与通信协同优化调度模型与算法研究", author: ())

#let song-font = ("SimSun", "Songti SC", "STSong", "Times New Roman")
#let kai-font = ("KaiTi", "Kaiti SC", "STKaiti", "SimSun")
#let hei-font = ("SimHei", "Heiti SC", "STHeiti", "SimSun")
#let code-font = ("Courier New", "Menlo")

#let heading-numbering(..nums) = {
  let ns = nums.pos()
  if ns.len() == 1 {
    numbering("1.", ns.at(0))
  } else if ns.len() == 2 {
    numbering("1.1", ns.at(0), ns.at(1))
  } else {
    numbering("1.1.1", ns.at(0), ns.at(1), ns.at(2))
  }
}

#set page(
  paper: "a4",
  margin: (top: 25mm, bottom: 25mm, left: 22.5mm, right: 22.5mm),
  numbering: "1",
)
#set text(font: song-font, size: 12pt, lang: "zh")
#set par(first-line-indent: (amount: 2em, all: true), justify: true, leading: 1.02em, spacing: 0.65em)
#set enum(numbering: "1.")
#set heading(numbering: heading-numbering)
#set math.equation(numbering: "(1)")

#show heading.where(level: 1): it => block(above: 1.15em, below: 1.0em, width: 100%)[
  #align(center)[#text(font: hei-font, size: 14pt, weight: "bold")[#it]]
]
#show heading.where(level: 2): it => block(above: 0.85em, below: 0.55em)[
  #text(font: hei-font, size: 12pt, weight: "bold")[#it]
]
#show heading.where(level: 3): it => block(above: 0.75em, below: 0.45em)[
  #text(font: hei-font, size: 12pt, weight: "bold")[#it]
]
#show raw.where(block: true): it => block(
  inset: (x: 0.7em, y: 0.55em),
  stroke: 0.5pt + rgb("#808080"),
  fill: rgb("#f7f7f7"),
  width: 100%,
)[#text(font: code-font, size: 9.5pt)[#it]]

#let cover-info-table() = align(center)[
  #block(width: 15.2cm)[
    #block(width: 100%, height: 1.55cm)[
      #grid(
        columns: (4.2cm, 1fr),
        align: (left + horizon, left + horizon),
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[学 #h(1em) 校]]
        ],
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[研究生数学建模竞赛]]
        ],
      )
      #line(length: 100%, stroke: 1.2pt)
    ]
    #block(width: 100%, height: 1.55cm)[
      #grid(
        columns: (4.2cm, 1fr),
        align: (left + horizon, left + horizon),
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[参赛队号]]
        ],
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[2026-D-TEAM]]
        ],
      )
      #line(length: 100%, stroke: 1.2pt)
    ]
    #grid(
      columns: (4.2cm, 1fr),
      align: (left + horizon, left + top),
      block(height: 3.3cm)[
        #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[队员姓名]]
      ],
      block(width: 100%)[
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[1. 建模队员 A]]]
          #line(length: 100%, stroke: 0.55pt)
        ]
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[2. 编程队员 B]]]
          #line(length: 100%, stroke: 0.55pt)
        ]
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[3. 论文队员 C]]]
          #line(length: 100%, stroke: 1.2pt)
        ]
      ],
    )
  ]
]

#let cover-page() = {
  counter(page).update(0)
  align(center)[#image("logo.pdf", width: 14.5cm)]
  v(1.35cm)
  align(center)[#image("title.pdf", width: 10.8cm)]
  v(2.35cm)
  cover-info-table()
  pagebreak()
}

#let abstract-page() = {
  counter(page).update(1)
  align(center)[#image("title.pdf", width: 10.8cm)]
  v(0.65cm)
  grid(
    columns: (4.5em, 1fr),
    align: (left + horizon, center + horizon),
    text(size: 14pt)[题 #h(1em) 目],
    block(width: 100%)[
      #align(center)[#text(font: hei-font, size: 15pt, weight: "bold")[山区洪涝灾害下无人机运输与通信协同优化调度模型与算法研究]]
      #line(length: 100%, stroke: 0.5pt)
    ],
  )
  v(0.35cm)
  align(center)[#text(font: hei-font, size: 14pt, weight: "bold")[摘 #h(2em) 要]]
  v(0.35cm)

  [针对极端洪涝灾害下山区“道路阻断、断水断电、基站损毁”的复杂救援场景，本文深度融合 30m 高精度数字高程模型（DEM）、非线性飞行能耗积分、动力电池两阶段充电时序以及无线微波视距遮挡传播机理，建立了一套系统、严密的异构无人机应急运投、中继通信与任务网格自治协同优化体系。]

  [*针对问题一（单点往返载荷模型与多批次组批）*，建立了包含球面大圆距离、三阶段飞行状态（爬升、巡航、下降）与载重衰减等效航程的精准物理能耗模型。严格证明了单点往返总能耗关于有效载荷的严格单调递增性，采用高精度二分法求解了三种机型在全部 15 个服务区的最大安全有效载荷。深入揭示了 C 型重载机在远距离与大爬升工况下的电池容量瓶颈（如 S008 点最大载重由额定 80kg 剧烈衰减至 50.26kg）。进而构建基于 0-1 集合划分（Set Partitioning Problem, SPP）的精确数学规划模型与紧上界分支定界求解算法，求得全局帕累托最优单点组批方案：仅需出动 19 个架次（锁定理论架次下界，B型10次，C型9次），总能耗由 68.622 kWh 显著优化至 63.758 kWh（节电 7.09%），累计作业时间缩短 1.69 小时（提速 15.0%），各架次返航 SOC 保持在 $22.5\% ~ 72.4\%$，100% 满足法定安全余量。]

  [*针对问题二（异构多点多架次时空协同调度）*，突破单点往返局限，面对 8 架实体机（4 A, 2 B, 2 C）与 14 组共享电池（A:6, B:4, C:4）资源硬约束，建立了多点航线动态载荷递减积分与“恒流快充（65%）+恒压慢充（35%）”两阶段充电状态机推进模型。通过深挖机队高并发潜能、满载压缩与动态事件驱动滚动调度（ASAP/EDF），求得 28 个架次（A型13次，B型8次，C型7次）的帕累托卓越解。成功挖掘出 T002（S002 $->$ S004）与 T024（S010 $->$ S013）双多点协同回路；全任务完工时间 Makespan 由 12463.7s 骤降至 **7353.1s（2.04h，耗时缩短 41.0%，提速 1.42 小时）**，总运输电耗优化降至 **79.915 kWh（跌破80kWh，节能5.03%）**；30 箱首批急救与保障物资 100% 履约（0 违约），期望时限违约由 18 箱剧减至 8 箱，8 架无人机完工时刻收敛于 1.48h~2.04h，机队利用率达到极致均衡。]

  [*针对问题三（DEM 视距遮挡与空地中继协同保障）*，提出了三维空间射线步进采样光线追踪算法（Ray-Casting LOS），结合 2.4GHz 射频双向链路损耗预算（直连门限 122dB，附加山体衰减 10dB），定量揭示了 12 个深山服务区由于地形阻断导致通信中断的内在机理。通过全空域网格化通视投影搜索，确定了西部主阵位（悬停海拔 686.2m）与东部辅阵位（悬停海拔 690.5m）两处战略制高点。受益于问题二运输效率的大幅跃升，中继任务由 6 架次精简为 **4 个高饱和度架次**，实现全周期 **88 个通信阶段（直连52个，中继36个）100% 连续通信保障**，通信盲区中断时长恒为 0 秒，返航 SOC 保持在 $64.3\% ~ 75.8\%$，成功为后方节约留存 2 组能源组件战略战备储备（节省率 33.3%）。]

  [*针对问题四（救援任务分区与独立资源配置优化）*，在遵守 T002 串联航线服务区强绑定硬约束前提下，基于图谱聚类分别构建了 $K=2$（东西两翼对半分区，各40箱/50%负荷）与 $K=3$（三格专业化联防）方案。利用区间并发扫描法精确核算各组独立自治运作所需的运力峰值。量化揭示了“集中池化协同（Pooling Effect）”相较于“分散独立运作”在节约装备资产上的显著优势：集中调度下零库存缺口，而在独立分区下由于并发脉冲叠加，产生明显的“分散配置开销”（$K=2$ 产生 7 架运输机与 1 架中继机缺口；$K=3$ 产生 8 架运输机与 3 架中继机缺口）。综合权衡建议优先采用 $K=2$ 对半分区。]

  [最后，进行了高空风速巡航扰动、安全余量阈值及遮挡衰减的敏感性分析，验证了方案的高鲁棒性，并提出了具有工业级应用价值的平战结合应急指挥推广方案。]

  v(0.65em)
  block[
    #set par(first-line-indent: 0pt)
    #text(font: hei-font, size: 12pt, weight: "bold")[关键词：] 应急物资配送；无人机时空调度；空中移动中继；30m DEM 视距遮挡；两阶段电池充电；自适应大邻域搜索；任务分区
  ]
  pagebreak()
}

#let toc-line(level, title, page) = {
  let indent = if level == 1 { 0pt } else if level == 2 { 28pt } else { 52pt }
  let weight = if level == 1 { "bold" } else { "regular" }
  block(above: if level == 1 { 0.52em } else { 0.24em })[
    #grid(
      columns: (auto, 1fr, auto),
      column-gutter: 0.55em,
      inset: (left: indent),
      text(font: if level == 1 { hei-font } else { song-font }, weight: weight)[#title],
      box(height: 1em, width: 100%)[#v(0.72em)#line(length: 100%, stroke: (dash: "dotted", thickness: 0.8pt))],
      text(weight: weight)[#page],
    )
  ]
}

#let toc-page() = {
  align(center)[#text(font: hei-font, size: 16pt, weight: "bold")[目 #h(1em) 录]]
  v(0.8cm)
  toc-line(1, [1. 问题重述], [3])
  toc-line(2, [1.1 问题背景], [3])
  toc-line(2, [1.2 问题内容], [3])
  toc-line(1, [2. 问题分析], [4])
  toc-line(2, [2.1 问题一的分析：非线性物理能耗机理与单点背包组批], [4])
  toc-line(2, [2.2 问题二的分析：异构机队时空协同与两阶段充电状态演进], [4])
  toc-line(2, [2.3 问题三的分析：30m DEM 空间光线追踪与空中中继协同保障], [5])
  toc-line(2, [2.4 问题四的分析：图谱聚类任务分区与分散资源配置开销], [5])
  toc-line(1, [3. 模型假设], [6])
  toc-line(1, [4. 符号说明], [7])
  toc-line(1, [5. 问题一的模型建立与求解], [8])
  toc-line(2, [5.1 单点往返物理能耗模型与最大安全载荷推导], [8])
  toc-line(2, [5.2 货箱多批次单点组批优化模型], [9])
  toc-line(2, [5.3 求解结果与单点组批方案分析], [10])
  toc-line(1, [6. 问题二的模型建立与求解], [11])
  toc-line(2, [6.1 异构多机多架次时空协同网络模型], [11])
  toc-line(2, [6.2 求解算法设计：基于状态机的大邻域自适应搜索（ALNS）], [12])
  toc-line(2, [6.3 求解结果与调度方案综合讨论], [13])
  toc-line(1, [7. 问题三的模型建立与求解], [14])
  toc-line(2, [7.1 30m DEM 空间光线追踪与射频链路预算], [14])
  toc-line(2, [7.2 中继无人机三维空间悬停优化与服务调度], [15])
  toc-line(2, [7.3 中继架次排班与空地连续通信保障结果], [16])
  toc-line(1, [8. 问题四的模型建立与求解], [17])
  toc-line(2, [8.1 航线强绑定约束与任务图谱聚类], [17])
  toc-line(2, [8.2 任务分区方案设计与物理网格定位], [17])
  toc-line(2, [8.3 独立资源配置核算与集中池化效应深度剖析], [18])
  toc-line(1, [9. 参数敏感性分析], [20])
  toc-line(2, [9.1 巡航飞行速度扰动对完工时间与系统总能耗的敏感性], [20])
  toc-line(2, [9.2 返航安全余量阈值对有效运载能力的敏感性], [20])
  toc-line(2, [9.3 地形遮挡附加衰减对直连盲区的敏感性], [21])
  toc-line(1, [10. 模型评价与推广], [22])
  toc-line(2, [10.1 模型的主要优点], [22])
  toc-line(2, [10.2 模型的局限性与改进方向], [22])
  toc-line(2, [10.3 灾后应急救援工程推广应用价值], [23])
  toc-line(1, [参考文献], [24])
  toc-line(1, [附录 A 核心算法源代码节选], [25])
  pagebreak()
}

#cover-page()
#abstract-page()
#toc-page()

#include("sections/1_restatement.typ")
#include("sections/2_analysis.typ")
#include("sections/3_assumptions.typ")
#include("sections/4_symbols.typ")
#include("sections/5_problem1.typ")
#include("sections/6_problem2.typ")
#include("sections/7_problem3.typ")
#include("sections/8_problem4.typ")
#include("sections/9_sensitivity.typ")
#include("sections/10_evaluation.typ")

#include("references.typ")

#pagebreak()
#align(center)[#text(font: hei-font, size: 14pt, weight: "bold")[附录 A #h(1em) 核心算法源代码节选]]
#v(0.6em)
#include("sections/A_code.typ")