# -*- coding: utf-8 -*-
import os
import shutil

def archive():
    print("开始执行工作区历史快照归档与重整...")
    
    # 创建目标目录
    os.makedirs('legacy_archive/reports', exist_ok=True)
    os.makedirs('legacy_archive/results', exist_ok=True)
    os.makedirs('legacy_archive/code_debug', exist_ok=True)

    # 1. 迁移 paper 目录
    if os.path.exists('paper'):
        if os.path.exists('legacy_archive/paper'):
            shutil.rmtree('legacy_archive/paper')
        shutil.move('paper', 'legacy_archive/paper')
        print(" -> 已迁移: paper/ => legacy_archive/paper/")

    # 2. 迁移 figures 目录
    if os.path.exists('figures'):
        if os.path.exists('legacy_archive/figures'):
            shutil.rmtree('legacy_archive/figures')
        shutil.move('figures', 'legacy_archive/figures')
        print(" -> 已迁移: figures/ => legacy_archive/figures/")

    # 3. 迁移旧 reports
    old_reports = ['Q1_Q2_RESULTS_REPORT.md', 'DRAWIO_REPORT.md', 'Q1_Q2_VERIFY_REPORT.md']
    for r in old_reports:
        src = os.path.join('reports', r)
        dst = os.path.join('legacy_archive/reports', r)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f" -> 已归档报告: {r}")

    # 4. 迁移旧 results (Q3, Q4, 旧模板)
    old_results = ['Q3_中继架次.csv', 'Q3_通信保障.csv', 'Q4_分区配置.csv', '结果提交模板.xlsx']
    for res in old_results:
        src = os.path.join('results', res)
        dst = os.path.join('legacy_archive/results', res)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f" -> 已归档旧结果: {res}")

    # 5. 迁移 code 调试临时脚本
    debug_scripts = [
        'apply_final_fixes.py', 'apply_specific_fixes.py', 'compile_paper.py', 'debug_compile.py',
        'find_line_err.py', 'find_math_err.py', 'fix_hav.py', 'fix_math_constants.py', 'fix_syms.py',
        'fix_typst_syntax.py', 'make_drawio.py', 'render_drawio_pdf.py', 'test_block.py', 'test_full.py',
        'test_math_syntax.py', 'test_q1.py'
    ]
    for s in debug_scripts:
        src = os.path.join('code', s)
        dst = os.path.join('legacy_archive/code_debug', s)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f" -> 已归档临时脚本: {s}")

    print("\n历史快照归档全部顺利完成！")

if __name__ == '__main__':
    archive()
