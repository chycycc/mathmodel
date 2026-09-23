# -*- coding: utf-8 -*-
"""
诊断并修复 Typst 语法问题脚本
确保所有独立公式均包裹在 $ ... $ 中，正文中的小于号正确置于数学环境
"""

import os
import glob
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修复正文中的 SOC<90%
    content = content.replace("（SOC<90%）", "（$" + "SOC" + " < 90%$）")
    content = content.replace("SOC < 90%", "$" + "SOC" + " < 90%$")
    content = content.replace("SOC < 0.90", "$" + "SOC" + " < 0.90$")

    # 2. 检查未被 $ 包裹的公式段落
    lines = content.splitlines()
    new_lines = []
    in_raw = False
    in_math = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_raw = not in_raw
            new_lines.append(line)
            continue
            
        if in_raw:
            new_lines.append(line)
            continue

        # 检查是否是单行公式却漏了 $
        if stripped.startswith('$') and stripped.endswith('$') and len(stripped) > 1:
            new_lines.append(line)
            continue

        if stripped == '$':
            in_math = not in_math
            new_lines.append(line)
            continue

        if in_math:
            new_lines.append(line)
            continue

        # 如果在普通正文中，包含典型数学符号如 <=, sum_, max_t, arg max 却不在 $ 里
        math_triggers = [
            'E_("round")', 'W_("safe")', 'sum_m y_', 'sum_(k in', 'E_p <=',
            'z_("ray")', '100.04 + 20 lg', 'N_m^((k)) =', 'B_m^((k)) =',
            'd = 2 R_("earth")', 'R(m, w) =', 'E_("out")', 'E_("back")',
            '(diff E_("round"))', 'Delta E_j =', 'Delta t_("charge") =',
            't_("start")^(p\')', 't_("start")^(p\'\')', 't_("deliv")^k <=',
            'W_(i j) =', 'S002, S004 in'
        ]
        
        is_isolated_formula = False
        for trig in math_triggers:
            if trig in stripped and not stripped.startswith('#') and not stripped.startswith('*') and not stripped.startswith('-'):
                is_isolated_formula = True
                break
                
        if is_isolated_formula:
            # 把它包裹成独立公式
            new_lines.append('$')
            new_lines.append(stripped)
            new_lines.append('$')
        else:
            new_lines.append(line)

    fixed_content = '\n'.join(new_lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

def main():
    for f in glob.glob('paper/**/*.typ', recursive=True):
        fix_file(f)
    print("Typst 文件语法修复完成！")

if __name__ == '__main__':
    main()
