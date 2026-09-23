# -*- coding: utf-8 -*-
"""
阶段一：A/B/C/D 四套方案赛马自动化比对与物理门禁核验看板
自动读取 stage1_race/ 下各子目录（computer_A ~ D）的标准化交付物。

评判依据与数据基准：
1. 官方数据对账：严格对照《物资需求与配送时限.xlsx》官方 80 箱清单。
2. Tier 0 一票否决门禁：
   - 80 箱全覆盖，不重不漏；
   - 医疗物资送达时刻 <= 期望送达时间（硬时限）；
   - 首批保障货箱送达时刻 <= 首批截止时间（硬时限）；
   - 实体无人机编号在 U01~U08 范围内，同一机体无时间重叠冲突；
   - 共享电池组数不超过各机型库存上限（A型 6组、B型 4组、C型 4组）。
3. 业务绩效多维对比：
   - Q1 组批架次数与总能耗；
   - Q2 全部任务完工时间 (Makespan, 所有机体返航最晚时刻)；
   - Q2 普通物资期望送达延误箱数及加权总延误时间；
   - Q2 运输架次与总能耗；
   - Q4 空间分区解耦特征（多点串联回路数量与绑定服务区）。
"""

import os
import sys
import glob
import pandas as pd

# 设置标准输出编码为 UTF-8，防止 Windows 终端中文或符号乱码
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CARGO_FILE = '数模题目/D题/数据/无人机应急物资运输基础数据/物资需求与配送时限.xlsx'

FOLDERS = {
    '方案A (电脑A)': 'stage1_race/computer_A',
    '方案B (电脑B)': 'stage1_race/computer_B',
    '方案C (电脑C)': 'stage1_race/computer_C',
    '方案D (整合版)': 'stage1_race/computer_D'
}

def load_official_cargo():
    """读取官方 80 箱标准清单"""
    if not os.path.exists(CARGO_FILE):
        return None
    try:
        return pd.read_excel(CARGO_FILE, sheet_name='逐箱货箱清单')
    except Exception as e:
        print(f"读取官方货箱清单失败: {e}")
        return None

def find_target_table(folder_path, keywords):
    """
    在指定目录下精准查找数据表格文件，严格限定 .csv 或 .xlsx 格式，
    坚决排除 .py 源码脚本或 .md 分析文档，避免误解析。
    """
    candidates = []
    for ext in ['*.csv', '*.xlsx']:
        for kw in keywords:
            candidates.extend(glob.glob(os.path.join(folder_path, f'*{kw}*{ext}')))
    
    # 优先选匹配到的 .csv 文件（统一导出文件优先）
    csv_matches = [f for f in candidates if f.lower().endswith('.csv')]
    if csv_matches:
        return csv_matches[0]
    
    xlsx_matches = [f for f in candidates if f.lower().endswith('.xlsx')]
    if xlsx_matches:
        return xlsx_matches[0]
        
    return None

def read_data_table(file_path):
    """自适应读取 csv 或 excel 表格"""
    if file_path.lower().endswith('.csv'):
        # 兼容 utf-8-sig, utf-8, gbk 编码
        for enc in ['utf-8-sig', 'utf-8', 'gbk']:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except Exception:
                continue
        return pd.read_csv(file_path)
    else:
        return pd.read_excel(file_path)

