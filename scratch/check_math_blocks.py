# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET

docx_path = '数模题目/D题/山区洪涝灾害下无人机运输与通信协同优化.docx'

with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read('word/document.xml')

root = ET.fromstring(xml_content)

w_ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
m_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

math_blocks = []
for p in root.iter(f'{{{w_ns}}}p'):
    # 查看段落文字和其中的公式
    p_txt = []
    has_math = False
    for child in p.iter():
        if child.tag == f'{{{w_ns}}}t' and child.text:
            p_txt.append(child.text)
        elif child.tag == f'{{{m_ns}}}t' and child.text:
            p_txt.append(f"[MATH:{child.text}]")
            has_math = True
    full = ''.join(p_txt).strip()
    if has_math:
        math_blocks.append(full)

with open('scratch/all_docx_math_blocks.txt', 'w', encoding='utf-8') as f:
    for b in math_blocks:
        f.write(b + '\n\n')

print(f"Total paragraphs with math: {len(math_blocks)}")
