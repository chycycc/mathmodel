# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET

docx_path = '数模题目/D题/山区洪涝灾害下无人机运输与通信协同优化.docx'

with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read('word/document.xml')

root = ET.fromstring(xml_content)

w_ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
m_ns = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def omath_to_latex(node):
    tag = node.tag.replace(f'{{{m_ns}}}', '')
    
    if tag == 't':
        return node.text or ''
    elif tag == 'f':
        # 分数 \frac{num}{den}
        num = ''
        den = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'num':
                num = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'den':
                den = ''.join(omath_to_latex(c) for c in child)
        return f"\\frac{{{num}}}{{{den}}}"
    elif tag == 'sSup':
        # 上标 base^{sup}
        base = ''
        sup = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'e':
                base = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'sup':
                sup = ''.join(omath_to_latex(c) for c in child)
        return f"{{{base}}}^{{{sup}}}"
    elif tag == 'sSub':
        # 下标 base_{sub}
        base = ''
        sub = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'e':
                base = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'sub':
                sub = ''.join(omath_to_latex(c) for c in child)
        return f"{{{base}}}_{{{sub}}}"
    elif tag == 'sSubSup':
        # 上下标 base_{sub}^{sup}
        base = ''
        sub = ''
        sup = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'e':
                base = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'sub':
                sub = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'sup':
                sup = ''.join(omath_to_latex(c) for c in child)
        return f"{{{base}}}_{{{sub}}}^{{{sup}}}"
    elif tag == 'rad':
        # 根号 \sqrt[deg]{e}
        deg = ''
        base = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'deg':
                deg = ''.join(omath_to_latex(c) for c in child)
            elif c_tag == 'e':
                base = ''.join(omath_to_latex(c) for c in child)
        if deg:
            return f"\\sqrt[{deg}]{{{base}}}"
        return f"\\sqrt{{{base}}}"
    elif tag == 'd':
        # 括号
        content = ''
        for child in node:
            c_tag = child.tag.replace(f'{{{m_ns}}}', '')
            if c_tag == 'e':
                content = ''.join(omath_to_latex(c) for c in child)
        return f"({content})"
    else:
        # 其他递归处理
        return ''.join(omath_to_latex(c) for c in node)

lines = []
for p in root.iter(f'{{{w_ns}}}p'):
    p_text = []
    for child in p:
        tag = child.tag
        if tag == f'{{{m_ns}}}oMath' or tag == f'{{{m_ns}}}oMathPara':
            latex_expr = omath_to_latex(child).strip()
            p_text.append(f" ${latex_expr}$ ")
        else:
            for sub in child.iter():
                s_tag = sub.tag
                if s_tag == f'{{{w_ns}}}t' and sub.text:
                    p_text.append(sub.text)
    full_line = ''.join(p_text).strip()
    if full_line:
        lines.append(full_line)

with open('scratch/problem_text_latex.md', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(lines))

print(f"Parsed {len(lines)} paragraphs with full LaTeX math formulas!")