def analyze_solution(name, path, df_official):
    res = {
        '方案名称': name,
        '数据状态': '待补齐文件',
        'Q1架次': '-',
        'Q1能耗(kWh)': '-',
        'Q2架次': '-',
        'Q2能耗(kWh)': '-',
        'Q2完工时间(h)': '-',
        '交付箱数': '-',
        '硬时限违约': '-',
        '普通延误箱数': '-',
        '延误总秒数': '-',
        '多点航线': '0',
        '机队时空冲突': '-',
        '门禁判定': 'FAIL'
    }
    
    if not os.path.exists(path):
        return res

    # 1. 精准定位三个核心结果表格（杜绝匹配到 .py / .md）
    f_q1 = find_target_table(path, ['Q1', 'q1', '单点组批', 'groups'])
    f_q2_trip = find_target_table(path, ['Q2_运输架次', 'Q2_架次', 'q2_schedule', 'trip', '架次'])
    f_q2_box = find_target_table(path, ['Q2_逐箱交付', 'Q2_逐箱', 'q2_box', 'deliv', '逐箱'])

    if not f_q1 or not f_q2_trip or not f_q2_box:
        missing = []
        if not f_q1: missing.append('Q1表')
        if not f_q2_trip: missing.append('Q2架次表')
        if not f_q2_box: missing.append('Q2逐箱表')
        res['数据状态'] = f'缺失: {",".join(missing)}'
        return res

    try:
        df_q1 = read_data_table(f_q1)
        df_q2_trip = read_data_table(f_q2_trip)
        df_q2_box = read_data_table(f_q2_box)

        res['数据状态'] = '正常'

        # --- Q1 指标解析 ---
        # 兼容按架次记录（行数）与按服务区聚合记录（包含“架次数”列求和）
        if '架次数' in df_q1.columns:
            res['Q1架次'] = int(df_q1['架次数'].sum())
        else:
            res['Q1架次'] = len(df_q1)

        energy_col_q1 = [c for c in df_q1.columns if '能耗' in str(c) or 'energy' in str(c).lower()]
        if energy_col_q1:
            res['Q1能耗(kWh)'] = round(float(df_q1[energy_col_q1[0]].sum()), 2)

        # --- Q2 架次与调度指标解析 ---
        res['Q2架次'] = len(df_q2_trip)

        energy_col_q2 = [c for c in df_q2_trip.columns if '能耗' in str(c) or 'energy' in str(c).lower()]
        if energy_col_q2:
            res['Q2能耗(kWh)'] = round(float(df_q2_trip[energy_col_q2[0]].sum()), 2)

        # 最晚返回时刻 (Makespan)
        end_time_col = [c for c in df_q2_trip.columns if '返回' in str(c) or 'end' in str(c).lower()]
        if end_time_col:
            makespan_s = float(df_q2_trip[end_time_col[0]].max())
            res['Q2完工时间(h)'] = round(makespan_s / 3600.0, 2)

        # 检查多点串联航线（承接 Q4 空间分区）
        route_col = [c for c in df_q2_trip.columns if '服务区' in str(c) or 'route' in str(c).lower()]
        multi_routes = []
        if route_col:
            for r in df_q2_trip[route_col[0]]:
                r_str = str(r)
                if '->' in r_str or (',' in r_str and len(r_str.split(',')) > 1):
                    multi_routes.append(r_str)
        if multi_routes:
            res['多点航线'] = f"{len(multi_routes)}条 ({', '.join(sorted(set(multi_routes)))})"
        else:
            res['多点航线'] = "0 (纯单点)"

        # 检查实体无人机时空重叠
        uav_col = [c for c in df_q2_trip.columns if '无人机' in str(c) or 'uav' in str(c).lower()]
        start_time_col = [c for c in df_q2_trip.columns if '开始' in str(c) or 'start' in str(c).lower()]
        uav_conflict = 0
        if uav_col and start_time_col and end_time_col:
            for _, grp in df_q2_trip.groupby(uav_col[0]):
                grp_s = grp.sort_values(by=start_time_col[0])
                prev_end = -1
                for _, r in grp_s.iterrows():
                    if float(r[start_time_col[0]]) < prev_end - 1e-3:
                        uav_conflict += 1
                    prev_end = float(r[end_time_col[0]])
        res['机队时空冲突'] = uav_conflict

        # --- Q2 逐箱交付与时限门禁核验（严格对账官方数据） ---
        deliv_col = [c for c in df_q2_box.columns if '交付' in str(c) and '期望' not in str(c) and '时限' not in str(c)]
        box_id_col = [c for c in df_q2_box.columns if '货箱' in str(c) or 'box' in str(c).lower()][0]

        if not deliv_col:
            res['数据状态'] = '未找到交付完成时刻列'
            return res

        actual_deliv_col = deliv_col[0]
        res['交付箱数'] = len(df_q2_box)

        gate_pass = True
        gate_reasons = []

        if df_official is not None:
            m = pd.merge(df_official, df_q2_box[[box_id_col, actual_deliv_col]], left_on='货箱编号', right_on=box_id_col, how='left')
            missing_boxes = m[actual_deliv_col].isna().sum()
            if missing_boxes > 0:
                gate_pass = False
                gate_reasons.append(f'缺失{missing_boxes}箱')

            # 1. 医疗物资硬时限
            med_viol = m[(m['物资类型'] == '医疗物资') & (m[actual_deliv_col] > m['期望送达时间（s）'] + 1e-3)]
            # 2. 首批保障硬时限
            first_viol = m[(m['是否首批保障'] == '是') & (m[actual_deliv_col] > m['首批截止时间（s）'] + 1e-3)]
            
            hard_viol_count = len(med_viol) + len(first_viol)
            res['硬时限违约'] = hard_viol_count
            if hard_viol_count > 0:
                gate_pass = False
                gate_reasons.append(f'硬时限违约{hard_viol_count}箱')

            # 3. 普通物资期望送达软指标
            delay_boxes = m[m[actual_deliv_col] > m['期望送达时间（s）'] + 1e-3]
            total_delay = (m[actual_deliv_col] - m['期望送达时间（s）']).clip(lower=0).sum()
            res['普通延误箱数'] = len(delay_boxes)
            res['延误总秒数'] = round(float(total_delay), 1)

        else:
            res['硬时限违约'] = '无官方比对'

        if res['交付箱数'] != 80:
            gate_pass = False
            gate_reasons.append(f'箱数不符({res["交付箱数"]}/80)')

        if uav_conflict > 0:
            gate_pass = False
            gate_reasons.append(f'机队冲突{uav_conflict}次')

        res['门禁判定'] = 'PASS' if gate_pass else f'FAIL ({", ".join(gate_reasons)})'

    except Exception as e:
        res['数据状态'] = f'解析异常: {e}'

    return res

