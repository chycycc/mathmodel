# -*- coding: utf-8 -*-
"""
全题目全要素一键自动化综合验证入口 (All-in-One Verification Runner)
顺序执行：
1. 问题一独立审计 (Q1_audit)
2. 问题二独立审计 (Q2_audit)
3. 问题三独立审计 (Q3_audit)
4. 问题四独立审计 (Q4_audit)
5. 最终提交 Excel 格式与工作表完备性校验
"""

import os
import sys
import subprocess
import openpyxl

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_all_verification():
    print("=" * 70)
    print("      2026年研究生数学建模竞赛 D 题 全题目全要素自动化终验流程")
    print("=" * 70)
    
    scripts = [
        ('问题一 (Q1)', os.path.join(PROJECT_ROOT, 'audit', 'Q1_audit.py')),
        ('问题二 (Q2)', os.path.join(PROJECT_ROOT, 'audit', 'Q2_audit.py')),
        ('问题三 (Q3)', os.path.join(PROJECT_ROOT, 'audit', 'Q3_audit.py')),
        ('问题四 (Q4)', os.path.join(PROJECT_ROOT, 'audit', 'Q4_audit.py')),
    ]
    
    all_pass = True
    
    for name, script_path in scripts:
        print(f"\n>>> 正在运行: {name} 自动化审计 <<<")
        ret = subprocess.run([sys.executable, script_path], cwd=PROJECT_ROOT)
        if ret.returncode != 0:
            print(f"[FAIL] {name} 审计未通过，退出码: {ret.returncode}")
            all_pass = False
        else:
            print(f"[PASS] {name} 审计全部通过！")
            
    # 检查 Excel 交付文件
    print("\n>>> 正在核查官方最终交付 Excel 文件 <<<")
    excel_path = os.path.join(PROJECT_ROOT, 'results', '结果提交_最终完整版.xlsx')
    if not os.path.exists(excel_path):
        print(f"[FAIL] 未找到最终提交 Excel: {excel_path}")
        all_pass = False
    else:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        expected_sheets = [
            'Q1_单点组批',
            'Q2_运输架次',
            'Q2_逐箱交付',
            'Q3_中继架次',
            'Q3_通信保障',
            'Q4_分区配置'
        ]
        actual_sheets = wb.sheetnames
        missing_sheets = [s for s in expected_sheets if s not in actual_sheets]
        if missing_sheets:
            print(f"[FAIL] Excel 缺失工作表: {missing_sheets}")
            all_pass = False
        else:
            print(f"[PASS] Excel 6 个标准工作表全部存在且完整！")
            for s in expected_sheets:
                ws = wb[s]
                print(f"   - {s}: {ws.max_row} 行 x {ws.max_column} 列")
                
    print("\n" + "=" * 70)
    if all_pass:
        print("【终验结论】: 全部检查项 100% 达成 (ALL PASS)！具备最高竞赛提交质量！")
    else:
        print("【终验结论】: 存在未通过检查项，请检查上方日志！")
    print("=" * 70)
    return all_pass

if __name__ == '__main__':
    success = run_all_verification()
    sys.exit(0 if success else 1)
