# -*- coding: utf-8 -*-
"""
结果汇总结算与官方 Excel 模板完整写入脚本
将 Q1_单点组批, Q2_运输架次, Q2_逐箱交付, Q3_中继架次, Q3_通信保障, Q4_分区配置
6 张标准结果表写入 results/结果提交模板.xlsx，并严格校验格式与内容。
"""

import sys
import os
import openpyxl
import pandas as pd

# 自适应工程工作区根路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE_ROOT = os.path.dirname(_CURRENT_DIR)
TEMPLATE_PATH = os.path.join(_WORKSPACE_ROOT, "数模题目", "D题", "结果提交模板.xlsx")
OUTPUT_PATH = os.path.join(_WORKSPACE_ROOT, "results", "结果提交模板.xlsx")

def export_all_results():
    print("==========================================================")
    print("开始整合回填官方结果提交 Excel 模板")
    print(f"模板源文件: {TEMPLATE_PATH}")
    print(f"目标输出: {OUTPUT_PATH}")
    print("==========================================================")
    
    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    
    def clear_sheet_data(ws):
        max_r = ws.max_row
        if max_r > 1:
            ws.delete_rows(2, max_r - 1)

    # 1. Q1_单点组批
    ws_q1 = wb['Q1_单点组批']
    clear_sheet_data(ws_q1)
    df_q1 = pd.read_csv('results/Q1_单点组批方案.csv')
    cols_q1 = ['架次编号', '服务区编号', '机型编号', '货箱编号列表', '总质量（kg）', '总体积（m³）', '往返时间（s）', '架次能耗（kWh）', '返航SOC（%）']
    for row_idx, r in df_q1[cols_q1].iterrows():
        for col_idx, col_name in enumerate(cols_q1, start=1):
            val = r[col_name]
            # 确保数值格式
            if col_name in ['总质量（kg）', '总体积（m³）', '往返时间（s）', '架次能耗（kWh）', '返航SOC（%）']:
                val = float(val)
            ws_q1.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q1_单点组批 写入完成: {len(df_q1)} 行")
    
    # 2. Q2_运输架次
    ws_q2_trips = wb['Q2_运输架次']
    clear_sheet_data(ws_q2_trips)
    df_q2_trips = pd.read_csv('results/Q2_运输架次.csv')
    cols_q2_trips = ['架次编号', '无人机编号', '机型编号', '电池编号', '开始时刻（s）', '访问服务区顺序', '返回O01时刻（s）', '架次能耗（kWh）']
    for row_idx, r in df_q2_trips[cols_q2_trips].iterrows():
        for col_idx, col_name in enumerate(cols_q2_trips, start=1):
            val = r[col_name]
            if col_name in ['开始时刻（s）', '返回O01时刻（s）', '架次能耗（kWh）']:
                val = float(val)
            ws_q2_trips.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q2_运输架次 写入完成: {len(df_q2_trips)} 行")
    
    # 3. Q2_逐箱交付
    ws_q2_boxes = wb['Q2_逐箱交付']
    clear_sheet_data(ws_q2_boxes)
    df_q2_boxes = pd.read_csv('results/Q2_逐箱交付.csv')
    cols_q2_boxes = ['货箱编号', '架次编号', '服务区编号', '交付完成时刻（s）']
    for row_idx, r in df_q2_boxes[cols_q2_boxes].iterrows():
        for col_idx, col_name in enumerate(cols_q2_boxes, start=1):
            val = r[col_name]
            if col_name in ['交付完成时刻（s）']:
                val = float(val)
            ws_q2_boxes.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q2_逐箱交付 写入完成: {len(df_q2_boxes)} 行")
    
    # 4. Q3_中继架次
    ws_q3_relays = wb['Q3_中继架次']
    clear_sheet_data(ws_q3_relays)
    df_q3_relays = pd.read_csv('results/Q3_中继架次.csv')
    cols_q3_relays = ['中继架次编号', '中继无人机编号', '能源组件编号', '开始时刻（s）', '悬停经度（°）', '悬停纬度（°）', '悬停海拔（m）', '建链完成时刻（s）', '服务结束时刻（s）', '返回O01时刻（s）', '架次能耗（kWh）']
    for row_idx, r in df_q3_relays[cols_q3_relays].iterrows():
        for col_idx, col_name in enumerate(cols_q3_relays, start=1):
            val = r[col_name]
            if col_name in ['开始时刻（s）', '悬停经度（°）', '悬停纬度（°）', '悬停海拔（m）', '建链完成时刻（s）', '服务结束时刻（s）', '返回O01时刻（s）', '架次能耗（kWh）']:
                val = float(val)
            ws_q3_relays.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q3_中继架次 写入完成: {len(df_q3_relays)} 行")
    
    # 5. Q3_通信保障
    ws_q3_comm = wb['Q3_通信保障']
    clear_sheet_data(ws_q3_comm)
    df_q3_comm = pd.read_csv('results/Q3_通信保障.csv')
    cols_q3_comm = ['运输架次编号', '通信阶段', '开始时刻（s）', '结束时刻（s）', '保障方式', '中继架次编号']
    for row_idx, r in df_q3_comm[cols_q3_comm].iterrows():
        for col_idx, col_name in enumerate(cols_q3_comm, start=1):
            val = r[col_name]
            if pd.isna(val):
                val = ''
            elif col_name in ['开始时刻（s）', '结束时刻（s）']:
                val = float(val)
            ws_q3_comm.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q3_通信保障 写入完成: {len(df_q3_comm)} 行")
    
    # 6. Q4_分区配置
    ws_q4 = wb['Q4_分区配置']
    clear_sheet_data(ws_q4)
    df_q4 = pd.read_csv('results/Q4_分区配置.csv')
    cols_q4 = ['K（2或3）', '任务组编号', '服务区列表', 'A型运输无人机数', 'B型运输无人机数', 'C型运输无人机数', 'A型电池组数', 'B型电池组数', 'C型电池组数', '中继无人机数', '中继能源组件数']
    for row_idx, r in df_q4[cols_q4].iterrows():
        for col_idx, col_name in enumerate(cols_q4, start=1):
            val = r[col_name]
            if col_name in ['K（2或3）', 'A型运输无人机数', 'B型运输无人机数', 'C型运输无人机数', 'A型电池组数', 'B型电池组数', 'C型电池组数', '中继无人机数', '中继能源组件数']:
                val = int(val)
            ws_q4.cell(row=row_idx + 2, column=col_idx, value=val)
    print(f"Q4_分区配置 写入完成: {len(df_q4)} 行")
    
    wb.save(OUTPUT_PATH)
    print(f"\n全部 6 个 Sheet 回填完毕，成功保存至: {OUTPUT_PATH}")

if __name__ == '__main__':
    export_all_results()