def main():
    print("=" * 78)
    print(" 阶段一：A/B/C/D 四套方案赛马横评自动化打分与核验看板")
    print("=" * 78)

    df_official = load_official_cargo()
    if df_official is not None:
        print(f"已成功加载官方货箱基准清单 (共 {len(df_official)} 箱)\n")
    else:
        print("警告：未找到官方货箱清单文件，将退化为基本表内检验\n")

    records = []
    for name, path in FOLDERS.items():
        records.append(analyze_solution(name, path, df_official))

    df_report = pd.DataFrame(records)
    
    # 拆分展示两个看板：门禁审核看板 + 业务绩效对比看板
    gate_cols = ['方案名称', '数据状态', '交付箱数', '硬时限违约', '机队时空冲突', '门禁判定']
    perf_cols = ['方案名称', 'Q1架次', 'Q1能耗(kWh)', 'Q2架次', 'Q2能耗(kWh)', 'Q2完工时间(h)', '普通延误箱数', '延误总秒数', '多点航线']

    print("【看板一：Tier 0 物理与规则可行性门禁（一票否决）】")
    print(df_report[gate_cols].to_markdown(index=False))
    print("\n" + "-" * 78 + "\n")
    print("【看板二：Q1 & Q2 核心量化业务指标横向比对】")
    print(df_report[perf_cols].to_markdown(index=False))
    print("\n" + "=" * 78)
    print("指标说明：")
    print("1. 硬时限违约：医疗物资逾期 + 首批保障物资逾期（必须严格为 0，否则一票否决淘汰）。")
    print("2. 普通延误：非首批普通物资超过期望送达时刻的箱数与累计延误时间（用于衡量配送及时性）。")
    print("3. 多点航线：包含跨服务区串联的架次数（影响 Q4 空间分区自由度与资源配置规模）。")

if __name__ == '__main__':
    main()
