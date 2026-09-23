# -*- coding: utf-8 -*-
"""
替换 Typst 公式中的节点常量为带引号文本
如 O01 -> "O01", S002 -> "S002", BAT_A_01 -> "BAT_A_01" 等
"""

import glob
import re

CONSTANTS = [
    'O01', 'S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007',
    'S008', 'S009', 'S010', 'S011', 'S012', 'S013', 'S014', 'S015',
    'U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07', 'U08',
    'R01', 'R02', 'RT01', 'RT02', 'RT03', 'RT04', 'RT05', 'RT06',
    'G01'
]

def fix_math_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 处理段落中 $...$ 内部的常量
    def replace_in_math(match):
        text = match.group(0)
        for c in CONSTANTS:
            # 避免重复加引号
            text = re.sub(r'(?<!")\b' + c + r'\b(?!")', f'"{c}"', text)
        return text

    # 替换单行或多行公式 $ ... $
    content = re.sub(r'\$[^$]+\$', replace_in_math, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for f in glob.glob('paper/**/*.typ', recursive=True):
        fix_math_in_file(f)
    print("公式常量引号处理完毕！")

if __name__ == '__main__':
    main()
