# -*- coding: utf-8 -*-
"""
论文编译脚本
调用 typst 原生 Rust 编译器将 paper/main.typ 编译为 paper/main.pdf
并输出编译耗时、页数与文件大小
"""

import time
import os
import typst

def compile_paper():
    print("==========================================================")
    print("开始编译 Typst 华为杯论文工程")
    print("源文件: paper/main.typ -> 目标: paper/main.pdf")
    print("==========================================================")
    
    start_time = time.time()
    try:
        typst.compile("paper/main.typ", output="paper/main.pdf", root=".")
        elapsed = time.time() - start_time
        size_kb = os.path.getsize("paper/main.pdf") / 1024.0
        print(f"\n编译成功！耗时: {elapsed:.2f} 秒, 生成 PDF 大小: {size_kb:.1f} KB")
        return True
    except Exception as e:
        print(f"\n编译失败: {e}")
        return False

if __name__ == '__main__':
    compile_paper()
