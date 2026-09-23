# -*- coding: utf-8 -*-
with open('scratch/problem_text_latex.md', encoding='utf-8') as f:
    text = f.read()

idx = text.find('附录 2')
if idx != -1:
    end_idx = text.find('附录 3', idx)
    app2_text = text[idx:end_idx] if end_idx != -1 else text[idx:]
    with open('scratch/appendix2_audit.txt', 'w', encoding='utf-8') as out:
        out.write(app2_text)
    print("Extracted Appendix 2 successfully!")
else:
    print("Appendix 2 not found!")
