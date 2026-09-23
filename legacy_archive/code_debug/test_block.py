# -*- coding: utf-8 -*-
import typst

with open('paper/sections/5_problem1.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# 按段落测试
blocks = text.split('\n\n')
print(f"Total blocks: {len(blocks)}")

# 逐步累加段落
for i in range(1, len(blocks) + 1):
    sub = '\n\n'.join(blocks[:i])
    with open('paper/_tmp_b.typ', 'w', encoding='utf-8') as fp:
        fp.write(sub)
    try:
        typst.compile('paper/_tmp_b.typ', output='paper/_tmp_b.pdf')
    except Exception as e:
        if 'unclosed delimiter' in str(e):
            print(f"Error at block {i}:")
            print(blocks[i-1])
            break
